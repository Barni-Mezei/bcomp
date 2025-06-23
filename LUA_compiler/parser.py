from misc import *

class ParsingError(Exception):
    _place : CharacterPos

    def __init__(self, row : int = -1, col : int = -1, *args):
        super().__init__(*args)

        self._place = CharacterPos(row, col)

    @property
    def row(self):
        return "?" if self._place.row == -1 else self._place.row

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        raise ParsingError(0, 0, "Parser not implemented...")
    
    def _generate_parse_tree(self):
        pass