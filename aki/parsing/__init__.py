import logging
from lark import Lark, Transformer, logger

logger.setLevel(logging.DEBUG)
from akiast import Number, BinOp, UnOp, Op, Name, Function, IfExpr

with open("aki\\parsing\\grammar.lark") as f:
    grammar = f.read()


def pos(n):
    return (n.line, n.column)


class T(Transformer):
    def __init__(self):
        pass

    def number(self, node):
        n = node[0]
        return Number(pos(n), n.value)

    def binop(self, node, op):
        return BinOp(pos(node[0]), node[0], node[1], op)

    def add(self, node):
        return self.binop(node, Op.ADD)

    def sub(self, node):
        return self.binop(node, Op.SUB)

    def eq(self, node):
        return self.binop(node, Op.EQ)

    def neq(self, node):
        return self.binop(node, Op.NEQ)

    def neg(self, node):
        return UnOp(pos(node[0]), node[0], Op.NEG)

    def funcdef(self, node):
        p = pos(node[0])
        name = Name(p, node[0].value)
        return Function(p, name, [], None, node[2])

    def statements(self, node):
        return node

    def ifexpr(self, node):
        return IfExpr(pos(node[0]), node[0], node[1], node[2])


parser = Lark(grammar, parser="lalr", debug=False, transformer=T())