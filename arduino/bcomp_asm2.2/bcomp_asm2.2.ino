#include <stdbool.h>
#include <avr/pgmspace.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "./mnemonic.h";
#include "./rom.h";

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library.
#define SCREEN_ADDRESS 0x3C // See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

int line_index = 0; // The current line index on the display (for scrolling)
int char_index = 0; // The current char index on the display (for scrolling)
bool was_updated = false;

int state = 0;  //0: console mode, 1: executing instructions, 2: waiting for input

int program_counter = 0;
char flags = 0b00000000; //----icnz: in interrupt, carry, negative, zero
unsigned int instruction = 0;
unsigned int registers[] = {
  0, //0: SYS system register
  0, //1: A GP, alu input
  0, //2: B GP, alu input
  0, //3: C GP (usually alu output)
  0, //4: X GP (loop counter)
  0, //5: Y GP (loop counter)
  0, //6: RADR read address
  0, //7: WADR write address
};

unsigned int memory[32] = {};
unsigned int call_stack[8] = {};
int cs_index = 0;

enum REGISTER_INDEX {
  rSYS,
  rA,
  rB,
  rC,
  rX,
  rY,
  rRADR,
  rWADR,
};

/**
* Devices:
* OUT 0: Digital pins (from LSB to MSB 2 3 4 5 6 7)
* OUT 1: Console number + new line (char 04 is clear)
* OUT 2: COnsole character, no new line
* OUT 3: Display commands (number to set row index, MSB to send commands)
* OUT 4: Display row

* IN 0: Digital pins (from LSB to MSB 8 9 10 11 12 13?)
* IN 1: Serial input, wait for a number
* IN 2: millis(), with overflow
*/

unsigned int device_display_row_index = 0;
const int device_display_pixel_size = 4;

#define RSYS registers[rSYS]
#define RA registers[rA]
#define RB registers[rB]
#define RC registers[rC]
#define RX registers[rX]
#define RY registers[rY]
#define RRADR registers[rRADR]
#define RWADR registers[rWADR]

#define FI 0b00001000 // Mask for the interrupt flag
#define FC 0b00000100 // Mask for the carry flag
#define FN 0b00000010 // Mask for the negative flag
#define FZ 0b00000001 // Mask for the zero flag

#define LOG_DEVICE 0 // Log device updates
#define LOG_DEBUG 0 // Log every instruction
#define LAZY_DISPLAY 1 // 0 to update after OUT, 1 to update after HLT, N to update every Nth instruction

/**
* Commands:
* s: Set ROM (numbers separated by nonnumerical characters)
* l: List loaded program
* c: Clear program from rom
* r: Run program
*/

void setup() {
  Serial.begin(9600);

  // Set pin 8 9 10 11 12 13 as an outputa
  DDRB = 0b00011111;
  // Set pin 1 2 3 4 5 6 7 as an inputa
  DDRD = 0b00000000;

  // Initialize OLED display with address for 128x64
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    while (true);
  }

  Serial.println(F("BCOMP Ready!"));

  // Clear the buffer
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(1);

  display.setCursor(0, 0);
  display.println(F("BCOMP Ready!"));
  display.display();
}

void loop() {
  if (Serial.available() > 0) {
    switch (state) {
      case 0:  // Waiting for input
        String input = Serial.readStringUntil('\n');

        Serial.print(F("Input: "));
        Serial.println(input);

        // ROM set mode
        if (input.startsWith("s")) {
          //TODO: read until... don't use strings, bc of memory usage. Now it can only load 6 commands.
          Serial.println(F("Loading code..."));

          display.clearDisplay();
          display.setCursor(0, 0);
          display.println(F("Loading code..."));
          display.display();

          parseCommands(input.substring(2));
        }

        // List mode
        if (input.startsWith("l")) {
          Serial.print(F("Listing ROM ("));
          Serial.print(rom_length, DEC);
          Serial.println(F("):"));

          display.clearDisplay();
          display.setCursor(0, 0);
          display.print("Listing ROM (");
          display.print(rom_length);
          display.println("):");
          display.display();

          // Line index on the LCD display
          line_index = 1;

          for (int i = 0; i < rom_length; i++) {
            display.setCursor(0, (line_index)*8);
            printCmd(i, true);
            display.display();
            line_index++;
            if (line_index > 7) {
              display.fillRect(0, 8, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK);
              line_index = 1;
            }
          }
        }

        // Clear mode
        if (input.startsWith("c")) {
          Serial.println(F("Clearing ROM!"));

          display.clearDisplay();
          display.setCursor(0, 0);
          display.println("Clearing ROM...");
          display.display();

          /*for (int i = 0; i < rom_length; i++) {
            rom[i].ins = 0;
            rom[i].arg = 0;
          }*/

          rom_index = 0;
          rom_length = 0;
        }

        // Run program
        if (input.startsWith("r")) {
          Serial.print(F("Running code ("));
          Serial.print(rom_length, DEC);
          Serial.println("):");

          display.clearDisplay();
          display.setCursor(64, 0);
          display.print("Exec ");
          display.println(rom_length);
          display.display();

          program_counter = 0; //Start from the beginning
          flags = 0b00000000; //Reset flags
          instruction = 0; //Reset instruction
          RSYS = 0; //Reset registers
          RA = 0;
          RB = 0;
          RC = 0;
          RX = 0;
          RY = 0;
          RRADR = 0;
          RWADR = 0;

          line_index = 1;
          device_display_row_index = 0;

          //Lazy update counter
          int i = 0;

          //Execute commands
          while (program_counter > -1 && program_counter < rom_length) {
            instruction = pgm_read_word(&(rom[program_counter].ins));
            RSYS = pgm_read_word(&(rom[program_counter].arg));

            if (LOG_DEBUG) printCmd(program_counter, false);

            int result = executeCommand();
            if (result < 0) {
              if (result == -99) { // Halting
                program_counter = -1;
              } else {
                program_counter += 1;
              }
            } else {
              program_counter = result;
            }

            i++;
            if (LAZY_DISPLAY > 1 && i > LAZY_DISPLAY) {
              display.display();
              i = 0;
            }
          }

          logReg(false);

          display.fillRect(64, 0, 64, 8, BLACK);
          display.setCursor(64, 0);
          display.print("Done ");
          display.println(rom_length);
          display.display();
        }

        break;
    }
  }
}

void logReg(bool useDisplay) {
  if (useDisplay) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Registers:");
    display.print("SYS: "); display.println(RSYS);
    display.print("A: "); display.println(RA);
    display.print("B: "); display.println(RB);
    display.print("C: "); display.println(RC);
    display.print("X: "); display.println(RX);
    display.print("Y: "); display.println(RY);
    display.print("RADR: "); display.println(RRADR);
    display.print("WADR: "); display.println(RWADR);
    display.display();
  }

  Serial.println(F("Registers:"));
  Serial.print(F("SYS: ")); Serial.println(RSYS);
  Serial.print(F("A: ")); Serial.println(RA);
  Serial.print(F("B: ")); Serial.println(RB);
  Serial.print(F("C: ")); Serial.println(RC);
  Serial.print(F("X: ")); Serial.println(RX);
  Serial.print(F("Y: ")); Serial.println(RY);
  Serial.print(F("RADR: ")); Serial.println(RRADR);
  Serial.print(F("WADR: ")); Serial.println(RWADR);

  Serial.print(F("Flags: ["));
  if (flags & FC) Serial.print("c");
  if (flags & FN) Serial.print("n");
  if (flags & FZ) Serial.print("z");
  Serial.println(F("]"));
}

void logCallStack(bool useDisplay) {
  if (useDisplay) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Call stack:");
    display.display();
  }

  Serial.println(F("Call stack:"));

  for (int i = 0; i < cs_index; i++) {
    if (useDisplay) {
      display.print(call_stack[i]);
      display.print(", ");
    }

    Serial.print(call_stack[i]);
    Serial.println(F(", "));
  }

  if (useDisplay) {
    display.display();
  }
}

void callStackPush(int value) {
  if (cs_index >= sizeof(call_stack)/sizeof(call_stack[0])) {
    Serial.println(F("<!> Call stack overflow!"));
    return;
  }

  call_stack[cs_index++] = value;
}

int callStackPop() {
  if (cs_index <= 0) {
    Serial.println(F("<!> Call stack underflow!"));
    return -1;
  }

  return call_stack[--cs_index];
}

void setMem(int adr, int val) {
  if (adr < 0 || adr > sizeof(memory)/sizeof(memory[0])) {
    Serial.print(F("<!> Invalid memory address: "));
    Serial.print(adr);
    Serial.println(F("!"));
    return;
  }

  memory[adr] = val;
}

int getMem(int adr) {
  if (adr < 0 || adr > sizeof(memory)/sizeof(memory[0])) {
    Serial.print(F("<!> Invalid memory address: "));
    Serial.print(adr);
    Serial.println(F("!"));
    return;
  }

  return memory[adr];
}

int setZeroFlag(int value) {
  flags = 0;

  if (value == 0) flags |= FZ;
}

int executeCommand() {
  int arg1 =  (int)(RSYS & 0b0000000011111111);
  int arg2 = (int)((RSYS & 0b1111111100000000) >> 8);

  switch (instruction) {
    case 0: //NOP
      break;

    case 1: //STA
      RA = RSYS;
      break;

    case 2: //STB
      RB = RSYS;
      break;

    case 3: //STC
      RC = RSYS;
      break;

    case 4: //STX
      RX = RSYS;
      break;

    case 5: //STY
      RY = RSYS;
      break;

    case 6: //STR
      RRADR = RSYS;
      break;

    case 7: //STW
      RWADR = RSYS;
      break;

    case 8: //MOV
      registers[arg2] = registers[arg1];
      break;

    case 9: //ADD
      registers[arg1] = RA + RB;

      setZeroFlag(registers[arg1]);
      if (RA + RB > 65535) flags |= FC;
      break;

    case 10: //INC
      {
        int result = registers[arg1] + arg2;

        setZeroFlag(registers[arg1]);
        if (registers[arg1] + arg2 > 65535) flags |= FC;
        registers[arg1] = result;
      }
      break;

    case 11: //SUB
      flags = 0;
      if (RB > RA) {
        registers[arg1] = RB - RA;
        flags |= FC | FN;
      } else {
        registers[arg1] = RA - RB;
      }

      if (registers[arg1] == 0) flags |= FZ;
      break;

    case 12: //DEC
      {
        flags = 0;
        int result = 0;
        if (arg2 > registers[arg1]) {
          result = arg2 - registers[arg1];
          flags |= FC | FN;
        } else {
          result = registers[arg1] - arg2;
        }

        if (result == 0) flags |= FZ;
        registers[arg1] = result;
      }
      break;

    case 13: //BOR
      registers[arg1] = RA | RB;
      setZeroFlag(registers[arg1]);
      break;

    case 14: //SET
      RC = RA | RSYS;
      setZeroFlag(RC);
      break;

    case 15: //AND
      registers[arg1] = RA & RB;
      setZeroFlag(registers[arg1]);
      break;

    case 16: //MSK
      RC = RA & RSYS;
      setZeroFlag(RC);
      break;

    case 17: //XOR
      registers[arg1] = RA ^ RB;
      setZeroFlag(registers[arg1]);
      break;

    case 18: //ENC
      RC = RA ^ RSYS;
      setZeroFlag(RC);
      break;

    case 19: //NOT
      registers[arg1] = !RA;
      setZeroFlag(registers[arg1]);
      break;

    case 20: //SHR
      flags = 0;
      if (RA & 1 == 1) flags |= FC;
      registers[arg1] = RA >> 1;
      if (registers[arg1] == 0) flags |= FZ;
      break;

    case 21: //SHL
      flags = 0;
      if (RA & -1 == 1) flags |= FC;
      registers[arg1] = RA << 1;
      if (registers[arg1] == 0) flags |= FZ;
      break;

    case 22: //CMP
      RC = registers[arg1] == registers[arg2] ? 0 : (registers[arg1] < registers[arg2] ? 1 : 2);
      break;

    case 23: // FLG
      registers[arg1] = flags;
      break;

    case 24: //LDA
      registers[arg1] = getMem(RRADR);
      break;

    case 25: //SVV
      setMem(RWADR, RSYS);
      break;

    case 26: //SVR
      setMem(RWADR, registers[arg1]);
      break;

    case 27: //CPY
      setMem(RWADR, getMem(RRADR));
      break;

    case 28: //PSV
      break;

    case 29: //PSH
      break;

    case 30: //POP
      break;

    case 31: //JMP
      return RSYS;
      break;

    case 32: //JSR
      callStackPush(program_counter);
      return RSYS;
      break;

    case 33: //JIC
      if (flags & FC) return RSYS;
      break;

    case 34: //JIN
      if (flags & FN) return RSYS;
      break;

    case 35: //JIO
      if (flags & FZ) return RSYS;
      break;

    case 36: //RTN
      {
        int new_address = callStackPop();
        if (new_address != -1) return new_address + 1;
      }
      break;

    case 37: //RTI
      break;

    case 38: //OUT
      if (LOG_DEVICE) {
        Serial.print(F("port"));
        Serial.print(arg2);
        Serial.print(F(": "));
        Serial.println(registers[arg1]);
      }

      was_updated = true;

      //Emulate devices connected to different ports
      switch (arg2) {
        case 0:
          //Pin output
          PORTB = (uint8_t)(registers[arg1] & 0b0000000000111111);
          break;

        case 1:
          //Console output (number)
          if (line_index > 7) {
            display.fillRect(64, 8, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK);
            line_index = 1;
          }

          display.setCursor(64, line_index*8);
          display.println(registers[arg1]);

          line_index++;
          break;

        case 2:
          //Console output (character)
          if (char_index >= 10) {
            line_index++;
            char_index = 0;
          }

          if (line_index >= 8) {
            display.fillRect(64, 8, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK);
            line_index = 1;
          }

          display.setCursor(64 + char_index*6, line_index*8);
          display.print((char)registers[arg1]);

          char_index++;
          break;

        case 3:
          //Display control
          if (registers[arg1] & 0b1000000000000000) {
            //Command mode
            if (registers[arg1] ^ 0b1100000000000000 == 0) {
              //Flush display
              if (LOG_DEVICE) {
                Serial.println(F("Flushing display!"));
              }
              display.display();
            }
          } else {
            //Row index mode
            device_display_row_index = registers[arg1];
            if (LOG_DEVICE) {
              Serial.print(F("DISPLAY: Setting row index to "));
              Serial.println(device_display_row_index);
            }
          }
          break;

        case 4:
          //Display set row
          if (LOG_DEVICE) {
            Serial.print(F("Setting row ("));
            Serial.print(device_display_row_index);
            Serial.print(") to: ");
          }
          for (int i = 0; i < 16; i++) {
            bool value = ((registers[arg1] >> i) & 1) != 0;
            display.fillRect(
              i * device_display_pixel_size,// - device_display_pixel_size, //x
              (device_display_row_index & 0b0000000000001111) * device_display_pixel_size,// - device_display_pixel_size, //y (clamped to 4 bits)
              device_display_pixel_size, //width
              device_display_pixel_size, //height
              value //color
            );
            if (LOG_DEVICE) Serial.print(value);
          }
          if (LOG_DEVICE) Serial.println("");
          break;

        default:
          break;
      }

      if (!LAZY_DISPLAY) display.display();

      break;


    case 39: //INP
      //Emulate devices connected to different ports
      switch (arg2) {
        case 0:
          //Pin input
          registers[arg1] = (unsigned int)(PIND >> 2);
          break;

        case 1:
          //Serial prompt (number)
          registers[arg1] = 0;
          break;

        case 2:
          //Time
          registers[arg1] = (unsigned int)(millis() & 65535);
          break;

        default:
          break;
      }
      break;

    case 63: //HLT
      Serial.println(F("<!> HALT"));
      return -99;
      break;
    
    default:
      break;
  }

  return -1;
}

void parseCommands(String input) {
    int startIndex = 0;
    rom_index = 0;

    Serial.print(F("Parser: "));
    Serial.println(input);

    while (startIndex < input.length() && rom_index < sizeof(rom)/sizeof(rom[0])) {
      // Find the next command separator
      int endIndex = input.indexOf(';', startIndex);
      
      // If no more separators, set endIndex to the end of the string
      if (endIndex == -1) {
          endIndex = input.length();
      }

      // Extract the command and argument
      String command = input.substring(startIndex, endIndex);
      /*Serial.print(command);
      Serial.print(F(" -> "));*/

      // Find the position of the comma
      int commaIndex = command.indexOf(',');
      /*Serial.print(commaIndex);
      Serial.print(F(" "));
      Serial.print(command.substring(0, commaIndex));
      Serial.print(F(","));
      Serial.println(command.substring(commaIndex + 1));*/

      // Extract the numbers
      /*rom[rom_index].ins = command.substring(0, commaIndex).toInt();
      rom[rom_index].arg = command.substring(commaIndex + 1).toInt();*/
      
      rom_index++;
      startIndex = endIndex + 1; // Move to the next number
    }

    rom_length = rom_index;
}

char* binToStr(int val) {
  static char buf[17]; // 16 bits + null terminator
  buf[16] = '\0';
  for (int i = 0; i < 16; i++) {
    buf[15 - i] = (val & (1 << i)) ? '1' : '0';
  }

  return buf;
}

void printCmd(int index, bool useDisplay) {
  Command cmd;
  cmd.ins = pgm_read_word(&(rom[index].ins));
  cmd.arg = pgm_read_word(&(rom[index].arg));

  char ins_name[4] = "";
  strcpy_P(ins_name, Instruction_names[cmd.ins]);

  if (useDisplay) {
    display.print(ins_name);
    display.print(F(" "));
    display.println(binToStr(cmd.arg));
  }

  Serial.print(F("INS: "));
  Serial.print(ins_name);
  Serial.print(F(" ("));
  Serial.print(cmd.ins);
  Serial.print(F(") ARG: "));
  Serial.print(binToStr(cmd.arg));
  Serial.print(F(" ("));
  Serial.print(cmd.arg);
  Serial.println(F(")"));
}
