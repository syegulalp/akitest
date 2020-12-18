from utils import BaseTest


class TestBaseValues(BaseTest):
    def test_boolean(self):
        self.eq("True", True)

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
    def test_int_eq_comp(self):
        self.eq("2==2", True)
        self.eq("2==4", False)

    def test_int_neq_comp(self):
        self.eq("2!=2", False)
        self.eq("2!=4", True)
