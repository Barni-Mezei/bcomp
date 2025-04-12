import tokeniser

normalised_code = tokeniser.normalise('hjz')
pre_tokens = tokeniser.pre_tokenise(normalised_code)

out = []

for index, token in enumerate(pre_tokens):
    new_token = tokeniser.Token(row = token["row"], col = token["col"])
    new_token.fromString(token["value"])
    out.append(new_token)

tokens = tokeniser.grammar_get_exp(out, 0, "root")
print(tokens)
if tokens: tokeniser.print_tokens(tokens)

tokeniser.print_logs()