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
    recursion = { # The maximum number of chained 
        "prefixexp": { # prefixexp: "a.b.c.d.e.f" or "a[b[c[d[]]]]"
            "value": 0,
            "current_max": 5,
            "max": 5,
        },

        "exp": { # binop "a + b + c + d + e" or "a and b or c"
            "value": 0,
            "current_max": 5,
            "max": 5,
        },
    }

    error_stack : list

    log_level : int = 0
    debug_indent : int

    def __init__(self, tokens):
        self.tokens = tokens
        self.code_pointer = 0


        self.error_stack = []
        self.debug_indent = 0

        self.generate_parse_tree()

    def log_function(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            
            if self.log_level >= 2:
                print(f"{'| ' * self.debug_indent}Function: {AQUA}{inspect.stack()[1][3]}{WHITE} Current token: {self._peek()}")
                self.debug_indent += 1
            
            result = func(*args, **kwargs)
            
            if self.log_level >= 2:
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

    def accept(self, value : str|list = None, token_type : TokenType = None):
        match : int = 0
        target_match : int = 0
        next_token : Token = self._peek()

        if value:
            target_match += 1
            if type(value) == list and next_token.value in value: match += 1
            elif next_token.value == value: match += 1

        if token_type:
            target_match += 1
            if next_token.type == token_type: match += 1

        # Return
        if match == target_match: self._next()
        return match == target_match


    def expect(self, value : str = None, type : TokenType = None, message = ""):
        if self.accept(value, type): return True
        
        t = self._peek()

        raise ParsingError(t.row, t.col, f"Unexpected symbol near '{self._peek_prev().value}' expected '{value}'" + message)

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

            # Reset recursion counter for expressions, inside parenthesis
            self.recursion["exp"]["current_max"] += self.recursion["exp"]["max"]
            result = self.grammar_get_exp()
            self.recursion["exp"]["current_max"] -= self.recursion["exp"]["max"]

            if not result: return False

            self.expect(value = ")", message = f" to close '(' at {start_parenthesis.place}")

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
        return self.try_prefixexp()

    #############
    # Get <exp> #
    #############

    # TERMINAL
    @log_function
    def try_exp_nil(self):
        if self.accept(token_type = TokenType.NIL):
            return {"type": "exp", "exp_type": TokenType.NIL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_ellipsis(self):
        if self.accept(token_type = TokenType.ELLIPSIS):
            return {"type": "exp", "exp_type": TokenType.ELLIPSIS, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_bool(self):
        if self.accept(token_type = TokenType.BOOL_LITERAL):
            return {"type": "exp", "exp_type": TokenType.BOOL_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_number(self):
        if self.accept(token_type = TokenType.NUMBER_LITERAL):
            return {"type": "exp", "exp_type": TokenType.NUMBER_LITERAL, "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_string(self):
        if self.accept(token_type = TokenType.STRING_LITERAL):
            return {"type": "exp", "exp_type": TokenType.STRING_LITERAL, "value": self._peek_prev().value[1:-1], "row": self._peek_prev().row, "col": self._peek_prev().col}

        if self.accept(token_type = TokenType.MULTILINE_STRING_LITERAL):
            if self._peek_prev().value[2] == "=":
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[3:-3], "row": self._peek_prev().row, "col": self._peek_prev().col}
            else:
                return {"type": "exp", "exp_type": TokenType.MULTILINE_STRING_LITERAL, "value": self._peek_prev().value[2:-2], "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_exp_prefixexp(self):
        return self.grammar_get_prefixexp()

    def try_exp_unop(self):
        operator = self._peek()
        if self.accept(token_type = TokenType.OPERATOR, value = UNOP):
            result = self.grammar_get_exp()
            if not result: return False
            return {"type": "exp", "exp_type": TokenType.UNARY_OPERATOR, "operand": operator.value, "value": result, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False


    def try_exp_binop(self):
        result_exp1 = self.grammar_get_exp()
        if not result_exp1: return False

        operator = self._peek()
        if self.accept(token_type = TokenType.OPERATOR, value = BINOP):
            result_exp2 = self.grammar_get_exp()
            if not result_exp2: return False

            return {"type": "exp", "exp_type": TokenType.BINARY_OPERATOR, "operand": operator.value, "value_a": result_exp1, "value_b": result_exp2}

        return result_exp1

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
            self.try_exp_unop,         # Looks like: unop <exp>
        ]

        if self.recursion["exp"]["value"] < self.recursion["exp"]["current_max"]:
            self.recursion["exp"]["value"] += 1
            all_expressions.insert(0, self.try_exp_binop)

        # Return with the result
        for index, expression in enumerate(all_expressions):
            result = expression()
            if expression == self.try_exp_binop: self.recursion["exp"]["value"] -= 1
            if result != False: return result

        # Default to failure (no expression found)
        #   self.recursion["exp"]["value"] -= 1
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
                raise ParsingError(self._peek().row, self._peek().col, "Invalid expression!")
           
            output.append(result)

        return {"type": "explist", "exps": output}

    #############
    # Get <var> #
    #############

    # TERMINAL
    @log_function
    def try_var_name(self):
        if self.accept(token_type = TokenType.IDENTIFIER):
            return {"type": "var", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_var_prefix_name(self):
        prefix_result = self.grammar_get_prefixexp()
        if not prefix_result: return False

        if self.accept(value = "."):
            if self.accept(token_type = TokenType.IDENTIFIER):
                return {"type": "var", "value": prefix_result["value"]+"."+self._peek_prev().value, "row": prefix_result["row"], "col":  prefix_result["col"]}
            else:
                raise ParsingError(prefix_result["row"], prefix_result["col"], f"Invalid idetifier: '{prefix_result["value"]}.'")


        return prefix_result

    @log_function
    def try_var(self):
        # Try all defined variables
        all_vars = [
            self.try_var_name,           # Looks like: [a-z][A-Z]*
        ]

        if self.recursion["prefixexp"]["value"] < self.recursion["prefixexp"]["current_max"]:
            self.recursion["prefixexp"]["value"] += 1
            all_vars.insert(0, self.try_var_prefix_name)    # Looks like: <prefiexp> "." [a-z][A-Z]

        # Return with the result
        for index, var in enumerate(all_vars):
            result = var()
            if var == self.try_var_prefix_name: self.recursion["prefixexp"]["value"] -= 1
            if result != False: return result

        # Default to failure (no var found)
        #self.recursion["prefixexp"]["value"] -= 1
        return False

    @log_function
    def grammar_get_var(self):
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
                raise ParsingError(self._peek().row, self._peek().col, "Invalid identifier!")
           
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

        self.expect(value = "=")

        result_explist = self.grammar_get_explist()
        if not result_explist: return False

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