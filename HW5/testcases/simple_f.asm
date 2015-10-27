.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t2, 0
	move $t2, $t2
	label_0 :
	li $t1, 10
	slt $t1, $t2, $t1
	beq $t1, 0, label_3
	b label_1
	label_2 :
	li $t0, 1
	add $t0, $t2, $t0
	move $t2, $t0
	b label_0
	label_1 :
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_2
	label_3 :
	li $t0, 10
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
exit:
	li $v0, 10
	syscall
