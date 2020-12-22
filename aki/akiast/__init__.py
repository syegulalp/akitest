from llvmlite.ir import IRBuilder


class UnOps:
    class NEG:
        op = "-"


class BinOps:
    class ADD:
        op = "+"

    class SUB:
        op = "-"

    class MUL:
        op = "*"

    class DIV:
        op = "/"

    class EQ:
        op = "=="

    class NEQ:
        op = "!="

    class GT:
        op = ">"

    class LT:
        op = "<"

    class GTEQ:
        op = ">="

    class LTEQ:
        op = "<="

    class BITAND:
        op = "&"

    class BITOR:
        op = "|"

    class BITXOR:
        op = "^"

    class RSHIFT:
        op = ">>"

    class LSHIFT:
        op = "<<"


unops = {}
binops = {}

for _op, _Op in (unops, UnOps), (binops, BinOps):
    for _ in _Op.__dict__.values():
        op1 = getattr(_, "op", None)
        if not op1:
            continue
        _op[op1] = _


class Node:
    def __init__(self, pos):
        self.line, self.column = pos

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

class Immediate(Node):
    def __init__(self, pos, nodes):
        super().__init__(pos)
        self.nodes = nodes

class Number(Node):
    def __init__(self, pos, value: str):
        super().__init__(pos)
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"<Number: {self.value}>"


class Float(Number):
    pass


class Float16(Float):
    def __repr__(self):
        return f"<Float16: {self.value}>"


class Float32(Float):
    def __repr__(self):
        return f"<Float32: {self.value}>"


class Float64(Float):
    def __repr__(self):
        return f"<Float64: {self.value}>"


class Integer(Number):
    def __repr__(self):
        return f"<Integer: {self.value}>"


class SignedInteger(Integer):
    def __repr__(self):
        return f"<SignedInteger: {self.value}>"


class UnsignedInteger(Integer):
    def __repr__(self):
        return f"<UnsignedInteger: {self.value}>"


class Boolean(Number):
    def __repr__(self):
        return f"<Boolean: {self.value}>"


class Name(Node):
    def __init__(self, pos, value: str):
        super().__init__(pos)
        self.value = value

    def __eq__(self, other: Node):
        return self.value == other.value

    def __repr__(self):
        return f"<Name {self.value}>"

class VarRef(Name):
    def __repr__(self):
        return f"<VarRef {self.value}>"

class Function(Node):
    def __init__(self, pos, name: str, args: list, return_type: Node, body: Node):
        super().__init__(pos)
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body

    def __eq__(self, other: Node):
        return (
            self.args == other.args
            and self.return_type == other.return_type
            and self.body == other.body
        )

    def __repr__(self):
        return f"<Function {self.name}: {self.return_type}: {self.body}>"


class Call(Node):
    def __init__(self, pos, name: str, args: list):
        super().__init__(pos)
        self.name = name
        self.args = args

    def __eq__(self, other: Node):
        return (
            self.args == other.args
        )

    def __repr__(self):
        return f"<Call {self.name}: {self.args}>"

class IfExpr(Node):
    def __init__(self, pos, if_expr: Node, then_expr: Node, else_expr: Node):
        super().__init__(pos)
        self.if_expr = if_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __eq__(self, other: Node):
        return (
            self.if_expr == other.condition_expr
            and self.then_expr == other.then_expr
            and self.else_expr == other.else_expr
        )

    def __repr__(self):
        return f"<If {self.if_expr}: {self.then_expr}: {self.else_expr}>"


class WhenExpr(IfExpr):
    def __repr__(self):
        return f"<When {self.if_expr}: {self.then_expr}: {self.else_expr}>"


class OpNode(Node):
    pass


class BinOp(OpNode):
    def __init__(self, pos, lhs: Node, rhs: Node, op: str):
        super().__init__(pos)
        self.lhs = lhs
        self.rhs = rhs
        self.op = op

    def __eq__(self, other: Node):
        return self.lhs == other.lhs and self.rhs == other.rhs and self.op == other.op

    def __repr__(self):
        return f"<BinOp: {self.lhs} {self.op} {self.rhs}>"


class UnOp(OpNode):
    def __init__(self, pos, lhs: Node, op: str):
        super().__init__(pos)
        self.lhs = lhs
        self.op = op

    def __eq__(self, other: Node):
        return self.lhs == other.lhs and self.op == other.op

    def __repr__(self):
        return f"<UnOp: {self.op} {self.lhs}>"
