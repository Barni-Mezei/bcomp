from enum import Enum

RED = "\033[31m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
AQUA = "\033[36m"
GRAY = "\033[90m"
WHITE = "\033[0m"



UNOP = ["-", "not", "#", "~"]
BINOP = ["+", "-", "*", "/", "//", "^", "%",
         "&", "~", "|", ">>", "<<", ".."
         "<", "<=", ">", ">=", "==", "~=",
         "and", "or"]

OPERATORS = UNOP + BINOP

TOKEN_SEPARATORS = [
    "\n",
    " ",
    ",",
    ":",
    ".",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]"
] + OPERATORS

BLOCK_BOUNDARY = [
    "\n",
    "end"
]

STRING_BOUNDARY = [
    "\"",
    "'",
    "`"
]

KEYWORDS = [
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "goto",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while"
]

class TokenType(Enum):
    UNKNOWN = -1
    KEYWORD = 0
    COMMENT = 1
    IDENTIFIER = 2
    TABLE = 3
    OPERATOR = 4
    STRING_LITERAL = 5
    NUMBER_LITERAL = 6
    BOOL_LITERAL = 7
    ELLIPSIS = 8
    NIL = 9
    UNARY_EXPRESSION = 10 # ~, not
    BINARY_EXPRESSION= 11 # +, and
    SPECIAL = 99 # The control characters


class CharacterPos:
    row : int = 0
    col : int = 0

    def __init__(self, row : int, column : int) -> None:
        self.row = row
        self.col = column

class Token:
    type : TokenType = TokenType.UNKNOWN
    value : str = ""
    _place : CharacterPos

    def __init__(self, type : TokenType = TokenType.UNKNOWN, value : str = "", row = -1, col = -1) -> None:
        self.type = type
        self.value = value
        self._place = CharacterPos(row, col)

    def get_place_str(self) -> str:
        return f"[Ln {str(self._place.row + 1)} Col {str(self._place.col + 1)}]"

    @property
    def row(self):
        return self._place.row

    @property
    def col(self):
        return self._place.col

    def __str__(self):
        text_color = WHITE

        match self.type:
            case TokenType.UNKNOWN: text_color = GRAY
            case TokenType.KEYWORD: text_color = RED
            case TokenType.COMMENT: text_color = GRAY
            case TokenType.IDENTIFIER: text_color = WHITE
            case TokenType.TABLE: text_color = WHITE
            case TokenType.OPERATOR: text_color = AQUA
            case TokenType.STRING_LITERAL: text_color = YELLOW
            case TokenType.NUMBER_LITERAL: text_color = AQUA
            case TokenType.BOOL_LITERAL: text_color = GREEN
            case TokenType.ELLIPSIS: text_color = AQUA
            case TokenType.NIL: text_color = RED
            case TokenType.UNARY_EXPRESSION: text_color = WHITE
            case TokenType.BINARY_EXPRESSION: text_color = WHITE
            case TokenType.SPECIAL: text_color = RED

        return f"{text_color}{str(self.type).split('.')[1]:<20}{WHITE}{self.place:<15}{(GREEN if self.value == '\tSOF' else RED) + self.value.replace(chr(9), '') + WHITE if self.type == TokenType.SPECIAL else repr(self.value)}"
