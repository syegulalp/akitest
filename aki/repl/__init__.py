from parsing import parser
from codegen import Codegen
from jitengine import Jit
from errors import ReloadException, QuitException, AkiBaseException, AkiSyntaxError
import os
import textwrap
from itertools import zip_longest
from functools import lru_cache
import lark


class Repl:
    def __init__(self):
        if os.get_terminal_size().columns < 80:
            print(
                "NOTE: terminal width less than 80 columns, errors may not format properly"
            )
        print("Aki v.0.01\n.h for help")
        self.reset()

    def reset(self):
        self.jit = Jit()
        self.codegen = Codegen()

    def run(self):
        while True:
            self.command()

    def command(self, cmd_input=None):
        if not cmd_input:
            try:
                cmd = input("» ")
            except KeyboardInterrupt:
                print()
                return
            except EOFError:
                raise QuitException
        else:
            print("»", cmd_input)
            cmd = cmd_input

        cmd = cmd.strip()

        if not cmd:
            return

        if cmd == "..":
            raise ReloadException

        if cmd == ".":
            print("JIT/REPL reset")
            self.reset()
            return

        if not cmd.startswith("."):
            self.execute(cmd)
        else:
            cmd = cmd[1:]
            args = cmd.split(" ", 1)
            try:
                cmd_exec = getattr(self, cmd_map[cmd])
            except KeyError:
                print(f"ERR: command not found: '{cmd}'")
            else:
                cmd_exec(cmd, args)

    def quit(self, *a):
        raise QuitException

    def test(self, *a):
        import unittest

        tests = unittest.TestLoader().discover(".\\test", pattern="test_*.py")
        unittest.TextTestRunner(failfast=True).run(tests)

    # TODO:

    def execute(self, cmd):
        try:
            ast = parser.parse(cmd, start="immediate")
        except lark.exceptions.UnexpectedToken as e:
            print(AkiSyntaxError(cmd, e, "unexpected token"))
            return

        try:
            self.codegen.gen(ast, cmd)
        except AkiBaseException as e:
            print(e)
            return
        except Exception:
            import traceback

            print("*** Python error:")
            traceback.print_exc()
            return

        entry = self.codegen.anon_counter()

        try:
            result = self.jit.execute(self.codegen, entry_point=entry)
        except RuntimeError as e:
            import traceback

            print("*** Runtime error:")
            traceback.print_exc()
            return
        print(result)

    def demo(self, *a):
        from .demo import commands

        for command in commands:
            self.command(command)

    def dump(self, *a):
        print(str(self.codegen.module))

    def help(self, *a):
        print(self._help())

    @lru_cache()
    def _help(self):
        output = []

        cmd_help = []
        last_cmd = None

        for k, v in cmd_map.items():
            if last_cmd != v:
                last_cmd = v
                cmd_help.append([[k], cmd_descriptions[last_cmd]])

            else:
                cmd_help[-1][0].append(k)

        for cmds in cmd_help:
            cmds[0] = textwrap.wrap("." + "|".join(cmds[0]), 15)
            cmds[1] = textwrap.wrap(cmds[1], 60)

        for cmds in cmd_help:
            spacer = True
            for a, b in zip_longest(cmds[0], cmds[1], fillvalue=""):
                output.append(f"{a.rjust(15)}{' : ' if spacer else '  '}{b}")
                spacer = False

        return "\n" + "\n".join(output) + "\n"


cmd_map = {
    "q": "quit",
    "quit": "quit",
    "exit": "quit",
    "t": "test",
    "test": "test",
    "demo": "demo",
    "d": "demo",
    "x": "dump",
    "dump": "dump",
    "h": "help",
    "help": "help",
    "?": "help",
    ".": "reload",
    "": "reset",
}

cmd_descriptions = {
    "quit": "exit REPL",
    "test": "run test suite",
    "demo": "run demonstration",
    "dump": "dump current module IR to console",
    "help": "display this help message",
    "reset": "reset JIT/REPL",
    "reload": "reload REPL entirely",
}

repl = Repl()

# rich
