import logging
from lark import Lark, Transformer, logger

logger.setLevel(logging.DEBUG)
from akiast import (
    Integer,
    Boolean,
    BinOp,
    UnOp,
    Op,
    Name,
    Function,
    IfExpr,
    SignedInteger,
    UnsignedInteger,
    Float16,
    Float32,
    Float64
)

with open("aki\\parsing\\grammar.lark") as f:
    grammar = f.read()


def pos(n):
    return (n.line, n.column)


class T(Transformer):
    def __init__(self):
        pass

    def signed_integer(self, node):
        n = node[0]
        return SignedInteger(pos(n), n.value)

    def unsigned_integer(self, node):
        n = node[0]
        return UnsignedInteger(pos(n), n.value)

    def float16(self, node):
        n = node[0]
        return Float16(pos(n), n.value)   

    def float32(self, node):
        n = node[0]
        return Float32(pos(n), n.value)    
    
    def float64(self, node):
        n = node[0]
        return Float64(pos(n), n.value)

    def nan(self, node):
        n = node[0]
        return Float64(pos(n), "NaN")

    def inf(self, node):
        n = node[0]
        return Float64(pos(n), "inf")

    def bool(self, node):
        n = node[0]
        return Boolean(pos(n), n.value)

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

    def gt(self, node):
        return self.binop(node, Op.GT)

    def lt(self, node):
        return self.binop(node, Op.LT)

    def gteq(self, node):
        return self.binop(node, Op.GTEQ)

    def lteq(self, node):
        return self.binop(node, Op.LTEQ)

    def neg(self, node):
        return UnOp(pos(node[0]), node[0], Op.NEG)

    def bitand(self, node):
        return self.binop(node, Op.BITAND)

    def bitor(self, node):
        return self.binop(node, Op.BITOR)

    def bitxor(self, node):
        return self.binop(node, Op.BITXOR)

    def rshift(self, node):
        return self.binop(node, Op.RSHIFT)

    def lshift(self, node):
        return self.binop(node, Op.LSHIFT)

    def funcdef(self, node):
        p = pos(node[0])
        name = Name(p, node[0].value)
        return Function(p, name, [], None, node[2])

    def statements(self, node):
        return node

    def ifexpr(self, node):
        return IfExpr(pos(node[0]), node[0], node[1], node[2])


parser = Lark(grammar, parser="lalr", debug=False, transformer=T())
