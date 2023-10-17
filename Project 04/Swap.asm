// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.
	
	@I
	M=1
	@R14
	D=M
	@MAX_ADD
	M=D
	@MIN_ADD
	AM=D
	D=M
	@MAX_NUM
	M=D
	@MIN_NUM
	M=D

(LOOP)
	@I
	D=M
	@R15
	D=M-D
	@SWAP
	D;JEQ // LOOP CONDITION

	@I
	D=M

	@R14
	A=M+D
	D=M
	@CURR_NUM
	M=D
	@SEC_NEG1 // check second negative
	D;JLT
	@MIN_NUM // check first negative
	D=M
	@FIRST_NEG1
	D;JLT
	@CURR_NUM // both pos
	D=D-M
	@SWAP_MIN
	D;JGT

(AFTER_MIN)
	@CURR_NUM
	D=M
	@SEC_NEG2
	D;JLT
	@MAX_NUM // check first negative
	D=M
	@FIRST_NEG2
	D;JLT
	@CURR_NUM // both pos
	D=D-M
	@SWAP_MAX
	D;JLT
	@CONTINUE_LOOP
	0;JMP

(CONTINUE_LOOP)
	@I
	M=M+1
	@LOOP
	0;JMP

(SEC_NEG1)
	@MIN_NUM
	D=M
	@SEC_FIRST_NEG1 // both negative
	D;JLT
	@SWAP_MIN // second num is negative and min is pos
	0;JMP

(SEC_NEG2)
	@MAX_NUM
	D=M
	@SEC_FIRST_NEG2 // both negative
	D;JLT
	@CONTINUE_LOOP // second num is negative and max is pos
	0;JMP

(SEC_FIRST_NEG2)
	@MAX_NUM
	D=M
	@CURR_NUM
	D=D-M
	@SWAP_MAX
	D;JLT
	@CONTINUE_LOOP
	0;JMP

(SEC_FIRST_NEG1)
	@MIN_NUM
	D=M
	@CURR_NUM
	D=D-M
	@SWAP_MIN
	D;JGT
	@AFTER_MIN
	0;JMP

(FIRST_NEG1)
	@AFTER_MIN
	0;JMP

(FIRST_NEG2)
	@SWAP_MAX
	0;JMP

(SWAP_MIN)
	@I
	D=M
	@R14
	D=D+M
	@MIN_ADD
	AM=D
	D=M
	@MIN_NUM
	M=D
	@CONTINUE_LOOP
	0;JMP

(SWAP_MAX)
	@I
	D=M
	@R14
	D=D+M
	@MAX_ADD
	AM=D
	D=M
	@MAX_NUM
	M=D
	@CONTINUE_LOOP
	0;JMP

(SWAP)
	@MAX_ADD
	A=M
	D=M
	@STORE
	M=D
	@MIN_ADD
	A=M
	D=M
	@MAX_ADD
	A=M
	M=D
	@STORE
	D=M
	@MIN_ADD
	A=M
	M=D
	@END
	0;JMP

(END)
	@END
	0;JMP