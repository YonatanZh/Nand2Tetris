"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """
    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.__input_lines = input_file.read().splitlines()
        self.__input_lines = [self.clear(line).replace(' ', '') for line in self.__input_lines]
        self.__input_lines = [line for line in self.__input_lines if line != '']
        self.__current_line_num = 0
        self.__curr_command = ''

    def clear(self, line: str):
        if '//' in line:
            return line[:line.index('//')]
        if '/*' in line:
            return line[:line.index('/*')]
        return line

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return len(self.__input_lines) > self.__current_line_num

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # if self.has_more_commands():
        self.__curr_command = self.__input_lines[self.__current_line_num]
        self.__current_line_num += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if '@' in self.__curr_command:
            return "A_COMMAND"
        if '(' in self.__curr_command:
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if '@' in self.__curr_command:
            return self.__curr_command.replace('@', '')
        return self.__curr_command.replace('(', '').replace(')', '')

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.__curr_command.split('=')[0] if '=' in self.__curr_command else None

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        comp = self.__curr_command
        if '=' in comp:
            comp = comp.split('=')[1]
        if ';' in comp:
            comp = comp.split(';')[0]
        return comp

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.__curr_command.split(';')[1] if ';' in self.__curr_command else None

    def reset (self) -> None:
        self.__current_line_num = 0
        self.__curr_command = self.__input_lines[0]