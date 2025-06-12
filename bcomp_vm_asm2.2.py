import sys
from lib.lib import *
import lib.matrixLib
#import keyboard # type: ignore
from time import sleep


if len(sys.argv) > 1 and not ".o" in sys.argv[1]:
    print(f"{RED}Invalid or missing file type! (Must be .o){WHITE}")
    exit()

NUMBER_OF_BITS = 16
MAX_NUMBER = 2**NUMBER_OF_BITS

########################
## Machine components ##
########################

devices = {
    'display': {
        'row_index': 0,
        'matrix': lib.matrixLib.createMatrix(16, 16, 0),
    },
}

registers = {
    'sys': 0,
    'a': 0,
    'b': 0,
    'c': 0,
    'x': 0,
    'y': 0,
    'radr': 0,
    'wadr': 0,
    'ins': 0,
}

flags = {
    'zero': False,
    'overflow': False,
    'negative': False,
}

rom = []
memory = []

stacks = {
    "call": {
        "size": 32,
        "value": [],
    },

    "data": {
        "size": 32,
        "value": [],
    },

    "int_reg": {
        "size": 32,
        "value": [],
    },

    "int_adr": {
        "size": 8,
        "value": [],
    },
}

ports = {
    'input': [[False, 0] for _ in range(0, 8)],
    'output':  [[False, 0] for _ in range(0, 8)],
}
break_points = []
counter = 0
has_jumped = False
result = "" #Result of the last program

def loadProgram(file_path):
    global rom
    global break_points

    rom = []
    break_points = []

    print(f"--- Loading program to ROM: {AQUA}{file_path}{WHITE}")

    with open(file_path, "r", encoding="utf8") as f:
        for i, cmd in enumerate(f.readline().strip().split(";")):
            if cmd == "": continue

            cmd = cmd.strip().split(",")
            cmd = [int("0" if n == "" else n) for n in cmd]

            ins = decToBin(cmd[0], 8)
            arg = decToBin(cmd[1], 16)

            #print(f"{GRAY}{arg} {AQUA}{ins}{WHITE}")

            rom.append([arg, ins])
            break_points.append(0)

def getMnemonic(binNumber : str):
    return command_lookup[binToDec(binNumber)]

def getReg(reg_index : int) -> int:
    return registers[list(registers.keys())[reg_index]]

def getRegKey(reg_index : int) -> int:
    return list(registers.keys())[reg_index]

def getRegName(reg_index : int) -> int:
    return "R" + list(registers.keys())[reg_index].upper()

def bitwiseNot(number : int, length : int = NUMBER_OF_BITS) -> int:
    out = list(decToBin(number, length))
    for i, chr in enumerate(out):
        out[i] = "0" if chr == "1" else "1"
    return binToDec("".join(out))

def initialiseMemory():
    return [0 for _ in range(0, 256)]

def pushToStack(value : int, stack_name : str):
    if len(stacks[stack_name]["value"]) < stacks[stack_name]["size"]:
        stacks[stack_name]["value"].append(value)

def popFromStack(stack_name : str):
    if len(stacks[stack_name]["value"]) > 0: return stacks[stack_name]["value"].pop()
    else: return 0

############################################
## The actual executor part of the script ##
############################################

def executeLine(index : int) -> str:
    global registers
    global memory
    global counter
    global has_jumped

    #Read command
    registers['sys'] = binToDec(rom[counter][0])
    registers['ins'] = binToDec(rom[counter][1])
    mnemonic = command_lookup[registers['ins']]

    arg1 = binToDec(rom[counter][0][8::])
    arg2 = binToDec(rom[counter][0][0:8])

    local_debug = debug or break_points[index] != 0
    has_jumped = False

    if debug:
        print(f"Clock: {index}\tCommand: {AQUA}{mnemonic}\t{WHITE}Breakpoint: {break_points[index]} Arg1: {arg1} Arg2. {arg2} {rom[counter][0]}")

    match mnemonic:
        case "nop":
            if local_debug: print("- Doing nothing")
            sleep(0.1)
        
        case "sta":
            if local_debug:
                print(f"- Setting RA to RSYS ({registers['sys']})")
            registers['a'] = registers['sys']

        case "stb":
            if local_debug:
                print(f"- Setting RB to RSYS ({registers['sys']})")
            registers['b'] = registers['sys']

        case "stc":
            if local_debug:
                print(f"- Setting RC to RSYS ({registers['sys']})")
            registers['c'] = registers['sys']

        case "stx":
            if local_debug:
                print(f"- Setting RX to RSYS ({registers['sys']})")
            registers['x'] = registers['sys']

        case "sty":
            if local_debug:
                print(f"- Setting RY to RSYS ({registers['sys']})")
            registers['y'] = registers['sys']

        case "str":
            if local_debug:
                print(f"- Setting RRADR to RSYS ({registers['sys']})")
            registers['radr'] = registers['sys']

        case "stw":
            if local_debug:
                print(f"- Setting RWADR to RSYS ({registers['sys']})")
            registers['wadr'] = registers['sys']

        case "mov":
            if local_debug:
                print(f"- Moving from {getRegName(arg1)} ({getReg(arg1)}) to {getRegName(arg2)} ({getReg(arg2)})")
            registers[getRegKey(arg1)] = getReg(arg2)

        case "add":
            if local_debug:
                print(f"- Adding RA ({registers['a']}) and RB ({registers['b']}) to {getRegName(arg1)}")

            result = registers['a'] + registers['b']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            if result >= MAX_NUMBER:
                result = trimToSize(result, NUMBER_OF_BITS)
                flags['overflow'] = True

            registers[getRegKey(arg1)] = result

        case "inc":
            if local_debug:
                print(f"- Incrementing {getRegName(arg1)} by {arg2}")

            result = getReg(arg1) + arg2

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            if result >= MAX_NUMBER:
                result = trimToSize(result, NUMBER_OF_BITS)
                flags['overflow'] = True

            registers[getRegKey(arg1)] = result

        case "sub":
            if local_debug:
                print(f"- Subtracting RB ({registers['b']}) from RA ({registers['a']}) to {getRegName(arg1)}")

            result = registers['a'] - registers['b']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            if result < 0:
                result = abs(result)
                flags['negative'] = True

            if result >= MAX_NUMBER:
                result = trimToSize(result, NUMBER_OF_BITS)
                flags['overflow'] = True

            registers[getRegKey(arg1)] = result

        case "dec":
            if local_debug:
                print(f"- Decrementing {getRegName(arg1)} by {arg2}")

            result = getReg(arg1) - arg2

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            if result < 0:
                result = abs(result)
                flags['negative'] = True

            if result >= MAX_NUMBER:
                result = trimToSize(result, NUMBER_OF_BITS)
                flags['overflow'] = True

            registers[getRegKey(arg1)] = result

        case "bor":
            if local_debug:
                print(f"- Bitwise OR of RA ({registers['a']}) and RB ({registers['b']}) to {getRegName(arg1)}")
            result = registers['a'] | registers['b']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "set":
            if local_debug:
                print(f"- Setting RC to RA ({registers['a']}) OR RSYS ({registers['sys']})")
            result = registers['a'] | registers['sys']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] =  result == 0

            registers['c'] = result

        case "and":
            if local_debug:
                print(f"- Bitwise AND of RA ({registers['a']}) and RB ({registers['b']}) to {getRegName(arg1)}")
            result = registers['a'] & registers['b']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "msk":
            if local_debug:
                print(f"- Setting RC to RA ({registers['a']}) AND RSYS ({registers['sys']})")
            result = registers['a'] & registers['sys']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] =  result == 0

            registers['c'] = result

        case "xor":
            if local_debug:
                print(f"- Bitwise XOR of RA ({registers['a']}) and RB ({registers['b']}) to {getRegName(arg1)}")
            result = registers['a'] ^ registers['b']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "enc":
            if local_debug:
                print(f"- Setting RC to RA ({registers['a']}) XOR RSYS ({registers['sys']})")
            result = registers['a'] ^ registers['sys']

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] =  result == 0

            registers['c'] = result

        case "not":
            if local_debug:
                print(f"- Bitwise NOT of RA ({registers['a']}) to {getRegName(arg1)}")
            result = bitwiseNot(registers['a'])

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "shr":
            if local_debug:
                print(f"- Right shifting RA ({registers['a']}) to {getRegName(arg1)}")
            result = registers['a'] >> 1

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "shl":
            if local_debug:
                print(f"- Left shifting RA ({registers['a']}) to {getRegName(arg1)}")
            result = trimToSize(registers['a'] << 1, NUMBER_OF_BITS)

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers[getRegKey(arg1)] = result

        case "cmp":
            if local_debug:
                print(f"- Comapring {getRegName(arg1)} with {getRegName(arg2)}")

            num_a = getReg(arg1)
            num_b = getReg(arg1)
            result = 0
            if num_a < num_b: result = 1
            if num_a > num_b: result = 2

            flags['negative'] = False
            flags['overflow'] = False
            flags['zero'] = result == 0

            registers['c'] = result

        case "flg":
            if local_debug:
                print(f"- Loading flags to {getRegName(arg1)}")

            # Flag bits: 00000000_00000cnz
            result = ["0" for _ in range(NUMBER_OF_BITS)]
            result[-1] = flags["zero"]
            result[-2] = flags["negative"]
            result[-3] = flags["carry"]

            registers[getRegKey(arg1)] = binToDec(result)

        case "lda":
            if local_debug:
                print(f"- Reading from memory[{registers['radr']}] ({memory[registers['radr']]}) to {getRegName(arg1)}")
            registers[getRegKey(arg1)] = memory[registers['radr']]

        case "svv":
            if local_debug:
                print(f"- Writing to memory[{registers['wadr']}] = RSYS ({registers['sys']})")
            memory[registers['wadr']] = registers['sys']

        case "svr":
            if local_debug:
                print(f"- Writing to memory[{registers['wadr']}] = {getRegName(arg1)} ({getReg(arg1)})")
            memory[registers['wadr']] = getReg(arg1)

        case "cpy":
            if local_debug:
                print(f"- Copying in memory[{registers['wadr']}] ({memory[registers['wadr']]})\
                       = memory[{registers['radr']}] ({memory[registers['radr']]})")
            memory[registers['wadr']] = memory[registers['radr']]

        case "psv":
            if local_debug:
                print(f"- Pushing RSYS ({registers['sys']}) to stack")

            pushToStack(registers["sys"], "data")

        case "psh":
            if local_debug:
                print(f"- Pushing {getRegName(arg1)} ({getReg(arg1)}) to stack")

            pushToStack(getReg(arg1), "data")

        case "pop":
            if local_debug:
                print(f"- Popping value from stack ({stacks['data']['value'][-1]}) to {getRegName(arg1)}")

            registers[getRegKey(arg1)] = popFromStack("data")

        case "jmp":
            if local_debug:
                print(f"- Jumping to address {registers['sys']}")
            counter = registers['sys'] - 1
            has_jumped = True

        case "jsr":
            if local_debug:
                print(f"- Jumping to subroutine {registers['sys']}, pushing to stack: {counter}")
            pushToStack(counter, "call")
            counter = registers['sys'] - 1
            has_jumped = True

        case "jic":
            if local_debug:
                print(f"- Jumping to address {registers['sys']} condition: overflow value: {flags['overflow']}")
            if flags['overflow']: counter = registers['sys'] - 1

        case "jin":
            if local_debug:
                print(f"- Jumping to address {registers['sys']} condition: negative value: {flags['negative']}")
            if flags['negative']:
                counter = registers['sys'] - 1
                has_jumped = True

        case "jio":
            if local_debug:
                print(f"- Jumping to address {registers['sys']} condition: null value: {flags['zero']}")
            if flags['zero']:
                counter = registers['sys'] - 1
                has_jumped = True

        case "rtn":
            return_address = popFromStack("call")
            if local_debug:
                print(f"- Returning to address {return_address}")
            counter = return_address #No -1 because it will continue on the next line (the curent address wa pushed, JSR would run again)
            has_jumped = True

        case "rti":
            return_address = popFromStack("int_adr")
            if local_debug:
                print(f"- Returning to address {return_address} (from interrupt)")
            counter = return_address
            has_jumped = True

        case "out":
            if local_debug:
                print(f"- Outputting {getRegName(arg1)} ({getReg(arg1)}) to port[{arg2}]")
            ports['output'][arg2] = [True, getReg(arg1)]

        case "inp":
            handleInputDevices(arg2)

            if local_debug:
                print(f"- Inputting from port[{arg2}] ({ports['input'][arg2][1]}) to {getRegName(arg1)}")
            registers[getRegKey(arg1)] = ports['input'][arg2][1]

        case "hlt":
            if local_debug:
                print(f"- Stopping program")
            return "stop"    

    if break_points[index] == 2:
        print(f"{RED}Stopped at breakpoint, at address {WHITE}{index}")
        return "break"

    return ""

#############
## Devices ##
#############

def handleInputDevices(selectedDevice):
    if selectedDevice == 0: # Keyboard (bitmap)
        pressed_keys = ["0" for _ in range(0, 16)]
        #pressed_keys[0] = "1" if keyboard.is_pressed("w") else "0"
        #pressed_keys[1] = "1" if keyboard.is_pressed("a") else "0"
        #pressed_keys[2] = "1" if keyboard.is_pressed("s") else "0"
        #pressed_keys[3] = "1" if keyboard.is_pressed("d") else "0"
        ports['input'][selectedDevice][1] = binToDec("".join(pressed_keys))

    if selectedDevice == 1: # Prompt (number)
        user_in = input(f"{GRAY}# {WHITE}")
        if len(user_in) == 0: user_in = '0'
        ports['input'][selectedDevice][1] = int(user_in)

    if selectedDevice == 2: # Milliseconds
        ports['input'][selectedDevice][1] = 0

def handleOutputDevices():
    #Console port[0]
    if ports['output'][0][0]:
        pass

    #Console port[1] number
    if ports['output'][1][0]:
        if debug: print(f"- DEVICE 'Console': Printing value (number)")
        print(f"{f'{GRAY}$ ' if result == 'break' else ''}{GRAY}{decToBin(ports['output'][1][1], 16)} {WHITE}{ports['output'][1][1]:>5d}{WHITE}")
        ports['output'][1][0] = False

    #Console port[2] character
    if ports['output'][2][0]:
        if debug: print(f"- DEVICE 'Console': Printing value (character)")
        char_code = ports['output'][2][1]
        char = chr(char_code)
        print(char, end="")
        ports['output'][2][0] = False

    #Display command port[3]
    if ports['output'][3][0]:
        #Command mode
        if decToBin(ports['output'][3][1], 16)[0] == "1":
            if debug: print(f"- DEVICE 'Display': Command mode")
            if decToBin(ports['output'][3][1], 16)[1] == "1": #0b11000000_00000000 -> flush
                if debug: print(f"  Flush")
                lib.matrixLib.renderMatrix(devices['display']['matrix'], ".#")
        else:
            #Row index mode
            if debug: print(f"- DEVICE 'Display': Row index mode ({trimToSize(ports['output'][3][1], 4)})")
            devices['display']['row_index'] = trimToSize(ports['output'][3][1], 4)
        ports['output'][2][0] = False

    #Display row data port[4]
    if ports['output'][4][0]:
        if debug: print(f"- DEVICE 'Display': Writing row: {decToBin(ports['output'][4][1], 16)}")
        devices['display']['matrix'][devices['display']['row_index']] = [int(b) for b in decToBin(ports['output'][4][1], 16)]
        ports['output'][4][0] = False

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
    print(f"{AQUA}dump stack {GRAY}Gives info about the stacks{WHITE}")
    print(f"{AQUA}debug on {GRAY}Turns on debug mode{WHITE}")
    print(f"{AQUA}debug off {GRAY}Turns off debug mode{WHITE}")
    print(f"{AQUA}breakpoint clear {GRAY}Removes all breakpoints{WHITE}")
    print(f"{AQUA}breakpoint set {WHITE}[adress] [value] {GRAY}Sets the breakpoint at the given address to value (0: -, 1: print, 2: stop){WHITE}")
    print(f"{AQUA}breakpoint range {WHITE}[address from] [address to] {GRAY}Sets STOP breakpoints to all given addresses{WHITE}")
    print(f"{AQUA}load {WHITE}[file path] {GRAY}Loads the file to the ROM{WHITE}")
    print(f"{AQUA}run {GRAY}Executes the program or resumes the program{WHITE}")
    print(f"{AQUA}reset {GRAY}Resets the computer, NOT erasing the rom{WHITE}")
    print(f"{AQUA}exit {GRAY}Exits the VM{WHITE}")

def commandDumpRom():
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
    for name in registers:
        value = registers[name]
        print(f"{registers.get(name)}: {AQUA}{name.ljust(5, ' ')} {WHITE}{value:<5d} {GRAY}{decToBin(value, NUMBER_OF_BITS)}{WHITE}")

def commandDumpPort():
    print(f"{AQUA}Input ports:             Output ports:")
    print(f"{GRAY}0: {WHITE}Raw input (keys)      Raw output")
    print(f"{GRAY}1: {WHITE}Number input          Console (number)    {GRAY}(with new line){WHITE}")
    print(f"{GRAY}2: {WHITE}Milliseconds          Console (character) {GRAY}(without new line){WHITE}")
    print(f"{GRAY}3: {WHITE}-                     Display commands")
    print(f"{GRAY}4: {WHITE}-                     Display row data")
    print(f"{GRAY}5: {WHITE}-                     -")
    print(f"{GRAY}6: {WHITE}-                     -")
    print(f"{GRAY}7: {WHITE}-                     -")

def commandDumpStacks():
    print(f"The call stack ({len(stacks["call"])}):")
    for i, line in enumerate(stacks["call"]["value"]):
        print(f"{i:>3d}: {AQUA}{line}{WHITE}")

    print(f"The data stack ({len(stacks["data"])}):")
    for i, line in enumerate(stacks["data"]["value"]):
        print(f"{i:>3d}: {AQUA}{line}{WHITE}")

    print(f"The interrupt address stack ({len(stacks["int_adr"])}):")
    for i, line in enumerate(stacks["int_adr"]["value"]):
        print(f"{i:>3d}: {AQUA}{line}{WHITE}")

    print(f"The interrupt register stack ({len(stacks["int_reg"])}):")
    for i, line in enumerate(stacks["int_reg"]["value"]):
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
    global registers
    global stacks

    counter = 0
    debug = False
    memory = initialiseMemory()
    
    for r in registers: registers[r] = 0
    for s in stacks: stacks[s]["value"] = []

    commandBreakpointClear()


##############################
## Start of the main script ##
##############################

memory = initialiseMemory()

#Load commands and construct key lookup table
print(f"--- Loading {AQUA}commands{WHITE}")

commands, command_lookup = load_commands(False)
#command_lookup = ["" for _ in range(0, 32)]
#for key in commands: command_lookup[int(commands[key][0])] = key

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
    if user_in == "dump stack": commandDumpStacks()
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
print(f"{WHITE}Bye!")