#Balaji Srinivasan - 02/09/15
#hw1p1.asm - Program that reads a single 32-bit signed integer n, and prints the number of steps for the Hailstone sequence starting at n to terminate at 1
#Registers used :
#           		t0 	-	to hold/update the integer n
#			t1	- 	to hold the length of the hailstone sequence
#			t2 	-	to print the remainder in even/odd check
#			t3	-	to hold the constant 2
#			v0 	-	syscall number

#Text section
	.text
main:
	#Read integer n
	li $v0, 5
	syscall
	move $t0, $v0
	#Perform initial check on n
	blez $t0, exit

	#Initialize the length of hailstone sequence and temporary register
	li $t1, 0
	li $s0, 2

#Increment the length by 1. And check if n is 1. Yes->goto end_of_hailstone_loop. No-> Find the next number in the hailstone sequence
hailstone_loop:
	add $t1, $t1, 1
	beq $t0, 1 , end_of_hailstone_loop
	#n is not 1. Check if n is even or odd and update n accordingly
	li $t3, 2
	div $t0, $t3
	mfhi $t2
	beqz $t2, even_number

#n is odd. Set n=3n+1
odd_number:
	mul $t0, $t0, 3
	add $t0, $t0, 1
	b hailstone_loop

#n is even. Set n=n/2
even_number:
	div $t0, $t0, 2
	b hailstone_loop

end_of_hailstone_loop:
	#Print the length of hailstone sequence
	move $a0, $t1
	li $v0, 1
	syscall

#Exit the program
exit:
	li $v0, 10
	syscall
