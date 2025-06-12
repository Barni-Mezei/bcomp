"""
This is the macro, library for BCOMP asm V2.2
"""

from lib.lib import *

# Returns with the index of the command
def c(command : str): return int(commands[command][0])

# Base macro class
class Macro:
    arguments = []
    instructions = []
    error_message = "Not implemented!"
    success = False

    def __init__(self, args : list):
        self.arguments = self.join(args, '"', ' ', '"')
        self.arguments = self.join(self.arguments, '[', ' ', ']')

        # Convert to integers, if the first character is a number
        for i in range(len(self.arguments)):
            try: int(self.arguments[i][0])
            except: continue

            self.arguments[i] = parseNumber(self.arguments[i])

        self.instructions = []

        self.execute()

    def join(self, array : list, start : str, sep : str, end : str):
        tmp = []

        inBlock = False
        block = ""
        for a in array:
            if not inBlock and a[0] == start:
                inBlock = True
            if inBlock:
                block += a
                if a[-1] == end:
                    tmp.append(block)
                    block = ""
                    inBlock = False
                else:
                    block += sep
            else:
                tmp.append(a)

        return tmp

    def raiseError(self, message : str) -> bool:
        self.success = False
        self.error_message = message
        return False

    def execute(self):
        pass


##########
# Macros #
##########

class loadStr(Macro):
    def execute(self):
        if len(self.arguments) != 2: return self.raiseError("Number of parameters does not match")

        text = self.arguments[0][1:-1:].replace("\\n", "\n").replace("\\t", "\t")
        start_address = int(self.arguments[1])

        # Save register values
        self.instructions += [
            ["psh", "RWADR"],
        ]

        # Insert every character
        for i, char in enumerate(text):
            self.instructions += [
                ["stw", start_address + i],
                ["stv", ord(char)],
            ]

        # Load back register values
        self.instructions += [
            ["pop", "RWADR"],
        ]

        self.success = True
        return

class loadArray(Macro):
    def execute(self):
        if len(self.arguments) != 2: return self.raiseError("Number of parameters does not match")

        text = self.arguments[0][1:-1:].replace(" ", "").split(",")
        start_address = int(self.arguments[1])

        print(self.arguments)

        # Insert every character
        for i, value in enumerate(text):
            self.instructions += [
                ["swv", start_address + i],
                ["stv", value],
            ]

        # Reset RA and write address
        self.instructions += [
            ["swv", 0],
        ]

        self.success = True
        return

class printStr(Macro):
    def execute(self):
        if len(self.arguments) != 3: return self.raiseError("Number of parameters does not match")

        start_address = self.arguments[0]
        length = self.arguments[1]
        counter_address = self.arguments[2]

        label_names = {
            "loop": f":print_loop_{id(self)}",
            "end": f":print_loop_end_{id(self)}",
        }

        self.instructions += [
            ["swv", counter_address],
            ["stv", start_address],

            # Loop
            [label_names["loop"], 0],

            # Get counter value
            ["adr", counter_address],
            ["lda", 0],

            # Output character at address
            ["sra", 0],
            ["lda", 0],
            ["out", 2], # Character output

            # Get counter value
            ["srv", counter_address],
            ["lda", 0],

            # Increment counter
            ["inc", 1],
            ["mca", 0],
            ["sta", 0],
            ["enc", start_address + length],
            # Exit or loop back
            ["jio", label_names["end"]],
            ["jmp", label_names["loop"]],
            [label_names["end"], 0],
        ]

        self.success = True
        return

class forLoop(Macro):
    def execute(self):
        if len(self.arguments) != 4: return self.raiseError("Number of parameters does not match")

        start_number = self.arguments[0]
        end_number = self.arguments[1]
        label_name = self.arguments[2]
        counter_address = self.arguments[3]

        label_names = {
            "loop": f":for_loop_{id(self)}",
            "end": f":for_loop_end_{id(self)}",
        }

        self.instructions += [
            ["swv", counter_address],
            ["stv", start_number],

            # Loop
            [label_names["loop"], 0],

            # Get counter value
            ["adr", counter_address],
            ["lda", 0],

            # Call loop body
            ["jsr", label_name],

            # Get counter value
            ["srv", counter_address],
            ["lda", 0],

            # Increment counter
            ["inc", 1],
            ["mca", 0],
            ["sta", 0],
            ["enc", end_number],
            # Exit or loop back
            ["jio", label_names["end"]],
            ["jmp", label_names["loop"]],
            [label_names["end"], 0],
        ]

        self.success = True
        return

class reverseForLoop(Macro):
    def execute(self):
        if len(self.arguments) != 4: return self.raiseError("Number of parameters does not match")

        start_number = self.arguments[0]
        end_number = self.arguments[1]
        label_name = self.arguments[2]
        counter_address = self.arguments[3]

        label_names = {
            "loop": f":for_loop_{id(self)}",
            "end": f":for_loop_end_{id(self)}",
        }

        self.instructions += [
            ["swv", counter_address],
            ["stv", start_number],

            # Loop
            [label_names["loop"], 0],

            # Get counter value
            ["adr", counter_address],
            ["lda", 0],

            # Call loop body
            ["jsr", label_name],

            # Get counter value
            ["srv", counter_address],
            ["lda", 0],

            # Increment counter
            ["dec", 1],
            ["mca", 0],
            ["sta", 0],
            ["enc", end_number],
            # Exit or loop back
            ["jio", label_names["end"]],
            ["jmp", label_names["loop"]],
            [label_names["end"], 0],
        ]

        self.success = True
        return


###############
# Main script #
###############

# List of all defined macros
MACROS = {}
for cls in Macro.__subclasses__(): MACROS[cls.__name__ ] = cls

commands, command_lookup = load_commands(False)

class Execute:
    success = False
    instructions = []

    def __init__(self, name : str, argumments : list):
        if name in MACROS:
            macro = MACROS[name](argumments)
            if not macro.success:
                print(f"{RED}ERROR: {macro.error_message}{WHITE}")
            
            self.success = macro.success
            if self.success:
                self.instructions = macro.instructions
            return

        print(f"{RED}ERROR: Macro not found!{WHITE}")
        return