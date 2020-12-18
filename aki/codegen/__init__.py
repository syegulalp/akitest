from lark import Token
from akitypes import Integer, Boolean
from llvmlite import ir


class Codegen:
    def __init__(self):
        pass

    def reset(self):
        self.module = ir.Module()
        main_func_type = ir.FunctionType(ir.IntType(64), [])
        self.main_func = ir.Function(self.module, main_func_type, "main")
        main_block = self.main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(main_block)

    def gen(self, ast):
        self.reset()
        if not isinstance(ast, list):
            ast = [ast]
            last = ast
        for node in ast:
            last = self.codegen(node)

        if self.main_func.return_value.type != last.type:
            self.main_func.type = ir.FunctionType(last.type, [])
            self.main_func.return_value.type = last.type

        self.builder.ret(last)
        self.return_value = last

    def codegen(self, node):
        return getattr(self, f"codegen_{node.__class__.__name__}")(node)

    def codegen_BinOp(self, node):
        lhs = self.codegen(node.lhs)
        rhs = self.codegen(node.rhs)
        return lhs.aki.op(node.op)(lhs, rhs, self.builder)

    def codegen_UnOp(self, node):
        lhs = self.codegen(node.lhs)
        return lhs.aki.op(node.op)(lhs, None, self.builder)

    def codegen_Integer(self, node):
        return Integer.llvm(node.value, 64)

    def codegen_Boolean(self, node):
        return Boolean.llvm(node.value, 1)

    def codegen_IfExpr(self, node):

        then_expr = self.codegen(node.then_expr)
        else_expr = self.codegen(node.else_expr)
        # todo: check that types agree or can be nondestructively coerced

        if_expr = self.codegen(node.condition_expr)
        # todo: if_expr should be boolified if not already so

        r = self.builder.select(if_expr, then_expr, else_expr)
        r.aki = then_expr.aki
        return r


codegen = Codegen()
