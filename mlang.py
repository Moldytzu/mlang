# mlang
import subprocess
import sys

#utils
def Error(name,details):
    print(name + ": " + details)

# operations
PUSH = 0
PLUS = 1
MINUS = 2
DISPLAYI = 3
EQUAL = 4
IF = 5
END = 6
ELSE = 7
DUPLICATE = 8
GREATER = 9
LESS = 10
WHILE = 11
DO = 12
MEM = 13
STORE = 14
LOAD = 15
MEMINC = 16
MEMDEC = 17
SYSCALL = 18
STRING  = 19
DISPLAY = 20

class Operation():
    type = None
    value = None
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"{self.type}:{self.value}"

# parser
def parse(data):
    operations = []
    data = data.split()
    errors = 0
    startedComment = 0
    for word in data:
        try:
            if startedComment == 0:
                if word in "" or word in "\t" or word in "\n":
                    continue
                if word[0] == "#":
                    startedComment = 1
                    continue
                if word[0] == "'" and word[-1] == "'":
                    operations.append(Operation(PUSH,ord(word[1])))
                    continue
                if word == "+":
                    operations.append(Operation(PLUS))
                elif word == "-":
                    operations.append(Operation(MINUS))
                elif word == "=":
                    operations.append(Operation(EQUAL))
                elif word == "<":
                    operations.append(Operation(LESS))
                elif word == ">":
                    operations.append(Operation(GREATER))
                elif word.lower() == "displayi" or word.lower() == "dispi":
                    operations.append(Operation(DISPLAYI))
                elif word.lower() == "display" or word.lower() == "disp":
                    operations.append(Operation(DISPLAY))
                elif word.lower() == "if":
                    operations.append(Operation(IF))
                elif word.lower() == "while":
                    operations.append(Operation(WHILE))
                elif word.lower() == "do":
                    operations.append(Operation(DO))
                elif word.lower() == "end":
                    operations.append(Operation(END))
                elif word.lower() == "else":
                    operations.append(Operation(ELSE))
                elif word.lower() == "duplicate" or word.lower() == "dp":
                    operations.append(Operation(DUPLICATE))
                elif word.lower() == "memory" or word.lower() == "mem":
                    operations.append(Operation(MEM))
                elif word.lower() == "store" or word.lower() == "ste":
                    operations.append(Operation(STORE))   
                elif word.lower() == "load" or word.lower() == "lod":
                    operations.append(Operation(LOAD)) 
                elif word.lower() == "memory+" or word.lower() == "mem+" or word.lower() == "m+":
                    operations.append(Operation(MEMINC)) 
                elif word.lower() == "memory-" or word.lower() == "mem-" or word.lower() == "m-":
                    operations.append(Operation(MEMDEC))
                elif word.lower() == "syscall" or word.lower() == "sys" or word.lower() == "kcall":
                    operations.append(Operation(SYSCALL))
                else:
                    operations.append(Operation(PUSH,int(word)))
            else:
                if "#" in word:
                    startedComment = 0
        except:
            Error("ParsingError",f"Unknown operation '{word}'")
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
        if op.type == IF:
            stack.append(ip)
        elif op.type == ELSE:
            if_ip = stack.pop()
            if program[if_ip].type != IF:
                Error("SyntaxError", "Else should be used only in if blocks")
                errors += 1
            program[if_ip].value = ip + 1
            stack.append(ip)
        elif op.type == END:
            block_ip = stack.pop()
            if program[block_ip].type == IF or program[block_ip].type == ELSE:
                program[block_ip].value = ip
                program[ip].value = ip + 1
            elif program[block_ip].type == DO:
                program[ip].value = program[block_ip].value
                program[block_ip].value = ip + 1
            else:
                Error("SyntaxError", "End should be used only to close if and while blocks")
                errors += 1
                exit(1)
        elif op.type == WHILE:
            stack.append(ip)
        elif op.type == DO:
            while_ip = stack.pop()
            program[ip].value = while_ip
            stack.append(ip)
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
        # optimization: include display only if it's used
        displayIsUsed = 0
        for i in range(len(prg)):
            if prg[i].type == DISPLAYI:
                displayIsUsed = 1
        if displayIsUsed:
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
            asm.write(f"address_{ip}:\n")
            if op.type == PUSH:
                asm.write(f"    ; -- PUSH {str(op.value)} --\n")
                asm.write(f"    push {str(op.value)}\n")
            elif op.type == PLUS:
                asm.write(f"    ; -- PLUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    add rax, rbx\n") # add registers
                asm.write(f"    push rax\n")
            elif op.type == MINUS:
                asm.write(f"    ; -- MINUS --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    sub rbx, rax\n") # substract registers
                asm.write(f"    push rbx\n")
            elif op.type == DISPLAYI:
                asm.write(f"    ; -- DISPLAYI --\n")
                asm.write(f"    pop rdi\n")
                asm.write(f"    call display\n") # display
            elif op.type == EQUAL:
                asm.write(f"    ; -- EQUAL --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rax, rbx\n")
                asm.write(f"    cmove r10, r11\n")
                asm.write(f"    push r10\n")
            elif op.type == GREATER:
                asm.write(f"    ; -- GREATER --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rbx, rax\n")
                asm.write(f"    cmovg r10, r11\n")
                asm.write(f"    push r10\n")
            elif op.type == LESS:
                asm.write(f"    ; -- LESS --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rbx, rax\n")
                asm.write(f"    cmovl r10, r11\n")
                asm.write(f"    push r10\n")
            elif op.type == IF:
                asm.write(f"    ; -- IF --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    test rax, rax\n")
                asm.write(f"    jz address_{op.value}\n")
            elif op.type == ELSE:
                asm.write(f"    ; -- ELSE --\n")
                asm.write(f"    jmp address_{op.value}\n")
                asm.write(f"address_{ip+1}:\n")
            elif op.type == END:
                if ip + 1 != op.value:
                    asm.write(f"    jmp address_{op.value}\n")
            elif op.type == DUPLICATE:
                asm.write(f"    ; -- DUPLICATE --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    push rax\n")
                asm.write(f"    push rax\n")
            elif op.type == DO:
                asm.write(f"    ; -- WHILE DO --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    test rax, rax\n")
                asm.write(f"    jz address_{op.value}\n")
            elif op.type == MEM:
                asm.write(f"    ; -- MEMORY --\n")
                asm.write(f"    mov rax, mem\n")
                asm.write(f"    add rax, r15\n")
                asm.write(f"    push rax\n")
            elif op.type == LOAD:
                asm.write(f"    ; -- LOAD --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    xor rbx,rbx\n")
                asm.write(f"    mov bl, [rax]\n")
                asm.write(f"    push rbx\n")
            elif op.type == STORE:
                asm.write(f"    ; -- STORE --\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    mov [rax], bl\n")
            elif op.type == MEMINC:
                asm.write(f"   ; -- MEM+ -- \n")
                asm.write(f"   inc r15\n")
            elif op.type == MEMDEC:
                asm.write(f"   ; -- MEM- -- \n")
                asm.write(f"   dec r15\n")
            elif op.type == SYSCALL:
                asm.write(f"   ; -- SYSCALL -- \n")
                asm.write(f"   pop rax\n")
                asm.write(f"   pop rdi\n")
                asm.write(f"   pop rsi\n")
                asm.write(f"   pop rdx\n")
                asm.write(f"   pop r10\n")
                asm.write(f"   pop r8\n")
                asm.write(f"   pop r9\n")
                asm.write(f"   syscall\n")
            elif op.type == DISPLAY:
                asm.write(f"   ; -- DISPLAY -- \n")
                asm.write(f"   mov rax, 1\n")
                asm.write(f"   mov rdi, 1\n")
                asm.write(f"   pop rsi\n")
                asm.write(f"   pop rdx\n")
                asm.write(f"   mov r10, 0\n")
                asm.write(f"   mov r8, 0\n")
                asm.write(f"   mov r9, 0\n")
                asm.write(f"   syscall\n")


        asm.write(f"address_{ip+1}:\n")
        asm.write("    mov rax, 60\n")
        asm.write("    mov rdi, 0\n")
        asm.write("    syscall\n")
        asm.write("\nsection .bss\n")
        asm.write(f"mem resb 640000")

    subprocess.call(["nasm", "-felf64", "_tmp.asm"])
    subprocess.call(["ld", "-o", "program" , "_tmp.o"])

# program

if len(sys.argv) < 2:
    print("Not enough arguments!")
    exit(-1)

program = crossreference_blocks(parse(open(sys.argv[1], "r").read()))

generate(program)