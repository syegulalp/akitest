import sys

sys.path.insert(0, "aki")

from parsing import parser
from codegen import codegen
from jitengine import jit

commands = [
    "True",
    "2",
    "2+2",
    "2==2",
    "2==4",
    "2.0",
    "if 32==2 0 else 1",
    "when 32 0 else 1",
    "def test(){32} when test()==32 0 else 1",
]

for command in commands:
    print("IN >", command)
    ast = parser.parse(command, start="immediate")
    # print(ast)
    codegen.gen(ast)
    print(str(codegen.module))
    entry = codegen.anon_counter()
    result = jit.execute(codegen, entry_point=entry)
    print("OUT>", result, codegen.return_value(entry).aki)
    jit.clear()
