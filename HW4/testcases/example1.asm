.data

new_line:	.asciiz "\n"


.text

main:
b func_main
	func_sum :
	sub $sp, $sp, 60
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
	sw $a0, 40($sp)
	sw $a1, 44($sp)
	sw $a2, 48($sp)
	sw $a3, 52($sp)
	sw $ra, 56($sp)

	add $t3, $a1, $a2
	add $t2, $a0, $t3
	move $t0, $t2
	move $a0, $a0
	move $a1, $a1
	move $a2, $t0
	jal func_product
	move $a0, $v0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	move $v0, $t0
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
	lw $a0, 40($sp)
	lw $a1, 44($sp)
	lw $a2, 48($sp)
	lw $a3, 52($sp)
	lw $ra, 56($sp)
	add $sp, $sp, 60
	jr $ra
	func_product :
	sub $sp, $sp, 60
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
	sw $a0, 40($sp)
	sw $a1, 44($sp)
	sw $a2, 48($sp)
	sw $a3, 52($sp)
	sw $ra, 56($sp)

	mul $t5, $a1, $a2
	mul $t4, $a0, $t5
	move $t0, $t4
	move $v0, $t0
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
	lw $a0, 40($sp)
	lw $a1, 44($sp)
	lw $a2, 48($sp)
	lw $a3, 52($sp)
	lw $ra, 56($sp)
	add $sp, $sp, 60
	jr $ra
	func_main :
	li $t1, 10
	move $t3, $t1
	li $t1, 20
	move $t2, $t1
	li $t1, 30
	move $t1, $t1
	move $a0, $t3
	move $a1, $t2
	move $a2, $t1
	jal func_sum
	move $a0, $v0
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
	move $a0, $t3
	move $a1, $t2
	move $a2, $t1
	jal func_product
	move $t1, $v0
	move $a0, $t1
	li $v0, 1
	syscall
	la $a0, new_line
	li $v0, 4
	syscall
exit:
	li $v0, 10
	syscall
