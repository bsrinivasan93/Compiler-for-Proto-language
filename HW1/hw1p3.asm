#Balaji Srinivasan - 02/09/15
#hw1p3.asm           - Program that reads a single 32-bit signed integer n and prints out the largest k such that n.2^k ≥ k!
#Registers used :
#           		t0  	-	to hold/update the number n
#			t1	- 	to hold the control variable k
#			t2 	-	to hold the value of k!
#			t3	-	to hold the value of n.2^k
#			s0, s1	-	to hold temporary values
#			v0 	-	syscall number

#Text section
	.text
main:
	#Read integer n
	li $v0, 5
	syscall
	move $t0, $v0
	#Perform initial check
	blez $t0, exit
	#Initialize k=1
	li $t1, 1

bigger_loop:
	move $s0, $t1
	li $s1, 1

#Find k! in factorial_loop and store it in t2
factorial_loop:
	mul $s1, $s1, $s0
	sub $s0, $s0, 1
	bnez $s0, factorial_loop
	move $t2, $s1

	move $s0, $t1
	li $s1, 1
#Find n.2^k in power_loop and store it in t3
power_loop:
	mul $s1, $s1, 2
	sub $s0, $s0, 1
	bnez $s0, power_loop
	move $t3, $s1
	mul $t3, $t3, $t0

	#Check if n.2^k >= k! . Yes->Increment k and loop. No->Print (k-1) and exit
	bge $t3, $t2, continue_bigger_loop
	b print_largest_k

continue_bigger_loop:
	add $t1, $t1, 1
	b bigger_loop

#Print largest k such that n.2^k >= k!
print_largest_k:
	sub $t1, $t1, 1
	move $a0, $t1
	li $v0, 1
	syscall

#Exit the program
exit:
	li $v0, 10
	syscall
