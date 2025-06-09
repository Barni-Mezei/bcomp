# Bcomp - A computer

This is a complete computer, with a custom made architecture, built on different platforms. With a custom architecture, also comes a custom assembly. This repository contains tools, nescesseary for developing on BCOMP. There are also virtual machies created, emulating different architectures.

## Bcomp assembly

To get started, create a file with the ".asm" extension. Here you can write your assembly code. For the language documentation read the [Bcomp assembly](doc/bcomp_assembly.md) file

### Assembling your script

To assemble your code you can use the following script: `python assembler.py <your file .asm>`. This will generate a .o file, with a specified format. If you want to specify the parameters of the output file, type `-h` for help. For more information read the [Assembler](doc/assembler.md) file.

### Assembly versions

There are multiple versions of this machine and architecture. Each architecture comes with its own assembly version. To specify the assembly version of a script, put this line at the beginning of a file: `;asm 2.0`. This tells the assembler, that this file contains *bcomp assembly V2.0* To convert between versions, you can use the: `assembly_converter.py` script.

### Viewing assembled scripts (bytecodes)

To view an already existing .o file, you can use the `python bytecode_viewer.py <your file .o>` script. Be aware, that the bytecode viewer, can only render normally assembled scripts, with the comma separated format.

## Compiling LUA to assembly

The `compiler.py` script provides an almost full ***LUA*** to *bcomp assembly* compiltion support. To compile your ***LUA*** scipts to *bcomp assembly*, you can run the following command: `python compiler.py <your file .lua>` For additional details read the [LUA compiler](doc/lua_compiler.md) file.

## The bcomp VM

The `bcomp_vm_asm.py` is a virtual version of the machine. To start it up you can run the following script: `python bcomp_vm_<version>.py <your file .o>` If you specify an assembled program, it will be automaticallyloaded to the rom. The VM has other features, such as debugging, and viewing the memory and registers, while the program is running. Type `help` to get started.