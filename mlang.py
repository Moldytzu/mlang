# mlang

# iota counter implementation transpiled from C++
iotaCounter = 0
def getIota(shouldReset=False):
    global iotaCounter
    if shouldReset:
        iotaCounter = 0
    iotaCounter += 1
    return iotaCounter - 1