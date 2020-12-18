from utils import BaseTest


class TestExpressions(BaseTest):
    def test_int_if(self):
        self.eq("if 2==2 1 else 0", 1)
