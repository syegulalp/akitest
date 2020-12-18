from utils import BaseTest
from errors import AkiTypeException


class TestBaseValues(BaseTest):
    def test_boolean(self):
        self.eq("True", True)
        self.eq("-False", True)
        self.eq("-True", False)

    def test_integer(self):
        self.eq("2", 2)
        self.eq("-2", -2)


class TestBaseOperations(BaseTest):
    def test_int_add(self):
        self.eq("2+2", 4)
        self.eq("-2+4", 2)

    def test_int_sub(self):
        self.eq("2-2", 0)
        self.eq("2-4", -2)


class TestBaseComparisons(BaseTest):
    def test_bool_eq_comp(self):
        self.eq("True==True", True)
        self.eq("False==False", True)

    def test_bool_neq_comp(self):
        self.eq("True!=False", True)
        self.eq("True!=True", False)

    def test_int_eq_comp(self):
        self.eq("2==2", True)
        self.eq("2==4", False)

    def test_int_neq_comp(self):
        self.eq("2!=2", False)
        self.eq("2!=4", True)

    def test_illegal_comparison(self):
        self.ex("2==True", AkiTypeException)
        self.ex("2!=True", AkiTypeException)
