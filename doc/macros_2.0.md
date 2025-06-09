# Bcomp assembly - syntax

## Quick guide
- Instructions: `mva 0`
- Comments: `add ; Cool code`
- Labels: `:loop` `jmp :loop`
- Constants: `$magic_number 13` `mvb $magic_number`
- Macros: `#loadStr "Hello, world!" 0`

## Versions

The *bcomp assembly* has many versions, for many architectures, and platforms.

- `1.0`: Architecture: 1.0, Platform: Scrap Mechanic computer
- `1.1`: Architecture: 1.0, Platform: Scrap Mechanic computer 1.1, bcomp_vm_asm1.1
- ~`2.0`: Architecture: ~2.0, Platform: bcomp_vm_asm2.0, Arduino UNO, Texas Instruments TI-84 Plus Python edition

## Comments
Commants in this language, will be completely ignored during compilation. A comment starts with a `;` character and spans until the end of the line.

## Instructions
The format of an instruction is the following: `instruction argument`. Note that the space is nescesseary between the instruction and the argument. An instruction is always 3 letters long and contains only letters. The case does not matter, `mCa` and `MCa` are the same.

Arguments must be numbers. The assembler accepts 3 formats for numbers: decimal (`23`) binary (prefixed with `0b`: `0b1001`) and hexadecimal (prefixed with `0x`:`0xf8`). If a command does not need an argument, you can still specify it, but will be ignored, or you can omit it entirely. Omitted arguments will be compiled as 0.

To learn, what instruction does what, and how the architecture was built, you can take a look at the files, in the doc folder. Specifically, the architecture pngs and the Bcomp - Assembly csvs.

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