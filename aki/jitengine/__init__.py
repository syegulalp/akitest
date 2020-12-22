import llvmlite.binding as llvm
from ctypes import c_int64, CFUNCTYPE


class Jit:
    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.create_execution_engine()
        self.mod = None

    def create_execution_engine(self):
        # Create a target machine representing the host
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # And an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly("")
        self.engine = llvm.create_mcjit_compiler(backing_mod, target_machine)

    def compile_ir(self, llvm_ir):
        # Create a LLVM module object from the IR
        try:
            mod = llvm.parse_assembly(llvm_ir)
        except RuntimeError:
            print (llvm_ir)
            raise Exception
        mod.verify()
        # Now add the module and make sure it is ready for execution
        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    def execute(self, codegen, entry_point="main"):
        self.mod = self.compile_ir(str(codegen.module))
        func_ptr = self.engine.get_function_address(entry_point)
        cfunc = CFUNCTYPE(codegen.return_value(codegen.anon_counter()).aki.ctype)(func_ptr)
        res = cfunc()
        return res

    def clear(self):
        self.engine.remove_module(self.mod)
        self.mod = None


jit = Jit()
