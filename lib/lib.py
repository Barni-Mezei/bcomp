from random import randint

RED = "\033[31m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
AQUA = "\033[36m"
GRAY = "\033[90m"
WHITE = "\033[0m"

def load_commands(log = False, file_path = "commands.txt") -> dict:
    commands = {}
    lookup = ["" for _ in range(0, 64)]

    # Get commands
    try:
        with open(file_path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip().split(" ")
                commands[line[0]] = line[1:len(line)]
                lookup[int(line[1])] = line[0]

                if log: print(f"{AQUA}{line[0]}: {GRAY}{line[1]}\t{GREEN if line[2] == '1' else RED}#{WHITE}")
    except FileNotFoundError as e:
        print(f"{RED}ERROR: 'commands.txt' is not found. Please create one, or use the command_parser.py{WHITE}")
        exit()

    # get lookup
    for key in commands: lookup[int(commands[key][0])] = key

    return commands, lookup

def binToDec(number : str):
    out = 0
    for i, char in enumerate(number):
        out += int(char) * 2**(len(number) - i - 1)

    return out

def decToBin(number : int, length : int = 8):
    return (bin(number).replace('0b', '').rjust(length, "0")+".")[-length-1:-1]

def trimToSize(number : int, size : int) -> int:
    return binToDec(decToBin(number, size))

def get_id(length : int = 10):
    return "".join([str(randint(0,9)) for _ in range(length)])