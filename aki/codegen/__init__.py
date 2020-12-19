from lark import Token
from akitypes import Integer, Boolean
from llvmlite import ir
from errors import AkiTypeException


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
        last = None
        
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
        if lhs.aki != rhs.aki:
            raise AkiTypeException("incompatible types for op")
        return lhs.aki.op(node.op)(lhs, rhs, self.builder)

    def codegen_UnOp(self, node):
        lhs = self.codegen(node.lhs)
        return lhs.aki.op(node.op)(lhs, self.builder)

    def codegen_Integer(self, node):
        return Integer.llvm(node.value, 64)

    def codegen_Boolean(self, node):
        return Boolean.llvm(node.value)

    def codegen_IfExpr(self, node):

        then_expr = self.codegen(node.then_expr)
        else_expr = self.codegen(node.else_expr)
        if then_expr.aki != else_expr.aki:
            raise AkiTypeException("then/else expressions must yield same type")

        if_expr = self.codegen(node.if_expr)

        # coerce to boolean if not already so
        if not isinstance(if_expr.aki, Boolean):
            if_expr = if_expr.aki.op_BOOL(if_expr, self.builder)

        r = self.builder.select(if_expr, then_expr, else_expr)
        r.aki = then_expr.aki
        return r


codegen = Codegen()
