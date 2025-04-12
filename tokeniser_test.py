import tokeniser


def test(code : str, expected_result):
    print(f"Testing code: '{code}'")

    normalised_code = tokeniser.normalise(code)
    pre_tokens = tokeniser.pre_tokenise(normalised_code)
    tokens = tokeniser.tokenise(pre_tokens)

    tokeniser.print_tokens(tokens, "Tokenised code:")

    print("\nExpression parser result:")
    tokeniser.log_tree = []
    tokens = tokeniser.grammar_get_exp(tokens, 0, "root")
    print(tokens)
    if tokens: tokeniser.print_tokens(tokens)

    print("\nLogs:")
    tokeniser.print_logs()
    print("----------")


test("5", tokeniser.TokenType.NUMBER_LITERAL)
test("5.", tokeniser.TokenType.NUMBER_LITERAL)
test(".5", tokeniser.TokenType.NUMBER_LITERAL)
test(".5.", "error")
test("5.0", tokeniser.TokenType.NUMBER_LITERAL)
test("0.5", tokeniser.TokenType.NUMBER_LITERAL)
test("e4", "error")
test("4e", "error")
test("4e6", tokeniser.TokenType.NUMBER_LITERAL)
test("0b", "error")
test("0b3", "error")
test("0b1", tokeniser.TokenType.NUMBER_LITERAL)
test("0x", "error")
test("0x0", "error")
test("0xh", "error")
test("0x4f", tokeniser.TokenType.NUMBER_LITERAL)
test('"H', "error")
test('"H"', tokeniser.TokenType.STRING_LITERAL)
test('"Hello!"', tokeniser.TokenType.STRING_LITERAL)
test('"56"', tokeniser.TokenType.STRING_LITERAL)
test("nil", tokeniser.TokenType.NIL)
test("true", tokeniser.TokenType.BOOL_LITERAL)
test("false", tokeniser.TokenType.BOOL_LITERAL)
test("...", tokeniser.TokenType.ELLIPSIS)
test("a", tokeniser.TokenType.IDENTIFIER)
test("a.b", tokeniser.TokenType.IDENTIFIER)