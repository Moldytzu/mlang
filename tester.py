import subprocess

class Test():
    file = ""
    expectedOutput = ""
    def __init__(self, file, expectedOutput):
        self.file = file
        self.expectedOutput = expectedOutput

tests = [
    Test("examples/helloWorld.mlsrc","Hello, World!\n"),
    Test("examples/ifs.mlsrc","N\nY\nN\n"),
    Test("examples/loops.mlsrc","ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"),
    Test("examples/macros.mlsrc","A\n"),
    Test("examples/math.mlsrc","6\n2\n8\n2\n1\n"),
    Test("examples/memory.mlsrc","990\nH\n993\n"),
]

def run(test,optimize):
    arguments = ["python3","mlang.py",test.file,"-a"]
    if optimize: arguments.append("-ob")

    out = subprocess.Popen(arguments,stdout=subprocess.PIPE).stdout.read().decode()
    result = ">>Failed<<"
    if out == test.expectedOutput: result = "Passed"
    print(f"Testing {test.file}... {result}")

print("mlang Tester")
print("Testing unoptimized")
for test in tests:
    run(test,False)
print("Testing optimized")
for test in tests:
    run(test,True)