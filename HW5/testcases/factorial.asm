.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $v0, 5
	syscall
	move $t2, $v0
	move $t3, $t2
	li $t2, 1
	move $t4, $t2
	li $t2, 1
	seq $t2, $t3, $t2
	beq $t2, 0, label_4
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_5
	label_4 :
	li $t1, 2
	move $t1, $t1
	label_0 :
	sle $t0, $t1, $t3
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t1, $t1, 1
	b label_0
	label_1 :
	mul $t0, $t4, $t1
	move $t4, $t0
	b label_2
	label_3 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_5 :
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $v0, 5
	syscall
	move $t2, $v0
	move $t3, $t2
	li $t2, 1
	move $t4, $t2
	li $t2, 1
	seq $t2, $t3, $t2
	beq $t2, 0, label_4
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_5
	label_4 :
	li $t1, 2
	move $t1, $t1
	label_0 :
	sle $t0, $t1, $t3
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t1, $t1, 1
	b label_0
	label_1 :
	mul $t0, $t4, $t1
	move $t4, $t0
	b label_2
	label_3 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_5 :
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_main :
	li $v0, 5
	syscall
	move $t2, $v0
	move $t3, $t2
	li $t2, 1
	move $t4, $t2
	li $t2, 1
	seq $t2, $t3, $t2
	beq $t2, 0, label_4
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_5
	label_4 :
	li $t1, 2
	move $t1, $t1
	label_0 :
	sle $t0, $t1, $t3
	beq $t0, 0, label_3
	b label_1
	label_2 :
	add $t1, $t1, 1
	b label_0
	label_1 :
	mul $t0, $t4, $t1
	move $t4, $t0
	b label_2
	label_3 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_5 :
exit:
	li $v0, 10
	syscall
