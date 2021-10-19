# mlang
import subprocess
import sys

# operations
PUSH = 0
PLUS = 1
MINUS = 2
DISPLAY = 3
EQUAL = 4
IF = 5
END = 6
ELSE = 7

def push(x):
    return (PUSH, x)

def plus():
    return (PLUS, )

def minus():
    return (MINUS, )

def display():
    return (DISPLAY, )

def equal():
    return (EQUAL, )

def fi():
    return (IF, )

def end():
    return (END, )

def ese():
    return (ELSE, )

# parser
def parse(data):
    operations = []
    data = data.split()
    errors = 0
    for word in data:
        try:
            if word in ("","\n","\t"):
                continue
            if word == "+":
                operations.append(plus())
            elif word == "-":
                operations.append(minus())
            elif word == "=":
                operations.append(equal())
            elif word.lower() == "display":
                operations.append(display())
            elif word.lower() == "if":
                operations.append(fi())
            elif word.lower() == "else":
                operations.append(ese())
            elif word.lower() == "end":
                operations.append(end())
            else:
                operations.append(push(int(word)))
        except:
            print(f"Syntax Error! {word}")
            errors += 1
    if errors == 0:
        return operations
    else:
        return []

# generator

def crossreference_blocks(program):
    stack = []
    errors = 0
    for ip in range(len(program)):
        op = program[ip]
        if op[0] == IF:
            stack.append(ip)
        elif op[0] == ELSE:
            try:
                if_ip = stack.pop()
                program[if_ip] = (IF, ip + 1)
                stack.append(ip)
            except:
                print("SyntaxError! Else used outside of if blocks")
                errors += 1
        elif op[0] == END:
            try:
                block_ip = stack.pop()
                if program[block_ip][0] == IF or program[block_ip][0] == ELSE:
                    program[block_ip] = (program[block_ip][0], ip)
            except:
                print("SyntaxError! End used without needing to close an if block")
                errors += 1
    if errors == 0:
        return program
    else:
        return []

def generate(prg):
    if prg == []:
        print("Generator: Nothing to generate!")
        exit(0)
    with open("_tmp.asm", "w") as asm:
        asm.write("section .text\n")

        asm.write("display:\n")
        asm.write("    mov     r9, 0xCCCCCCCCCCCCCCCD\n")
        asm.write("    sub     rsp, 40\n")
        asm.write("    mov     BYTE [rsp+31], 10\n")
        asm.write("    lea     rcx, [rsp+30]\n")
        asm.write(".loop:\n")
        asm.write("    mov     rax, rdi\n")
        asm.write("    lea     r8, [rsp+32]\n")
        asm.write("    mul     r9\n")
        asm.write("    mov     rax, rdi\n")
        asm.write("    sub     r8, rcx\n")
        asm.write("    shr     rdx, 3\n")
        asm.write("    lea     rsi, [rdx+rdx*4]\n")
        asm.write("    add     rsi, rsi\n")
        asm.write("    sub     rax, rsi\n")
        asm.write("    add     eax, 48\n")
        asm.write("    mov     BYTE [rcx], al\n")
        asm.write("    mov     rax, rdi\n")
        asm.write("    mov     rdi, rdx\n")
        asm.write("    mov     rdx, rcx\n")
        asm.write("    sub     rcx, 1\n")
        asm.write("    cmp     rax, 9\n")
        asm.write("    ja      .loop\n")
        asm.write("    lea     rax, [rsp+32]\n")
        asm.write("    mov     edi, 1\n")
        asm.write("    sub     rdx, rax\n")
        asm.write("    xor     eax, eax\n")
        asm.write("    lea     rsi, [rsp+32+rdx]\n")
        asm.write("    mov     rdx, r8\n")
        asm.write("    mov     rax, 1\n")
        asm.write("    syscall\n")
        asm.write("    add     rsp, 40\n")
        asm.write("    ret\n")
    
        asm.write("global _start\n")
        asm.write("_start:\n")
        for ip in range(len(program)):
            op = program[ip]
            if op[0] == PUSH:
                asm.write(f"    ; -- PUSH {str(op[1])} --\n")
                asm.write(f"    push {str(op[1])}\n")
            elif op[0] == PLUS:
                asm.write(f"    ; -- PLUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    add rax, rbx\n") # add registers
                asm.write(f"    push rax\n")
            elif op[0] == MINUS:
                asm.write(f"    ; -- MINUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    sub rbx, rax\n") # substract registers
                asm.write(f"    push rbx\n")
            elif op[0] == DISPLAY:
                asm.write(f"    ; -- DISPLAY --\n")
                asm.write(f"    pop rdi\n")
                asm.write(f"    call display\n") # display
            elif op[0] == EQUAL:
                asm.write(f"    ; -- EQUAL --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rax, rbx\n")
                asm.write(f"    cmove r10, r11\n") # move only if eq flag is set
                asm.write(f"    push r10\n")
            elif op[0] == IF:
                asm.write(f"    ; -- IF --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    test rax, rax\n")
                asm.write(f"    jz endif_{op[1]}\n")
            elif op[0] == END:
                asm.write(f"endif_{ip}:\n")

        asm.write("    mov rax, 60\n")
        asm.write("    mov rdi, 0\n")
        asm.write("    syscall\n")

    subprocess.call(["nasm", "-felf64", "_tmp.asm"])
    subprocess.call(["ld", "-o", "program" , "_tmp.o"])

# program

if len(sys.argv) < 2:
    print("Not enough arguments!")
    exit(-1)

program = crossreference_blocks(parse(open(sys.argv[1], "r").read()))

generate(program)