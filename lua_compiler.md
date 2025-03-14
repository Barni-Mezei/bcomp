# Compiling to assembly

To compile your ***LUA*** code to bcomp assembly the `compiler.py` will be helpful. By running the following scipt: `python compiler.py <your file .lua>`, you can compile a `.asm` file (with the same name) from your ***LUA*** script.

# Compiler flags

The compiler can be configured, via command line arguments. Here are the available parammeters: (yes, the flags are similar to [gcc](https://en.wikipedia.org/wiki/GNU_Compiler_Collection))

* `-o <path>` Specifies the output path
* `-f <file name>` Specifies the output file's name
* `-w` Disables all warnings
* `-Wall` logs ALL of the warnings that come up during compiling