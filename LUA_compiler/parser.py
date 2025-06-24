from misc import *

class ParsingError(Exception):
    _place : CharacterPos

    def __init__(self, row : int = -1, col : int = -1, *args):
        super().__init__(*args)

        self._place = CharacterPos(row, col)

    @property
    def row(self):
        return "?" if self._place.row == -1 else self._place.row

    @property
    def place(self) -> str:
        return f"[Ln {str(self._place.row + 1)} Col {str(self._place.col + 1)}]"

    def __str__(self):
        return "\n\t".join(self.args)

class Parser:
    tokens : list
    tree : dict
    code_pointer : int

    def __init__(self, tokens):
        self.tokens = tokens
        self.code_pointer = 0

        self.generate_parse_tree()
    
    # Returns with the current token
    def _peek(self):
        t : Token

        if self.code_pointer >= 0 and self.code_pointer < len(self.tokens):
            t = self.tokens[self.code_pointer]
        else:
            t = Token(TokenType.SPECIAL, "\tEOF")

        return t

    # Returns with the previous token
    def _peek_prev(self):
        t : Token

        if self.code_pointer - 1 >= 0 and self.code_pointer < len(self.tokens):
            t = self.tokens[self.code_pointer - 1]
        else:
            t = Token(TokenType.SPECIAL, "\tEOF")

        return t

    # Returns with the next token and andvances the token pointer
    def _next(self):
        t = self._peek()
        self.code_pointer += 1
        return t

    def accept(self, value : str = None, type : TokenType = None):
        if value:
            if self._peek().value == value:
                self._next()
                return True
        if type:
            if self._peek().type == type:
                self._next()
                return True
        return False

    def expect(self, value : str = None, type : TokenType = None):
        if self.accept(value, type):
            return True
        
        t = self._peek()

        raise ParsingError(t.row, t.col, f"Expected: '{value}'")
        return False

    ###########
    # Grammar #
    ###########

    #############
    # Get <exp> #
    #############

    # TERMINAL
    def try_exp_nil(self):
        if self.accept(type = TokenType.NIL):
            return {"type": "exp", "exp_type": TokenType.NIL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    def try_exp_ellipsis(self):
        if self.accept(type = TokenType.ELLIPSIS):
            return {"type": "exp", "exp_type": TokenType.ELLIPSIS, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    def try_exp_bool(self):
        if self.accept(type = TokenType.BOOL_LITERAL):
            return {"type": "exp", "exp_type": TokenType.BOOL_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    def try_exp_number(self):
        if self.accept(type = TokenType.NUMBER_LITERAL):
            return {"type": "exp", "exp_type": TokenType.NUMBER_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    def try_exp_string(self):
        if self.accept(type = TokenType.STRING_LITERAL):
            return {"type": "exp", "exp_type": TokenType.STRING_LITERAL, "value": self._peek_prev().value[1:-1], "row": self._peek_prev().row, "col": self._peek_prev().col}

        if self.accept(type = TokenType.MULTILINE_STRING_LITERAL):
            if self._peek_prev().value[2] == "=":
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[3:-3], "row": self._peek_prev().row, "col": self._peek_prev().col}
            else:
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[2:-2], "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    """def try_exp_prefixexp(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
        if caller == "prefixexp" and recursion_depth >= max_recursion_depth: return False

        result = grammar_get_prefixexp(code_tokens, code_pointer, "exp", recursion_depth)

        if result == False: return False
        return result[0], result[1]

    def try_exp_unop(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
        if caller == "exp" and recursion_depth >= max_recursion_depth: return False

        if not code_tokens[code_pointer].value in UNOP: return False

        log_group("Expression")
        result_exp = grammar_get_exp(code_tokens, code_pointer + 1, "exp", recursion_depth + 1)
        log_group_end()
        if result_exp == False: return False

        return {"type": "exp", "exp_type": TokenType.UNARY_EXPRESSION, "operand": code_tokens[code_pointer].value, "value": result_exp[0]}, 1 + result_exp[1]

    def try_exp_binop(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
        if caller == "exp" and recursion_depth >= max_recursion_depth: return False

        result_exp1 = grammar_get_exp(code_tokens, code_pointer, "exp", recursion_depth + 1)
        if result_exp1 == False: return False

        pointer_offset = result_exp1[1]

        if not code_tokens[code_pointer + pointer_offset].value in BINOP: return False

        result_exp2 = grammar_get_exp(code_tokens, code_pointer + pointer_offset + 1, "exp", recursion_depth + 1)
        if result_exp2 == False: return False

        pointer_offset += 1 + result_exp2[1]

        return {"type": "exp", "exp_type": TokenType.BINARY_EXPRESSION, "operand": code_tokens[code_pointer + result_exp1[1]].value, "value_a": result_exp1[0], "value_b": result_exp2[0]}, pointer_offset
"""
    def try_exp(self):
        # Try all defined statements
        all_expressions = [
            #self.try_exp_prefixexp,  # Looks like: <var> | "(" <exp> ")"
            #self.try_exp_binop,      # Looks like: <exp> binop <exp>
            self.try_exp_nil,        # Looks like: "nil"
            self.try_exp_ellipsis,   # Looks like: "..."
            self.try_exp_bool,       # Looks like: "true"
            self.try_exp_number,     # Looks like: "5" | "3.25"
            self.try_exp_string,     # Looks like: '"asd"' (between quotes) or '[[asd]]' (in double brackets)
            #self.try_exp_unop,       # Looks like: unop <exp>
        ]

        # Return with the result
        for index, expression in enumerate(all_expressions):
            result = expression()
            if result != False: return result

        # Default to failure (no expression found)
        return False

    def grammar_get_exp(self):
        return self.try_exp()

    #################
    # Get <explist> #
    #################

    def grammar_get_explist(self):
        output : list = []

        while True:
            result = self.grammar_get_exp()

            if not result:
                print(self.code_pointer)
                raise ParsingError(self._peek().row, self._peek().col, "Invalid expression!")
                break
           
            output.append(result)

            if not self.accept(value = ","):
                break

        if len(output) == 0: return False
        return {"type": "explist", "exps": output}

    #############
    # Get <var> #
    #############

    # TERMINAL
    def try_var_name(self):
        if self.accept(type = TokenType.IDENTIFIER):
            return {"type": "var", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    """def try_var_prefix_name(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
        if caller == "prefixexp" and recursion_depth >= max_recursion_depth: return False

        result = grammar_get_prefixexp(code_tokens, code_pointer, "var", recursion_depth)
        if result == False: return False

        if len(code_tokens) >= 3 and code_tokens[code_pointer + 1].value == ".":
            top = code_tokens.pop(code_pointer)
            mid = code_tokens.pop(code_pointer)
            bottom = code_tokens.pop(code_pointer)

            #print("Top:", top, "mid", mid, "bottom", bottom)

            if bottom.type != TokenType.IDENTIFIER:
                code_tokens.insert(code_pointer, bottom)
                bottom = Token()
                if mid.value == ".": return False

            new_token = Token(TokenType.IDENTIFIER, top.value + mid.value + bottom.value, top.row, top.col)

            #print("New token:", new_token)

            code_tokens.insert(code_pointer, new_token)

            #print_tokens(code_tokens)

            return {"type": "var", "value": code_tokens[code_pointer].value, "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

        return False"""

    def try_var(self):
        # Try all defined variables
        all_vars = [
            #try_var_prefix_name,    # Looks like: <prefiexp> "." [a-z][A-Z]
            self.try_var_name,           # Looks like: [a-z][A-Z]*
        ]

        # Return with the result
        for index, var in enumerate(all_vars):
            #print("trying", index)
            result = var()
            if result != False: return result

        # Default to failure (no var found)
        return False

    def grammar_get_var(self):
        return self.try_var()

    #################
    # Get <varlist> #
    #################

    def grammar_get_varlist(self):
        output : list = []

        while True:
            result = self.grammar_get_var()

            if not result:
                raise ParsingError(self._peek().row, self._peek().col, "Invalid identifier!")
                break
           
            output.append(result)

            if not self.accept(value = ","):
                break

        if len(output) == 0: return False
        return {"type": "varlist", "vars": output}

    ##############
    # Get <stat> #
    ##############

    # TERMINAL
    def try_statement_semicolon(self) -> dict:
        if self.accept(value = ";"):
            return {"type": "statement", "stat_type": "semicolon", "value": ";", "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_statement_assignment(self) -> dict:
        result_varlist = self.grammar_get_varlist()
        if not result_varlist: return False

        print("result varlist:", result_varlist)
        print(self.code_pointer, self._peek())

        self.expect(value = "=")

        result_explist = self.grammar_get_explist()
        if not result_varlist: return False

        print("result explist:", result_explist)
        print(self.code_pointer, self._peek())

        #return {"type": "statement", "stat_type": "assignment", "varlist": result_varlist[0], "explist": result_explist[0]}
        return {"type": "statement", "stat_type": "assignment", "varlist": result_varlist}

    def try_statement(self) -> dict:
        # Try all defined statements
        all_statements = [
            self.try_statement_semicolon, # Looks like: ";"
            self.try_statement_assignment, # Looks like: "a.k, b = 'test', 8"
        ]

        # Return with the first result
        for index, statement in enumerate(all_statements):
            result = statement()
            if result != False: return result

        # Default to failure (no statement found)
        return False

    def grammar_get_statement(self) -> dict:
        return self.try_statement()

    ###############
    # Get <block> #
    ###############

    def try_block_statement(self) -> list:
        output : list = []

        while True:
            result = self.grammar_get_statement()

            if not result:
                break

            output.append(result)

        if len(output) == 0: return False
        return output

    def try_block_return_statement(self) -> dict:
        if self.accept(value = "return"):

            explist_result = self.grammar_get_explist()

            self.accept(value = ";")

            return {"type": "return_statement", "explist": explist_result}

    def grammar_get_block(self) -> dict:
        stat_result = self.try_block_statement()

        if not stat_result: return False

        retstat_result = self.try_block_return_statement()

        return {"type": "block", "statements": stat_result, "return_statement": retstat_result}

    ###############
    # Get <chunk> #
    ###############

    def grammar_get_chunk(self) -> dict:
        return self.grammar_get_block()

    def generate_parse_tree(self):
        self.code_pointer = 0
        self.tree = self.grammar_get_chunk()
        print("Tree:", self.tree)