# mlang
import subprocess
import sys
import re

#utils
def error(name,details):
    print(f"{name}: {details}")

def findallMatches(expression,data):
    matches = []
    c = re.compile(expression) # compile the expression
    for m in c.finditer(data): # iterate thru the findings
        matches.append((m.groups()[0],m.span(0))) # get the content and the range
    return matches

def doVerbose(text):
    global verbose
    if verbose:
        print(text)

# options
enableLinking = True
appendExit = True
shouldCallNASM = True
verbose = False
autoRun = False
outputName = "program"
entryName = "_start"

# operations
PUSH = 0
PLUS = 1
MINUS = 2
DISPLAI = 3
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
SWAP = 19
MEMINDEX = 20
MEMSET = 21
MULTIPLY = 22
DIVIDE = 23

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
    doVerbose("Parsing")
    for word in data:
        try:
            if word in ("","\t","\n"): continue # whitespace
            if word[0] == "'" and word[-1] == "'" and len(word) == 3: # character
                doVerbose(f"Appending PUSH with {ord(word[1])}")
                operations.append(Operation(PUSH,ord(word[1])))
                continue
            if word.startswith("0x") and len(word) > 2: # hexdecimal
                doVerbose(f"Appending PUSH with {int(word,base=16)}")
                operations.append(Operation(PUSH,int(word,base=16)))
                continue
            if word == "+":
                doVerbose("Appending PLUS")
                operations.append(Operation(PLUS))
            elif word == "-":
                doVerbose("Appending MINUS")
                operations.append(Operation(MINUS))
            elif word == "*":
                doVerbose("Appending MULTIPLY")
                operations.append(Operation(MULTIPLY))
            elif word == "/":
                doVerbose("Appending DIVIDE")
                operations.append(Operation(DIVIDE))
            elif word == "=":
                doVerbose("Appending EQUAL")
                operations.append(Operation(EQUAL))
            elif word == "<":
                doVerbose("Appending LESS")
                operations.append(Operation(LESS))
            elif word == ">":
                doVerbose("Appending GREATER")
                operations.append(Operation(GREATER))
            elif word.lower() == "displai" or word.lower() == "dispi":
                doVerbose("Appending DISPLAI")
                operations.append(Operation(DISPLAI))
            elif word.lower() == "if":
                doVerbose("Appending IF")
                operations.append(Operation(IF))
            elif word.lower() == "while":
                doVerbose("Appending WHILE")
                operations.append(Operation(WHILE))
            elif word.lower() == "do":
                doVerbose("Appending DO")
                operations.append(Operation(DO))
            elif word.lower() == "end":
                doVerbose("Appending END")
                operations.append(Operation(END))
            elif word.lower() == "else":
                doVerbose("Appending ELSE")
                operations.append(Operation(ELSE))
            elif word.lower() == "duplicate" or word.lower() == "dp":
                doVerbose("Appending DUPLICATE")
                operations.append(Operation(DUPLICATE))
            elif word.lower() == "memory" or word.lower() == "mem":
                doVerbose("Appending MEM")
                operations.append(Operation(MEM))
            elif word.lower() == "store" or word.lower() == "ste":
                doVerbose("Appending STORE")
                operations.append(Operation(STORE))   
            elif word.lower() == "load" or word.lower() == "lod":
                doVerbose("Appending LOAD")
                operations.append(Operation(LOAD)) 
            elif word.lower() == "swap" or word.lower() == "swp":
                doVerbose("Appending SWAP")
                operations.append(Operation(SWAP)) 
            elif word.lower() == "memory+" or word.lower() == "mem+" or word.lower() == "m+":
                doVerbose("Appending MEMINC")
                operations.append(Operation(MEMINC)) 
            elif word.lower() == "memory-" or word.lower() == "mem-" or word.lower() == "m-":
                doVerbose("Appending MEMDEC")
                operations.append(Operation(MEMDEC))
            elif word.lower() == "memoryindex" or word.lower() == "memidx" or word.lower() == "mi":
                doVerbose("Appending MEMINDEX")
                operations.append(Operation(MEMINDEX))
            elif word.lower() == "memoryset" or word.lower() == "memset" or word.lower() == "ms":
                doVerbose("Appending MEMSET")
                operations.append(Operation(MEMSET))
            elif word.lower() == "syscall" or word.lower() == "sys" or word.lower() == "kcall":
                doVerbose("Appending SYSCALL")
                operations.append(Operation(SYSCALL))
            else:
                doVerbose(f"Appending PUSH with {word}")
                operations.append(Operation(PUSH,int(word)))
        except:
            error("ParsingError",f"Unknown operation '{word}'")
            errors += 1
    doVerbose(f"Done, with {errors} errors")
    if errors == 0:
        return operations
    else:
        return []

# preprocessor
def referenceBlocks(program):
    stack = []
    errors = 0
    for ip in range(len(program)):
        op = program[ip]
        if op.type == IF:
            stack.append(ip)
        elif op.type == ELSE:
            if_ip = stack.pop()
            if program[if_ip].type != IF:
                error("SyntaxError", "Else should be used only in if blocks")
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
                error("SyntaxError", "End should be used only to close if and while blocks")
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

def processIncludes(data):
    toinclude = findallMatches(r'(?s)\%include \'(.*?)\'',data)

    errors = 0
    for file in toinclude:
        data = data.replace(f"%include '{file[0]}'", "")
        try:
            data = open(file[0],"r").read() + data
        except:
            error("IncludeError",f"'{file[0]}' not found!")
            errors += 1

    if errors == 0:
        return data
    else:
        return ""

def processMacros(data):
    macrosMatches = findallMatches(r'(?s)%macro (.*?)%macro',data)
    macros = []

    # replace macro statements
    for m in macrosMatches:
        name = m[0].split()[0]
        content = m[0][len(name)+1:].strip()
        span = m[1]
        macros.append((name,content,span))
        data = data.replace(m[0],"").replace("%macro","")
    # replace macros
    for passNo in range(0,16):
        doVerbose(f"Replacing macros: pass {passNo}")
        for m in macros:
            data = data.replace(f"{m[0]} ",f"{m[1]} ") # replace only full words
            data = data.replace(f"{m[0]}\n",f"{m[1]}\n")

    return data

def processComments(data):
    commentMatches = findallMatches(r'(?s)#(.*?)#',data)

    # replace comments
    for comment in commentMatches:
        data = data.replace(comment[0],"").replace("#","")

    return data

def preprocessor(data):
    if(data[-1] != "\n"):
        data += "\n"
    while data.__contains__("%include"): # check all includes
        data = processIncludes(data)
    data = processComments(data)
    data = processMacros(data)
    return data

#generator
def generate(prg):
    if prg == []:
        print("Nothing to generate!")
        exit(0)
    doVerbose("Generating: " + str(prg))
    with open(outputName + ".asm", "w") as asm:
        asm.write("section .text\n")
        # optimization: include display only if it's used
        displaisUsed = 0
        for i in range(len(prg)):
            if prg[i].type == DISPLAI:
                displaisUsed = 1
        if displaisUsed:
            asm.write("displai:\n")
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
    
        asm.write("global " + entryName + "\n")
        asm.write(entryName + ":\n")
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
            elif op.type == DISPLAI:
                asm.write(f"    ; -- displai --\n")
                asm.write(f"    pop rdi\n")
                asm.write(f"    call displai\n") # displai
            elif op.type == EQUAL:
                asm.write(f"    ; -- EQUAL --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rax, rbx\n")
                asm.write(f"    cmove r10, r11\n") # move on equal flag
                asm.write(f"    push r10\n")
            elif op.type == GREATER:
                asm.write(f"    ; -- GREATER --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rbx, rax\n")
                asm.write(f"    cmovg r10, r11\n") # move on greater flag
                asm.write(f"    push r10\n")
            elif op.type == LESS:
                asm.write(f"    ; -- LESS --\n")
                asm.write(f"    mov r10, 0\n")
                asm.write(f"    mov r11, 1\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    cmp rbx, rax\n")
                asm.write(f"    cmovl r10, r11\n") # move on less flag
                asm.write(f"    push r10\n")
            elif op.type == IF:
                asm.write(f"    ; -- IF --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    test rax, rax\n")
                asm.write(f"    jz address_{op.value}\n") # jump on zero flag
            elif op.type == ELSE:
                asm.write(f"    ; -- ELSE --\n")
                asm.write(f"    jmp address_{op.value}\n") # jump to end
                asm.write(f"address_{ip+1}:\n")
            elif op.type == END:
                if ip + 1 != op.value:
                    asm.write(f"    jmp address_{op.value}\n") # jump back
            elif op.type == DUPLICATE:
                asm.write(f"    ; -- DUPLICATE --\n")
                asm.write(f"    pop rax\n") 
                asm.write(f"    push rax\n")
                asm.write(f"    push rax\n") # get the value, push it twice 
            elif op.type == DO:
                asm.write(f"    ; -- WHILE DO --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    test rax, rax\n")
                asm.write(f"    jz address_{op.value}\n") # jump on zero flag
            elif op.type == MEM:
                asm.write(f"    ; -- MEMORY --\n")
                asm.write(f"    mov rax, mem\n")
                asm.write(f"    add rax, r15\n") # add index
                asm.write(f"    push rax\n")
            elif op.type == LOAD:
                asm.write(f"    ; -- LOAD --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    mov rbx, 0\n")  
                asm.write(f"    mov bl, [rax]\n")
                asm.write(f"    push rbx\n")
            elif op.type == STORE:
                asm.write(f"    ; -- STORE --\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    mov [rax], bl\n")
            elif op.type == MEMINC:
                asm.write(f"   ; -- MEM+ -- \n")
                asm.write(f"   inc r15\n") # increase index
            elif op.type == MEMDEC:
                asm.write(f"   ; -- MEM- -- \n")
                asm.write(f"   dec r15\n") # decrease index
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
            elif op.type == SWAP:
                asm.write(f"   ; -- SWAP -- \n")
                asm.write(f"   pop rax\n")
                asm.write(f"   pop rbx\n")
                asm.write(f"   push rax\n")
                asm.write(f"   push rbx\n")
            elif op.type == MEMINDEX:
                asm.write(f"   ; -- MEMINDEX -- \n")
                asm.write(f"   push r15\n") # push index
            elif op.type == MEMSET:
                asm.write(f"   ; -- MEMSET -- \n")
                asm.write(f"   pop r15\n") # pop index
            elif op.type == MULTIPLY:
                asm.write(f"    ; -- MULTIPLY --\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    mul rbx\n") # multiply registers
                asm.write(f"    push rax\n")
            elif op.type == DIVIDE:
                asm.write(f"    ; -- DIVIDE --\n")
                asm.write(f"    mov rdx, 0\n")
                asm.write(f"    pop rbx\n")
                asm.write(f"    pop rax\n")
                asm.write(f"    div rbx\n") # divide registers
                asm.write(f"    push rax\n")

        asm.write(f"address_{ip+1}:\n")
        if appendExit:
            asm.write("    mov rax, 60\n") # exit syscall
            asm.write("    mov rdi, 0\n") # code 0
            asm.write("    syscall\n")
        asm.write("\nsection .bss\n")
        asm.write(f"mem resb 64000")
    
    doVerbose("Done")

    if shouldCallNASM:
        subprocess.call(["nasm", "-felf64", f"{outputName}.asm"])

        if enableLinking:
            subprocess.call(["ld", "-o", "program" , f"{outputName}.o"])
            if autoRun:
                doVerbose(f"Running: {sys.path[0]}/{outputName}")
                subprocess.call([f"{sys.path[0]}/{outputName}"])

# program

def usage():
    print("Usage: mlang.py <source file> [options]")
    print("")
    print("Aditional options:")
    print("-a -> auto run program if compilation succeded")
    print("-v -> verbose")
    print("-l -> disable automatic linking")
    print("-es -> disable the exit syscall on the end")
    print("-n -> disable calling nasm")
    print("-e [entry name] -> change entry point name from _start to [entry name]")
    print("-o [output name] -> output name")

def parseArguments(args,argslen):
    global enableLinking
    global verbose
    global autoRun
    global appendExit
    global outputName
    global entryName
    global shouldCallNASM
    # parse arguments
    if argslen < 2:
        print("Not enough arguments!")
        usage()
        exit(-1)

    if argslen > 2:
        for idx in range(2,argslen):
            if args[idx] == "-a":
                autoRun = True
            elif args[idx] == "-v":
                verbose = True
            elif args[idx] == "-l":
                enableLinking = False
            elif args[idx] == "-es":
                appendExit = False
            elif args[idx] == "-e":
                if idx < argslen:
                    entryName = args[idx+1]
            elif args[idx] == "-o":
                if idx < argslen:
                    outputName = args[idx+1]
            elif args[idx] == "-n":
                shouldCallNASM = False

arguments = sys.argv
argumentsLen = len(sys.argv)

parseArguments(arguments, argumentsLen)

inputData = ""
try:
    inputData = open(sys.argv[1], "r").read()
except:
    error("FileError",f"Source code '{sys.argv[1]}' not found")

program = referenceBlocks(parse(preprocessor(inputData)))

generate(program)