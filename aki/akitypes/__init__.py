from llvmlite.ir.types import IntType
from llvmlite.ir import Constant, IRBuilder
from akiast import Op
from ctypes import c_bool, c_int64


class AkiTypeBase:
    @classmethod
    def op(cls, optype):
        return getattr(cls, f"op_{optype.__name__}")


class IntegerBase(AkiTypeBase):
    _cache = {}

    @classmethod
    def llvm(cls, value, size):
        val = int(value)
        llvm_value = Constant(IntType(size), val)
        llvm_value.aki = Integer(size)
        return llvm_value

    def __new__(cls, size):
        try:
            return cls._cache[size]
        except KeyError:
            a = cls.__new(size)
            cls._cache[size] = a
            return a

    @classmethod
    def __new(cls, size):
        new = AkiTypeBase.__new__(cls)
        return new

    def __init__(self, size):
        self.size = size

    @property
    def typename(self):
        return f"int{self.size}"

    def __repr__(self):
        return f"<{self.typename}>"


class Boolean(IntegerBase):
    ctype = c_bool

    @classmethod
    def llvm(cls, value):
        val = 1 if value == "True" else 0
        llvm_value = Constant(IntType(1), val)
        llvm_value.aki = Bool
        return llvm_value

    def __init__(self, *a):
        self.size = 1

    @property
    def typename(self):
        return f"bool"

    def op_EQ(self, other, builder):
        f = IRBuilder.icmp_unsigned(builder, Op.EQ.op, self, other)
        f.aki = Bool
        return f

    def op_NEQ(self, other, builder):
        f = IRBuilder.icmp_unsigned(builder, Op.NEQ.op, self, other)
        f.aki = Bool
        return f

    def op_NEG(self, other, builder):
        f= IRBuilder.xor(builder, Constant(self.type, 1), self)
        f.aki = Bool
        return f

Bool = Boolean(1)


class Integer(IntegerBase):
    ctype = c_int64

    def op_ADD(self, other, builder):
        f = IRBuilder.add(builder, self, other)
        f.aki = self.aki
        return f

    def op_SUB(self, other, builder):
        f = IRBuilder.sub(builder, self, other)
        f.aki = self.aki
        return f

    def op_EQ(self, other, builder):
        f = IRBuilder.icmp_signed(builder, Op.EQ.op, self, other)
        f.aki = Bool
        return f

    def op_NEQ(self, other, builder):
        f = IRBuilder.icmp_signed(builder, Op.NEQ.op, self, other)
        f.aki = Bool
        return f

    def op_NEG(self, other, builder):
        f = IRBuilder.sub(builder, Constant(self.type, 0), self)
        f.aki = self.aki
        return f
