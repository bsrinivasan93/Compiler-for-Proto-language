.data

new_line:	.asciiz "\n"


.text

main:
	li $t0, 0
	move $t5, $t0
	li $t2, 20
	mul $t2, $t5, $t2
	li $t7, 1
	li $t6, 2
	li $t4, 5
	mul $t4, $t6, $t4
	add $t4, $t7, $t4
	add $t2, $t2, $t4
	move $t6, $t2
	li $t2, 0
	move $t4, $t2
	li $v0, 5
	syscall
	move $t2, $v0
	move $t2, $t2
	label_0 :
	li $t1, 0
	sgt $t1, $t2, $t1
	beq $t1, 0, label_1
	li $t0, 10
	li $t9, $t0
	divu $t2, $t9
	mfhi $t0
	add $t0, $t4, $t0
	move $t4, $t0
	li $t0, 10
	divu $t0, $t2, $t0
	move $t2, $t0
	b label_0
	label_1 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t7, 3
	li $t1, 11
	slt $t1, $t5, $t1
	beq $t7, 0, sc_label_0
	move $t1, $t1
	b sc_label_1
sc_label_0:
	li $t1, 0
sc_label_1:
	sgt $t1, $t6, $t1
	beq $t1, 0, label_4
	li $t1, 2
	add $t1, $t2, $t1
	move $t2, $t1
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t1, 3
	sgt $t1, $t2, $t1
	beq $t1, 0, label_2
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_3
	label_2 :
	add $t0, $t4, $t2
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_3 :
	b label_5
	label_4 :
	li $t3, 2
	move $t6, $t3
	li $t0, 3
	move $t5, $t0
	li $t0, 4
	label_5 :
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
	li $t0, 0
	move $t5, $t0
	li $t2, 20
	mul $t2, $t5, $t2
	li $t7, 1
	li $t6, 2
	li $t4, 5
	mul $t4, $t6, $t4
	add $t4, $t7, $t4
	add $t2, $t2, $t4
	move $t6, $t2
	li $t2, 0
	move $t4, $t2
	li $v0, 5
	syscall
	move $t2, $v0
	move $t2, $t2
	label_0 :
	li $t1, 0
	sgt $t1, $t2, $t1
	beq $t1, 0, label_1
	li $t0, 10
	li $t9, $t0
	divu $t2, $t9
	mfhi $t0
	add $t0, $t4, $t0
	move $t4, $t0
	li $t0, 10
	divu $t0, $t2, $t0
	move $t2, $t0
	b label_0
	label_1 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t7, 3
	li $t1, 11
	slt $t1, $t5, $t1
	beq $t7, 0, sc_label_0
	move $t1, $t1
	b sc_label_1
sc_label_0:
	li $t1, 0
sc_label_1:
	sgt $t1, $t6, $t1
	beq $t1, 0, label_4
	li $t1, 2
	add $t1, $t2, $t1
	move $t2, $t1
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t1, 3
	sgt $t1, $t2, $t1
	beq $t1, 0, label_2
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_3
	label_2 :
	add $t0, $t4, $t2
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_3 :
	b label_5
	label_4 :
	li $t3, 2
	move $t6, $t3
	li $t0, 3
	move $t5, $t0
	li $t0, 4
	label_5 :
exit:
	li $v0, 10
	syscall
.data

new_line:	.asciiz "\n"


.text

main:
	li $t0, 0
	move $t5, $t0
	li $t2, 20
	mul $t2, $t5, $t2
	li $t7, 1
	li $t6, 2
	li $t4, 5
	mul $t4, $t6, $t4
	add $t4, $t7, $t4
	add $t2, $t2, $t4
	move $t6, $t2
	li $t2, 0
	move $t4, $t2
	li $v0, 5
	syscall
	move $t2, $v0
	move $t2, $t2
	label_0 :
	li $t1, 0
	sgt $t1, $t2, $t1
	beq $t1, 0, label_1
	li $t0, 10
	li $t9, $t0
	divu $t2, $t9
	mfhi $t0
	add $t0, $t4, $t0
	move $t4, $t0
	li $t0, 10
	divu $t0, $t2, $t0
	move $t2, $t0
	b label_0
	label_1 :
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t7, 3
	li $t1, 11
	slt $t1, $t5, $t1
	beq $t7, 0, sc_label_0
	move $t1, $t1
	b sc_label_1
sc_label_0:
	li $t1, 0
sc_label_1:
	sgt $t1, $t6, $t1
	beq $t1, 0, label_4
	li $t1, 2
	add $t1, $t2, $t1
	move $t2, $t1
	move $a0, $t2
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	li $t1, 3
	sgt $t1, $t2, $t1
	beq $t1, 0, label_2
	move $a0, $t4
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	b label_3
	label_2 :
	add $t0, $t4, $t2
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	label_3 :
	b label_5
	label_4 :
	li $t3, 2
	move $t6, $t3
	li $t0, 3
	move $t5, $t0
	li $t0, 4
	label_5 :
exit:
	li $v0, 10
	syscall
