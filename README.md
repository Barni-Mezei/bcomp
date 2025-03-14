# Setting up the language

First, load your assemnbly in to the commands.txt. If you have a .CSV file, you can convert it to the commands.txt using the `python command_parser.py <your csv>` command

# Writing assembly

Once you have your assembly instructions loaded, with their numbers, you can write some code. The assembler supports comments, if they are prefixed with the `;` character. The format of a line if the following: `command argument` The command and the arguments are separated by a space. You can omit the argument, and it will assemble as a `0`

### Assembling your script

To assemble your code you have to run the following script: `python assembler.py <your file .asm>`

### Viewing assembled scripts (bytecodes)

This will create a file, with roughly the same name and a `.o` extension. To view an already existing .o file, you cna use the `python bytecode_viewer.py <your file .o>` script.

# Compiling LUA to assembly

The `compiler.py` script provides an almost full ***LUA*** to bcomp assembly support. To compile your ***LUA*** scipts to assembly, you can run the following command: `python compiler.py <your file .lua>` For additional details read the [LUA compiler](lua_compiler.md) markdown file.

# The bcomp VM

The `bcomp_vm.py` is a virtual version of the machine. To start it up you can run the following script: `python bcomp_vm.py <your file .o>` The VM expects an assembled program, to start with. Any additional functionality, can be viewed and accessed via the biult-in console. type `help` to get started.