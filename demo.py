import sys

sys.path.insert(0, "aki")

from parsing import parser
from codegen import codegen
from jitengine import jit

commands = ["2", "2+2", "2==2", "2==4", "if 32==2 0 else 1"]

for command in commands:
    ast = parser.parse(command)
    codegen.gen(ast)
    print(str(codegen.module))
    result = jit.execute(codegen)
    jit.clear()
    print(codegen.return_value.aki)
    print(">", result)
