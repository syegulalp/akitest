from lark import Token
from akitypes import (
    Integer,
    Boolean,
    SignedInteger,
    UnsignedInteger,
    Float64,
    Float32,
    Float16,
)
from llvmlite import ir
from errors import AkiTypeException


class Codegen:
    def __init__(self):
        pass

    def reset(self, main_func="main"):
        self.module = ir.Module()
        main_func_type = ir.FunctionType(ir.IntType(64), [])
        self.main_func = ir.Function(self.module, main_func_type, main_func)
        main_block = self.main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(main_block)

    def gen(self, ast, main_func="main"):
        self.reset(main_func=main_func)
        last = None

        if not isinstance(ast, list):
            ast = [ast]
            last = ast

        for node in ast:
            # print (node)
            last = self.codegen(node)

        if self.main_func.return_value.type != last.type:
            self.main_func.type = ir.FunctionType(last.type, [])
            self.main_func.return_value.type = last.type

        self.builder.ret(last)
        self.return_value = last

    def codegen(self, node):
        return getattr(self, f"codegen_{node.__class__.__name__}")(node)

    # Codegen for primitive values

    def codegen_SignedInteger(self, node):
        return SignedInteger.llvm(node.value, 64)

    def codegen_UnsignedInteger(self, node):
        return UnsignedInteger.llvm(node.value, 64)

    def codegen_Float16(self, node):
        return Float16.llvm(node.value)

    def codegen_Float32(self, node):
        return Float32.llvm(node.value)

    def codegen_Float64(self, node):
        return Float64.llvm(node.value)

    def codegen_Boolean(self, node):
        return Boolean.llvm(node.value)

    # Codegen for operations

    def codegen_BinOp(self, node):
        lhs = self.codegen(node.lhs)
        rhs = self.codegen(node.rhs)
        if lhs.aki != rhs.aki:
            raise AkiTypeException("incompatible types for op")
        return lhs.aki.op(node.op)(lhs, rhs, self.builder)

    def codegen_UnOp(self, node):
        lhs = self.codegen(node.lhs)
        return lhs.aki.op(node.op)(lhs, self.builder)

    def codegen_WhenExpr(self, node):
        return self.codegen_IfExpr(node, True)

    def codegen_IfExpr(self, node, when_expr=False):

        # if expr returns the results of the if
        # when results the rsults of the branches

        if_block = self.builder.append_basic_block("if_block")
        then_block = self.builder.append_basic_block("then_block")
        else_block = self.builder.append_basic_block("else_block")
        end_block = self.builder.append_basic_block("end_block")

        return_value = None

        # Generate if block

        self.builder.branch(if_block)
        self.builder.position_at_start(if_block)
        if_expr = self.codegen(node.if_expr)

        if not when_expr:
            return_value = if_expr.aki.ptr(if_expr, self.builder)
            return_value.store(if_expr, self.builder)

        # coerce to boolean if not already so
        if not isinstance(if_expr.aki, Boolean):
            if_expr = if_expr.aki.op_BOOL(if_expr, self.builder)

        self.builder.cbranch(if_expr, then_block, else_block)

        # Generate then block

        self.builder.position_at_start(then_block)
        then_expr = self.codegen(node.then_expr)
        
        if when_expr:
            return_value = then_expr
        
        then_branch = self.builder.branch(end_block)

        # Generate else block

        self.builder.position_at_start(else_block)
        else_expr = self.codegen(node.else_expr)
        
        if when_expr:
            return_value = else_expr

        else_branch = self.builder.branch(end_block)

        if then_expr.aki != else_expr.aki:
            raise AkiTypeException("then/else expressions must yield same type")

        # Store possible return values if we are not in a while

        if when_expr:

            self.builder.position_at_start(if_block)
            return_value = then_expr.aki.ptr(then_expr, self.builder)

            self.builder.position_before(then_branch)
            return_value.store(then_expr, self.builder)

            self.builder.position_before(else_branch)
            return_value.store(else_expr, self.builder)

        self.builder.position_at_start(end_block)

        # Return return value

        result = return_value.load(self.builder)
        return result


codegen = Codegen()
