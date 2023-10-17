"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from utils import *

indent_count = 0


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
        self._tokenizer = input_stream
        self._symbol_table = SymbolTable()
        self._out = output_stream
        self._label_count = 0
        self._if_count = 0
        self._class_name = ''
        self._curr_subroutine_name = ''
        self._current_subroutine_void = False
        if self._tokenizer.has_more_tokens():
            self._tokenizer.advance()
            self.compile_class()

    def get_keyword(self, expected):
        if self._tokenizer.token_type() == KEYWORD and re.match(expected, self._tokenizer.keyword()):
            word = self._tokenizer.keyword()
            self._tokenizer.advance()
            return word
        return None

    def get_identifier(self):
        if self._tokenizer.token_type() == IDENTIFIER:
            ident = self._tokenizer.identifier()
            self._tokenizer.advance()
            return ident
        return None

    def get_keyword_or_identifier(self, expected):
        key_word = self.get_keyword(expected)
        if not key_word:
            ident = self.get_identifier()
            if ident is None:
                return
            return ident
        return key_word

    def get_symbol(self, expected):
        if self._tokenizer.token_type() == SYMBOL and re.match(expected, self._tokenizer.symbol()):
            symbol = OPP_DICT[self._tokenizer.symbol()]
            self._tokenizer.advance()
            return symbol
        return None

    def is_next_comma(self):
        if self._tokenizer.token_type() == SYMBOL and re.match(COMMA, self._tokenizer.symbol()):
            return True
        return False

    def get_same_type_var_to_table(self, kind):
        typ = self.get_keyword_or_identifier(TYPE)
        name = self.get_identifier()
        self._symbol_table.define(name, typ, kind.upper())
        while self.is_next_comma():
            self._tokenizer.advance()
            name = self.get_identifier()
            self._symbol_table.define(name, typ, kind.upper())
        self._tokenizer.advance()

    def const_func_method_special_cases(self, func_typ, void_type, class_name):
        if re.match(func_typ, CONSTRUCTOR):
            class_fields = self._symbol_table.var_count(FIELD.upper())
            self._out.write_push(CONSTANT, class_fields)
            self._out.write_call(ALLOC, 1)
            self._out.write_pop(POINTER, 0)
        elif re.match(func_typ, METHOD):
            self._out.write_push(ARGUMENT, 0)
            self._out.write_pop(POINTER, 0)

    def compile_string(self):
        string_name = self._tokenizer.string_val().replace('"', '')
        self._out.write_push("constant", len(string_name))
        self._out.write_call("String.new", 1)
        for c in string_name:
            self._out.write_push("constant", ord(c))
            self._out.write_call("String.appendChar", 2)
        self._tokenizer.advance()

    def compile_int(self):
        self._out.write_push("constant", self._tokenizer.int_val())
        self._tokenizer.advance()

    def write_keyword_constant_expressions(self, keyword):
        if re.match(keyword, TRUE):
            self._out.write_push("constant", 0)
            self._out.write_arithmetic("not")
        elif re.match(keyword, FALSE):
            self._out.write_push("constant", 0)
        elif re.match(keyword, THIS):
            self._out.write_push("pointer", 0)
        elif re.match(keyword, NULL):
            self._out.write_push("constant", 0)
        # self._tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self._tokenizer.advance()  # advances through Class
        self._class_name = self.get_identifier()
        self._tokenizer.advance()  # advances through left curly bracket
        while self._tokenizer.token_type() == KEYWORD and re.match(STATIC_OR_FIELD, self._tokenizer.keyword()):
            self.compile_class_var_dec()
        while self._tokenizer.token_type() == KEYWORD and re.match(CONST_FUNC_METHOD, self._tokenizer.keyword()):
            self.compile_subroutine()
        self._tokenizer.advance()  # advances through right curly bracket

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        kind = self.get_keyword(STATIC_OR_FIELD)
        self.get_same_type_var_to_table(kind)

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self._symbol_table.start_subroutine()

        const_func_method = self.get_keyword(CONST_FUNC_METHOD)
        void_or_typ = self.get_keyword_or_identifier(VOID_OR_TYPE)
        name = self.get_identifier()
        self._curr_subroutine_name = self._class_name + '.' + name

        if re.match(void_or_typ, VOID):
            self._current_subroutine_void = True
        else:
            self._current_subroutine_void = False

        if re.match(const_func_method, METHOD):
            self._symbol_table.define(THIS, name, ARG)
        self._tokenizer.advance()  # advances through left bracket
        self.compile_parameter_list()
        self._tokenizer.advance()  # advances through right bracket
        self.compile_subroutine_body(const_func_method, void_or_typ, name)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        var_type = self.get_keyword_or_identifier(TYPE)
        var_name = self.get_identifier()

        while var_type and var_name:  # if parameter list is empty while will not be invoked
            self._symbol_table.define(var_name, var_type, ARG)
            var_name = None
            var_type = None
            if self.is_next_comma():
                self._tokenizer.advance()
                var_type = self.get_keyword_or_identifier(TYPE)
                var_name = self.get_identifier()

    def compile_subroutine_body(self, const_func_method, void_o_type, name):
        self._tokenizer.advance()  # advances through left curly bracket
        while self._tokenizer.token_type() == KEYWORD and self._tokenizer.keyword() == VAR:
            self.compile_var_dec()

        self._out.write_function(self._curr_subroutine_name, self._symbol_table.var_count("VAR"))
        self.const_func_method_special_cases(const_func_method, void_o_type, name)
        self.compile_statements()
        self._tokenizer.advance()  # advances through left curly bracket

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self._tokenizer.advance()  # advances through Var
        self.get_same_type_var_to_table(VAR.upper())
        # self._tokenizer.advance()  # advances through semi-colon

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self._tokenizer.token_type() == KEYWORD and re.match(STATEMENTS, self._tokenizer.keyword()):
            func = f'compile_{self._tokenizer.keyword()}'
            getattr(self, func)()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self._tokenizer.advance()  # advances through DO
        self.compile_expression()
        self._out.write_pop("temp", 0)
        self._tokenizer.advance()  # advances through semicolon

    def compile_subroutine_call(self, identifier):
        if re.match(SYMBOL, self._tokenizer.token_type()) and re.match(L_BRACE, self._tokenizer.symbol()):
            self._tokenizer.advance()  # advances through left bracket
            self._out.write_push("pointer", 0)
            count = self.compile_expression_list()
            count += 1
            subroutine_name = self._class_name + "." + identifier
            self._out.write_call(subroutine_name, count)
            self._tokenizer.advance()  # advances through right bracket
        elif re.match(SYMBOL, self._tokenizer.token_type()) and re.match(DOT, self._tokenizer.symbol()):
            self._tokenizer.advance()  # advances through dot
            count = 0
            if self._symbol_table.kind_of(identifier) is not None:
                segment = self._symbol_table.kind_of(identifier)
                index = self._symbol_table.index_of(identifier)
                self._out.write_push(segment.lower(), index)
                count += 1
                subroutine_name = self._symbol_table.type_of(identifier) + "." + self.get_identifier()
            else:
                subroutine_name = identifier + "." + self.get_identifier()
            self._tokenizer.advance()  # advances through left bracket
            count += self.compile_expression_list()
            self._out.write_call(subroutine_name, count)
            self._tokenizer.advance()  # advances through right bracket


    def compile_let(self) -> None:
        """Compiles a let statement."""
        self._tokenizer.advance()  # advances through let
        var_name = self.get_identifier()
        if var_name is None:
            if self._tokenizer.token_type() == KEYWORD and self._tokenizer.keyword() == THIS:
                var_name = self.get_keyword(THIS)
        is_array = False

        if self._tokenizer.token_type() == SYMBOL and re.match(L_SQUARE_BRACES, self._tokenizer.symbol()):
            is_array = True
            seg = self._symbol_table.kind_of(var_name)
            index = self._symbol_table.index_of(var_name)
            self._out.write_push(seg, index)
            self._tokenizer.advance()  # advances through left square bracket
            self.compile_expression()
            self._out.write_arithmetic("add")
            self._tokenizer.advance()  # advances through right square bracket
        self._tokenizer.advance()  # advances through equal sign
        self.compile_expression()
        if is_array:
            self._out.write_pop("temp", 0)
            self._out.write_pop("pointer", 1)
            self._out.write_push("temp", 0)
            self._out.write_pop("that", 0)
        else:
            kind = self._symbol_table.kind_of(var_name)
            index = self._symbol_table.index_of(var_name)
            self._out.write_pop(kind, index)
        self._tokenizer.advance()  # advances through semicolon

    def compile_while(self) -> None:
        """Compiles a while statement."""
        true_label = "WHILE_TRUE{0}".format(self._label_count)
        false_label = "WHILE_FALSE{0}".format(self._label_count)
        self._label_count += 1
        self._tokenizer.advance()  # advances through while
        self._out.write_label(true_label)
        self._tokenizer.advance()  # advances through left bracket
        self.compile_expression()
        self._tokenizer.advance()  # advances through right bracket
        self._out.write_arithmetic("not")
        self._out.write_if(false_label)
        self._tokenizer.advance()  # advances through left curley bracket
        self.compile_statements()
        self._out.write_goto(true_label)
        self._tokenizer.advance()  # advances through right curley bracket
        self._out.write_label(false_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self._tokenizer.advance()  # advances through return
        if self._tokenizer.token_type() != SYMBOL or (
                self._tokenizer.token_type() == SYMBOL and re.match(UNARY, self._tokenizer.symbol())):
            self.compile_expression()
        if self._current_subroutine_void:
            self._out.write_push("constant", 0)
        self._out.write_return()
        self._tokenizer.advance()  # advances through semicolon

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        true_label = "IF_TRUE{0}".format(self._if_count)
        false_label = "IF_FALSE{0}".format(self._if_count)
        self._if_count += 1
        self._tokenizer.advance()  # advances through if
        self._tokenizer.advance()  # advances through left bracket
        self.compile_expression()
        self._tokenizer.advance()  # advances through right bracket
        self._out.write_arithmetic("not")
        self._out.write_if(false_label)
        self._tokenizer.advance()  # advances through left curley bracket
        self.compile_statements()
        self._out.write_goto(true_label)
        self._tokenizer.advance()  # advances through right curley bracket
        self._out.write_label(false_label)
        if self._tokenizer.token_type() == KEYWORD and re.match(ELSE, self._tokenizer.keyword()):
            self._tokenizer.advance()  # advances through else
            self._tokenizer.advance()  # advances through left curley bracket
            self.compile_statements()
            self._tokenizer.advance()  # advances through right curley bracket
        self._out.write_label(true_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self._tokenizer.token_type() == "SYMBOL" and re.match(OP, self._tokenizer.symbol()):
            op_symbol = self._tokenizer.symbol()
            self._tokenizer.advance()
            self.compile_term()
            if re.match(fr'({ASTERISK}|{SLASH})', op_symbol):
                self._out.write_call(OPP_DICT[f'\\{op_symbol}'], 2)
            else:
                self._out.write_arithmetic(OPP_DICT[op_symbol])

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
            keyword = self.get_keyword(KEYWORD_CONSTANT)
            self.write_keyword_constant_expressions(keyword)
        elif self._tokenizer.token_type() == SYMBOL:
            if re.match(L_BRACE, self._tokenizer.symbol()):
                self._tokenizer.advance()  # advances through left bracket
                self.compile_expression()
                self._tokenizer.advance()  # advances through right bracket
            elif re.match(UNARY, self._tokenizer.symbol()):
                operator = self.get_symbol(UNARY)
                if operator == "sub":
                    operator = "neg"
                self.compile_term()
                self._out.write_arithmetic(operator)
        else:
            identifier = self.get_identifier()
            if self._tokenizer.token_type() == SYMBOL and re.match(L_SQUARE_BRACES, self._tokenizer.symbol()):
                self._tokenizer.advance()  # advance through left square bracket
                segment = self._symbol_table.kind_of(identifier)
                index = self._symbol_table.index_of(identifier)
                self._out.write_push(segment, index)
                self.compile_expression()
                self._out.write_arithmetic("add")
                self._out.write_pop("pointer", 1)
                self._out.write_push("that", 0)
                self._tokenizer.advance()  # advance through right square bracket
            elif self._tokenizer.token_type() == SYMBOL and re.match(DOT, self._tokenizer.symbol()):
                self.compile_subroutine_call(identifier)
            elif self._tokenizer.token_type() == SYMBOL and re.match(L_BRACE, self._tokenizer.symbol()):
                self._tokenizer.advance()  # advances through left bracket
                self._out.write_push("pointer", 0)
                count = self.compile_expression_list()
                count += 1
                subroutine_name = self._class_name + "." + identifier
                # )
                self._out.write_call(subroutine_name, count)
                self._tokenizer.advance()  # advances through right bracket
            else:
                kind = self._symbol_table.kind_of(identifier)
                index = self._symbol_table.index_of(identifier)
                self._out.write_push(kind, index)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        counter = 0
        if self._tokenizer.token_type() != SYMBOL or \
                (self._tokenizer.token_type() == SYMBOL and (
                        re.match(L_BRACE, self._tokenizer.symbol()) or re.match(UNARY, self._tokenizer.symbol()))):
            self.compile_expression()
            counter += 1
            while self._tokenizer.token_type() != SYMBOL or self.is_next_comma():  # todo might want to change this to only ask if next is comma and advance through it
                if self.is_next_comma():
                    self._tokenizer.advance()  # advances through comma
                self.compile_expression()
                counter += 1
        return counter
