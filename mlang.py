# mlang
import subprocess

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
DUMP = getIota()
OPCOUNT = getIota()

def push(x):
    return (PUSH, x)

def plus():
    return (PLUS, )

def dump():
    return (DUMP, )

# generator
def generate(prg):
    with open("_tmp.asm", "w") as asm:
        asm.write("section .text\n")
        asm.write("global _start\n")
        asm.write("_start:\n")
        asm.write("    mov rax, 60\n")
        asm.write("    mov rdi, 0\n")
        asm.write("    syscall\n")

    subprocess.call(["nasm", "-felf64", "_tmp.asm"])
    subprocess.call(["ld", "-o", "program" , "_tmp.o"])

# program

program = [
    push(31),
    push(23),
    plus(),
    dump()
]

generate(program)