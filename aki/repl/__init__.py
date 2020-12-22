from parsing import parser
from codegen import Codegen
from jitengine import Jit
from errors import ReloadException, QuitException

class Repl:
    def __init__(self):
        self.reset()

    def reset(self):
        self.jit = Jit()
        self.codegen = Codegen()
    
    def run(self):
        while True:
            self.command()
    
    def command(self):
        try:
            cmd = input(">>> ")
        except KeyboardInterrupt:
            print ()
            return
        except EOFError:
            raise QuitException

        if cmd == "..":
            raise ReloadException
        
        if cmd==".":
            self.reset()
            return

        if not cmd.startswith('.'):
            self.execute(cmd)
        else:
            cmd = cmd[1:]
            args = cmd.split(' ',1)
            getattr(self, cmd_map[cmd])(cmd, args)
    
    def quit(self, *a):
        raise QuitException

    def test(self, *a):        
        import unittest
        tests = unittest.TestLoader().discover(".\\test", pattern="test_*.py")
        unittest.TextTestRunner(failfast=True).run(tests)        

    def execute(self, cmd):
        ast = parser.parse(cmd, start="immediate")
        self.codegen.gen(ast)
        entry = self.codegen.anon_counter()
        result = self.jit.execute(self.codegen, entry_point = entry)
        print(result)
        #self.jit.clear()

cmd_map = {
    "q": "quit",
    "quit": "quit",
    "exit": "quit",
    "t": "test",
    "test": "test"
}

repl = Repl()