"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from utils import ARITHMETIC_COMMANDS_BINARY, ARITHMETIC_COMMANDS_COMP, ARITHMETIC_COMMANDS_UNARY, MEMORY_COMMANDS, \
    SEGMENT_POINTERS, C_PUSH, END_SEG_TO_STACK, RETURN_FRAME_DECOMPOSE

SYS_INIT_FUNC_NAME = 'Sys.init'


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self._out = output_stream
        self._art_counter = 0
        self._pp_counter = 0
        self._ret_counter = 0
        self._basename = ''
        self._current_func = ''

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self._basename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        out = ARITHMETIC_COMMANDS_BINARY.get(command)
        if not out:
            out = ARITHMETIC_COMMANDS_COMP.get(command, '').format(i=self._art_counter)
            if out:
                self._art_counter += 1
            else:
                out = ARITHMETIC_COMMANDS_UNARY.get(command, '')
        self._out.write(out)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        symbol = None
        if segment == 'static':
            symbol = f'{self._basename}.{index}'
        elif segment == 'constant':
            symbol = f'{index}'

        command_code = command + SEGMENT_POINTERS.get(segment)
        out = MEMORY_COMMANDS.get(command_code).format(seg=segment, index=index, symbol=symbol, i=self._pp_counter)
        self._pp_counter += 1
        self._out.write(out)

    def __format_label(self, label: str = None) -> str:
        return f'{self._current_func}${label}' if label else f'{self._current_func}'

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        formatted = self.__format_label(label)
        self._out.write(f'({formatted})\n')

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        formatted = self.__format_label(label)
        self._out.write(f'@{formatted}\n0;JMP\n')

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        formatted = self.__format_label(label)
        self._out.write(f'@SP\nM=M-1\nA=M\nD=M\n@{formatted}\nD;JNE\n')

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        self._current_func = function_name
        self._out.write(f'({self.__format_label()})\n')
        for _ in range(n_vars):
            self.write_push_pop(C_PUSH, 'constant', 0)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        if function_name != SYS_INIT_FUNC_NAME:
            return_address = self.__format_label(f'ret.{self._ret_counter}')
            self._ret_counter += 1
        else:
            return_address = 0
        self._out.write(END_SEG_TO_STACK.format(seg=return_address, val='A'))
        # push LCL              // saves LCL of the caller
        self._out.write(END_SEG_TO_STACK.format(seg='LCL', val='M'))
        # push ARG              // saves ARG of the caller
        self._out.write(END_SEG_TO_STACK.format(seg='ARG', val='M'))
        # push THIS             // saves THIS of the caller
        self._out.write(END_SEG_TO_STACK.format(seg='THIS', val='M'))
        # push THAT             // saves THAT of the caller
        self._out.write(END_SEG_TO_STACK.format(seg='THAT', val='M'))

        # ARG = SP-5-n_args     // repositions ARG
        if function_name != SYS_INIT_FUNC_NAME:
            # There is no meaning for repositioning ARG and LCL for the init function
            x = 5 + n_args
            self._out.write(f'@SP\nD=M\n@{x}\nD=D-A\n@ARG\nM=D\n')
            # LCL = SP              // repositions LCL
            self._out.write(f'@SP\nD=M\n@LCL\nM=D\n')

        # goto function_name    // transfers control to the callee
        self._out.write(f'@{function_name}\n0;JMP\n')
        # (return_address)      // injects the return address label into the code
        self._out.write(f'({return_address})\n')

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        self._out.write(f'@LCL\nD=M\n@_FRAME\nM=D\n')
        # return_address = *(frame-5)   // puts the return address in a temp var
        self._out.write(RETURN_FRAME_DECOMPOSE.format(seg='_RETURN_ADDR', i=5))
        # *ARG = pop()                  // repositions the return value for the caller
        self._out.write(f'@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n')
        # SP = ARG + 1                  // repositions SP for the caller
        self._out.write(f'@ARG\nD=M+1\n@SP\nM=D\n')
        # THAT = *(frame-1)             // restores THAT for the caller
        self._out.write(RETURN_FRAME_DECOMPOSE.format(seg='THAT', i=1))
        # THIS = *(frame-2)             // restores THIS for the caller
        self._out.write(RETURN_FRAME_DECOMPOSE.format(seg='THIS', i=2))
        # ARG = *(frame-3)              // restores ARG for the caller
        self._out.write(RETURN_FRAME_DECOMPOSE.format(seg='ARG', i=3))
        # LCL = *(frame-4)              // restores LCL for the caller
        self._out.write(RETURN_FRAME_DECOMPOSE.format(seg='LCL', i=4))
        # goto return_address           // go to the return address
        self._out.write('@_RETURN_ADDR\nA=M\n0;JMP\n')

    def write_bootstrap(self) -> None:
        """Writes the bootstrap assembly code. Inits SP to 256"""
        self._out.write("""@256\nD=A\n@SP\nM=D\n""")
        self.write_call(SYS_INIT_FUNC_NAME, 0)
