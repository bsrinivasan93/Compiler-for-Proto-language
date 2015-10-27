.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $t0, 10
	move $t0, $t0
	li $t0, 0
	move $t2, $t0
	label_0 :
	li $t1, 10
	slt $t0, $t2, $t1
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t2, $t2, 1
	b label_0
	label_1 :
	add $t2, $t2, 1
	move $t0, $t2
	move $t0, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_2
	label_3 :
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
	move $t0, $t0
	li $t0, 0
	move $t2, $t0
	label_0 :
	li $t1, 10
	slt $t0, $t2, $t1
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t2, $t2, 1
	b label_0
	label_1 :
	add $t2, $t2, 1
	move $t0, $t2
	move $t0, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_2
	label_3 :
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
	move $t0, $t0
	li $t0, 0
	move $t2, $t0
	label_0 :
	li $t1, 10
	slt $t0, $t2, $t1
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t2, $t2, 1
	b label_0
	label_1 :
	add $t2, $t2, 1
	move $t0, $t2
	move $t0, $t0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_2
	label_3 :
exit:
	li $v0, 10
	syscall
