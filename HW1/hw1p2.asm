#Balaji Srinivasan - 02/09/15
#hw1p2.asm           - Program that reads two 32-bit signed integers m and n, and prints their greatest common divisor if both m and n are positive
#Registers used :
#           		t0  	-	to hold integer m
#			t1	- 	to hold integer n / contains GCD(m, n) at the end_of_gcd_loop
#			t2 	-	to hold temporary values
#			v0 	-	syscall number

#Text section
	.text
main:
	#Read integer m
	li $v0, 5
	syscall
	move $t0, $v0

	#Read integer n
	li $v0, 5
	syscall
	move $t1, $v0

	#Perform intial checks on m and n
	blez $t0, exit
	blez $t1, exit

#Euclidean algorithm to find the GCD(m, n)
gcd_loop:
	#If m==0, n is the GCD
	beqz $t0, end_of_gcd_loop
	
	#If m>n, call GCD(n, m)
	bgt $t0, $t1, m_is_bigger
	
	#m<n. Call GCD(n%m, m)
	move $t2, $t0
	div $t1, $t0
	mfhi $t0
	move $t1, $t2
	b gcd_loop

m_is_bigger:
	move $t2, $t0
	move $t0, $t1
	move $t1, $t2
	b gcd_loop

end_of_gcd_loop:
	#Print the GCD.i.e.n
	move $a0, $t1
	li $v0, 1
	syscall

#Exit the program
exit:
	li $v0, 10
	syscall
