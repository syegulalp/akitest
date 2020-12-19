from parsing import parser
from codegen import codegen
from jitengine import jit
import unittest

main_func_name="main"
class BaseTest(unittest.TestCase):
    #incr = 0

    def cmd(self, command):
        ast = parser.parse(command)
        #main_func_name = f"main_{BaseTest.incr}"
        codegen.gen(ast, main_func=main_func_name)
        #print (str(codegen.module))
        #print (codegen.return_value.aki)
        result = jit.execute(codegen, entry_point=main_func_name)
        jit.clear()
        #BaseTest.incr+=1
        return result

    def eq(self, command, assertion):
        self.assertEqual(self.cmd(command), assertion)

    def ex(self, command, exception):
        with self.assertRaises(exception):
            self.cmd(command)
