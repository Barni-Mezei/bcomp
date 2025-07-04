import importlib
import os
import argparse
from lib.lib import *

arg_parser = argparse.ArgumentParser(
    exit_on_error = True,
    prog = "BCOMP Assembler",
    description = "This program assembles your '.asm' files in to '.o' files, using the commands specified in commands.txt",
    usage="To assemble your code, you have to specify the path to your '.asm' file, and run it.\nFor additional information use the -h flag.",
)

arg_parser.add_argument('input_file', help="The path to your '.asm' file")
arg_parser.add_argument('-o', '--output-path', help="The path to the directory, that will contain your compiled code")
arg_parser.add_argument('-f', '--file-name', help="The name of your compiled file. Filetype will be ignored!")
arg_parser.add_argument('-cpp', '--cpp', default=False, action='store_true', help="Export as C++ array for importing to Arduino")
arg_parser.add_argument('-ino', '--arduino', default=False, action='store_true', help="Export as C++ array in to the specified arduino file")
arg_parser.add_argument('-v', '--version', default="0", type=str, help="The assembly version. Set to 0 to read from file. (Requires the 1st line to be a comment)")
arg_parser.add_argument('-lm', '--list-macros', default=False, action='store_true', help="List all available macros for the specified assembly version")

#Parse command line arguments
try:
    arguments = arg_parser.parse_args()
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()

"""if len(sys.argv[1::]) == 0:
    print(f"{RED}No input file given!{WHITE}")
    exit()

if len(sys.argv) > 1 and not ".asm" in sys.argv[1]:
    print(f"{RED}Missing or invalid file type! (Must be .asm){WHITE}")
    exit()"""

print(f"--- Loading {AQUA}commands{WHITE}")

commands, command_lookup = load_commands(True)

out = []
labels = {}
constants = {}
built_in = {
    "RSYS": 0,
    "RA": 1,
    "RB": 2,
    "RC": 3,
    "RX": 4,
    "RY": 5,
    "RRADR": 6,
    "RADR": 6,
    "RWADR": 7,
}

read_lines = []

ASM_VERSION = arguments.version
MACRO = None # The dynamically loaded python macro library

print(f"--- Preprocessing: {AQUA}{arguments.input_file}{WHITE}")
try:
    with open(arguments.input_file, "r", encoding="utf8") as f:
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
                if len(t) > 0 and t[0] == ";": break
                tokens.append(t)

            # Fix literal spaces (" ")
            for i, t in enumerate(tokens):
                if t == '"' and tokens[i-1] == '"':
                    tokens.insert(i-1, t + " " + tokens.pop(i))
                    tokens.pop(i)

            # Join separated arguments, if not in string or is macro
            if tokens[0][0] != "#" and len(tokens) > 2:
                if len(tokens[1]) > 0 and tokens[1][0] != '"' and tokens[1][-1] == ',':
                    print("Comma!", tokens[1], tokens[2])
                    tokens.insert(1, [tokens.pop(1)[:-1:], tokens.pop(1)])

            # make it min. 2 tokens, and wrap 2nd token
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

ASM_VERSION = ASM_VERSION.strip()
print(f"--- Importing macros for assembly version: {AQUA}{ASM_VERSION}{WHITE}")
if ASM_VERSION == "0":
    print(f"--- {GRAY}No assembly version specified!{WHITE}")
else:
    MACRO = importlib.import_module(f"assembler_macros.v{ASM_VERSION.replace('.', '_')}")

#Executing macros
i = 0
while i < len(read_lines):
    data = read_lines[i]
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    macro_name = ins[1::]

    #Is macro?
    if MACRO == None or ins[0] != "#":
        i += 1
        continue

    print(f"{GRAY}Executing macro {AQUA}{macro_name}{WHITE}")

    result = MACRO.Execute(macro_name, data["tokens"][1::])
    if not result.success: exit()

    inserted_code_length = len(result.instructions)
    insertion_line_index = read_lines[i]["index"]

    # Insert the code from the macro, but convert all int -> str
    for macro_index, line in enumerate(result.instructions):
        return_tokens = [(str(a) if type(a) == int else a) for a in line]

        if type(return_tokens[1]) == list:
            for j, t in enumerate(return_tokens[1]):
                if type(t) == int: return_tokens[1][j] = str(t)

        read_lines.insert(i + macro_index, {
            "index": i + macro_index,
            "tokens": return_tokens
        })

    # Remove the original macro line
    read_lines.pop(i + inserted_code_length)

    i += inserted_code_length

# Fix line indexes
for i, line in enumerate(read_lines): line["index"] = i

#for data in read_lines:
#    print(data)
#exit()

print(f"--- Compiling: {AQUA}{arguments.input_file}{WHITE}")

#Scanning for labels, constants and macros
special_offset = 0 # Offset caused by labels, constants or macros (whole empty line)
for i, data in enumerate(read_lines):
    index = data["index"]
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

    #Is built-in constant?
    if ins[0] == "R":
        print(f"{WHITE}Built-in constant found: {AQUA}{ins}{WHITE} value: {GRAY}{arg}")
        if arg[0] == '"': constants[special_name] = ord(arg[1:-1:][0]) # Get character index
        else: constants[special_name] = parseNumber(arg)
        special_offset += 1
        continue

# Reaplace label, constant and word values
for _, data in enumerate(read_lines):
    index = data["index"]
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    print(f"{GRAY}{index:03d}: {AQUA}{ins}\t{WHITE}{arg}")

    #Is label declaration?
    if ins[0] == ":": continue

    #Is constant declaration?
    if ins[0] == "$": continue

    ins = ins.lower()

    #Is keyword?
    if not ins in commands:
        print(f"{RED}ERROR: Unrecognised keyword: '{ins.upper()}'!{WHITE}")
        exit()

    # Convert string and int arguments to list
    if type(arg) == str: arg = [arg]

    # Replace values in all arguments
    for i, a in enumerate(arg):
        label_arg = a.replace(":", "")
        constant_arg = a.replace("$", "")
        built_in_arg = a

        #Replace label value in argument
        if a[0] == ":":
            if not label_arg in labels:
                print(f"{RED}ERROR: Unrecognised label: {WHITE}{label_arg}")
                exit()

            arg[i] = str(labels[label_arg])
            print(f"{GRAY}Replacing label {AQUA}{label_arg}{GRAY} with {WHITE}{labels[label_arg]}")

        #Replace constant value in argument
        if a[0] == "$":
            if not constant_arg in constants:
                print(f"{RED}ERROR: Unrecognised constant: {WHITE}{constant_arg}")
                exit()

            arg[i] = str(constants[constant_arg])
            print(f"{GRAY}Replacing constant {AQUA}{constant_arg}{GRAY} with {WHITE}{constants[constant_arg]}")

        #Replace built-in constant value in argument
        if a[0] == "R":
            if not built_in_arg in built_in:
                print(f"{RED}ERROR: Unrecognised built-in value: {WHITE}{built_in_arg}")
                exit()

            arg[i] = str(built_in[built_in_arg])
            print(f"{GRAY}Replacing built-in value {AQUA}{built_in_arg}{GRAY} with {WHITE}{built_in[built_in_arg]}")

   

    #Append command index
    out.append(commands[ins][0]) 

    # Join values to a single number and append argument
    bin_arg = ""
    for i, a in enumerate(arg):
        #print(i, "a:", a)
        try:
            bin_arg = decToBin(parseNumber(a, throwError = True), 16 // len(arg)) + bin_arg
        except Exception as e:
            print(f"{RED}ERROR: Invalid argument! (Numbers only){WHITE}")
            exit()

    #print("bin_arg", bin_arg)

    out.append(binToDec(bin_arg))

#Writing to file
def path_leaf(path):
    head, tail = os.path.split(path)
    return tail or os.basename(head)

def give_new_type(full_file_path, new_type):
    return ".".join(path_leaf(full_file_path).split(".")[0:-1]) + new_type

save_path = "./binaries/" if os.path.exists("./binaries/") else "./"
save_name = give_new_type(arguments.input_file, ".o")

if arguments.output_path: save_path = arguments.output_path
if arguments.file_name: save_name = give_new_type(arguments.file_name + ".D", ".o")

# Reset save name if saving to .h file
if arguments.arduino: save_name = ""

f = open(save_path + save_name, "w", encoding="utf8")

print(f"--- Writing to: {AQUA}{os.path.join(save_path, save_name)}{WHITE}")

if arguments.cpp:
    # As valid C++ code
    for i,ins in enumerate(out[::2]):
        arg = out[i*2+1]

        f.write("{" + str(ins) + "," + str(arg) + "},\n")

if arguments.arduino:
    # As valid C++ code to rom.h

    f.write("typedef struct {\n")
    f.write("  unsigned int ins;\n")
    f.write("  unsigned int arg;\n")
    f.write("} Command;\n")
    f.write("\n")
    f.write("const PROGMEM Command rom[] = {")

    for i,ins in enumerate(out[::2]):
        arg = out[i*2+1]

        f.write("\n{" + str(ins) + "," + str(arg) + "},")

    f.write("\n};\n\n")

    f.write(f"int rom_index = 0;\n")
    f.write(f"int rom_length = sizeof(rom) / sizeof(rom[0]);")
else:
    # As comma separated values
    for i,ins in enumerate(out[::2]):
        #print(f"{AQUA}{ins}\t{WHITE}{out[i*2+1]}\t({AQUA}{command_lookup[int(ins)]}{WHITE})")
        f.write(f"{ins},{out[i*2+1]}{';' if i*2+2 < len(out) else ''}")

f.close()
