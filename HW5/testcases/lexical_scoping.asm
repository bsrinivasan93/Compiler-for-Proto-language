.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 20
	move $t0, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t0, 30
	move $t0, $t0
	move $t0, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
exit:
	li $v0, 10
	syscall
