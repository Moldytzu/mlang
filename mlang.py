# mlang

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

program = [
    push(31),
    push(23),
    plus(),
    dump()
]