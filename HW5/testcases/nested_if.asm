.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t1, 10
	move $t1, $t1
	move $t2, $t1
	li $t1, 10
	slt $t1, $t2, $t1
	beq $t1, 0, label_2
	move $t1, $t2
	li $t0, 20
	slt $t0, $t1, $t0
	beq $t0, 0, label_0
	move $a0, $t1
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_1
	label_0 :
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_1 :
	b label_3
	label_2 :
	li $t0, 10
	add $t0, $t2, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_3 :
exit:
	li $v0, 10
	syscall
