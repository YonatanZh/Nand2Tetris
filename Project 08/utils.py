BINARY_ARITHMETIC_COMMAND = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM={}\n'
UNARY_ARITHMETIC_COMMAND = '@SP\nA=M-1\nM={a}M{b}\n'
COMPARATIVE_ARITHMETIC_COMMAND = """
@SP
M=M-1
A=M
D=M
@YPOS{i}
D;JGT
@SP
A=M-1
D=M
@XPOS{i}
D;JGT
// SAME SIGN
(SAMESIGN{i})
@SP
A=M
D=M
A=A-1
D=M-D
@TRUE{i}
D;{jmp}
@FALSE{i}
0;JMP

(YPOS{i})
@SP
A=M-1
D=M
@SAMESIGN{i}
D;JGT
// X < 0 < Y
@TRUE{i}
-1;{jmp}
@FALSE{i}
0;JMP

(XPOS{i})
// X > 0 > Y
@TRUE{i}
1;{jmp}
@FALSE{i}
0;JMP

(TRUE{i})
D=-1
@ENDC{i}
0;JMP
(FALSE{i})
D=0
(ENDC{i})
@SP
A=M-1
M=D
"""

EQUALS_COMMAND = '@SP\nM=M-1\nA=M\nD=M\nA=A-1\nD=D-M\n@ARC{i}\nD;{jmp}\n' \
                 'D=0\n@END{i}\n0;JMP\n(ARC{i})\nD=-1\n(END{i})\n@SP\nA=M-1\nM=D\n'

ARITHMETIC_COMMANDS_BINARY = {
    'add': BINARY_ARITHMETIC_COMMAND.format('D+M'),
    'sub': BINARY_ARITHMETIC_COMMAND.format('M-D'),
    'and': BINARY_ARITHMETIC_COMMAND.format('D&M'),
    'or': BINARY_ARITHMETIC_COMMAND.format('D|M'),
}
ARITHMETIC_COMMANDS_COMP = {
    'eq': EQUALS_COMMAND.format(i='{i}', jmp='JEQ'),
    'gt': COMPARATIVE_ARITHMETIC_COMMAND.format(i='{i}', jmp='JGT'),
    'lt': COMPARATIVE_ARITHMETIC_COMMAND.format(i='{i}', jmp='JLT'),
}
ARITHMETIC_COMMANDS_UNARY = {
    'neg': UNARY_ARITHMETIC_COMMAND.format(a='-', b=''),
    'not': UNARY_ARITHMETIC_COMMAND.format(a='!', b=''),
    'shiftleft': UNARY_ARITHMETIC_COMMAND.format(a='', b='<<'),
    'shiftright': UNARY_ARITHMETIC_COMMAND.format(a='', b='>>'),
}

C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
C_LABEL = 'C_LABEL'
C_GOTO = 'C_GOTO'
C_IF = 'C_IF'
C_FUNCTION = 'C_FUNCTION'
C_RETURN = 'C_RETURN'
C_CALL = 'C_CALL'

COMMAND_TYPES = {
    'add': C_ARITHMETIC,
    'sub': C_ARITHMETIC,
    'and': C_ARITHMETIC,
    'or': C_ARITHMETIC,
    'eq': C_ARITHMETIC,
    'gt': C_ARITHMETIC,
    'lt': C_ARITHMETIC,
    'neg': C_ARITHMETIC,
    'not': C_ARITHMETIC,
    'shiftleft': C_ARITHMETIC,
    'shiftright': C_ARITHMETIC,
    'push': C_PUSH,
    'pop': C_POP,
    'label': C_LABEL,
    'if-goto': C_IF,
    'goto': C_GOTO,
    'call': C_CALL,
    'function': C_FUNCTION,
    'return': C_RETURN
}

LCL = 'LCL'
ARG = 'ARG'
THIS = 'THIS'
THAT = 'THAT'
PTR = 'PTR'
TEMP = 'TEMP'
STATIC = 'STATIC'
CONST = 'CONST'

SEGMENT_POINTERS = {
    'local': LCL,
    'argument': ARG,
    'this': THIS,
    'that': THAT,
    'pointer': PTR,
    'temp': TEMP,
    'static': STATIC,
    'constant': CONST,
}

INDEX_PLHOLDER = '{index}'
BASE_SEG_POP_COMMAND = '@' + INDEX_PLHOLDER + \
                       """
D=A
@{seg}
D=D+M
@ADDR
M=D
@SP
M=M-1
A=M
D=M
@ADDR
A=M
M=D
"""

BASE_SEG_PUSH_COMMAND = '@' + INDEX_PLHOLDER + \
                       """
D=A
@{seg}
A=D+M
D=M
@SP
M=M+1
A=M-1
M=D
"""

CONST_PUSH_COMMAND = \
    """@{symbol}
D=A
@SP
M=M+1
A=M-1
M=D
"""

STATIC_PUSH_COMMAND = \
    """@{symbol}
D=M
@SP
M=M+1
A=M-1
M=D
"""

STATIC_POP_COMMAND = \
    """@SP
M=M-1
A=M
D=M
@{symbol}
M=D
"""

TEMP_PUSH_COMMAND = '@' + INDEX_PLHOLDER + \
                    """
D=A
@5
A=D+A
D=M
@SP
M=M+1
A=M-1
M=D
"""

TEMP_POP_COMMAND = '@' + INDEX_PLHOLDER + \
                   """
D=A
@5
D=D+A
@ADDR
M=D
@SP
M=M-1
A=M
D=M
@ADDR
A=M
M=D
"""

COUNTER_PLHOLDER = '{i}'
PTR_PUSH_COMMAND = F"""@{INDEX_PLHOLDER}
D=A
@PUTHIS{COUNTER_PLHOLDER}
D;JEQ
@THAT
D=M
@PUPTR{COUNTER_PLHOLDER}
0;JMP
(PUTHIS{COUNTER_PLHOLDER})
@THIS
D=M
(PUPTR{COUNTER_PLHOLDER})
@SP
M=M+1
A=M-1
M=D
"""

PTR_POP_COMMAND = F"""@{INDEX_PLHOLDER}
D=A
@POTHIS{COUNTER_PLHOLDER}
D;JEQ
@THAT
D=A
@POPTR{COUNTER_PLHOLDER}
0;JMP
(POTHIS{COUNTER_PLHOLDER})
@THIS
D=A
(POPTR{COUNTER_PLHOLDER})
@ADDR
M=D
@SP
M=M-1
A=M
D=M
@ADDR
A=M
M=D
"""

MEMORY_COMMANDS = {
    C_POP + LCL: BASE_SEG_POP_COMMAND.format(index=INDEX_PLHOLDER, seg=LCL),
    C_POP + ARG: BASE_SEG_POP_COMMAND.format(index=INDEX_PLHOLDER, seg=ARG),
    C_POP + THIS: BASE_SEG_POP_COMMAND.format(index=INDEX_PLHOLDER, seg=THIS),
    C_POP + THAT: BASE_SEG_POP_COMMAND.format(index=INDEX_PLHOLDER, seg=THAT),

    C_PUSH + LCL: BASE_SEG_PUSH_COMMAND.format(index=INDEX_PLHOLDER, seg=LCL),
    C_PUSH + ARG: BASE_SEG_PUSH_COMMAND.format(index=INDEX_PLHOLDER, seg=ARG),
    C_PUSH + THIS: BASE_SEG_PUSH_COMMAND.format(index=INDEX_PLHOLDER, seg=THIS),
    C_PUSH + THAT: BASE_SEG_PUSH_COMMAND.format(index=INDEX_PLHOLDER, seg=THAT),

    C_PUSH + STATIC: STATIC_PUSH_COMMAND,
    C_POP + STATIC: STATIC_POP_COMMAND,

    C_PUSH + CONST: CONST_PUSH_COMMAND,
    # NO POP FOR CONST

    C_PUSH + TEMP: TEMP_PUSH_COMMAND,
    C_POP + TEMP: TEMP_POP_COMMAND,

    C_PUSH + PTR: PTR_PUSH_COMMAND,
    C_POP + PTR: PTR_POP_COMMAND
}

END_LOOP = '(ENDLOOP)\n@ENDLOOP\n0;JMP\n'
END_SEG_TO_STACK = '@{seg}\nD={val}\n@SP\nM=M+1\nA=M-1\nM=D\n'
RETURN_FRAME_DECOMPOSE = '@_FRAME\nD=M\n@{i}\nA=D-A\nD=M\n@{seg}\nM=D\n'
