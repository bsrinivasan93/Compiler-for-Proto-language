#Balaji Srinivasan - 02/09/15
#hw1p4.asm  - Program that reads a single signed integer n and prints "perfect" if n is perfect; "deficient" if n is deficient; "abundant" if n is abundant
#Registers used :
#  		        t0  	-	to hold integer n
#			t1	- 	to hold the sum of factors of n
#			t2 	-	to hold the control vaiable for the factor_loop
#			s0	-	to hold temporary values
#			v0 	-	syscall number
#Data variables	:
#	string_perfect 	- to hold the string "Perfect!"
#	string_deficient- to hold the string "Deficient:("
#	string_abundant - to hold the string "Abundant:)"
	
#Text section
	.text
main:
	#Read integer n and perform an intial check on n
	li $v0, 5
	syscall
	move $t0, $v0
	blez $t0, exit

	#Find all factors of n from (n-1) to 1 and compute their sum in t1
	li $t1, 0
	move $t2, $t0
	sub $t2, $t2, 1
factor_loop:
	div $t0, $t2
	mfhi $s0
	bnez $s0, not_a_factor
	add $t1, $t1, $t2

not_a_factor:
	sub $t2, $t2, 1
	beqz $t2, out_of_factor_loop
	b factor_loop

#Sum of all factors computed in t1. 
out_of_factor_loop:
	#Check if sum==n or sum<n and branch accordingly
	beq $t1, $t0, print_string_perfect
	#n is not a perect number
	blt $t1, $t0, print_string_deficient
	#n is an abundant number
	b print_string_abundant

#Print "Perfect"
print_string_perfect:
	la $a0, string_perfect
	li $v0, 4
	syscall
	b exit

#Print "Deficient"
print_string_deficient:
	la $a0, string_deficient
	li $v0, 4
	syscall
	b exit

#Print "Abundant"
print_string_abundant:
	la $a0, string_abundant
	li $v0, 4
	syscall

#Exit the program
exit:
	li $v0, 10
	syscall
	
#Data variables to store the strings displayed
	.data
string_perfect:	.asciiz "Perfect!\n"
string_deficient:	.asciiz	"Deficient:(\n"
string_abundant:	.asciiz	"Abundant:)\n"
