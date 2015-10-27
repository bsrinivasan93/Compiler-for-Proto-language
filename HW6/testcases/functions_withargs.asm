.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_sum :
	sub $sp, $sp, 40
	sw $t0, ($sp)
	sw $t1, 4($sp)
	sw $t2, 8($sp)
	sw $t3, 12($sp)
	sw $t4, 16($sp)
	sw $t5, 20($sp)
	sw $t6, 24($sp)
	sw $t7, 28($sp)
	sw $t8, 32($sp)
	sw $t9, 36($sp)
	add $t2, $a1, $a2
	add $t1, $a0, $t2
	move $t5, $t1
	move $v0, $t5
	lw $t0, ($sp)
	lw $t1, 4($sp)
	lw $t2, 8($sp)
	lw $t3, 12($sp)
	lw $t4, 16($sp)
	lw $t5, 20($sp)
	lw $t6, 24($sp)
	lw $t7, 28($sp)
	lw $t8, 32($sp)
	lw $t9, 36($sp)
	add $sp, $sp, 40
	jr $ra
	func_product :
	sub $sp, $sp, 40
	sw $t0, ($sp)
	sw $t1, 4($sp)
	sw $t2, 8($sp)
	sw $t3, 12($sp)
	sw $t4, 16($sp)
	sw $t5, 20($sp)
	sw $t6, 24($sp)
	sw $t7, 28($sp)
	sw $t8, 32($sp)
	sw $t9, 36($sp)
	mul $t4, $a1, $a2
	mul $t3, $a0, $t4
	move $t5, $t3
	move $v0, $t5
	lw $t0, ($sp)
	lw $t1, 4($sp)
	lw $t2, 8($sp)
	lw $t3, 12($sp)
	lw $t4, 16($sp)
	lw $t5, 20($sp)
	lw $t6, 24($sp)
	lw $t7, 28($sp)
	lw $t8, 32($sp)
	lw $t9, 36($sp)
	add $sp, $sp, 40
	jr $ra
	func_main :
	li $t0, 10
	move $t2, $t0
	li $t0, 20
	move $t1, $t0
	li $t0, 30
	move $t0, $t0
	move $a0, $t2
	move $a1, $t1
	move $a2, $t0
	jal func_sum
	move $a0, $v0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	move $a0, $t2
	move $a1, $t1
	move $a2, $t0
	jal func_product
	move $t0, $v0
	move $a0, $t0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
exit:
	li $v0, 10
	syscall
