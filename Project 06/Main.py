"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

FIRST_SLOT = 16

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    table = SymbolTable()
    parser = Parser(input_file)
    line_counter = 0
    variable_counter = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "L_COMMAND" and not table.contains(parser.symbol()):
            table.add_entry(parser.symbol(), line_counter)
            # parser.advance()
            # line_counter += 1
            continue
        line_counter += 1

    parser.reset()
    get_bin = lambda x, n: format(x, 'b').zfill(n)

    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "A_COMMAND" and not parser.symbol().isnumeric() and not table.contains(parser.symbol()):
            table.add_entry(parser.symbol(), FIRST_SLOT + variable_counter)
            variable_counter += 1
        if parser.command_type() == "A_COMMAND" and table.contains(parser.symbol()):
            output_file.write(get_bin(table.get_address(parser.symbol()), 16))
            output_file.write('\n')
        elif parser.command_type() == "A_COMMAND":
            output_file.write(get_bin(int(parser.symbol()), 16))
            output_file.write('\n')
        if parser.command_type() == "C_COMMAND":
            comp = parser.comp()
            if '<' in comp or '>' in comp:
                output_file.write(f'{Code.comp(parser.comp())}{Code.dest(parser.dest())}{Code.jump(parser.jump())}\n')
            else:
                output_file.write(f'111{Code.comp(parser.comp())}{Code.dest(parser.dest())}{Code.jump(parser.jump())}\n')



if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
