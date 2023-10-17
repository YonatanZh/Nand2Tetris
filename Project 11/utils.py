import re

KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
STRING_CONST = "STRING_CONST"
INT_CONST = "INT_CONST"

# keywords
CLASS = 'class'
CONSTRUCTOR = 'constructor'
FUNCTION = 'function'
METHOD = 'method'
FIELD = 'field'
STATIC = 'static'
VAR = 'var'
INT = 'int'
CHAR = 'char'
BOOL = 'boolean'
VOID = 'void'
TRUE = 'true'
FALSE = 'false'
NULL = 'null'
THIS = 'this'
LET = 'let'
DO = 'do'
IF = 'if'
ELSE = 'else'
WHILE = 'while'
RETURN = 'return'
KEY_WORDS = [
    CLASS, CONSTRUCTOR, FUNCTION, METHOD, FIELD, STATIC, VAR, INT, CHAR, BOOL, VOID, TRUE, FALSE, NULL, THIS, LET, DO,
    IF, ELSE, WHILE, RETURN
]

# symboles
L_CURLY_BRACE = '\{'
R_CURLY_BRACE = '\}'
L_BRACE = '\('
R_BRACE = '\)'
L_SQUARE_BRACES = '\['
R_SQUARE_BRACES = '\]'
DOT = '\.'
COMMA = ','
SEMI_COLON = ';'
PLUS = '\+'
MINUS = '-'
ASTERISK = '\*'
SLASH = '\/'
AND = '&'
PIPE = '\|'
LESS = '<'
MORE = '>'
EQUAL = '='
SIM = '~'
UP = '\^'
SHARP = '#'
SYMBOLS = [
    L_CURLY_BRACE, R_CURLY_BRACE, L_BRACE, R_BRACE, L_SQUARE_BRACES, R_SQUARE_BRACES, DOT, COMMA, SEMI_COLON,
    PLUS, MINUS, ASTERISK, SLASH, AND, PIPE, LESS, MORE, EQUAL, SIM, UP,
    SHARP
]

COMMENT_START = r'\/\*'
COMMENT_END = r'\*\/'
COMMENT = fr'({COMMENT_START}|{COMMENT_END})'

KEY_WORDS_REGEX = '|'.join(KEY_WORDS)
SYMBOLS_REGEX = '|'.join(SYMBOLS)
INTEGER_CONSTANT = r'\d+'
STRING = r'\"[^\"\n]+\"'
REG_IDENTIFIER = r'[a-zA-Z_][a-zA-Z_0-9]*'

ALL_TOKENS = r'(' + '|'.join(
    [COMMENT_START, COMMENT_END, REG_IDENTIFIER, SYMBOLS_REGEX, KEY_WORDS_REGEX, INTEGER_CONSTANT, STRING, ]) + ')'

# SPECIAL_VALUES = {
#     '>': '&gt;',
#     '<': '&lt;',
#     '&': '&amp;'
# }

STATIC_OR_FIELD = fr'({STATIC}|{FIELD})'
CONST_FUNC_METHOD = fr'({CONSTRUCTOR}|{FUNCTION}|{METHOD})'
TYPE = fr'({INT}|{CHAR}|{BOOL}|{REG_IDENTIFIER})'
VOID_OR_TYPE = fr'({VOID}|{TYPE})'
STATEMENTS = fr'({LET}|{IF}|{WHILE}|{DO}|{RETURN})'

OP = fr'({PLUS}|{MINUS}|{ASTERISK}|{SLASH}|{AND}|{PIPE}|{MORE}|{LESS}|{EQUAL})'
UNARY = fr'({MINUS}|{SIM}|{UP}|{SHARP})'

KEYWORD_CONSTANT = fr'({TRUE}|{FALSE}|{NULL}|{THIS})'
ROUTINE = fr'({L_BRACE}|{DOT})'

ARG = "ARG"
CLASS_SCOPE = fr'({STATIC.upper()}|{FIELD.upper()})'
SUBROUTINE_SCOPE = fr'({ARG}|{VAR.upper()})'

KIND_DICT = {"ARG": "argument", "VAR": "local", "FIELD": "this", "STATIC": "static"}

OPP_DICT = {'+': "add", SLASH: "Math.divide", AND: "and", '|': "or",
            LESS: "lt", MORE: "gt", EQUAL: "eq", SIM: "not", MINUS: "sub",
            ASTERISK: "Math.multiply", '^': "shiftleft", SHARP: "shiftright"}

ARGUMENT = "argument"
POINTER = "pointer"
CONSTANT = "constant"
ALLOC = "Memory.alloc"
