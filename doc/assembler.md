# Bcomp assembly - The assmeblers

## What is it?

The assembler, is a python script ([this one](../assembler.py)) that converts your assembly files into "machine code", for the specified platform.

## Supported platforms

- The python VM machine, in the root directory (Emulated VM)
- A version of this computer, built in the game "Scrap Mechanic" (Natively executed bytecode)
- Arduino UNO, or Nano, or similar microcontrollers. (Emulated VM)
- Texas Instruments TI-84 Plus Python edition (Emulated VM)

The data on every architecture, and assembly version, can be found in the doc folder, specifically the architecture pngs and the Bcomp - Assembly csvs.

## How to use it?

First, you have to make a script, that you want to run on your selected platform / machine. This file must have the ".asm" extension.

After writing your program, you should load your instruction set, from an external source, or from one of the available version, in the docs folder. To do this, you can use the [Command parser](../command_parser.py). To use it type: `python command_parser.py <language file>.csv`. This will generate a "commands.txt" file, that contains information about the available commands.

When your code is ready, and your instructions are loaded, you can run the following command `python assembler.py <your code>.asm`.
You can specify parameters to the assembler, for example the assembly version, you are working with. Here is a list of available parameters.

- `-o` You can specify the output directory
- `-f` You can specify the output file name
- `-cpp` If this flag is present, the output will be a valid C or C++ code, for pasting in to the Arduino source code, for hardcoding a program.
- `-v` The assembly version of your script. You cna also specify it at the top of your script like so: `;asm 2.0`
- `-lm` Lists all available macros, for the specified assembly version. (-v Must be specified) If this flag is present, no assembling will be executed.

The list of macros can be found here:
- [Bcomp assembly V2.0 macros](macros_2.0.md)

The content of the output file, (which has the extenbsion `.o`) can be inputted to one of the selected platfroms, if the correct format was given, and the correct assembly version was used.