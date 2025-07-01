import sys
import os

# Import modules
from misc import *
from lexer import Lexer

def test_fail():
    print(f"Test {RED}FAILED{WHITE}")
    return False

def test_pass():
    global completed_tests
    completed_tests += 1

    print(f"Test {GREEN}PASSED{WHITE}")
    return True

def run_test(code : str, expected_tokens : list) -> bool:
    global max_tests
    max_tests += 1

    print(f"Testing code: {GRAY}'{code}'{WHITE}")

    lexer = Lexer()

    # try tokenising code
    try:
        lexer.tokenise_string(code)
    except:
        return test_fail()

    # Print tokens
    if log_level > 0:
        for t in lexer.tokens:
            print(t)

    # Compare result
    if len(lexer.tokens) != len(expected_tokens) + 1: return test_fail()
    
    success = True
    for i, t in enumerate(expected_tokens):
        if not t.value == lexer.tokens[i].value or not t.type == lexer.tokens[i].type:
            success = False
            break

    # Return result
    if success: return test_pass()

    return test_fail()

############
# Settings #
############

# Log level:
# 0: Only results
# 1: Reults & tokens
log_level = 0

max_tests = 0
completed_tests = 0

#########
# Tests #
#########

run_test("a = 5", [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "="), Token(TokenType.NUMBER_LITERAL, "5")])
run_test("a= 5", [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "="), Token(TokenType.NUMBER_LITERAL, "5")])
run_test("a =5", [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "="), Token(TokenType.NUMBER_LITERAL, "5")])
run_test("a=5", [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "="), Token(TokenType.NUMBER_LITERAL, "5")])

run_test("if a == 6", [Token(TokenType.KEYWORD, "if"), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "=="), Token(TokenType.NUMBER_LITERAL, "6")])
run_test("if a== 6", [Token(TokenType.KEYWORD, "if"), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "=="), Token(TokenType.NUMBER_LITERAL, "6")])
run_test(" if   a==    6", [Token(TokenType.KEYWORD, "if"), Token(TokenType.IDENTIFIER, "a"), Token(TokenType.OPERATOR, "=="), Token(TokenType.NUMBER_LITERAL, "6")])
run_test('print("Hello")', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.STRING_LITERAL, '"Hello"'), Token(TokenType.RIGHT_PARENTHESIS, ")")])
run_test('print("Hello")--comment', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.STRING_LITERAL, '"Hello"'), Token(TokenType.RIGHT_PARENTHESIS, ")")])
run_test('print("Hello") -- comment', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.STRING_LITERAL, '"Hello"'), Token(TokenType.RIGHT_PARENTHESIS, ")")])
run_test('print([[Hello]])', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.MULTILINE_STRING_LITERAL, '[[Hello]]'), Token(TokenType.RIGHT_PARENTHESIS, ")")])
run_test('print([=[Hello]=])', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.MULTILINE_STRING_LITERAL, '[=[Hello]=]'), Token(TokenType.RIGHT_PARENTHESIS, ")")])
run_test('print([=[[[Hello]=])', [Token(TokenType.IDENTIFIER, "print"), Token(TokenType.LEFT_PARENTHESIS, "("), Token(TokenType.MULTILINE_STRING_LITERAL, '[=[[[Hello]=]'), Token(TokenType.RIGHT_PARENTHESIS, ")")])

run_test('a, b = 4, 5', [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.IDENTIFIER, 'b'), Token(TokenType.OPERATOR, '='), Token(TokenType.NUMBER_LITERAL, "4"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.NUMBER_LITERAL, '5')])
run_test('a,b=4,5', [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.IDENTIFIER, 'b'), Token(TokenType.OPERATOR, '='), Token(TokenType.NUMBER_LITERAL, "4"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.NUMBER_LITERAL, '5')])
run_test(' a,   b=   4, 5   ', [Token(TokenType.IDENTIFIER, "a"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.IDENTIFIER, 'b'), Token(TokenType.OPERATOR, '='), Token(TokenType.NUMBER_LITERAL, "4"), Token(TokenType.PUNCTUATION, ","), Token(TokenType.NUMBER_LITERAL, '5')])

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