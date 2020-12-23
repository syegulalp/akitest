from utils import BaseTest
from errors import AkiTypeError
from math import isnan, isinf

all_binops = ("==", "!=", ">=", "<=", ">", "<")
all_unops = "-"


class TestA(BaseTest):
    def test_a(self):
        pass


class TestBaseValues(BaseTest):
    def test_boolean(self):
        self.eq("True", True)
        self.eq("False", False)
        self.eq("-False", True)
        self.eq("-True", False)

    def test_integer(self):
        self.eq("2", 2)
        self.eq("-2", -2)
        self.eq(f"{2**63}_U", 2 ** 63)

    def test_float(self):
        self.eq("2.0+.INF", float("inf"))
        self.eq("2.0", 2.0)
        self.eq("2.0_F", 2.0)

        # self.eq("2.2_H", 0)
        # TODO: perform proper conversions in both directions for half-width floats

        result = self.cmd(".NAN")
        self.assertTrue(type(result) is float and isnan(result))
        result = self.cmd(".INF")
        self.assertTrue(type(result) is float and isinf(result))


class TestBaseOperations(BaseTest):
    def test_int_add(self):
        self.eq("2+2", 4)
        self.eq("-2+4", 2)

    def test_int_sub(self):
        self.eq("2-2", 0)
        self.eq("2-4", -2)

    def test_int_muldiv(self):
        self.eq("2*2", 4)
        self.eq("4/2", 2)

    def test_int_bit_ops(self):
        self.eq("2 & 3", 2)
        self.eq("2 | 3", 3)
        self.eq("2 ^ 3", 1)
        self.eq("2 << 2", 8)
        self.eq("8 >> 3", 1)
        self.eq("8 >> 5", 0)
        # TODO: unsigned shifts, signed bit ops

    def test_float_add(self):
        self.eq("2.0+2.2", 4.2)
        self.eq("-2.0+4.2", 2.2)

    def test_float_sub(self):
        self.eq("2.0-4.2", -2.2)
        self.eq("4.2-2.0", 2.2)

    def test_float_muldiv(self):
        self.eq("2.*2.", 4.0)
        self.eq("4./2.", 2.0)

    def test_bool_math(self):
        self.eq("True-True", False)
        self.eq("True+True", 2)
        self.eq("False+True", True)
        self.eq("False-True", -1)
        self.eq("True*True", True)
        self.eq("True*False", False)
        self.eq("False/True", False)
        # TODO: division by zero trapping
        self.eq("True/False", False)


class TestBaseComparisons(BaseTest):
    def test_bool_eq_comp(self):
        self.eq("True==True", True)
        self.eq("False==False", True)
        self.eq("False==True", False)

    def test_bool_neq_comp(self):
        self.eq("True!=False", True)
        self.eq("True!=True", False)

    def test_int_eq_comp(self):
        self.eq("2==2", True)
        self.eq("2==4", False)

    def test_int_neq_comp(self):
        self.eq("2!=2", False)
        self.eq("2!=4", True)

    def test_int_gt_lt_comp(self):
        self.eq("2>3", False)
        self.eq("2<3", True)
        self.eq("2<=3", True)
        self.eq("2>=3", False)

    def test_float_eq_comp(self):
        self.eq("2.0==2.0", True)
        self.eq("-2.0==-2.0", True)
        self.eq("-2.0==2.0", False)

    def test_float_neq_comp(self):
        self.eq("2.0!=2.0", False)
        self.eq("-2.0!=-2.0", False)
        self.eq("-2.0!=2.0", True)

    def test_float_gt_lt_comp(self):
        self.eq("2.>3.", False)
        self.eq("2.<3.", True)
        self.eq("2.<=3.", True)
        self.eq("2.>=3.", False)

    # TODO: NaN

    def test_illegal_comparison(self):
        for op in all_binops:
            self.ex(f"2{op}True", AkiTypeError)


class TestBindings(BaseTest):
    def test_pemdas(self):
        self.eq("2+2+2", 6)
        self.eq("(2+2)+2", 6)
        self.eq("(4/2)+2", 4)
        self.eq("4/2+2", 4)
        self.eq("4/(2+2)", 1)
