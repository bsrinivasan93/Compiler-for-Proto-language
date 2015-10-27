.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t2, 10
	move $t2, $t2
	mul $t2, $t2, 4
	li $v0, 9
	move $a0, $t2
	syscall
	move $t2, $v0
	move $t2, $t2
	li $t4, 0
	move $t4, $t4
	label_0 :
	li $t0, 10
	slt $t0, $t4, $t0
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t4, $t4, 1
	b label_0
	label_1 :
	mul $t0, $t4, 4
	add $t0, $t2, $t0
	sw $t4, ($t0)
	b label_2
	label_3 :
	li $t1, 0
	move $t4, $t1
	label_4 :
	li $t3, 10
	slt $t0, $t4, $t3
	beq $t0, 0, label_7
	b label_5
	label_6 :
	add $t4, $t4, 1
	b label_4
	label_5 :
	mul $t1, $t4, 4
	add $t0, $t2, $t1
	lw $t1, ($t0)
	move $a0, $t1
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_6
	label_7 :
exit:
	li $v0, 10
	syscall
