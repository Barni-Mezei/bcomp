# Add the outter folder to the paths so python can see the "lib" python file
import sys
import os
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), '..')) )

# Import modules
from lib.lib import *
import tokeniser

def test_fail():
    print(f"Test {RED}FAILED{WHITE}")
    return False

def test_pass():
    global completed_tests
    completed_tests += 1

    print(f"Test {GREEN}PASSED{WHITE}")
    return True

def _test_main(code : str):
    global max_tests
    max_tests += 1

    normalised_code = tokeniser.normalise(code)
    pre_tokens = tokeniser.pre_tokenise(normalised_code)
    tokens = tokeniser.tokenise(pre_tokens)

    tokeniser.log_tree = []
    tokeniser.reset_logs()

    return tokens

def test_exp(code : str, expected_result):
    print(f"Testing code (exp) {GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    if log_level == 2: tokeniser.print_tokens(tokens, "Tokenised code:")

    if log_level > 0: print("Expression parser result: ", end="")
    tokens = tokeniser.grammar_get_exp(tokens, 0, "root")

    if log_level > 0:
        if tokens == False: print(f"{RED}False{WHITE}")
        else: print(tokens)

    if tokens == False:
        if expected_result == "error":
            test_pass()
        else:
            test_fail()
    else:
        if expected_result == tokeniser.TokenType.IDENTIFIER and tokens[0]["type"] == "var":
            test_pass()
        elif tokens[0]["type"] == "exp" and tokens[0]["exp_type"] == expected_result:
            test_pass()
        else:
            test_fail()

    if log_level == 2:
        print("\nLogs:")
        tokeniser.print_logs()
    if log_level > 0: print("----------")

def test_var(code : str, expected_result):
    print(f"Testing code (var) {GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    if log_level == 2: tokeniser.print_tokens(tokens, "Tokenised code:")

    if log_level > 0: print("Expression parser result: ", end="")
    tokens = tokeniser.grammar_get_var(tokens, 0, "root")
    print("TOKENS", tokens)

    if log_level > 0:
        if tokens == False: print(f"{RED}False{WHITE}")
        else: print(tokens)

    if tokens == False:
        if expected_result == "error":
            test_pass()
        else:
            test_fail()
    else:
        if tokens[0]["type"] == "var" and tokens[0]["value"] == expected_result:
            test_pass()
        else:
            test_fail()

    if log_level == 2:
        print("\nLogs:")
        tokeniser.print_logs()
    if log_level > 0: print("----------")

def test_varlist(code : str, expected_result):
    print(f"Testing code (varlist) {GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    if log_level == 2: tokeniser.print_tokens(tokens, "Tokenised code:")

    if log_level > 0: print("Expression parser result: ", end="")
    tokens = tokeniser.grammar_get_varlist(tokens, 0, "root")

    if log_level > 0:
        if tokens == False: print(f"{RED}False{WHITE}")
        else: print(tokens)

    if tokens == False:
        if expected_result == "error":
            test_pass()
        else:
            test_fail()
    else:
        if tokens[0]["type"] == "varlist":
            if not len(tokens[0]["vars"]) == len(expected_result):
                test_fail()
            else:
                success = True
                for index, var in enumerate(tokens[0]["vars"]):
                    if not var["value"] == expected_result[index]:
                        success = False
                        break
                if success: test_pass()
                else: test_fail()
        else:
            test_fail()

    if log_level == 2:
        print("\nLogs:")
        tokeniser.print_logs()
    if log_level > 0: print("----------")

def test_explist(code : str, expected_result):
    print(f"Testing code (explist) {GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    if log_level == 2: tokeniser.print_tokens(tokens, "Tokenised code:")

    if log_level > 0: print("Expression parser result: ", end="")
    tokens = tokeniser.grammar_get_explist(tokens, 0, "root")

    if log_level > 0:
        if tokens == False: print(f"{RED}False{WHITE}")
        else: print(tokens)

    if tokens == False:
        if expected_result == "error":
            test_pass()
        else:
            test_fail()
    else:
        if tokens[0]["type"] == "explist":
            if not len(tokens[0]["exps"]) == len(expected_result):
                test_fail()
            else:
                success = True
                for index, var in enumerate(tokens[0]["exps"]):
                    if not var["value"] == expected_result[index]:
                        success = False
                        break
                if success: test_pass()
                else: test_fail()
        else:
            test_fail()

    if log_level == 2:
        print("\nLogs:")
        tokeniser.print_logs()
    if log_level > 0: print("----------")

def test_statement_modes(tokens : list, expected_result):
    match expected_result[0]:
        case "semicolon":
            if not tokens[0]["value"] == ";":
                return False

        case "assignment":
            if not "varlist" in tokens[0] or not "explist" in tokens[0]:
                return False

            if not len(tokens[0]["varlist"]["vars"]) == len(expected_result[1]) or\
            not len(tokens[0]["explist"]["exps"]) == len(expected_result[2]):
                return False

            # Check if variables match
            for index, var in enumerate(tokens[0]["varlist"]["vars"]):
                if not var["value"] == expected_result[1][index]:
                    return False
            
            # Check if expressions match
            for index, var in enumerate(tokens[0]["explist"]["exps"]):
                if not var["value"] == expected_result[2][index]:
                    return False
    return True

def test_statement(code : str, expected_result):
    print(f"Testing code (statement) {GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    if log_level == 2: tokeniser.print_tokens(tokens, "Tokenised code:")

    if log_level > 0: print("Expression parser result: ", end="")
    tokens = tokeniser.grammar_get_statement(tokens, 0, "root")

    if log_level > 0:
        if tokens == False: print(f"{RED}False{WHITE}")
        else: print(tokens)

    if tokens == False:
        if expected_result == "error":
            test_pass()
        else:
            test_fail()
    else:
        if tokens[0]["type"] == "statement":
            if not tokens[0]["stat_type"] == expected_result[0]:
                test_fail()
            else:
                success = test_statement_modes(tokens, expected_result)

                # Set state
                if success: test_pass()
                else: test_fail()
        else:
            test_fail()

    if log_level == 2:
        print("\nLogs:")
        tokeniser.print_logs()
    if log_level > 0: print("----------")

def test_code(code : str):
    print(f"Testing full code:\n{GRAY}'{code}'{WHITE}")

    tokens = _test_main(code)

    tokeniser.print_tokens(tokens, "Tokenised code:")

    print("Chunk parser result: ", end="")
    tokens = tokeniser.model(tokens)

    if tokens == False:
        print(f"{RED}False{WHITE}")
        test_fail()
    else:
        print(tokens)
        test_pass()

    print("\nLogs:")
    tokeniser.print_logs()
    print("----------")

############
# Settings #
############

# Log level:
# 0: Only results
# 1: Reults and states
# 2: Everything
log_level = 0

max_tests = 0
completed_tests = 0

#########
# Tests #
#########

test_exp("5", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("5.", tokeniser.TokenType.NUMBER_LITERAL)
test_exp(".5", tokeniser.TokenType.NUMBER_LITERAL)
test_exp(".5.", tokeniser.TokenType.NUMBER_LITERAL) # .5 .
test_exp(".5.0", tokeniser.TokenType.NUMBER_LITERAL) # .5 .0
test_exp(".5.0.", tokeniser.TokenType.NUMBER_LITERAL) # .5 .0 .
test_exp("5.0.", tokeniser.TokenType.NUMBER_LITERAL) # 5.0 .
test_exp("5.0", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("0.5", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("e4", tokeniser.TokenType.IDENTIFIER)
test_exp("4e", "error")
test_exp("4e6", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("0b", "error")
test_exp("0b3", "error")
test_exp("0b1", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("0x", "error")
test_exp("0x0", tokeniser.TokenType.NUMBER_LITERAL)
test_exp("0xh", "error")
test_exp("0x4f", tokeniser.TokenType.NUMBER_LITERAL)
test_exp('"H', "error")
test_exp('"H"', tokeniser.TokenType.STRING_LITERAL)
test_exp('"Hello!"', tokeniser.TokenType.STRING_LITERAL)
test_exp('"Multi word"', tokeniser.TokenType.STRING_LITERAL)
test_exp('"Multi\nline"', "error")
test_exp(r'"Escaped \" quotes \""', tokeniser.TokenType.STRING_LITERAL)
test_exp('"56"', tokeniser.TokenType.STRING_LITERAL)
test_exp("nil", tokeniser.TokenType.NIL)
test_exp("true", tokeniser.TokenType.BOOL_LITERAL)
test_exp("false", tokeniser.TokenType.BOOL_LITERAL)
test_exp("...", tokeniser.TokenType.ELLIPSIS)
test_exp("a", tokeniser.TokenType.IDENTIFIER)
test_exp("a.b", tokeniser.TokenType.IDENTIFIER)

test_var("a", "a")
test_var("a.b", "a.b")
test_var("house.door", "house.door")
test_var("house.door.frame", "house.door.frame")
test_var("house.door.", "error")
test_var(".house.door", "error")
test_var(".house.door.", "error")
test_var(".g", "error")
test_var(".", "error")
test_var("k.l..g", "k.l")
test_var("4abc", "error")
test_var("abc4_", "abc4_")

test_varlist("", "error")
test_varlist("a", ["a"])
test_varlist("a.b", ["a.b"])
test_varlist("a.b., c", "error")
test_varlist("a, b", ["a", "b"])
test_varlist("a.b, c", ["a.b", "c"])
test_varlist("a.b.c,  d.e, f, g.h", ["a.b.c", "d.e", "f", "g.h"])
test_varlist("h,", ["h"])
test_varlist(",k", "error")

test_explist("5", ["5"])
test_explist("5.", ["5."])
test_explist(".5.", [".5"])
test_explist("a.b, 4", ["a.b", "4"])
test_explist("a.b, 5.45, nil", ["a.b", "5.45", "nil"])
test_explist("false,", ["false"])
test_explist(",true", "error")

test_statement(";", ["semicolon"])
test_statement("5", "error")
test_statement("a.b", "error")
test_statement("c =", "error")
test_statement("= 67", "error")
test_statement("a = 5", ["assignment", ["a"], ["5"]])
test_statement("house.door = 34.6", ["assignment", ["house.door"], ["34.6"]])
test_statement('house.door, a = 12., "string"', ["assignment", ["house.door", "a"], ["12.", '"string"']])
test_statement('house.door., a = 12., "string"', "error")
test_statement('house.door, = 5', "error")

test_code('house.door = 5\na = 6')

##############
# Evaluation #
##############

print("\nAll tests finished.")
print(f"Number of tests: {GRAY}{max_tests}{WHITE}")
print(f"Succesful tests: {GRAY}{completed_tests}{WHITE}")
print(f"Failed tests: {GRAY}{max_tests - completed_tests}{WHITE}")

ratio = completed_tests / max_tests
bar_length = 20
fill_length = round(bar_length * ratio)
empty_length = bar_length - fill_length

print(f"Result: {GREEN + 'PASS' if completed_tests ==  max_tests else RED + 'FAIL'}{WHITE} [{'='*(fill_length-1)}>{'.'*empty_length}] ({round(ratio * 100, 1)}%)")