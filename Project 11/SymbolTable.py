"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re

from utils import CLASS_SCOPE, SUBROUTINE_SCOPE, KIND_DICT
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_table = dict()
        self.subroutine_table = dict()
        self.static_index = 0
        self.field_index = 0
        self.arg_index = 0
        self.var_index = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_table = dict()
        self.arg_index = 0
        self.var_index = 0

    def define(self, name: str, typ: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            typ (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # string_index_kind = f'{kind.lower()}_index'
        # relevant_index = getattr(self, string_index_kind)
        # if re.match(CLASS_SCOPE, kind):
        #     self.class_table[name] = [typ, kind.lower(), relevant_index]
        #     relevant_index += 1
        # elif re.match(SUBROUTINE_SCOPE, kind):
        #     self.subroutine_table[name] = [typ, KIND_DICT[kind], relevant_index]
        #     relevant_index += 1
        # # TODO: make sure this code works as intended
        if re.match("VAR", kind):
            self.subroutine_table[name] = [typ, KIND_DICT[kind], self.var_index]
            self.var_index += 1
        elif re.match("ARG", kind):
            self.subroutine_table[name] = [typ, KIND_DICT[kind], self.arg_index]
            self.arg_index += 1
        elif re.match("FIELD", kind):
            self.class_table[name] = [typ, KIND_DICT[kind], self.field_index]
            self.field_index += 1
        elif re.match("STATIC", kind):
            self.class_table[name] = [typ, kind.lower(), self.static_index]
            self.static_index += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # count = 0
        # if re.match(CLASS_SCOPE, kind):
        #     count = len(list(filter(lambda lst: kind in lst, self.class_table.values())))
        # elif re.match(SUBROUTINE_SCOPE, kind):
        #     count = len(list(filter(lambda lst: kind in lst, self.subroutine_table.values())))
        # return count
        if kind == "STATIC":
            return self.static_index
        elif kind == "FIELD":
            return self.field_index
        elif kind == "ARG":
            return self.arg_index
        else:
            return self.var_index

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.subroutine_table.get(name):
            return self.subroutine_table.get(name)[1]
        elif self.class_table.get(name):
            return self.class_table.get(name)[1]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.subroutine_table.get(name):
            return self.subroutine_table.get(name)[0]
        elif self.class_table.get(name):
            return self.class_table.get(name)[0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if self.subroutine_table.get(name):
            return self.subroutine_table.get(name)[2]
        elif self.class_table.get(name):
            return self.class_table.get(name)[2]
