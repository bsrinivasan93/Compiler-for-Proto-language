.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 10
	move $t5, $t0
	li $t0, 20
	move $t3, $t0
	li $t0, 243
	move $t4, $t0
	add $t0, $t3, $t4
	slt $t0, $t5, $t0
	beq $t0, 0, label_2
	sgt $t0, $t3, $t4
	beq $t0, 0, label_0
	add $t0, $t5, $t4
	move $t3, $t0
	b label_1
	label_0 :
	sub $t1, $t5, $t4
	move $t3, $t1
	label_1 :
	b label_3
	label_2 :
	add $t2, $t3, $t4
	move $t5, $t2
	label_3 :
	move $a0, $t3
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
exit:
	li $v0, 10
	syscall
