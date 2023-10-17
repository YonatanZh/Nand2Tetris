"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re

from JackTokenizer import JackTokenizer
from utils import *

indent_count = 0


def indent(ctx):
    def wrapper(func):
        def inner(*args, **kwargs):
            global indent_count
            pre = indent_count * "\t"
            args[0]._out.write(f'{pre}<{ctx}>\n')
            indent_count += 1
            res = func(*args, **kwargs)
            indent_count -= 1
            args[0]._out.write(f'{pre}</{ctx}>\n')
            return res

        return inner

    return wrapper


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self._tokenizer = input_stream
        self._out = output_stream
        if self._tokenizer.has_more_tokens():
            self._tokenizer.advance()
            self.compile_class()

    def output_terminal(self, token_type, out):
        curr_indent = indent_count * "\t"
        self._out.write((f'{curr_indent}<{token_type}> {out} </{token_type}>\n'))

    def compile_keyword(self, expected):
        if self._tokenizer.token_type() == KEYWORD and re.match(expected, self._tokenizer.keyword()):
            self.output_terminal(KEYWORD.lower(), self._tokenizer.keyword())
            self._tokenizer.advance()
            return expected
        return None

    def compile_identifier(self):
        if self._tokenizer.token_type() == IDENTIFIER:
            ident = self._tokenizer.identifier()
            self.output_terminal(IDENTIFIER.lower(), ident)
            self._tokenizer.advance()
            return ident
        return None

    def compile_symbol(self, expected):
        if self._tokenizer.token_type() == SYMBOL and re.match(expected, self._tokenizer.symbol()):
            symb = self._tokenizer.symbol()
            if symb in SPECIAL_VALUES:
                self.output_terminal(SYMBOL.lower(), SPECIAL_VALUES.get(symb))
            else:
                self.output_terminal(SYMBOL.lower(), symb)
            self._tokenizer.advance()
            return symb
        return None

    def compile_int(self):
        self.output_terminal("integerConstant", self._tokenizer.int_val())
        self._tokenizer.advance()

    def compile_string(self):
        self.output_terminal("stringConstant", self._tokenizer.string_val())
        self._tokenizer.advance()

    def compile_same_type_var(self):
        typ = self.compile_keyword(TYPE)
        if not typ:
            self.compile_identifier()
        identifier = ''
        while self._tokenizer.token_type() == IDENTIFIER or self.compile_symbol(COMMA):
            identifier = self.compile_identifier()
        return typ and identifier

    @indent(CLASS)
    def compile_class(self) -> None:
        """Compiles a complete class."""
        cls = self.compile_keyword(CLASS)
        class_name = self.compile_identifier()
        sym = self.compile_symbol(L_CURLY_BRACE)
        if not (cls and class_name and sym):
            return
        while self._tokenizer.token_type() == KEYWORD and re.match(STATIC_OR_FIELD, self._tokenizer.keyword()):
            self.compile_class_var_dec()
        while self._tokenizer.token_type() == KEYWORD and re.match(CONST_FUNC_METHOD, self._tokenizer.keyword()):
            self.compile_subroutine()
        self.compile_symbol(R_CURLY_BRACE)

    @indent("classVarDec")
    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.compile_keyword(STATIC_OR_FIELD)
        self.compile_same_type_var()
        self.compile_symbol(SEMI_COLON)

    @indent("subroutineDec")
    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        if self._tokenizer.token_type() == KEYWORD and re.match(CONSTRUCTOR, self._tokenizer.keyword()):
            self.compile_keyword(CONSTRUCTOR)
            self.compile_identifier()
            self.compile_identifier()
        else:
            self.compile_keyword(CONST_FUNC_METHOD)
            if not self.compile_keyword(VOID_OR_TYPE):
                self.compile_identifier()
            self.compile_identifier()
        self.compile_symbol(L_BRACE)
        self.compile_parameter_list()
        self.compile_symbol(R_BRACE)
        self.compile_subroutine_body()

    # todo: how to remove tab if list is empty.
    # todo: need to witre \n when done, meaning after closing </...>
    @indent("parameterList")
    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        key_type = self.compile_keyword(TYPE)
        first_identifier = self.compile_identifier()
        sec_identifier = self.compile_identifier()
        while ((key_type and first_identifier) or (first_identifier and sec_identifier)) and self.compile_symbol(COMMA):
            typ = self.compile_keyword(TYPE)
            if not typ:
                self.compile_identifier()
            identify = self.compile_identifier()

    @indent("subroutineBody")
    def compile_subroutine_body(self):
        self.compile_symbol(L_CURLY_BRACE)
        # todo migh not be the correct condtion
        while self._tokenizer.token_type() == KEYWORD and self._tokenizer.keyword() == VAR:
            self.compile_var_dec()
        self.compile_statements()
        self.compile_symbol(R_CURLY_BRACE)

    # todo: need to witre \n when done, meaning after closing </...>
    @indent("varDec")
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.compile_keyword(VAR)
        self.compile_same_type_var()
        self.compile_symbol(SEMI_COLON)

    @indent("statements")
    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self._tokenizer.token_type() == KEYWORD and re.match(STATEMENTS, self._tokenizer.keyword()):
            func = f'compile_{self._tokenizer.keyword()}'
            getattr(self, func)()

    @indent("doStatement")
    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.compile_keyword(DO)
        self.compile_identifier()
        self.compile_subroutine_call()
        self.compile_symbol(SEMI_COLON)

    def compile_subroutine_call(self):
        if self.compile_symbol(L_BRACE):
            self.compile_expression_list()
            self.compile_symbol(R_BRACE)
        elif self.compile_symbol(DOT):
            self.compile_identifier()
            self.compile_symbol(L_BRACE)
            self.compile_expression_list()
            self.compile_symbol(R_BRACE)

    @indent("letStatement")
    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.compile_keyword(LET)
        self.compile_identifier()
        if self._tokenizer.token_type() == SYMBOL and re.match(L_SQUARE_BRACES, self._tokenizer.symbol()):
            self.compile_symbol(L_SQUARE_BRACES)
            self.compile_expression()
            self.compile_symbol(R_SQUARE_BRACES)
        self.compile_symbol(EQUAL)
        self.compile_expression()
        self.compile_symbol(SEMI_COLON)

    @indent("whileStatement")
    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.compile_keyword(WHILE)
        self.compile_symbol(L_BRACE)
        self.compile_expression()
        self.compile_symbol(R_BRACE)
        self.compile_symbol(L_CURLY_BRACE)
        self.compile_statements()
        self.compile_symbol(R_CURLY_BRACE)

    @indent("returnStatement")
    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.compile_keyword(RETURN)
        if self._tokenizer.token_type() != SYMBOL or (self._tokenizer.token_type() == SYMBOL and re.match(UNARY, self._tokenizer.symbol())):
            self.compile_expression()
        self.compile_symbol(SEMI_COLON)

    @indent("ifStatement")
    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.compile_keyword(IF)
        self.compile_symbol(L_BRACE)
        self.compile_expression()
        self.compile_symbol(R_BRACE)
        self.compile_symbol(L_CURLY_BRACE)
        self.compile_statements()
        self.compile_symbol(R_CURLY_BRACE)
        if self._tokenizer.token_type() == KEYWORD and re.match(ELSE, self._tokenizer.keyword()):
            self.compile_keyword(ELSE)
            self.compile_symbol(L_CURLY_BRACE)
            self.compile_statements()
            self.compile_symbol(R_CURLY_BRACE)

    @indent("expression")
    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self._tokenizer.token_type() == SYMBOL and re.match(OP, self._tokenizer.symbol()):
            self.compile_symbol(OP)
            self.compile_term()

    @indent("term")
    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self._tokenizer.token_type() == STRING_CONST:
            self.compile_string()
        elif self._tokenizer.token_type() == INT_CONST:
            self.compile_int()
        elif self._tokenizer.token_type() == KEYWORD and re.match(KEYWORD_CONSTANT, self._tokenizer.keyword()):
            self.compile_keyword(KEYWORD_CONSTANT)
        elif self._tokenizer.token_type() == SYMBOL:  # and not key_constant and not flag:
            if re.match(L_BRACE, self._tokenizer.symbol()):
                self.compile_symbol(L_BRACE)
                self.compile_expression()
                self.compile_symbol(R_BRACE)
            elif re.match(UNARY, self._tokenizer.symbol()):
                self.compile_symbol(UNARY)
                self.compile_term()
        else:
            self.compile_identifier()
            if self.compile_symbol(L_SQUARE_BRACES):
                self.compile_expression()
                self.compile_symbol(R_SQUARE_BRACES)
            else:
                self.compile_subroutine_call()

    @indent("expressionList")
    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        if self._tokenizer.token_type() != SYMBOL or \
                (self._tokenizer.token_type() == SYMBOL and (re.match(L_BRACE, self._tokenizer.symbol()) or re.match(UNARY, self._tokenizer.symbol()))):
            self.compile_expression()
            while self._tokenizer.token_type() != SYMBOL or self.compile_symbol(COMMA):
                self.compile_expression()
