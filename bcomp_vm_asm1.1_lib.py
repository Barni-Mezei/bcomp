import sys
from lib import *
import matrixLib
import keyboard
from time import sleep

if len(sys.argv) > 1 and not ".o" in sys.argv[1]:
    print(f"{RED}Invalid or missing file type! (Must be .o){WHITE}")
    exit()

class Bcomp:
    NUMBER_OF_BITS = 16
    MAX_NUMBER = 2**NUMBER_OF_BITS
    MEMORY_SIZE = 256

    ########################
    ## Machine components ##
    ########################

    registers = {
        'a': 0,
        'b': 0,
        'ac': 0,
        'adr': 0,
        'arg': 0,
        'ins': 0,
    }
    flags = {
        'zero': False,
        'overflow': False,
        'negative': False,
    }
    rom = []
    memory = []
    call_stack = []
    ports = {
        'input': None,
        'output':  None,
    }

    break_points = []
    counter = 0
    has_jumped = False
    result = "" #Result of the last execution

    command_lookup = []

    def initialiseMemory(self): self.memory = [0 for _ in range(0, self.MEMORY_SIZE)]

    def __init__(self, number_of_bits : int = 16, memory_size : int = 256) -> None:
        self.NUMBER_OF_BITS = number_of_bits
        self.MAX_NUMBER = 2**self.NUMBER_OF_BITS
        self.MEMORY_SIZE = memory_size

        self.ports['input'] = [[False, 0] for _ in range(0, 8)]
        self.ports['output'] = [[False, 0] for _ in range(0, 8)]
        self.initialiseMemory()

        commands = load_commands(False)
        self.command_lookup = ["" for _ in range(0, 32)]
        for key in commands: self.command_lookup[int(commands[key][0])] = key


    def getMnemonic(self, binNumber : str):
        return self.command_lookup[binToDec(binNumber)]

    def bitwiseNot(number : int, length : int = NUMBER_OF_BITS) -> int:
        out = list(decToBin(number, length))
        for i, chr in enumerate(out):
            out[i] = "0" if chr == "1" else "1"
        return binToDec("".join(out))


    def execute(self, instruction : int, argument : int, breakpoint: int) -> bool:
        #Read command
        self.registers['arg'] = argument#binToDec(self.rom[counter][0])
        self.registers['ins'] = instruction#binToDec(self.rom[counter][1])
        mnemonic = self.command_lookup[instruction]

        local_debug = self.debug or breakpoint != 0
        self.has_jumped = False

        match mnemonic:
            case "nop":
                if local_debug: print("- Doing nothing")
                sleep(0.1)
            
            case "lda":
                if local_debug:
                    print(f"- Loading {self.registers['arg']} to RA")
                self.registers['a'] = self.registers['arg']

            case "ldb":
                if local_debug:
                    print(f"- Loading {self.registers['arg']} to RB")
                self.registers['b'] = self.registers['arg']

            case "mca":
                if local_debug:
                    print(f"- Loading RAC ({self.registers['ac']}) to RA")
                self.registers['a'] = self.registers['ac']

            case "mac":
                if local_debug:
                    print(f"- Loading RA ({self.registers['a']}) to RAC")
                self.registers['ac'] = self.registers['a']

            case "mab":
                if local_debug:
                    print(f"- Loading RA ({self.registers['a']}) to RB")
                self.registers['b'] = self.registers['a']

            case "mbc":
                if local_debug:
                    print(f"- Loading RB ({self.registers['b']}) to RAC")
                self.registers['ac'] = self.registers['b']

            case "add":
                if local_debug:
                    print(f"- Adding RA ({self.registers['a']}) and RB ({self.registers['b']}) [a+b]")

                self.registers['ac'] = self.registers['a'] + self.registers['b']

                self.flags['negative'] = False
                self.flags['overflow'] = False

                if self.registers['ac'] > self.MAX_NUMBER:
                    self.registers['ac'] = binToDec((bin(self.registers['ac']).replace("0b", "")+".")[-self.NUMBER_OF_BITS-1:-1])
                    self.flags['overflow'] = True

                self.flags['zero'] = self.registers['ac'] == 0

            case "sub":
                if local_debug:
                    print(f"- Subtracting RB ({self.registers['b']}) from RA ({self.registers['a']}) [a-b]")

                self.registers['ac'] = self.registers['a'] - self.registers['b']

                self.flags['negative'] = False
                self.flags['overflow'] = False

                if self.registers['ac'] < 0:
                    self.registers['ac'] = abs(self.registers['ac'])
                    self.flags['negative'] = True
        
                if self.registers['ac'] > self.MAX_NUMBER:
                    self.registers['ac'] = binToDec((bin(self.registers['ac']).replace("0b", "")+".")[-self.NUMBER_OF_BITS-1:-1])
                    self.flags['overflow'] = True

                self.flags['zero'] = self.registers['ac'] == 0

            case "and":
                if local_debug:
                    print(f"- Bitwise AND of RA ({self.registers['a']}) and RB ({self.registers['b']}) [a&b]")
                self.registers['ac'] = self.registers['a'] & self.registers['b']

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "bor":
                if local_debug:
                    print(f"- Bitwise OR of RA ({self.registers['a']}) and RB ({self.registers['b']}) [a|b]")
                self.registers['ac'] = self.registers['a'] | self.registers['b']

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "xor":
                if local_debug:
                    print(f"- Bitwise XOR of RA ({self.registers['a']}) and RB ({self.registers['b']}) [a|b]")
                self.registers['ac'] = self.registers['a'] ^ self.registers['b']

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "not":
                if local_debug:
                    print(f"- Bitwise NOT of RA ({self.registers['a']}) [~a]")
                self.registers['ac'] = self.bitwiseNot(self.registers['a'])

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "shl":
                if local_debug:
                    print(f"- Left shifting RA ({self.registers['a']}) [a<<1]")
                self.registers['ac'] = trimToSize(self.registers['a'] << 1, self.NUMBER_OF_BITS)

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "shr":
                if local_debug:
                    print(f"- Right shifting RA ({self.registers['a']}) [a>>1]")
                self.registers['ac'] = self.registers['a'] >> 1

                self.flags['negative'] = False
                self.flags['overflow'] = False
                self.flags['zero'] = self.registers['ac'] == 0

            case "adr":
                if local_debug:
                    print(f"- Setting address to {self.registers['arg']}")
                self.registers['adr'] = trimToSize(self.registers['arg'], 8)

            case "ara":
                if local_debug:
                    print(f"- Setting address from RA ({self.registers['a']})")
                self.registers['adr'] = trimToSize(self.registers['a'], 8)

            case "ldi":
                if local_debug:
                    print(f"- Writing to memory[{self.registers['adr']}] = {self.registers['arg']}")
                self.memory[self.registers['adr']] = self.registers['arg']

            case "str":
                if local_debug:
                    print(f"- Writing to memory[{self.registers['adr']}] = RAC ({self.registers['ac']})")
                self.memory[self.registers['adr']] = self.registers['ac']

            case "mov":
                if local_debug:
                    print(f"- Reading from memory[{self.registers['adr']}] ({self.memory[self.registers['adr']]}) to RA")
                self.registers['a'] = self.memory[self.registers['adr']]

            case "clk":
                if local_debug:
                    print(f"- Loading counter ({self.counter}) to RA")
                self.registers['a'] = self.counter

            case "jmp":
                if local_debug:
                    print(f"- Jumping to address {self.registers['arg']}")
                self.counter = self.registers['arg']
                self.has_jumped = True

            case "jsr":
                if local_debug:
                    print(f"- Jumping to subroutine {self.registers['arg']}, pushing to stack: {self.counter}")
                self.call_stack.append(self.counter)
                self.counter = self.registers['arg']
                self.has_jumped = True

            case "jic":
                if local_debug:
                    print(f"- Jumping to address {self.registers['arg']} condition: overflow value: {self.flags['overflow']}")
                if self.flags['overflow']:
                    self.counter = self.registers['arg']
                    self.has_jumped = True

            case "jin":
                if local_debug:
                    print(f"- Jumping to address {self.registers['arg']} condition: negative value: {self.flags['negative']}")
                if self.flags['negative']:
                    self.counter = self.registers['arg']
                    self.has_jumped = True

            case "jio":
                if local_debug:
                    print(f"- Jumping to address {self.registers['arg']} condition: null value: {self.flags['zero']}")
                if self.flags['zero']:
                    self.counter = self.registers['arg']
                    self.has_jumped = True

            case "rtn":
                return_address = self.call_stack.pop()
                if local_debug:
                    print(f"- Returning to address {return_address}")
                self.counter = return_address + 1 #It will continue on the next line (the curent address was pushed, JSR would run again)
                self.has_jumped = True

            case "out":
                if local_debug:
                    print(f"- Outputting to port[{self.registers['arg']}] from RA ({self.registers['a']})")
                self.ports['output'][self.registers['arg']] = [True, self.registers['a']]

            case "inp":
                self.handleInputDevices(self.registers['arg'])

                if local_debug:
                    print(f"- Inputting from port[{self.registers['arg']}] ({self.ports['input'][self.registers['arg']][1]}) to RA")
                self.registers['a'] = self.ports['input'][self.registers['arg']][1]

            case "hlt":
                if local_debug:
                    print(f"- Stopping program")
                return False   

        return True

    #############
    ## Devices ##
    #############

    def handleInputDevices(self, selectedDevice):
        if selectedDevice == 0: # Keyboard (last pressed key)
            pressed_keys = ["0" for _ in range(0, 16)]
            pressed_keys[0] = "1" if keyboard.is_pressed("w") else "0"
            pressed_keys[1] = "1" if keyboard.is_pressed("a") else "0"
            pressed_keys[2] = "1" if keyboard.is_pressed("s") else "0"
            pressed_keys[3] = "1" if keyboard.is_pressed("d") else "0"
            self.ports['input'][selectedDevice][1] = binToDec("".join(pressed_keys))

        if selectedDevice == 1: # Keyboard (number)
            user_in = input(f"{GRAY}# {WHITE}")
            if len(user_in) == 0: user_in = '0'
            self.ports['input'][selectedDevice][1] = int(user_in)

        if selectedDevice == 2: # Keyboard (letter)
            user_in = input(f"{GRAY}> {WHITE}")
            if len(user_in) == 0: user_in = ' '
            user_in = user_in[0]
            self.ports['input'][selectedDevice][1] = ord(user_in)

    def handleOutputDevices(self):
        #Console port[0]
        if self.ports['output'][0][0]:
            if debug: print(f"- DEVICE 'Console': Printing value")
            char_code = self.ports['output'][0][1]
            char = chr(char_code) if char_code >= 32 and char_code <= 127 else ' '
            print(f"{f'{GRAY}$ ' if self.result == 'break' else ''}{GRAY}{decToBin(self.ports['output'][0][1], 16)} {WHITE}{self.ports['output'][0][1]:>5d} {AQUA}{char}{WHITE}")
            self.ports['output'][0][0] = False

        #Display command port[1]
        if self.ports['output'][1][0]:
            #Command mode
            if decToBin(self.ports['output'][1][1], 16)[0] == "1":
                if self.debug: print(f"- DEVICE 'Display': Command mode")
                if decToBin(self.ports['output'][1][1], 16)[1] == "1": #0b11000000_00000000 -> flush
                    if self.debug: print(f"  Flush")
                    matrixLib.renderMatrix(self.devices['display']['matrix'], ".#")
            else:
                #Row index mode
                if self.debug: print(f"- DEVICE 'Display': Row index mode ({trimToSize(self.ports['output'][1][1], 4)})")
                self.devices['display']['row_index'] = trimToSize(self.ports['output'][1][1], 4)
            self.ports['output'][1][0] = False

        #Display row data port[2]
        if self.ports['output'][2][0]:
            if self.debug: print(f"- DEVICE 'Display': Writing row: {decToBin(self.ports['output'][2][1], 16)}")
            self.devices['display']['matrix'][self.devices['display']['row_index']] = [int(b) for b in decToBin(self.ports['output'][2][1], 16)]
            self.ports['output'][2][0] = False



bcomp = Bcomp(16)


def loadProgram(file_path):
    self.rom = []
    self.break_points = []

    print(f"--- Loading program to ROM: {AQUA}{file_path}{WHITE}")

    with open(file_path, "r", encoding="utf8") as f:
        for _, cmd in enumerate(f.readline().strip().split(";")):
            if cmd == "": continue

            cmd = cmd.strip().split(",")
            cmd = [int("0" if n == "" else n) for n in cmd]

            ins = decToBin(cmd[0], 8)
            arg = decToBin(cmd[1], 16)

            #print(f"{GRAY}{arg} {AQUA}{ins}{WHITE}")

            self.rom.append([arg, ins])
            self.break_points.append(0)



###############################
## Built-in console commands ##
###############################

def commandHelp():
    print("Available commands:")
    print(f"{AQUA}help {GRAY}Shows this menu{WHITE}")
    print(f"{AQUA}dump rom {GRAY}Gives info about the ROM{WHITE}")
    print(f"{AQUA}dump ram {GRAY}Gives info about the RAM{WHITE}")
    print(f"{AQUA}dump reg {GRAY}Gives info about the registers{WHITE}")
    print(f"{AQUA}dump port {GRAY}Gives info about the ports{WHITE}")
    print(f"{AQUA}dump stack {GRAY}Gives info about the stack{WHITE}")
    print(f"{AQUA}debug on {GRAY}Turns on debug mode{WHITE}")
    print(f"{AQUA}debug off {GRAY}Turns off debug mode{WHITE}")
    print(f"{AQUA}breakpoint clear {GRAY}Removes all breakpoints{WHITE}")
    print(f"{AQUA}breakpoint set {WHITE}[adress] [value] {GRAY}Sets the breakpoint at the given address to value (0: -, 1: print, 2: stop){WHITE}")
    print(f"{AQUA}breakpoint range {WHITE}[address from] [address to] {GRAY}Sets STOP breakpoints to all given addresses{WHITE}")
    print(f"{AQUA}load {WHITE}[file path] {GRAY}Loads the file to the ROM{WHITE}")
    print(f"{AQUA}run {GRAY}Executes the program or resumes the program{WHITE}")
    print(f"{AQUA}reset {GRAY}Resets the computer, NOT erasing the rom{WHITE}")
    print(f"{AQUA}exit {GRAY}Exits the VM{WHITE}")

def commandDumpRom(self):
    print("The ROM:")
    for i, line in enumerate(rom):
        command_name = getMnemonic(line[1]).upper()
        break_point = " "
        if break_points[i] == 1: break_point = f'{YELLOW}#{WHITE}'
        if break_points[i] == 2: break_point = f'{RED}#{WHITE}'
        arrow = f"{WHITE}->" if result == "" else f"{GRAY}->"
        if result != "" and counter == i + (0 if has_jumped else 1): arrow = f"{YELLOW}->"
        print(f"{i:>4d}: {GRAY}{line[0]} {AQUA}{line[1]}{WHITE} {break_point} {arrow} {AQUA}{command_name}{GRAY} {binToDec(line[0])}{WHITE}")

    print(f"{len(rom)} adresses used")

def commandDumpRam():
    segment_size = 48
    print("The RAM:", len(memory))
    for i, _ in enumerate(memory[0:segment_size]):
        col = [
            f"{WHITE}{i+offset*segment_size:>3d}: \
{GRAY}{decToBin(memory[i+offset*segment_size], 16)} \
{memory[i+offset*segment_size]:<5d}"
            for offset in range(0, int((len(memory)+1)/segment_size)+1)
            if i+offset*segment_size < len(memory)
        ]
        print("  ".join(col)+f"{WHITE}")

def commandDumpReg():
    print("Registers:")
    for _, name in enumerate(registers):
        value = registers[name]
        print(f"{AQUA}{name.ljust(3, ' ')} {WHITE}{value:<5d} {GRAY}{decToBin(value, NUMBER_OF_BITS)}{WHITE}")

def commandDumpPort():
    print(       f"{AQUA}Input ports:             Output ports:")
    print(f"{GRAY}0: {WHITE}Keyboard              Console            {GRAY}Keyboard: 2 bytes, with each bit representing a pressed key{WHITE}")
    print(f"{GRAY}1: {WHITE}Number input          Display commands   {GRAY}Number input: Waits for a number to be inputted. Stalls execution!{WHITE}")
    print(f"{GRAY}2: {WHITE}Letter input          Display row data   {GRAY}Letter input: Waits for a letter to be inputted. Stalls execution!{WHITE}")
    print(f"{GRAY}3: {WHITE}-                     -")
    print(f"{GRAY}4: {WHITE}-                     -")
    print(f"{GRAY}5: {WHITE}-                     -")
    print(f"{GRAY}6: {WHITE}-                     -")
    print(f"{GRAY}7: {WHITE}-                     -")

def commandDumpStack():
    print(f"The call stack ({len(call_stack)}):")
    for i, line in enumerate(call_stack):
        print(f"{i:>3d}: {AQUA}{line}{WHITE}")

def commandDebugOn():
    global debug

    print("Debug mode is turned on")
    debug = True

def commandDebugOff():
    global debug

    print("Debug mode is turned off")
    debug = False

def commandBreakpointClear():
    global break_points

    break_points = [0 for _ in break_points]

def commandBreakpointSet(line: str):
    global break_points

    local_tokens = line.split(" ")
    if len(local_tokens) != 4:
        print(f"{RED}ERROR: Not enough paramaters!{WHITE}")
        return
    if int(local_tokens[2]) < 0 or int(local_tokens[2]) >= len(break_points):
        print(f"{RED}ERROR: Index out of range!{WHITE}")
        return
    if int(local_tokens[3]) < 0 or int(local_tokens[3]) > 2:
        print(f"{RED}ERROR: Value out of range!{WHITE}")
        return
    print(f"Adding breakpoint to address: {local_tokens[2]} with value of: {local_tokens[3]}")
    break_points[int(local_tokens[2])] = int(local_tokens[3])

def commandBreakpointRange(line: str):
    global break_points

    local_tokens = line.split(" ")
    if len(local_tokens) < 4:
        print(f"{RED}ERROR: Not enough paramaters!{WHITE}")
        return
    if int(local_tokens[2]) < 0 or int(local_tokens[2]) >= len(break_points):
        print(f"{RED}ERROR: Address from is out of range!{WHITE}")
        return
    if int(local_tokens[3]) < 0 or int(local_tokens[3]) >= len(break_points):
        print(f"{RED}ERROR: Address to is out of range!{WHITE}")
        return
    if int(local_tokens[3]) < int(local_tokens[2]):
        print(f"{RED}ERROR: Address to is smaller than address from!{WHITE}")
        return
    print(f"Adding breakpoint to addresses {local_tokens[2]} to {local_tokens[3]}")

    for i in range(int(local_tokens[2]), int(local_tokens[3]) + 1):
        break_points[i] = 2

def commandLoad(line: str):
    local_tokens = line.split(" ")

    if len(local_tokens) < 2:
        print(f"{RED}ERROR: Not enough paramaters!{WHITE}")
        return
    if not ".o" in local_tokens[1]:
        print(f"{RED}ERROR: Invalid file type! (Must be .o){WHITE}")
        return

    try:
        loadProgram(local_tokens[1])
        commandReset()
        commandDumpRom()
    except FileNotFoundError as e:
        print(f"{RED}ERROR: File not found!{WHITE}")

def commandReset():
    global counter
    global debug
    global memory

    counter = 0
    debug = False
    memory = initialiseMemory()
    commandBreakpointClear()


##############################
## Start of the main script ##
##############################

memory = initialiseMemory()

#Load commands and construct key lookup table
print(f"--- Loading {AQUA}commands{WHITE}")

commands = load_commands(False)
command_lookup = ["" for _ in range(0, 32)]
for key in commands: command_lookup[int(commands[key][0])] = key

if len(sys.argv) >= 2: loadProgram(sys.argv[1])

print(f"--- Starting {AQUA}console{WHITE}")

commandDumpRom()

user_in = ""
debug = False
while user_in != "exit":
    try:
        user_in = input(f"{RED if result == 'break' else AQUA}: {GRAY}")
    except KeyboardInterrupt as e:
        break

    print(WHITE, end='')

    if user_in == "help": commandHelp()
    if user_in == "dump rom": commandDumpRom()
    if user_in == "dump ram": commandDumpRam()
    if user_in == "dump reg": commandDumpReg()
    if user_in == "dump port": commandDumpPort()
    if user_in == "dump stack": commandDumpStack()
    if user_in == "debug on": commandDebugOn()
    if user_in == "debug off": commandDebugOff()
    if user_in == "reset": commandReset()
    if " " in user_in and user_in.split(" ")[0] == "breakpoint" and user_in.split(" ")[1] == "set": commandBreakpointSet(user_in)
    if " " in user_in and user_in.split(" ")[0] == "breakpoint" and user_in.split(" ")[1] == "range": commandBreakpointRange(user_in)
    if " " in user_in and user_in.split(" ")[0] == "load": commandLoad(user_in)
    if user_in == "breakpoint clear":
        print("All breakpoints removed!")
        commandBreakpointClear()

    if user_in == "run" or (result == "break" and user_in == ""):
        #print(break_points)
        if result != "break":
            print(f"--- Starting {AQUA}execution{WHITE}")
            counter = 0
        while counter < len(rom):
            #Execute the command
            result = executeLine(counter)
            #Advance the clock
            counter += 1
            #IO
            handleOutputDevices()
            if result != "": break

        if result != "break": #  or counter >= len(rom) - 1
            print(f"--- Execution {AQUA}finished {WHITE}at address {counter - 1}")
            result = ""

#Close tkinter window
devices['display']['window'].destroy()
print(f"{WHITE}Bye!")