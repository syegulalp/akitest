import logging
from lark import Lark, Transformer, logger

logger.setLevel(logging.DEBUG)
from akiast import (
    Boolean,
    BinOp,
    UnOp,
    unops,
    binops,
    Name,
    Function,
    IfExpr,
    WhenExpr,
    SignedInteger,
    UnsignedInteger,
    Float16,
    Float32,
    Float64,
)


def pos(n):
    return (n.line, n.column)

def _p(n, value = None):
    return (n[0].line, n[0].column), n[0].value if not value else value


def _p(n, value=None):
    return (n[0].line, n[0].column), n[0].value if not value else value


class T(Transformer):
    def __init__(self):
        pass

    def signed_integer(self, node):
        return SignedInteger(*_p(node))

    def unsigned_integer(self, node):
        return UnsignedInteger(*_p(node))

    def float16(self, node):
        return Float16(*_p(node))

    def float32(self, node):
        return Float32(*_p(node))
    def float64(self, node):
        return Float64(*_p(node))

    def nan(self, node):
        return Float64(*_p(node, value="NaN"))

    def inf(self, node):
        n = node[0]
        return Float64(*_p(node, value="inf"))

    def bool(self, node):
        return Boolean(*_p(node))

    def binop(self, node, op):
        return BinOp(pos(node[0]), node[0], node[2], op)

    def unop(self, node):
        return UnOp(pos(node[1]), node[1], unops[node[0]])

    def compop(self, node):
        return self.binop(node, binops[node[1]])

    muldivop = prodop = compop

    def comparisons(self, node):
        return node[0].value

    muldivs = unops = products = comparisons

    def funcdef(self, node):
        p = _p(node)
        name = Name(*p)
        return Function(p[0], name, [], None, node[2])

    def statements(self, node):
        return node

    def ifexpr(self, node):
        return IfExpr(pos(node[0]), node[0], node[1], node[2])

    def whenexpr(self, node):
        return WhenExpr(pos(node[0]), node[0], node[1], node[2])

with open(".\\aki\\parsing\\grammar.lark") as f:
    grammar = f.read()

parser = Lark(
    grammar,
    parser="lalr",
    regex=True,
    cache=".\\aki\\grammar.cache",
    start=["start","statement"],
    debug=False,
    transformer=T()
)