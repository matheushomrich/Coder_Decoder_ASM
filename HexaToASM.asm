.text
.globl label_0
lui $1, 0x00001001
ori $8, $1, 0x00000030
lw $8, 0x00000000($8)
lui $1, 0x00001001
ori $9, $1, 0x0000002c
lw $9, 0x00000000($9)
lui $1, 0x00001001
ori $10, $1, 0x00000034
lw $10, 0x00000000($10)
lui $1, 0x00001001
ori $11, $1, 0x00000000
beq $9, $10, label_18
lw $12, 0x00000000($11)
addu $12, $12, $8
sw $12, 0x00000000($11)
addiu $11, $11, 0x00000004
addiu $10, $10, 0x00000001
j label_12
addiu $2, $0, 0x0000000a
syscall
