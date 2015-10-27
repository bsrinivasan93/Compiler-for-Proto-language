.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 10
	move $t3, $t0
	li $t0, 30
	move $t2, $t0
	li $t0, 40
	move $t1, $t0
	add $t0, $t3, $t2
	add $t0, $t2, $t1
	add $t0, $t3, $t0
	li $v0, 5
	syscall
	move $t0, $v0
	move $t3, $t0
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 10
	move $t3, $t0
	li $t0, 30
	move $t2, $t0
	li $t0, 40
	move $t1, $t0
	add $t0, $t3, $t2
	add $t0, $t2, $t1
	add $t0, $t3, $t0
	li $v0, 5
	syscall
	move $t0, $v0
	move $t3, $t0
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 10
	move $t3, $t0
	li $t0, 30
	move $t2, $t0
	li $t0, 40
	move $t1, $t0
	add $t0, $t3, $t2
	add $t0, $t2, $t1
	add $t0, $t3, $t0
	li $v0, 5
	syscall
	move $t0, $v0
	move $t3, $t0
exit:
	li $v0, 10
	syscall
