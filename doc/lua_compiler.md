# Compiling to assembly

To compile your ***LUA*** code to *bcomp assembly* the `compiler.py` will be helpful. By running the following scipt: `python compiler.py <your file .lua>`, you can compile a `.asm` file (with the same name) from your ***LUA*** script.
The compiler uses the `tokeniser.py` in the background. So, if you want to make a ***LUA*** compiler for your language, you can use the generated token tree.

# Compiler flags

The compiler can be configured, via command line arguments. Here are the available parammeters:

* `-o <path>` Specifies the output path
* `-f <file name>` Specifies the output file's name
* `-v <assembly version>` Sets the assembly version (Currently available: *V1.1*)
* `-m <num. of addresses>` The number of addresses, the computer can address
* `-w` Disables all warnings
* `-Wall` logs ALL of the warnings that come up during compiling