"""
LUA version: 5.3

Resources:
https://www.lua.org/manual/5.3/manual.html

The currently implemented BNF:
------------------------------
chunk ::= block

block ::= {stat} [retstat]

stat ::=  ';' | 
        varlist '=' explist |
        functioncall |
        break | 
        do block end |
        local namelist ['=' <explist>] |
        '::' Name '::' |
        break |
        goto Name |

prefixexp ::= var | '(' exp ')' | functioncall

var ::=  Name | prefixexp '.' Name

varlist ::= var {',' var}

exp ::=  nil | false | true | Numeral | LiteralString | '...' | prefixexp | exp binop exp | unop exp 

explist ::= exp {',' exp}

functioncall ::= prefixexp args | prefixexp ':' Name args

args ::= '(' [explist] ')' | ?LiteralString?
------------------------------
"""

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

        "functioncall": {
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

        self.debug_indent = 0

        self.generate_parse_tree()

    def log_function(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            
            if self.log_level >= 2:
                print(f"{'│' * self.debug_indent}Function: {AQUA}{inspect.stack()[1][3]}{WHITE} Current token: {self._peek()}")
                self.debug_indent += 1
            
            result = func(*args, **kwargs)
            
            if self.log_level >= 2:
                self.debug_indent -= 1
                print(f"{'│' * self.debug_indent}└─")
            
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


    def expect(self, value : str = None, token_type : TokenType = None, message = ""):
        if self.accept(value, token_type): return True
        
        t = self._peek()

        raise ParsingError(t.row, t.col, f"Unexpected symbol near '{self._peek_prev().value}' expected '{value}'" + message)

    ###########
    # Grammar #
    ###########

    ##############
    # Get <args> #
    ##############

    @log_function
    def try_args_string(self):
        if self.accept(token_type = TokenType.STRING_LITERAL):
            return {"type": "args", "arg_type": "string", "value": self._peek_prev().value[1:-1], "row": self._peek_prev().row, "col": self._peek_prev().col}

        if self.accept(token_type = TokenType.MULTILINE_STRING_LITERAL):
            if self._peek_prev().value[2] == "=":
                return {"type": "args", "arg_type": "multiline_string", "value": self._peek_prev().value[3:-3], "row": self._peek_prev().row, "col": self._peek_prev().col}
            else:
                return {"type": "args", "arg_type": "multiline_string", "value": self._peek_prev().value[2:-2], "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False


    @log_function
    def try_args_table(self):
        token = self._peek()

        result = self.grammar_get_tableconstructor()
        if not result: return False

        return {"type": "args", "arg_type": "table", "value": result, "row": token.row, "col": token.col}


    @log_function
    def try_args_explist(self):
        if not self.accept(value = "("): return False

        start_parenthesis = self._peek_prev()

        result = self.grammar_get_explist() # Optional

        self.expect(value = ")", message = f" to close '(' at {start_parenthesis.place}")

        return {"type": "args", "arg_type": "explist", "value": result}

    @log_function
    def try_args(self):
        # Try all defined arguments
        all_args = [
            self.try_args_explist, #Looks like: (4, a, "e")
            #self.try_args_table, #Looks like: {a = 5}
            self.try_args_string, #Looks like: "a"
        ]

        # Return with the result
        for index, arg in enumerate(all_args):
            result = arg()
            if result != False: return result

        # Default to failure (no argument found)
        return False

    @log_function
    def grammar_get_args(self):
        return self.try_args()


    ######################
    # Get <functioncall> #
    ######################

    @log_function
    def try_functioncall_table(self):
        token = self._peek()

        result_prefix = self.grammar_get_prefixexp()
        if not result_prefix: return False
        
        if not self.accept(value = ":"): return False

        result_name = self._peek()
        self.expect(token_type = TokenType.IDENTIFIER)

        result_args = self.grammar_get_args()
        if not result_args: return False

        return {"type": "functioncall", "prefix": result_prefix, "name": result_name.value, "args": result_args, "row": token.row, "col": token.col}

    @log_function
    def try_functioncall_normal(self):
        token = self._peek()

        result_prefix = self.grammar_get_prefixexp()
        if not result_prefix: return False
        
        result_args = self.grammar_get_args()
        if not result_args: return False

        return {"type": "functioncall", "prefix": result_prefix, "name":"", "args": result_args, "row": token.row, "col": token.col}

    @log_function
    def try_functioncall(self):
        # Try all defined function calls
        all_functioncall = [
            self.try_functioncall_table, #Looks like: a:b(4, 5, 6)
            self.try_functioncall_normal, #Looks like: a(4, 5, 6)
        ]

        # Return with the result
        for index, functioncall in enumerate(all_functioncall):
            starting_token_index = self.code_pointer # Store pointer before checking grammar
            result = functioncall()
            if result == False: self.code_pointer = starting_token_index # Restore pointer index, if the grammar does not match
            else: return result

        # Default to failure (no functioncall found)
        return False

    @log_function
    def grammar_get_functioncall(self):
        return self.try_functioncall()

    ###################
    # Get <prefixexp> #
    ###################

    @log_function
    def try_prefixexp_functioncall(self):
        return self.grammar_get_functioncall()

    @log_function
    def try_prefixexp_var(self):
        return self.grammar_get_var()

    @log_function
    def try_prefixexp_exp(self):
        if not self.accept(value = "("): return False

        start_parenthesis = self._peek_prev()

        # Reset recursion counter for expressions, inside parenthesis
        self.recursion["exp"]["current_max"] += self.recursion["exp"]["max"]
        result = self.grammar_get_exp()
        self.recursion["exp"]["current_max"] -= self.recursion["exp"]["max"]

        if not result: return False

        self.expect(value = ")", message = f" to close '(' at {start_parenthesis.place}")

        return {"type": "exp", "exp_type": "parenthesis", "value": result, "row": start_parenthesis.row, "col": start_parenthesis.col}

    @log_function
    def try_prefixexp(self):
        # Try all defined prefixexps
        all_prefixexp = [
            self.try_prefixexp_exp, #Looks like: "(" <exp> ")"
            self.try_prefixexp_var, #Looks like: <var>
        ]

        if self.recursion["functioncall"]["value"] < self.recursion["functioncall"]["current_max"]:
            self.recursion["functioncall"]["value"] += 1
            all_prefixexp.insert(2, self.try_prefixexp_functioncall)

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
            return {"type": "exp", "exp_type": "nil", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_ellipsis(self):
        if self.accept(token_type = TokenType.ELLIPSIS):
            return {"type": "exp", "exp_type": "ellipsis", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_bool(self):
        if self.accept(token_type = TokenType.BOOL_LITERAL):
            return {"type": "exp", "exp_type": "bool", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_number(self):
        if self.accept(token_type = TokenType.NUMBER_LITERAL):
            return {"type": "exp", "exp_type": "number", "value": self._peek_prev().value, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TERMINAL
    @log_function
    def try_exp_string(self):
        if self.accept(token_type = TokenType.STRING_LITERAL):
            return {"type": "exp", "exp_type": "string", "value": self._peek_prev().value[1:-1], "row": self._peek_prev().row, "col": self._peek_prev().col}

        if self.accept(token_type = TokenType.MULTILINE_STRING_LITERAL):
            if self._peek_prev().value[2] == "=":
                return {"type": "exp", "exp_type": "multiline_string", "value": self._peek_prev().value[3:-3], "row": self._peek_prev().row, "col": self._peek_prev().col}
            else:
                return {"type": "exp", "exp_type": "multiline_string", "value": self._peek_prev().value[2:-2], "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    def try_exp_prefixexp(self):
        return self.grammar_get_prefixexp()

    def try_exp_unop(self):
        operator = self._peek()
        if self.accept(token_type = TokenType.OPERATOR, value = UNOP):
            result = self.grammar_get_exp()
            if not result: return False
            return {"type": "exp", "exp_type": "unary_expression", "operand": operator.value, "value": result, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False


    def try_exp_binop(self):
        result_exp1 = self.grammar_get_exp()
        if not result_exp1: return False

        operator = self._peek()
        if self.accept(token_type = TokenType.OPERATOR, value = BINOP):
            result_exp2 = self.grammar_get_exp()
            if not result_exp2: return False

            return {"type": "exp", "exp_type": "binary_expression", "operand": operator.value, "value_a": result_exp1, "value_b": result_exp2}

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

    #################
    # Get <namelist> #
    #################

    # TOKEN
    @log_function
    def grammar_get_namelist(self):
        token : Token = self._peek()
        if not self.accept(token_type = TokenType.IDENTIFIER): return False
        
        output : list = [token.value]

        while self.accept(value = ","):
            token = self._peek()
            self.expect(token_type = TokenType.IDENTIFIER, message = "Invalid identifier!")

            #if not result:
            #    raise ParsingError(self._peek().row, self._peek().col, "Invalid identifier!")
        
            output.append(token.value)

        return {"type": "namelist", "names": output}


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
                raise ParsingError(prefix_result["row"], prefix_result["col"], f"Invalid identifier: '{prefix_result["value"]}.'")


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

        if not self.accept(value = "="): return False

        result_explist = self.grammar_get_explist()
        if not result_explist: raise ParsingError(self._peek_prev().row, self._peek_prev().col, "An exression is expected!")

        return {"type": "statement", "stat_type": "assignment", "varlist": result_varlist, "explist": result_explist}

    # TERMINAL
    @log_function
    def try_statement_break(self) -> dict:
        if self.accept(token_type = TokenType.KEYWORD, value = "break"):
            return {"type": "statement", "stat_type": "keyword", "value": "break", "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TOKEN
    @log_function
    def try_statement_do(self) -> dict:
        token = self._peek()
        
        if self.accept(token_type = TokenType.KEYWORD, value = "do"):

            # Reset recursion limits
            self.recursion["exp"]["current_max"] += self.recursion["exp"]["max"]
            self.recursion["prefixexp"]["current_max"] += self.recursion["prefixexp"]["max"]
            result = self.grammar_get_block()
            self.recursion["exp"]["current_max"] -= self.recursion["exp"]["max"]
            self.recursion["prefixexp"]["current_max"] -= self.recursion["prefixexp"]["max"]

            if not result: return False

            self.expect(token_type = TokenType.KEYWORD, value = "end")

            return {"type": "statement", "stat_type": "keyword", "value": "do", "block": result, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

    # TOKEN
    @log_function
    def try_statement_while(self) -> dict:
        token = self._peek()
        
        if not self.accept(token_type = TokenType.KEYWORD, value = "while"): return False

        result_exp = self.grammar_get_exp()
        if not result_exp: raise ParsingError(token.row, token.col, f"Invalid expression, in while loop!")

        self.expect(token_type = TokenType.KEYWORD, value = "do")

        # Reset recursion limits
        self.recursion["exp"]["current_max"] += self.recursion["exp"]["max"]
        self.recursion["prefixexp"]["current_max"] += self.recursion["prefixexp"]["max"]
        result_block = self.grammar_get_block()
        self.recursion["exp"]["current_max"] -= self.recursion["exp"]["max"]
        self.recursion["prefixexp"]["current_max"] -= self.recursion["prefixexp"]["max"]

        self.expect(token_type = TokenType.KEYWORD, value = "end")

        return {"type": "statement", "stat_type": "keyword", "value": "while", "exp": result_exp, "block": result_block, "row": token.row, "col": token.col}

    # TOKEN
    @log_function
    def try_statement_functioncall(self) -> dict:
        return self.grammar_get_functioncall()

    # TOKEN
    @log_function
    def try_statement_label(self) -> dict:
        if not self.accept(token_type = TokenType.PUNCTUATION, value = "::"): return False

        token = self._peek()

        self.expect(token_type = TokenType.IDENTIFIER)
        self.expect(token_type = TokenType.PUNCTUATION, value = "::")

        return {"type": "statement", "stat_type": "label", "value": token.value, "row": token.row, "col": token.col}
    
    # TOKEN
    @log_function
    def try_statement_goto(self) -> dict:
        token = self._peek()
        if not self.accept(token_type = TokenType.KEYWORD, value = "goto"): return False

        name_token = self._peek()

        self.expect(token_type = TokenType.IDENTIFIER)

        return {"type": "statement", "stat_type": "keyword", "value": "goto", "label": name_token.value, "row": token.row, "col": token.col}

    # TOKEN
    @log_function
    def try_statement_local(self) -> dict:
        if self.accept(token_type = TokenType.KEYWORD, value = "local"):
            result_namelist = self.grammar_get_namelist()
            if not result_namelist: raise ParsingError(self._peek_prev().row, self._peek_prev().col, f"Invalid identifier: '{self._peek_prev.value}'")

            result_explist = False

            if self.accept(value = "="):
                result_explist = self.grammar_get_explist()

            return {"type": "statement", "stat_type": "keyword", "value": "local", "namelist": result_namelist, "explist": result_explist, "row": self._peek_prev().row, "col": self._peek_prev().col}

        return False

   
    @log_function
    def try_statement(self) -> dict:
        # Try all defined statements
        all_statements = [
            self.try_statement_semicolon, # Looks like: ";"
            self.try_statement_assignment, # Looks like: "a.k, b = 'test', 8"
            self.try_statement_functioncall, # Looks like: <functioncall>
            self.try_statement_label, # Looks like: "::" <name> "::"
            self.try_statement_break, # Looks like: "break"
            self.try_statement_goto, # Looks like: "goto" <name>
            self.try_statement_do, # Looks like: "do" <block> "end"
            self.try_statement_while, # Looks like: "while" <exp> "do" <block> "end"
            self.try_statement_local, # Looks like: "local" <namelist> ["=" <explist>]
        ]

        # Return with the first result
        for index, statement in enumerate(all_statements):
            starting_token_index = self.code_pointer # Store pointer before checking grammar
            result = statement()
            if result == False: self.code_pointer = starting_token_index # Restore pointer index, if the grammar does not match
            else: return result

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
        token = self._peek()

        if self.accept(value = "return"):

            explist_result = self.grammar_get_explist()
            if not explist_result: explist_result = []

            self.accept(value = ";")

            return {"type": "return_statement", "explist": explist_result, "row": token.row, "col": token.col}

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
    
        # Debug
        print("Tree:", self.tree)



    # Prints a single token out to the screen, as a tree
    def print_parse_tree(self, token : dict = None, indentation_level : int = 0) -> None:
        if token is None and self.tree:
            self.print_parse_tree(self.tree)
            return

        tab = " " * indentation_level
        tab2 = " " * (indentation_level + 4)

        #print("TOKEN", token)
        print(tab + f"{token['type'].replace("_", " ").capitalize()}:", end="")

        match token["type"]:
            case "var":
                print(f" '{token['value']}'")

            case "exp":
                match token['exp_type']:
                    case "unary_expression":
                        print(f" '{token['operand']}' (unop)")
                        self.print_parse_tree(token['value'], indentation_level + 4)
                    
                    case "binary_expression":
                        print(f" '{token['operand']}'")
                        self.print_parse_tree(token['value_a'], indentation_level + 4)
                        self.print_parse_tree(token['value_b'], indentation_level + 4)
                    
                    case "parenthesis":
                        print(f" (")
                        self.print_parse_tree(token['value'], indentation_level + 4)
                        print(tab + ")")
                    
                    case _:
                        print(f" '{token['value']}' ({token['exp_type']})")

            case "args":
                match token['arg_type']:
                    case "explist":
                        print(f" (explist)")
                        if token['value']: self.print_parse_tree(token['value'], indentation_level + 4)
                    
                    case "string":
                        print(f" (string)")
                        self.print_parse_tree(token['value'], indentation_level + 4)
                    
                    case "table":
                        print(f" (table)")
                        self.print_parse_tree(token['value'], indentation_level + 4)
                    
                    case _:
                        print(f"{RED}Unknown{WHITE}")

            case "varlist":
                print()
                for v in token["vars"]: self.print_parse_tree(v, indentation_level + 4)
            
            case "namelist":
                print()
                for n in token["names"]: print(tab2 + "Name: '" + n + "'")

            case "explist":
                print()
                for e in token["exps"]: self.print_parse_tree(e, indentation_level + 4)

            case "statement":
                print(f" ({token['stat_type']})")
                match token["stat_type"]:
                    case "semicolon":
                        pass
                    
                    case "assignment":
                        self.print_parse_tree(token["varlist"], indentation_level + 4)
                        self.print_parse_tree(token["explist"], indentation_level + 4)
                    
                    case "label":
                        print(tab2 + f"{AQUA}::{token['value']}::{WHITE}")

                    case "keyword":
                        match token["value"]:
                            case "break":
                                print(tab2 + f"{RED}break{WHITE}")

                            case "goto":
                                print(tab2 + f"{RED}goto{WHITE}")
                                print(tab2 + f"Label: {AQUA}{token['label']}{WHITE}")

                            case "do":
                                print(tab2 + f"{RED}do{WHITE}")
                                self.print_parse_tree(token["block"], indentation_level + 4)
                                print(tab2 + f"{RED}end{WHITE}")

                            case "while":
                                print(tab2 + f"{RED}while{WHITE}")
                                self.print_parse_tree(token["exp"], indentation_level + 4)
                                print(tab2 + f"{RED}do{WHITE}")
                                self.print_parse_tree(token["block"], indentation_level + 4)
                                print(tab2 + f"{RED}end{WHITE}")

                            case "local":
                                print(tab2 + f"{RED}local{WHITE}")
                                self.print_parse_tree(token["namelist"], indentation_level + 4)
                                if token["explist"]: 
                                    self.print_parse_tree(token["explist"], indentation_level + 4)

            case "return_statement":
                print()
                self.print_parse_tree(token["explist"], indentation_level + 4)

            case "block":
                print()
                print(tab2 + f"Statements:")
                for s in token["statements"]: self.print_parse_tree(s, indentation_level + 8)

                if token["return_statement"]:
                    self.print_parse_tree(token["return_statement"], indentation_level + 4)

            case "functioncall":
                print()
                print(tab2 + f"Prefix:")
                self.print_parse_tree(token["prefix"], indentation_level + 8)
                print(tab2 + f"Name: {AQUA}'{token["name"]}'{WHITE}")
                print(tab2 + f"Arguments:")
                self.print_parse_tree(token["args"], indentation_level + 8)