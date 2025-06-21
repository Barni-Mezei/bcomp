#include <stdbool.h>
#include <avr/pgmspace.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library.
#define SCREEN_ADDRESS 0x3C // See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

int line_index = 0; // The current line index on the display (for scrolling)
int char_index = 0; // The current char index on the display (for scrolling)
bool was_updated = false;

const char PROGMEM Instruction_names[][4] = {
  "NOP\0", //0
  "MVA\0",
  "MVB\0",
  "MAB\0",
  "MCA\0",
  "MCB\0", //5
  "ADD\0",
  "INC\0",
  "SUB\0",
  "DEC\0",
  "BOR\0", //10
  "SET\0",
  "AND\0",
  "MSK\0",
  "XOR\0",
  "ENC\0", //15
  "NOT\0",
  "SHR\0",
  "SHL\0",
  "CMP\0",
  "ADR\0", //20
  "SRV\0",
  "SRA\0",
  "SWV\0",
  "SWA\0",
  "LDA\0", //25
  "LDB\0",
  "STV\0",
  "STA\0",
  "STB\0",
  "CPY\0", //30
  "JMP\0",
  "JSR\0",
  "JIC\0",
  "JIN\0",
  "JIO\0", //35
  "RTN\0",
  "OUT\0",
  "INP\0",
  "?39\0",
  "?40\0", //40
  "?41\0",
  "?42\0",
  "?43\0",
  "?44\0",
  "?45\0", //45
  "?46\0",
  "?47\0",
  "?48\0",
  "?49\0",
  "DBG\0", //50
  "?51\0",
  "?52\0",
  "?53\0",
  "?54\0",
  "?55\0", //55
  "?56\0",
  "?57\0",
  "?58\0",
  "?59\0",
  "?60\0", //60
  "?61\0",
  "?62\0",
  "HLT\0",
};

typedef struct {
  unsigned int ins;
  unsigned int arg;
} Command;

// max dynamic memory: 41%

const PROGMEM Command rom[] = {
{1,1},
{38,0},
{1,0},
{38,0},
{31,0},

};

int rom_index = 0;
int rom_length = sizeof(rom) / sizeof(rom[0]);

int state = 0;  //0: console mode, 1: executing instructions, 2: waiting for input

int program_counter = 0;
char flags = 0b00000000; //-----cnz carry, negative, zero
unsigned int registers[] = {
  0, //0: A auxillary A
  0, //1: B auxillary B
  0, //2: AC accumulation
  0, //3: RADR read address
  0, //4: WADR write address
  0, //5: INS write address
  0, //6: ARG write address
};

unsigned int memory[64] = {};
unsigned int call_stack[8] = {};
int cs_index = 0;

enum REGISTER_INDEX {
  rA,
  rB,
  rAC,
  rRADR,
  rWADR,
  rINS,
  rARG,
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

#define RA registers[rA]
#define RB registers[rB]
#define RAC registers[rAC]
#define RRADR registers[rRADR]
#define RWADR registers[rWADR]
#define RINS registers[rINS]
#define RARG registers[rARG]

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
          RA = 0; //Reset registers
          RB = 0;
          RAC = 0;
          RRADR = 0;
          RWADR = 0;
          RARG = 0;
          RINS = 0;

          line_index = 1;
          device_display_row_index = 0;

          //Lazy update counter
          int i = 0;

          //Execute commands
          while (program_counter > -1 && program_counter < rom_length) {
            RINS = pgm_read_word(&(rom[program_counter].ins));
            RARG = pgm_read_word(&(rom[program_counter].arg));

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
    display.print("A: "); display.println(RA);
    display.print("B: "); display.println(RB);
    display.print("AC: "); display.println(RAC);
    display.print("RADR: "); display.println(RRADR);
    display.print("WADR: "); display.println(RWADR);
    display.display();
  }

  Serial.println(F("Registers:"));
  Serial.print(F("A: ")); Serial.println(RA);
  Serial.print(F("B: ")); Serial.println(RB);
  Serial.print(F("AC: ")); Serial.println(RAC);
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

int executeCommand() {
  switch (RINS) {
    case 0: //NOP
      break;

    case 1: //MVA
      RA = RARG;
      break;

    case 2: //MVB
      RB = RARG;
      break;

    case 3: //MAB
      RB = RA;
      break;

    case 4: //MCA
      RA = RAC;
      break;

    case 5: //MCB
      RB = RAC;
      break;

    case 6: //ADD
      RAC = RA + RB;

      flags = 0;
      if (RA + RB > 65535) flags |= FC;
      if (RAC == 0) flags |= FZ;
      break;

    case 7: //INC
      RAC = RA + RARG;

      flags = 0;
      if (RA + RARG > 65535) flags |= FC;
      if (RAC == 0) flags |= FZ;
      break;

    case 8: //SUB
      flags = 0;

      if (RB > RA) {
        RAC = RB - RA;
        flags |= FC | FN;
      } else {
        RAC = RA - RB;
      }

      if (RAC == 0) flags |= FZ;
      break;

    case 9: //DEC
      flags = 0;

      if (RARG > RA) {
        RAC = RARG - RA;
        flags |= FC | FN;
      } else {
        RAC = RA - RARG;
      }

      if (RAC == 0) flags |= FZ;
      break;

    case 10: //BOR
      RAC = RA | RB;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 11: //SET
      RAC = RA | RARG;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 12: //AND
      RAC = RA & RB;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 13: //MSK
      RAC = RA & RARG;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 14: //XOR
      RAC = RA ^ RB;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 15: //ENC
      RAC = RA ^ RARG;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 16: //NOT
      RAC = !RA;

      flags = 0;
      if (RAC == 0) flags |= FZ;
      break;

    case 17: //SHR
      flags = 0;
      if (RA & 1 == 1) flags |= FC;

      RAC = RA >> 1;

      if (RAC == 0) flags |= FZ;
      break;

    case 18: //SHL
      flags = 0;
      if (RA & -1 == 1) flags |= FC;

      RAC = RA << 1;

      if (RAC == 0) flags |= FZ;
      break;

    case 19: //CMP
      RAC = RA == RARG ? 0 : (RA < RARG ? 1 : 2);
      break;

    case 20: //ADR
      RRADR = RARG;
      RWADR = RARG;
      break;

    case 21: //SRV
      RRADR = RARG;
      break;

    case 22: //SRA
      RRADR = RA;
      break;

    case 23: //SWV
      RWADR = RARG;
      break;

    case 24: //SWA
      RWADR = RA;
      break;

    case 25: //LDA
      RA = getMem(RRADR);
      break;

    case 26: //LDB
      RB = getMem(RRADR);
      break;

    case 27: //STI
      setMem(RWADR, RARG);
      break;

    case 28: //STA
      setMem(RWADR, RA);
      break;

    case 29: //STB
      setMem(RWADR, RB);
      break;

    case 30: //CPY
      setMem(RWADR, getMem(RRADR));
      break;

    case 31: //JMP
      return RARG;
      break;

    case 32: //JSR
      callStackPush(program_counter);
      return RARG;
      break;

    case 33: //JIC
      if (flags & FC) return RARG;
      break;

    case 34: //JIN
      if (flags & FN) return RARG;
      break;

    case 35: //JIO
      if (flags & FZ) return RARG;
      break;

    case 36: //RTN
      {
        int new_address = callStackPop();
        if (new_address != -1) return new_address + 1;
      }
      break;

    case 37: //OUT
      if (LOG_DEVICE) {
        Serial.print(F("port"));
        Serial.print(RARG);
        Serial.print(F(": "));
        Serial.println(RA);
      }

      was_updated = true;

      //Emulate devices connected to different ports
      switch (RARG) {
        case 0:
          //Pin output
          PORTB = (uint8_t)(RA & 0b0000000000111111);
          break;

        case 1:
          //Console output (number)
          if (line_index > 7) {
            display.fillRect(64, 8, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK);
            line_index = 1;
          }

          display.setCursor(64, line_index*8);
          display.println(RA);

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
          display.print((char)RA);

          char_index++;
          break;

        case 3:
          //Display control
          if (RA & 0b1000000000000000) {
            //Command mode
            if (RA ^ 0b1100000000000000 == 0) {
              //Flush display
              if (LOG_DEVICE) {
                Serial.println(F("Flushing display!"));
              }
              display.display();
            }
          } else {
            //Row index mode
            device_display_row_index = RA;
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
            bool value = ((RA >> i) & 1) != 0;
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


    case 38: //INP
      //Emulate devices connected to different ports
      switch (RARG) {
        case 0:
          //Pin input
          RA = (unsigned int)(PIND >> 2);
          break;

        case 1:
          //Serial prompt (number)
          RA = 0;
          break;

        case 2:
          //Time
          RA = millis() & 65535;
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
