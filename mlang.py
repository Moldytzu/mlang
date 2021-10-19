# mlang
import subprocess
import sys

# basic iota counter
iotaCounter = 0
def getIota(shouldReset=False):
    global iotaCounter
    if shouldReset:
        iotaCounter = 0
    iotaCounter += 1
    return iotaCounter - 1

# operations
PUSH = getIota(True)
PLUS = getIota()
MINUS = getIota()
DISPLAY = getIota()
OPCOUNT = getIota()

def push(x):
    return (PUSH, x)

def plus():
    return (PLUS, )

def minus():
    return (MINUS, )

def display():
    return (DISPLAY, )

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
            elif word.lower() == "display":
                operations.append(display())
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
def generate(prg):
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

        for op in prg:
            if op[0] == PUSH:
                asm.write(f"    ; -- PUSH {str(op[1])} --\n")
                asm.write(f"    push {str(op[1])}\n")
            if op[0] == PLUS:
                asm.write(f"    ; -- PLUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    add rax, rbx\n")
                asm.write(f"    push rax\n")
            if op[0] == MINUS:
                asm.write(f"    ; -- MINUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    sub rbx, rax\n")
                asm.write(f"    push rbx\n")
            if op[0] == DISPLAY:
                asm.write(f"    ; -- DISPLAY --\n")
                asm.write(f"    pop rdi\n")
                asm.write(f"    call display\n")

        asm.write("    mov rax, 60\n")
        asm.write("    mov rdi, 0\n")
        asm.write("    syscall\n")

    subprocess.call(["nasm", "-felf64", "_tmp.asm"])
    subprocess.call(["ld", "-o", "program" , "_tmp.o"])

# program

if len(sys.argv) < 2:
    print("Not enough arguments!")
    exit(-1)

program = parse(open(sys.argv[1], "r").read())

generate(program)