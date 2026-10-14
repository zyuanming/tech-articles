# SPDX-License-Identifier: MIT
# Original minimal Linux x86-64 entry point. No C runtime or libc.
.section .text
.globl _start
.type _start, @function
_start:
    call answer
    mov %eax, %edi
    mov $60, %eax
    syscall
.size _start, .-_start
.section .note.GNU-stack,"",@progbits
