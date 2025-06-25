import inspect
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
        return self.place + " " + "\n\t".join(self.args)

class Parser:
    tokens : list
    tree : dict
    code_pointer : int
    max_depth : int # The maximum number of chained a.b.c.d.e.f... and a[b[c[d[]]]]
    depth : int

    error_stack : list

    log_level : int
    debug_indent : int

    def __init__(self, tokens):
        self.tokens = tokens
        self.code_pointer = 0
        self.max_depth = 5
        self.depth = 0

        self.error_stack = []
        self.log_level = 2
        self.debug_indent = 0

        self.generate_parse_tree()

    def log_function(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            if self.log_level < 2: return
            print(f"{'| ' * self.debug_indent}Function ({self.depth}): {AQUA}{inspect.stack()[1][3]}{WHITE} Current token: {self._peek()}")
            self.debug_indent += 1
            result = func(*args, **kwargs)
            self.debug_indent -= 1
            print(f"{'| ' * self.debug_indent}└─")
            return result
        return wrapper

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
        if self.accept(value, type): return True
        
        t = self._peek()

        #self.push_error(ParsingError(t.row, t.col, f"Expected: '{value}'"))
        raise ParsingError(t.row, t.col, f"Expected: '{value}'")
        return False

    def push_error(self, error : ParsingError):
        self.error_stack.append(error)

    ###########
    # Grammar #
    ###########

    ###################
    # Get <prefixexp> #
    ###################

    @log_function
    def try_prefixexp_var(self):
        return self.grammar_get_var()

    @log_function
    def try_prefixexp_exp(self):
        if self.accept(value = "("):

            start_parenthesis = self._peek_prev()

            result = self.grammar_get_exp()
            if not result: return False

            self.expect(value = ")")

            return {"type": "exp", "exp_type": TokenType.LEFT_PARENTHESIS, "value": result, "row": start_parenthesis.row, "col": start_parenthesis.col}


        return False

    @log_function
    def try_prefixexp(self):
        # Try all defined prefixexps
        all_prefixexp = [
            self.try_prefixexp_exp, #Looks like: "(" <exp> ")"
            self.try_prefixexp_var, #Looks like: <var>
        ]

        # Return with the result
        for index, prefixexp in enumerate(all_prefixexp):
            result = prefixexp()
            if result != False: return result

        # Default to failure (no prefixexp found)
        return False

    @log_function
    def grammar_get_prefixexp(self):
        if self.depth > self.max_depth: return False
        else: self.depth += 1

        return self.try_prefixexp()

    #############
    # Get <exp> #
    #############

    # TERMINAL
    @log_function
    def try_exp_nil(self):
        if self.accept(type = TokenType.NIL):
            return {"type": "exp", "exp_type": TokenType.NIL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_ellipsis(self):
        if self.accept(type = TokenType.ELLIPSIS):
            return {"type": "exp", "exp_type": TokenType.ELLIPSIS, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_bool(self):
        if self.accept(type = TokenType.BOOL_LITERAL):
            return {"type": "exp", "exp_type": TokenType.BOOL_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_number(self):
        if self.accept(type = TokenType.NUMBER_LITERAL):
            return {"type": "exp", "exp_type": TokenType.NUMBER_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_string(self):
        if self.accept(type = TokenType.STRING_LITERAL):
            return {"type": "exp", "exp_type": TokenType.STRING_LITERAL, "value": self._peek_prev().value[1:-1], "row": self._peek_prev().row, "col": self._peek_prev().col}

        if self.accept(type = TokenType.MULTILINE_STRING_LITERAL):
            if self._peek_prev().value[2] == "=":
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[3:-3], "row": self._peek_prev().row, "col": self._peek_prev().col}
            else:
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[2:-2], "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_exp_prefixexp(self):
        return self.grammar_get_prefixexp()

    """def try_exp_unop(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
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
    @log_function
    def try_exp(self):
        # Try all defined statements
        all_expressions = [
            self.try_exp_prefixexp,    # Looks like: <var> | "(" <exp> ")"
            self.try_exp_nil,           # Looks like: "nil"
            self.try_exp_ellipsis,      # Looks like: "..."
            self.try_exp_bool,          # Looks like: "true"
            self.try_exp_number,        # Looks like: "5" | "3.25"
            self.try_exp_string,        # Looks like: '"asd"' (between quotes) or '[[asd]]' (in double brackets)
            #self.try_exp_binop,        # Looks like: <exp> binop <exp>
            #self.try_exp_unop,         # Looks like: unop <exp>
        ]

        # Return with the result
        for index, expression in enumerate(all_expressions):
            result = expression()
            if result != False: return result

        # Default to failure (no expression found)
        return False

    @log_function
    def grammar_get_exp(self):
        return self.try_exp()

    #################
    # Get <explist> #
    #################

    # TOKEN
    @log_function
    def grammar_get_explist(self):
        result = self.grammar_get_exp()
        if not result: return False

        output : list = [result]

        while self.accept(value = ","):
            result = self.grammar_get_exp()

            if not result:
                #self.push_error(ParsingError(self._peek().row, self._peek().col, "Invalid expression!"))
                raise ParsingError(self._peek().row, self._peek().col, "Invalid expression!")
                return False
           
            output.append(result)

        return {"type": "explist", "exps": output}

    #############
    # Get <var> #
    #############

    # TERMINAL
    @log_function
    def try_var_name(self):
        if self.accept(type = TokenType.IDENTIFIER):
            return {"type": "var", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_var_prefix_name(self):
        prefix_token = self._peek()

        prefix_result = self.grammar_get_prefixexp()
        if not prefix_result: return False

        if self.accept(value = "."):
            if self.accept(type = TokenType.IDENTIFIER):
                return {"type": "var", "value": prefix_token.value+"."+self._peek_prev().value, "row": prefix_token.row, "col":  prefix_token.col}

        return False

    @log_function
    def try_var(self):
        # Try all defined variables
        all_vars = [
            self.try_var_name,           # Looks like: [a-z][A-Z]*
            self.try_var_prefix_name,    # Looks like: <prefiexp> "." [a-z][A-Z]
        ]

        # Return with the result
        for index, var in enumerate(all_vars):
            #print("trying", index)
            result = var()
            if result != False: return result

        # Default to failure (no var found)
        return False

    @log_function
    def grammar_get_var(self):
        #if self.depth > self.max_depth: return False
        #else: self.depth += 1

        return self.try_var()

    #################
    # Get <varlist> #
    #################

    # TOKEN
    @log_function
    def grammar_get_varlist(self):
        result = self.grammar_get_var()
        if not result: return False

        output : list = [result]


        while self.accept(value = ","):
            result = self.grammar_get_var()

            if not result:
                self.push_error(ParsingError(self._peek().row, self._peek().col, "Invalid identifier!"))
                return False
           
            output.append(result)

        return {"type": "varlist", "vars": output}

    ##############
    # Get <stat> #
    ##############

    # TERMINAL
    @log_function
    def try_statement_semicolon(self) -> dict:
        if self.accept(value = ";"):
            return {"type": "statement", "stat_type": "semicolon", "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TOKEN
    @log_function
    def try_statement_assignment(self) -> dict:
        result_varlist = self.grammar_get_varlist()
        if not result_varlist: return False

        #print("result varlist:", result_varlist)
        #print(self.code_pointer, self._peek())

        self.expect(value = "=")

        result_explist = self.grammar_get_explist()
        if not result_varlist: return False

        #print("result explist:", result_explist)
        #print(self.code_pointer, self._peek())

        return {"type": "statement", "stat_type": "assignment", "varlist": result_varlist, "explist": result_explist}

    @log_function
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

    @log_function
    def grammar_get_statement(self) -> dict:
        return self.try_statement()

    ###############
    # Get <block> #
    ###############

    @log_function
    def try_block_statement(self) -> list:
        output : list = []

        while True:
            if self._peek().value == "\tEOF": break

            result = self.grammar_get_statement()
            if not result: break

            output.append(result)

        return output

    # TOKEN
    @log_function
    def try_block_return_statement(self) -> dict:
        if self.accept(value = "return"):

            explist_result = self.grammar_get_explist()
            if not explist_result: explist_result = []

            self.accept(value = ";")

            return {"type": "return_statement", "explist": explist_result}

        return False

    # TOKEN
    @log_function
    def grammar_get_block(self) -> dict:
        stat_result = self.try_block_statement()
        #if not stat_result: return False

        retstat_result = self.try_block_return_statement()
        #if not retstat_result: return False

        return {"type": "block", "statements": stat_result, "return_statement": retstat_result}

    ###############
    # Get <chunk> #
    ###############

    @log_function
    def grammar_get_chunk(self) -> dict:
        result = self.grammar_get_block()
        if not result: return False

        self.expect(value="\tEOF")

        return result

    def generate_parse_tree(self):
        self.debug_indent = 0

        self.code_pointer = 0
        self.tree = self.grammar_get_chunk()

        if not self.tree:
            for _ in range(len(self.error_stack)):
                print(self.error_stack.pop(0))
    
        print("Tree:", self.tree)