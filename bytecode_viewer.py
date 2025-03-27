import sys
from lib.lib import *

commands = load_commands(False)

if len(sys.argv[1::]) == 0:
    print(f"{RED}No input file given!{WHITE}")
    exit()

if not ".o" in sys.argv[1]:
    print(f"{RED}Invalid or missing file type! (Must be .o){WHITE}")
    exit()

print(f"--- Loading {AQUA}commands{WHITE}")

#Load commands and construct key lookup table
commands, command_lookup = load_commands(False)



#[
#    {"from": 3, "to": 5}
#]
jump_addresses = []
jump_characters = [] # [[".", ".", "."], [".", ".", "."]]

file_len = 0
max_arg_len = 0
max_ins_len = 0

# Extract jumps from the file
try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        for i, line in enumerate(f.readline().strip().split(";")):
            file_len += 1

            line = line.strip().split(",")
            line = [int("0" if n == "" else n) for n in line]

            max_ins_len = max(max_ins_len, len(str(line[0])) )
            max_arg_len = max(max_arg_len, len(str(line[1])) )

            mnemonic = command_lookup[int(line[0])]

            if mnemonic in ["jmp", "jsr"]:
                jump_addresses.append({"from": i, "to": int(line[1])})
except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

# Create jump graphs
for i in range(0, file_len):
    jump_characters.append( ["." for _ in range(len(jump_addresses))] )

for char_index, jump_line in enumerate(jump_addresses):
    address_from = min(jump_line["from"], jump_line["to"])
    address_to = max(jump_line["from"], jump_line["to"])

    for i in range(address_from, address_to + 1):
        char = "┃"

        if i == address_from: char = "┏"
        if i == address_to: char = "┗"

        jump_characters[i][char_index] = char


# Print out the file, with the jump lines integrated as well
with open(sys.argv[1], "r", encoding="utf8") as f:
    for i, line in enumerate(f.readline().strip().split(";")):
        line = line.strip().split(",")
        line = [int("0" if n == "" else n) for n in line]

        ins = decToBin(line[0], 8).replace("1", "#").replace("0", ".")
        arg = decToBin(line[1], 16).replace("1", "#").replace("0", ".")
        mnemonic = command_lookup[int(line[0])]

        formatted_ins = f"({line[0]})" + (" "*(max_ins_len - len(str(line[0])) + 1))
        formatted_arg = f"({line[1]})" + (" "*(max_arg_len - len(str(line[1])) + 1))
        formatted_jump_line = "".join(jump_characters[i])

        print(f"{WHITE}{i}: {GRAY}{arg} {WHITE}{formatted_arg}{AQUA}{ins} {WHITE}{formatted_ins}{formatted_jump_line} {AQUA}{mnemonic}{WHITE} {line[1]}")