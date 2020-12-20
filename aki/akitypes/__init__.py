from llvmlite.ir.types import IntType, DoubleType, FloatType, HalfType
from llvmlite.ir import Constant, IRBuilder, Value, Type
from akiast import UnOps, BinOps, OpNode
from ctypes import c_bool, c_double, c_float, c_uint16, c_int64, c_uint64
from errors import AkiTypeException


class AkiTypeBase:
    def op(self, optype: OpNode):
        return getattr(self, f"op_{optype.__name__}")

    def _zext(self, value: Value, target_type: "AkiTypeBase", builder: IRBuilder):
        f1 = builder.zext(value, target_type.llvm_type)
        f1.aki = target_type
        return f1

    def __repr__(self):
        return f"<{self.typename}>"

    def ptr(self, pointee, builder: IRBuilder):
        ptr = AkiPtr(pointee)
        ptr.alloca(builder)
        return ptr

# this so far is only used for internal LLVM pointers.
# it's not an actual *pointer* type.
class AkiPtr(AkiTypeBase):
    def __init__(self, pointee):
        self.pointee = pointee

    def alloca(self, builder: IRBuilder):
        self.allocation = builder.alloca(self.pointee.type)
        return self.allocation

    def store(self, value, builder: IRBuilder):
        builder.store(value, self.allocation)

    def load(self, builder: IRBuilder):
        result = builder.load(self.allocation)
        result.aki = self.pointee.aki
        return result


class IntegerBase(AkiTypeBase):
    _cache = {}

    @classmethod
    def llvm(cls, value: str, size: int):
        """
        Generates an LLVM Value object with the appropriate .aki object attached to it.
        """
        val = int(value)
        llvm_value = Constant(IntType(size), val)
        llvm_value.aki = cls(size)
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
        target_type = SignedInteger(64)

        # TODO: create a general mechanism for the coercion of certain type pairs? E.g., bool+int = int? or just have each base type implement conversions for other base types?

        f1 = self._zext(lhs, target_type.llvm_type, builder)
        f2 = self._zext(rhs, target_type.llvm_type, builder)
        return target_type.__class__.op_ADD(f1, f2, builder)

    def op_SUB(self, lhs: Value, rhs: Value, builder: IRBuilder):
        target_type = SignedInteger(64)
        f1 = builder.zext(lhs, target_type.llvm_type)
        f1.aki = target_type
        f2 = builder.zext(rhs, target_type.llvm_type)
        return target_type.__class__.op_ADD(f1, f2, builder)

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f


Bool = Boolean(1)


class Integer(IntegerBase):
    ctype = c_int64

    # Unary ops

    def op_BOOL(self, lhs: Value, builder: IRBuilder):
        is_zero = builder.icmp_signed(BinOps.EQ.op, Constant(lhs.type, 0), lhs)
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

    def op_MUL(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.mul(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_BITAND(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.and_(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_BITOR(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.or_(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_BITXOR(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.xor(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_LSHIFT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.shl(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_RSHIFT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.ashr(lhs, rhs)
        f.aki = lhs.aki
        return f

    # Comparisons

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.GT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.LT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.GTEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_signed(BinOps.LTEQ.op, lhs, rhs)
        f.aki = Bool
        return f


class SignedInteger(Integer):
    def op_DIV(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.sdiv(lhs, rhs)
        f.aki = lhs.aki
        return f


class UnsignedInteger(Integer):
    ctype = c_uint64
    _cache = {}

    @property
    def typename(self):
        return f"uint{self.size}"

    @classmethod
    def llvm(cls, value: str, size: int):
        """
        Generates an LLVM Value object with the appropriate .aki object attached to it.
        """
        val = int(value[:-2])
        llvm_value = Constant(IntType(size), val)
        llvm_value.aki = UnsignedInteger(size)
        return llvm_value

    def op_DIV(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.udiv(lhs, rhs)
        f.aki = lhs.aki
        return f

    # Unary ops

    def op_BOOL(self, lhs: Value, builder: IRBuilder):
        is_zero = builder.icmp_unsigned(BinOps.EQ.op, Constant(lhs.type, 0), lhs)
        f = builder.select(is_zero, Constant(IntType(1), 0), Constant(IntType(1), 1))
        f.aki = Bool
        return f

    def op_NEG(self, lhs: Value, builder: IRBuilder):
        raise AkiTypeException("unsigned values can't be negated")

    def op_RSHIFT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.lshr(lhs, rhs)
        f.aki = lhs.aki
        return f

    # Comparisons

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.GT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.LT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.GTEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.icmp_unsigned(BinOps.LTEQ.op, lhs, rhs)
        f.aki = Bool
        return f


class Pointer(UnsignedInteger):
    @property
    def typename(self):
        return f"ptr{self.size}"


class FloatBase(AkiTypeBase):
    _cache = {}

    def _zext(self, value: Value, target_type: "AkiTypeBase", builder: IRBuilder):
        raise NotImplementedError

    @property
    def typename(self):
        return f"float{self.size}"

    def __new__(cls, size: int):
        try:
            return cls._cache[size]
        except KeyError:
            a = cls.__new(size)
            cls._cache[size] = a
            return a

    @classmethod
    def __new(cls, size: int):
        new = AkiTypeBase.__new__(cls)
        new.size = size
        return new

    # Unary ops

    def op_NEG(self, lhs: Value, builder: IRBuilder):
        f = builder.fsub(Constant(lhs.type, 0), lhs)
        f.aki = lhs.aki
        return f

    def op_BOOL(self, lhs: Value, builder: IRBuilder):
        is_zero = builder.fcmp_ordered(BinOps.EQ.op, Constant(lhs.type, 0.0), lhs)
        f = builder.select(is_zero, Constant(IntType(1), 0), Constant(IntType(1), 1))
        f.aki = Bool
        return f

    # Binary ops

    def op_ADD(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fadd(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_SUB(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fsub(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_MUL(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fmul(lhs, rhs)
        f.aki = lhs.aki
        return f

    def op_DIV(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fdiv(lhs, rhs)
        f.aki = lhs.aki
        return f

    # Comparisons

    def op_EQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.EQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_NEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.NEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.GT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LT(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.LT.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_GTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.GTEQ.op, lhs, rhs)
        f.aki = Bool
        return f

    def op_LTEQ(self, lhs: Value, rhs: Value, builder: IRBuilder):
        f = builder.fcmp_ordered(BinOps.LTEQ.op, lhs, rhs)
        f.aki = Bool
        return f


class Float64(FloatBase):
    ctype = c_double

    @classmethod
    def llvm(cls, value: str):
        val = float(value)
        llvm_value = Constant(DoubleType(), val)
        llvm_value.aki = Float64(64)
        return llvm_value

    def __init__(self, *a):
        self.llvm_type = DoubleType()


class Float32(FloatBase):
    ctype = c_float

    @classmethod
    def llvm(cls, value: str):
        val = float(value[:2])
        llvm_value = Constant(FloatType(), val)
        llvm_value.aki = Float32(32)
        return llvm_value

    def __init__(self, *a):
        self.llvm_type = FloatType()


class Float16(FloatBase):
    ctype = c_uint16

    @classmethod
    def llvm(cls, value: str):
        val = float(value[:2])
        llvm_value = Constant(HalfType(), val)
        llvm_value.aki = Float16(16)
        return llvm_value

    def __init__(self, *a):
        self.llvm_type = HalfType()
