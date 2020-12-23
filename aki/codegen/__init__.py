from lark import Token
from akiast import Function, Immediate, Call, Name
from akitypes import (
    AkiTypeBase,
    Boolean,
    SignedInteger,
    UnsignedInteger,
    Float64,
    Float32,
    Float16,
)
from llvmlite import ir
from errors import AkiBaseException, AkiNameError, AkiTypeError


class Codegen:
    def __init__(self):
        self.reset()

    def reset(self):
        self.module = ir.Module()
        self.func_context = None
        self._anon_counter = 0

        # placeholder for start of stidlib generator
        # right now we just malloc/free, but later we'll use
        # platform-specific calls and wrap them

        u64 = UnsignedInteger(64).llvm_type()

        fns = (("malloc", u64, (u64,)), ("free", u64, (u64,)))

        for fn_name, fn_ret, fn_args in fns:

            fx = ir.Function(self.module, ir.FunctionType(fn_ret, fn_args), fn_name)
            fx.storage_class = "extern"

    def err(self, exception, node, message):
        raise exception(self.txt, node, message)

    def anon_counter(self):
        return f"ANONYMOUS_{self._anon_counter}"

    def gen(self, ast, txt):
        self.txt = txt
        if isinstance(ast, Immediate):
            return self.gen_immediate(ast.nodes)
        return self.gen_module(ast)

    def gen_module(self, ast):
        self.reset()
        pass

    def gen_immediate(self, ast):
        self.last_statement = None

        main_func_body = []

        for node in ast:
            if not isinstance(node, Function):
                main_func_body.append(node)
                continue
            self.codegen(node)

        try:

            if main_func_body:
                self._anon_counter += 1
                pos = (main_func_body[0].line, main_func_body[0].column)
                main_func = Function(
                    pos,
                    Name(pos, self.anon_counter()),
                    [],
                    SignedInteger(64),
                    main_func_body,
                )

                # TODO: unsuccessful codegen should roll back anon counter

                self.codegen(main_func)

        except Exception as e:
            del self.module.globals[self.anon_counter()]
            raise e

    def return_value(self, entry_point="main"):
        return self.module.globals[entry_point].ftype.return_type

    def codegen(self, node):
        return getattr(self, f"codegen_{node.__class__.__name__}")(node)

    # Codegen for primitive values

    def codegen_SignedInteger(self, node):
        return SignedInteger.llvm_value(node.value, 64)

    def codegen_UnsignedInteger(self, node):
        return UnsignedInteger.llvm_value(node.value, 64)

    def codegen_Float16(self, node):
        return Float16.llvm_value(node.value)

    def codegen_Float32(self, node):
        return Float32.llvm_value(node.value)

    def codegen_Float64(self, node):
        return Float64.llvm_value(node.value)

    def codegen_Boolean(self, node):
        return Boolean.llvm_value(node.value)

    # Operations

    def codegen_BinOp(self, node):
        lhs = self.codegen(node.lhs)
        rhs = self.codegen(node.rhs)
        if lhs.type.aki != rhs.type.aki:
            raise AkiTypeError(node, "incompatible types for op")
        return lhs.type.aki.op(node.op)(lhs, rhs, self.builder)

    def codegen_UnOp(self, node):
        lhs = self.codegen(node.lhs)
        return lhs.type.aki.op(node.op)(lhs, self.builder)

    # Control flow

    def codegen_Call(self, node: Call):

        function = self.module.globals.get(node.name.value)
        if not function:
            self.err(AkiNameError, node, f"function {node.name.value} not found")

        args = [self.codegen(arg) for arg in node.args]

        if len(args) != len(function.args):
            self.err(
                AkiBaseException,
                node,
                f"function {function.name} expected at least {len(function.args)} args, got {len(args)}",
            )

        result = self.builder.call(function, args)
        result.type.aki = function.return_value.type.aki
        return result

    def codegen_Function(self, node: Function):

        # set up a default return type
        func_return_type: AkiTypeBase = SignedInteger(64)
        func_return_type_llvm = func_return_type.llvm_type()

        # set up basic function information
        function_name = node.name.value
        func_type = ir.FunctionType(func_return_type.llvm_type(), [])
        func = ir.Function(self.module, func_type, function_name)

        # set this function as the current one in context
        self.func_context = func

        # create our function blocks
        entry_block = func.append_basic_block("entry")
        start_block = func.append_basic_block("start")
        exit_block = func.append_basic_block("exit")

        # create our builder and generate the body
        self.builder = ir.IRBuilder(entry_block)
        self.builder.position_at_start(start_block)

        body_result = None

        for _ in node.body:
            body_result = self.codegen(_)

        # compare body result type to default return type
        # correct if needed

        if func_return_type_llvm.aki != body_result.type.aki:
            func.type = ir.FunctionType(body_result.type, [])
            func.return_value.type = body_result.type
            func.ftype.return_type = body_result.type
            func_return_type_llvm = body_result.type

        # save current position
        last_body_block = self.builder.block

        # allocate space for return value in entry
        self.builder.position_at_start(entry_block)
        return_value = func_return_type_llvm.aki.alloca(self.builder)
        self.builder.branch(start_block)

        # save result into return value from end of body
        self.builder.position_at_end(last_body_block)
        self.builder.store(body_result, return_value)
        self.builder.branch(exit_block)

        # return the return value in the exit block
        self.builder.position_at_start(exit_block)
        self.builder.ret(self.builder.load(return_value))

        # clear function context
        self.func_context = None

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
            return_value = if_expr.type.aki.alloca(self.builder)
            self.builder.store(if_expr, return_value)

        # coerce to boolean if not already so
        if not isinstance(if_expr.type.aki, Boolean):
            if_expr = if_expr.type.aki.op_BOOL(if_expr, self.builder)

        self.builder.cbranch(if_expr, then_block, else_block)

        # Generate then block

        self.builder.position_at_start(then_block)
        then_expr = self.codegen(node.then_expr)

        then_branch = self.builder.branch(end_block)

        # Generate else block

        self.builder.position_at_start(else_block)
        else_expr = self.codegen(node.else_expr)

        else_branch = self.builder.branch(end_block)

        if then_expr.type.aki != else_expr.type.aki:
            self.err(
                AkiTypeError,
                node.then_expr,
                "then/else expressions must yield same type",
            )

        # Store possible return values if we are in a when expression

        if when_expr:

            self.builder.position_at_start(if_block)
            return_value = then_expr.type.aki.alloca(self.builder)

            self.builder.position_before(then_branch)
            self.builder.store(then_expr, return_value)

            self.builder.position_before(else_branch)
            self.builder.store(else_expr, return_value)

        self.builder.position_at_start(end_block)

        # Return return value

        result = return_value.type.aki.load(return_value, self.builder)
        return result


codegen = Codegen()

# .llvm_type might be a func that returns an .aki decorated type
# types vs values
