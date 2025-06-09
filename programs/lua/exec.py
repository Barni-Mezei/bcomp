#!/usr/bin/env python3

import sys
import os
import inspect
import time
import keyboard # type: ignore
from lupa import LuaRuntime # type: ignore

default_libs = [".\\math.lua", ".\\vector.lua", ".\\matrix.lua"]

class LuaEngine:
    def delay(ms):
        time.sleep(ms/1000)
   
    def getArguments():
        return sys.argv[2::]

    def clear():
        print("\033c")
        #os.system('cls' if os.name == 'nt' else 'clear')
        pass

    def getWidth():
        return os.get_terminal_size().columns

    def getHeight():
        return os.get_terminal_size().lines

    def exit(code = 0):
        exit(code)

    def keyIsDown(key):
        return keyboard.is_pressed(key)

    def repeatChar(char, n):
        return str(char)*int(n)

    def write(char):
        sys.stdout.write(char)

    def flush():
        sys.stdout.flush()

def get_class_methods(cls):
    methods = []
    for name, func in inspect.getmembers(cls, predicate = inspect.isfunction):
        methods.append({
            "name": name,
            "func": func,
        })
    return methods

def main(file_path_array):
    # Create a Lua runtime
    lua = LuaRuntime(unpack_returned_tuples=True)

    # Add custom functions to lua
    for method in get_class_methods(LuaEngine):
        lua.globals()[method["name"]] = method["func"]

    # Read the Lua script(s)
    lua_code = ""
    full_len = 0
    for path in file_path_array:
        with open(path, 'r', encoding="utf-8") as lua_file:
            for line in lua_file:
                lua_code += line
                full_len += 1

        #Include new line to the counting
        lua_code += "\n"
        full_len += 1


    # Execute the Lua code
    try:
        lua.execute(lua_code)
    except Exception as e:
        print(f"A \033[96mLUA\033[0m error occured (total: {full_len} lines):\n", e)

if __name__  == "__main__":
    lua_files = default_libs + list(set(sys.argv[1::]) - set(default_libs))

    if len(lua_files) > 0:
        main(lua_files)
    else:
        print("Invalid synax! (Minimum 1 '.lua' file must be provided)")
