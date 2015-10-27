.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t2, 0
	move $t2, $t2
	label_4 :
	li $t1, 10
	slt $t1, $t2, $t1
	beq $t1, 0, label_7
	b label_5
	label_6 :
	add $t2, $t2, 1
	b label_4
	label_5 :
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t1, 0
	move $t1, $t1
	label_0 :
	li $t0, 10
	slt $t0, $t1, $t0
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t1, $t1, 1
	b label_0
	label_1 :
	move $a0, $t1
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_2
	label_3 :
	b label_6
	label_7 :
exit:
	li $v0, 10
	syscall
