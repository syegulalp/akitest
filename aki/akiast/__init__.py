from llvmlite.ir import IRBuilder


class Op:
    class ADD:
        op = "+"

    class SUB:
        op = "-"

    class EQ:
        op = "=="

    class NEQ:
        op = "!="

    class NEG:
        op = "-"

    class GT:
        op = ">"

    class LT:
        op = "<"

    class GTEQ:
        op = ">="

    class LTEQ:
        op = "<="


class Node:
    def __init__(self, pos):
        self.line, self.column = pos

    def __eq__(self, other):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Number(Node):
    def __init__(self, pos, value: str):
        super().__init__(pos)
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"<Number: {self.value}>"


class Integer(Number):
    def __repr__(self):
        return f"<Integer: {self.value}>"


class Boolean(Number):
    def __repr__(self):
        return f"<Boolean: {self.value}>"


class Name(Node):
    def __init__(self, pos, val: str):
        super().__init__(pos)
        self.val = val

    def __eq__(self, other: Node):
        return self.val == other.val

    def __repr__(self):
        return f"<Name {self.val}>"


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


class IfExpr(Node):
    def __init__(self, pos, condition_expr: Node, then_expr: Node, else_expr: Node):
        super().__init__(pos)
        self.condition_expr = condition_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __eq__(self, other: Node):
        return (
            self.condition_expr == other.condition_expr
            and self.then_expr == other.then_expr
            and self.else_expr == other.else_expr
        )

    def __repr__(self):
        return f"<If {self.condition_expr}: {self.then_expr}: {self.else_expr}>"


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
