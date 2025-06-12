# Bcomp assembly 2.2 - syntax

The syntax in *Bcomp assembly 2.2* is similar to the ones before, but has 2 major additions to it. Multiple arguments, and built-in constants.



## Comments
Commants in this language, will be completely ignored during compilation. A comment starts with a `;` character and spans until the end of the line.



## Instructions and arguments
The format of an instruction is the following: `instruction argument (argument 2)`. Note that the space is nescesseary between the instruction and the argument(s). An instruction is always 3 letters long and contains only letters. The case does not matter, `mCa` and `MCa` are the same.

Arguments must be numbers. The assembler accepts 3 formats for numbers: decimal (`23`) binary (prefixed with `0b`: `0b1001`) and hexadecimal (prefixed with `0x`:`0xf8`). If a command does not need an argument, you can still specify it, but will be ignored, or you can omit it entirely. Omitted arguments will be compiled as 0. Some instructions use the single 16-bit argument, ans 2 8-bit arguments. To make it easy to read, you can type a comma, between the 2 arguments. The will be combined. So esentially: `mov 0b00001000_00000101` is the same as `mov 8, 5`.

To learn, what instruction does what, and how the architecture was built, you can take a look at the files, in the doc folder. Specifically, the architecture pngs and the Bcomp - Assembly csvs.



## Built-in constants

To make programming easier, there are some built-in constants for the register indexes. They are easy to write and remember, and tghey just hold the index of registers. here is the list of all of them: (GPR = general purpose register)
- 0: `RSYS`: System register, used by the system.Usually holds the value of the argument, but should not be used by programs.
- 1: `RA`: GPR, connected to the ALU
- 2: `RB`: GPR, connected to the ALU
- 3: `RC`: GPR, intended to be used as the output register for the ALU
- 4: `RX`: GPR, intended to be used as a loop iteration counter
- 5: `RY`:  GPR, intended to be used as a loop iteration counter
- 6: `RRADR`/`RADR`: The memory's read address
- 7: `RWADR`/`WADR`: The memory's write address
Note that the case does matter. `RA` and `ra` are not the same, and only `RA` is valid.

### How to use them

For example, say that you want to copy register A to register B, then you could write: `mov 1, 2` or `mov RA, RB` both compiling to the 1st one.



## Special functionality

### Labels

#### Functionality
Labels, hold the line number, they are created in, so they can be later used in jumps, or conditional jumps.

#### Creating labels
To create a label, start by typing a `:` then the name of the label, like this: `:loop`. Label names must be a single word (without any whitespace), but can contain any characters.

#### Using a label's value
The value of a label, can only be used as an argument to an instruction. Simply type the name of the label, prefixed with a `:`, like this: `JMP :<label name>`. The label's name will be replaced with the label's value (the line number it was created in) during compilation.



### Constants

#### Functionality
Constants allow you to "name a value". You can specify a name and an associated value to it.

#### Creating constants
If creating a constant you must prefix the name with a `$`, the specify a value to it, like this: `$special_address 6`. The specified value can be any number (in decimal, binary, or hexadecimal format), or a single character, enclsed in `"` double quotes. Example: `$letter_a "a"` If a character is specified, then the constant's value will be the character code of the specified character. In the case of multiple specified characters, then the first one will be used.

#### Using constants
You can use constants only as arguments to instructions. This works like the following: `MVA $letter_a`, where "$letter_a" will be replaced with 97, beacuse at the crateion of this constant we typed: `$letter_a "a"` which, stores the character code of the letter "a", which is 97.



### Macros
 
#### Functionality
Macros allow you to shorten long sequences of instructions.

### Using macros
To use a macro, you have to type it's name, prefixed by a `#`, like this: `$loadStr`, then you can specify thearguments to it. Be aware, that the arguments of a macro, is defined entirely inside the macro.

#### Creating macros
To create a custom macro, or edit an existing one, you have to do it in python. For the macro creation, please read [this](doc/macro_creation.md) guide