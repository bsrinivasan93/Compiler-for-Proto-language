.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t2, 0
	move $t2, $t2
	label_2 :
	li $t1, 10
	slt $t1, $t2, $t1
	beq $t1, 0, label_3
	li $t1, 0
	move $t1, $t1
	label_0 :
	li $t0, 5
	slt $t0, $t1, $t0
	beq $t0, 0, label_1
	li $t0, 1
	add $t0, $t1, $t0
	move $t1, $t0
	move $a0, $t1
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_0
	label_1 :
	li $t3, 1
	add $t0, $t2, $t3
	move $t2, $t0
	b label_2
	label_3 :
exit:
	li $v0, 10
	syscall
