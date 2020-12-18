from llvmlite.ir.types import IntType
from llvmlite.ir import Constant, IRBuilder, Value
from akiast import Op, OpNode
from ctypes import c_bool, c_int64


class AkiTypeBase:
    def op(self, optype: OpNode):
        return getattr(self, f"op_{optype.__name__}")

    def _zext(self, value: Value, target_type: "AkiTypeBase", builder: IRBuilder):
        f1 = builder.zext(value, target_type.llvm_type)
        f1.aki = target_type
        return f1


class IntegerBase(AkiTypeBase):
    _cache = {}

    @classmethod
    def llvm(cls, value: str, size: int):
        """
        Generates an LLVM Value object with the appropriate .aki object attached to it.
        """
        val = int(value)
        llvm_value = Constant(IntType(size), val)
        llvm_value.aki = Integer(size)
        return llvm_value

    def __new__(cls, size: int):
        """
        Use an existing, cached type if it already exists in our type cache.
        """
        try:
            return cls._cache[size]
        except KeyError:
            a = cls.__new(size)
            cls._cache[size] = a
            return a

    @classmethod
    def __new(cls, size: int):
        """
        Instantiates a new Integer type, with an .llvm_type attribute.
        """
        new = AkiTypeBase.__new__(cls)
        new.llvm_type = IntType(size)
        return new

    def __init__(self, size: int):
        self.size = size

    @property
    def typename(self):
        return f"int{self.size}"

    def __repr__(self):
        return f"<{self.typename}>"


class Boolean(IntegerBase):
    ctype = c_bool

    @classmethod
    def llvm(cls, value: str):
        val = 1 if value == "True" else 0
        llvm_value = Constant(IntType(1), val)
        llvm_value.aki = Bool
        return llvm_value

    def __init__(self, *a):
        self.size = 1

    @property
    def typename(self):
        return f"bool"

    # Unary ops

    def op_BOOL(self, lhs: Value, builder: IRBuilder):
        return lhs

    def op_NEG(self, lhs: Value, builder: IRBuilder):
        f = builder.xor(Constant(self.llvm_type, 1), lhs)
        f.aki = Bool
        return f

    # Binary ops

    def op_ADD(self, lhs: Value, rhs: Value, builder: IRBuilder):
        target_type = Integer(64)
        f1 = self._zext(lhs, target_type.llvm_type, builder)
        f2 = self._zext(rhs, target_type.llvm_type, builder)
        return target_type.__class__.op_ADD(f1, f2, builder)

    def op_SUB(self, lhs: Value, rhs: Value, builder: IRBuilder):
        target_type = Integer(64)
        f1 = builder.zext(lhs, target_type.llvm_type)
        f1.aki = target_type
        f2 = builder.zext(rhs, target_type.llvm_type)
        return target_type.__class__.op_ADD(f1, f2, builder)

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(Op.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(Op.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f


Bool = Boolean(1)


class Integer(IntegerBase):
    ctype = c_int64

    # Unary ops

    def op_BOOL(self, lhs: Value, builder: IRBuilder):
        is_zero = builder.icmp_signed(Op.EQ.op, Constant(lhs.type, 0), lhs)
        f = builder.select(is_zero, Constant(IntType(1), 0), Constant(IntType(1), 1))
        f.aki = Bool
        return f

    def op_NEG(self, lhs: Value, builder: IRBuilder):
        f = builder.sub(Constant(lhs.type, 0), lhs)
        f.aki = lhs.aki
        return f

    # Binary ops

    def op_ADD(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.add(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_SUB(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.sub(lhs, rhs)
        f.aki = lhs.aki
        return f

    # Comparisons

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.GT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.LT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.GTEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(Op.LTEQ.op, lhs, rhs)
        f.aki = Bool
        return f
