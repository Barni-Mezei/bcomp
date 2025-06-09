import sys
import os
import argparse
from lib.lib import *

arg_parser = argparse.ArgumentParser(
    exit_on_error = True,
    prog = "BCOMP Assembler",
    description = "This program assembles your '.asm' files in to '.o' files, using the commands specified in commands.txt",
    usage="To assemble your code, you have to specify the path to the '.asm' file,\nand it will create a new '.o' file, with the same name as the source code next to itself.\n"
    "If you want to specify the output location of the '.o' file, you can use the -o parameter.\nIf you want to name your output file, you can use the -f parameter.",
)

arg_parser.add_argument('input_file', help="The path to your '.asm' file")
arg_parser.add_argument('-o', '--output-path', help="The path to the directory, that will contain your compiled code")
arg_parser.add_argument('-f', '--file-name', help="The name of your compiled file. Filetype will be ignored!")
arg_parser.add_argument('-cpp', '--cpp', default=False, action='store_true', help="Export as C++ array for importing to Arduino")
arg_parser.add_argument('-v', '--version', default="0", type=str, help="The assembly version. Set to 0 to read from file. (Requires the 1st line to be a comment)")
arg_parser.add_argument('-lm', '--list-macros', default=False, action='store_true', help="Lists all available macros for the specified assembly version")

#Parse command line arguments
if len(sys.argv[1::]) == 0:
    print(f"{RED}No input file given!{WHITE}")
    exit()

if len(sys.argv) > 1 and not ".asm" in sys.argv[1]:
    print(f"{RED}Missing or invalid file type! (Must be .asm){WHITE}")
    exit()

try:
    arguments = arg_parser.parse_args()
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()

print(f"--- Loading {AQUA}commands{WHITE}")

commands, command_lookup = load_commands(True)

out = []
labels = {}
constants = {}
macros = {}
read_lines = []

ASM_VERSION = arguments.version

print(f"--- Preprocessing: {AQUA}{sys.argv[1]}{WHITE}")
try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            # Determine assembly version
            if arguments.version == "0" and i == 0 and line[0:5] == ";asm ":
                ASM_VERSION = line[5::]
                continue

            line = line.strip().replace("\t", " ")

            if line == "" or line[0] == ";":
                print(f"{RED}SKIPPING{WHITE}")
                continue

            tokens = []
            for t in line.split(" "):
                if t[0] == ";": break
                tokens.append(t)
            #print(tokens)

            #if len(tokens) > 1 and not tokens[0][0] in [":", "$"] and tokens[1] == "" and commands[tokens[0].lower()][1] == 1:
            #    print(f"{RED}ERROR: Not enough tokens!{WHITE}")
            #    exit()

            if len(tokens) == 1: tokens.append("0")
            if tokens[1] == "" or tokens[1] == ";": tokens[1] = "0"

            print(f"{GRAY}{i:>03d} {WHITE}{line}")

            read_lines.append({
                "index": i + 1,
                "tokens": tokens
            })
except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

print(f"--- Compiling: {AQUA}{sys.argv[1]}{WHITE} With assembly version: {AQUA}{ASM_VERSION}{WHITE}")

def parseNumber(number : str, throwError = False) -> int:
    if "0b" in number: return int(number, base=2)
    if "0x" in number: return int(number, base=16)

    if throwError:
        return int(number, base=10)
    else:
        try: return int(number, base=10)
        except: return 0

#Scanning for labels, constants and macros
special_offset = 0 # Offset caused by labels, constants or macros (whole empty line)
for i, data in enumerate(read_lines):
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    special_name = ins[1::]

    #Is label?
    if ins[0] == ":":
        print(f"{WHITE}Label found: {AQUA}{ins}{WHITE} value: {GRAY}{i - special_offset}")
        labels[special_name] = i - special_offset
        special_offset += 1
        continue

    #Is constant?
    if ins[0] == "$":
        print(f"{WHITE}Constant found: {AQUA}{ins}{WHITE} value: {GRAY}{arg}")
        if arg[0] == '"': constants[special_name] = ord(arg[1:-1:][0]) # Get character index
        else: constants[special_name] = parseNumber(arg)
        special_offset += 1
        continue

    #Is macro?
    if ins[0] == "#":
        print(f"{WHITE}Macro found: {AQUA}{ins}{WHITE} value: {GRAY}{arg}")

        macros[special_name] = {
            "name": special_name,
            "arguments": data["tokens"][1::]
        }
        
        special_offset += 1
        continue

print("Constants")
print(constants)
print("Macros")
print(macros)

# Reaplace label, constant and word values
for _, data in enumerate(read_lines):
    index = data["index"]
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    label_arg = arg.replace(":", "")
    constant_arg = arg.replace("$", "")
    macro_name = ins[1::]

    print(f"{GRAY}{index:03d}: {AQUA}{ins}\t{WHITE}{arg}")

    #Is label declaration?
    if ins[0] == ":": continue

    #Is constant declaration?
    if ins[0] == "$": continue

    #Is macro declaration?
    if ins[0] == "#":
        if not macro_name in macros:
            print(f"{RED}ERROR: Unrecognised macro: '{macro_name}'!{WHITE}")
            exit()
    
        print(f"{GRAY}Executing macro {AQUA}{macro_name}{GRAY}")
        continue

    ins = ins.lower()

    #Is keyword?
    if not ins in commands:
        print(f"{RED}ERROR: Unrecognised keyword: '{ins.upper()}'!{WHITE}")
        exit()

    #Replace label value in argument
    if arg[0] == ":":
        if not label_arg in labels:
            print(f"{RED}ERROR: Unrecognised label: {WHITE}{label_arg}")
            exit()

        arg = str(labels[label_arg])
        print(f"{GRAY}Replacing label {AQUA}{label_arg}{GRAY} with {WHITE}{labels[label_arg]}")

    #Replace constant value in argument
    if arg[0] == "$":
        if not constant_arg in constants:
            print(f"{RED}ERROR: Unrecognised constant: {WHITE}{constant_arg}")
            exit()

        arg = str(constants[constant_arg])
        print(f"{GRAY}Replacing constant {AQUA}{constant_arg}{GRAY} with {WHITE}{constants[constant_arg]}")

    out.append(commands[ins][0]) #Append command index
    #Append argument
    try:
        out.append(str(parseNumber(arg, throwError = True)))
    except Exception as e:
        print(f"{RED}ERROR: Invalid argument! (Must be a number){WHITE}")
        exit()

#Writing to file
def path_leaf(path):
    head, tail = os.path.split(path)
    return tail or os.basename(head)

def give_new_type(full_file_path, new_type):
    return ".".join(path_leaf(full_file_path).split(".")[0:-1]) + new_type

save_path = "./binaries/" if os.path.exists("./binaries/") else "./"
save_name = give_new_type(sys.argv[1], ".o")

if arguments.output_path: save_path = arguments.output_path
if arguments.file_name: save_name = give_new_type(arguments.file_name + ".D", ".o")

f = open(save_path + save_name, "w", encoding="utf8")

print(f"--- Writing to: {AQUA}{os.path.join(save_path, save_name)}{WHITE}")


if arguments.cpp:
    # As valid C++ code
    for i,ins in enumerate(out[::2]):
        arg = out[i*2+1]

        f.write("{" + str(ins) + "," + str(arg) + "},\n")

        #f.write(f"rom[rom_index  ].ins  = {ins};\n")
        #f.write(f"rom[rom_index++].arg  = {arg};\n")

    #f.write(f"rom_length = rom_index;\n")
    #f.write(f"rom_index--;")

else:
    # As comma separated values
    for i,ins in enumerate(out[::2]):
        #print(f"{AQUA}{ins}\t{WHITE}{out[i*2+1]}\t({AQUA}{command_lookup[int(ins)]}{WHITE})")
        f.write(f"{ins},{out[i*2+1]}{';' if i*2+2 < len(out) else ''}")

f.close()