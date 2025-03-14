RED = "\033[31m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
AQUA = "\033[36m"
GRAY = "\033[90m"
WHITE = "\033[0m"

def load_commands(log = False, file_path = "commands.txt"):
    commands = {}

    try:
        with open(file_path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip().split(" ")
                commands[line[0]] = line[1:len(line)]

                if log: print(f"{AQUA}{line[0]}: {GRAY}{line[1]}\t{GREEN if line[2] == '1' else RED}#{WHITE}")
    except FileNotFoundError as e:
        print(f"{RED}ERROR: 'commands.txt' is not found. Please create one, or use the command_parser.py{WHITE}")
        exit()

    return commands

def binToDec(number : str):
    out = 0
    for i, char in enumerate(number):
        out += int(char) * 2**(len(number) - i - 1)

    return out

def decToBin(number : int, length : int = 8):
    return (bin(number).replace('0b', '').rjust(length, "0")+".")[-length-1:-1]

def trimToSize(number : int, size : int) -> int:
    return binToDec(decToBin(number, size))
