# Setting up the language

First, load your assemnbly in to the commands.txt. This loads all available commands, and their metadata. If you have a .CSV file, you can convert it to the commands.txt using the `python command_parser.py <your csv>` command. After generating the commands.txt you can use the other scripts.

# Writing assembly

You can write your assembly code in to any file, with the `.asm` extension. For the language documentation read the [Bcomp assembly](doc/bcomp_assembly.md)

### Assembling your script

To assemble your code you can use the following script: `python assembler.py <your file .asm>`. This will generate a .o file, with a specified format. If you want to specify the parameters of the output file, type `-h` for help. For further information see [The assembler](doc/assembler.md)

### Assembly versions

There are multiple versions of this machine and architecture. Each architecture comes with its own assembly version. To specify the assembly version of a script, put this line at the beginning of a file: `;asm 2.0` for assembly version 2.0. To convert between versions, you can use the: `assembly_converter.py` script.

### Viewing assembled scripts (bytecodes)

To view an already existing .o file, you can use the `python bytecode_viewer.py <your file .o>` script. Be aware, that the bytecode viewer, can only render normally assembled scripts, with the comma separated format.

# Compiling LUA to assembly

The `compiler.py` script provides an almost full ***LUA*** to bcomp assembly support. To compile your ***LUA*** scipts to assembly, you can run the following command: `python compiler.py <your file .lua>` For additional details read the [LUA compiler](doc/lua_compiler.md) markdown file.

# The bcomp VM

The `bcomp_vm_<version>.py` is a virtual version of the machine. To start it up you can run the following script: `python bcomp_vm_<version>.py <your file .o>` If you specify an assembled program, it will be automaticallyloaded to the rom. The VM has other features, such as debugging, and viewing the memory and registers, while the program is running. Type `help` to get started.