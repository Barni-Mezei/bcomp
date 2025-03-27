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
read_lines = []

print(f"--- Preprocessing: {AQUA}{sys.argv[1]}{WHITE}")
try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        for i, line in enumerate(f):
            line = line.strip().replace("\t", " ")

            if line == "" or line[0] == ";":
                print(f"{RED}SKIPPING{WHITE}")
                continue

            tokens = line.split(" ")[0:2]
            print(tokens)

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

print(f"--- Compiling: {AQUA}{sys.argv[1]}{WHITE}")

#Scanning for labels and constants
special_offset = 0 # Offset caused by labels and constants (whole empty line)
for i, data in enumerate(read_lines):
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    label_name = ins.replace(":", "")
    constant_name = ins.replace("$", "")

    #Is label?
    if ins[0] == ":":
        print(f"{WHITE}Label found: {AQUA}{ins}{WHITE} value: {GRAY}{i - special_offset}")
        labels[label_name] = i - special_offset
        special_offset += 1
        continue

    #Is constant?
    if ins[0] == "$":
        print(f"{WHITE}Constant found: {AQUA}{ins}{WHITE} value: {GRAY}{arg}")
        if "0b" in arg: constants[constant_name] = int(arg, base=2)
        elif "0x" in arg: constants[constant_name] = int(arg, base=16)
        else: constants[constant_name] = int(arg, base=10)
        special_offset += 1
        continue

for _, data in enumerate(read_lines):
    index = data["index"]
    ins = data["tokens"][0]
    arg = data["tokens"][1]

    label_arg = arg.replace(":", "")
    constant_arg = arg.replace("$", "")

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
        if "0b" in arg: out.append(str(int(arg, base=2))) 
        elif "0x" in arg: out.append(str(int(arg, base=16)))
        else: out.append(str(int(arg, base=10)))
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
for i,ins in enumerate(out[::2]):
    #print(f"{AQUA}{ins}\t{WHITE}{out[i*2+1]}\t({AQUA}{command_lookup[int(ins)]}{WHITE})")
    f.write(f"{ins},{out[i*2+1]}{';' if i*2+2 < len(out) else ''}")

f.close()