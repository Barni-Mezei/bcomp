from lib.lib import *

log_tree = []
__log_tree_depth_old = 0 # Old tree depth
__log_tree_depth = 0 # Current tree depth
__log_tree_current_parent = "root"
__log_tree_print_depth = 0 # The indentation level of the printing

def log_group(title : str) -> None:
    global __log_tree_depth
    __log_tree_depth += 1
    log(title, "title")

def log_group_end() -> None:
    global __log_tree_depth
    __log_tree_depth = max(0, __log_tree_depth - 1)

# The error type can be "log" (for a normal error log) or "title" (for a category title)
def log(message : str = "- not specified -", type : str = "log"):
    global log_tree
    global __log_tree_depth
    global __log_tree_depth_old
    global __log_tree_current_parent

    if __log_tree_depth < __log_tree_depth_old:
        # Go 1 level out
        if __log_tree_current_parent != "root":
            __log_tree_current_parent = __log_tree_current_parent["parent"]

    elif __log_tree_depth > __log_tree_depth_old:
        # Go 1 level deeper
        if len(log_tree) != 0:
            __log_tree_current_parent = log_tree.pop()


    log_tree.append({"value": message, "parent": __log_tree_current_parent, "type": type})

    __log_tree_depth_old = __log_tree_depth

def get_parent(node : dict, max_depth : int, depth : int = 0):
    if depth >= max_depth  or (not "parent" in node) or node["parent"] == "root":
        return node, max_depth, depth

    return get_parent(node["parent"], max_depth, depth + 1)

def __print_log(log_tree : list):
    global __log_tree_print_depth

    for log in log_tree:
        indentation_base = "  │ "
        prev_indentation = "  │ "
        indentation      = "...."
        color = WHITE

        if log["type"] == "title":
            color = AQUA
            indentation = "──┬ " if __log_tree_print_depth > 1 else "  ┌ "
            prev_indentation = "  ├─" if __log_tree_print_depth > 1 else "  ┌ "
        if log["type"] == "log":
            indentation = "  ├ "
        if log["type"] == "error":
            color = RED
            indentation_base = f"{RED}────"
            prev_indentation = "────"
            indentation = "──> "
        if __log_tree_print_depth == 0:
            indentation = ""
        if __log_tree_print_depth < 2:
            prev_indentation = ""

        indentation_str = indentation_base * (__log_tree_print_depth - 2) + prev_indentation + indentation

        print(f"{indentation_str}{color}{log['value']}{WHITE}")

        if "children" in log:
            __log_tree_print_depth += 1
            __print_log(log["children"])

    __log_tree_print_depth -= 1

def __remove_parent(node : dict):
    if "parent" in node:
        del node["parent"]
    
    if "children" in node:
        for child in node["children"]:
            __remove_parent(child)

def print_logs():
    global __log_tree_print_depth

    print()

    reversed_log_tree = []

    # Reverse log tree (do not store parents, but the children)
    for log in log_tree:
        root,_,first_depth = get_parent(log, 10)

        for i in range(first_depth):
            d = first_depth - i
            parent,_,_ = get_parent(log, d)
            parent_shallow,_,_ = get_parent(log, d - 1)

            if not "children" in parent:
                parent["children"] = [parent_shallow]
            elif not parent_shallow in parent["children"]:
                parent["children"].append(parent_shallow)

        if not root in reversed_log_tree:
            reversed_log_tree.append(root)

    # Remove "parent" keys (for cleanup)
    for log in reversed_log_tree:
        __remove_parent(log)


    __log_tree_print_depth = 0
    __print_log(reversed_log_tree)

##################################
# Create a test log and print it #
##################################
if __name__ == "__main__":
    log("lvl 0 01")

    log_group("First group")
    log("lvl 1 01")

    log_group("Second group")
    log("lvl 2 01")
    log("lvl 2 02")

    log_group("Inner most group")
    log("lvl 3 01", "error")
    log("lvl 3 02")
    log_group_end()

    log_group("Asd")
    log("lvl 3 03")
    log_group_end()

    log("lvl 2 03")
    log("lvl 2 04")
    log_group_end()

    log("lvl 1 02")
    log_group_end()

    log("lvl 0 02")

    print_logs()