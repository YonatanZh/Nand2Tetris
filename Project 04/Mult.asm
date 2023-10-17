// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// MIGHT NEED TO CHANGE SO IT DOESNT ALTER ORIGINAL VALUES


//Checks if either inputs is zero
	@R0
	D=M
	@CHECK0
	D;JEQ
	@R1
	D=M
	@CHECK0
	D;JEQ

//Initialize starting point
	@i
	M=1
	@SUM
	M=0

//Selectes optimized loop
	@R0
	D=M
	@R1
	D=D-M
	@OPTION1
	D;JGE
	@OPTION2
	0;JMP
(OPTION1)
	@R1
	D=M
	@index
	M=D
(LOOP1)
	@R0
	D=M
	@SUM
	M=M+D
	@index
	M=M-1
	D=M
	@LOOP1
	D;JGT
	@STORE
	0;JMP
(OPTION2)
	@R0
	D=M
	@index
	M=D
(LOOP2)
	@R1
	D=M
	@SUM
	M=M+D
	@index
	M=M-1
	D=M
	@LOOP2
	D;JGT
	@STORE
	0;JMP
(STORE)
	@SUM
	D=M
	@R2
	M=D
	@END
	0;JMP
(CHECK0)
	@R2
	M=0
	@END
	0;JMP
(END)
	@END
	0;JMP
