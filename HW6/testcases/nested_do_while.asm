.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t3, 20
	move $t3, $t3
	label_2 :
	li $v0, 5
	syscall
	move $t2, $v0
	move $t3, $t2
	li $t2, 10
	add $t2, $t3, $t2
	move $t3, $t2
	move $a0, $t3
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t2, 30
	move $t2, $t2
	label_0 :
	li $v0, 5
	syscall
	move $t1, $v0
	move $t2, $t1
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t1, 3
	slt $t1, $t2, $t1
	beq $t1, 0, label_1
	b label_0
	label_1 :
	li $t0, 30
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t0, 2
	slt $t0, $t3, $t0
	beq $t0, 0, label_3
	b label_2
	label_3 :
exit:
	li $v0, 10
	syscall
