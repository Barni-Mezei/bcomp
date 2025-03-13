import sys
from lib import *

if len(sys.argv[1::]) == 0:
    print(f"{RED}No input file given!{WHITE}")
    exit()

if not ".o" in sys.argv[1]:
    print(f"{RED}Invalid or missing file type! (Must be .o){WHITE}")
    exit()

print(f"--- Loading {AQUA}commands{WHITE}")

#Load commands and construct key lookup table
commands = load_commands(False)
command_lookup = ["" for _ in range(0, 32)]
for key in commands: command_lookup[int(commands[key][0])] = key

try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        for i, line in enumerate(f.readline().strip().split(";")):
            line = line.strip().split(",")
            line = [int("0" if n == "" else n) for n in line]

            ins = decToBin(line[0], 8)#bin(line[0]).replace('0b', '').rjust(8, "0")
            arg = decToBin(line[1], 16)#bin(line[1]).replace("0b", "").rjust(16, "0")

            print(f"{GRAY}{arg} {WHITE}({line[1]})\t{AQUA}{ins} {WHITE}({line[0]})\t: {AQUA}{command_lookup[line[0]]}{WHITE} {line[1]}")
except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

def getMnemonic(binNumber : str):
    return command_lookup[binToDec(binNumber)]
