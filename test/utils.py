from parsing import parser
from codegen import codegen
from jitengine import jit
import unittest


class BaseTest(unittest.TestCase):
    def cmd(self, command):
        ast = parser.parse(command)
        codegen.gen(ast)
        # print(str(codegen.module))
        result = jit.execute(codegen)
        jit.clear()
        return result

    def eq(self, command, assertion):
        self.assertEqual(self.cmd(command), assertion)

    def ex(self, command, exception):
        with self.assertRaises(exception):
            self.cmd(command)
