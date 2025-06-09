# Bcomp assembly 2.0 - creating macros


## What are macros?

Macros are compacted code. By typing a single command, the assembler can generate a complex program from it, using the macro library.

## Where are macros defined?

The macros are created, and stored in the `assembler_macros/<assembly version/__init__.py>` python file. All macros are an instance of the main **Macro** calss.

## Macro structure

Each macro has an `execute` function. This function gets called when a macro is encountered during compilation. The objects properties are previously filled with the arguments, in the `arguments` property. Each argument is converted to an integer, or if not one, the left as a string. For example the following macro: `#test "Hello!" 5` gets the following arguments: `['"Hello!"', 5]`

Upon returning, the caller decides, if the macro executed successfully, based on the object's `success` property. If set to false, that means an error. To specify an error message, put it in the `error_message` field of the class.

If the esecution was a success, then the instructions in `instruction` will be replaced in place of the macro line. The format for instructions is the following:
```python
self.instructions = [
    ["jmp", 6],
    ["mva", 0],
]
```

Each instruction must be a 2 items long array. This is basically the same cde, you would write in a file, but already sliced by spaces. You can use constants, and labels inside your inserted instructions like so:
```python
self.instructions = [
    [":loop", 6],
    ["mva", 0],
    ["out", 1],
    ["jmp", ":loop"],
]
```
Be careful tho, because if you hardcode the name of your labels, the next time you use this macro, the same label will be used, and the new on will overwrite the old one's value. Same with constants. It is recommended to append the id of this object to your labels.

## Creating new macros

Let's say, you want a macro that outputs a letter to the character console.

Start by locating the [`assembler_macros/v2_0/__init__.py`](doc/lua_compiler.md) file.

Then scroll down, just abowe the commented "Main" part, and create a new class, with the name of your macro, as the class name, and make sure it inherits the Macro class.
```python
class sayLetter(Macro):
    def execute(self):
        pass
```

After creating the class, and the execute function, we can start writing our macro's code. Start by defining the parameters of this macro. Here, we are ignoring the types of the parameters, but you can add it if you ant to. You my have noticed, the `self.raiseError` function. This sets the success to False, and the error message to the input parameter.

```python
class sayLetter(Macro):
    def execute(self):
        # Check if the macro was called with exactly one argument
        if len(self.arguments) != 1:
            return self.raiseError("Number of parameters does not match")

        # The first argument must be a string, so remove quotes
        character = self.arguments[0][1:-1:]

        return
```

After grabbing the 1st argument from the macro, we have something like this: `#sayLetter "a"` where character will be "a"

The next thing is to write some assembly, that will be put in place of the macro.

```python
class sayLetter(Macro):
    def execute(self):
        # Check if the macro was called with exactly one argument
        if len(self.arguments) != 1:
            return self.raiseError("Number of parameters does not match")

        # The first argument must be a string, so remove quotes
        character = self.arguments[0][1:-1:]

        self.instructions = [
            ["mva", ord(character)], # Put the character code to RA
            ["out", 2], # Output RA's value to the character console
        ]

        return
```

The last thing is to return from the macro, with a success.

```python
class sayLetter(Macro):
    def execute(self):
        # Check if the macro was called with exactly one argument
        if len(self.arguments) != 1:
            return self.raiseError("Number of parameters does not match")

        # The first argument must be a string, so remove quotes
        character = self.arguments[0][1:-1:]

        self.instructions = [
            ["mva", ord(character)], # Put the character code to RA
            ["out", 2], # Output RA's value to the character console
        ]

        self.success = True
        return
```

And now, when we write this line in assembly: `#sayLetter "a"` the letter "a" appears in the console!

### Good job! You succesfully made a working macro for *bcomp assembly V2.0*!