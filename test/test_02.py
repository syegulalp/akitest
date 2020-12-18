from utils import BaseTest
from errors import AkiTypeException


class TestExpressions(BaseTest):
    def test_int_if(self):
        self.eq("if 2==2 1 else 0", 1)
        self.eq("if 2!=2 1 else 0", 0)

    def test_bool_if(self):
        self.eq("if True 1 else 0", 1)
        self.eq("if False 1 else 0", 0)

    def test_illegal_if(self):
        self.ex("if 2==True 1 else 0", AkiTypeException)
        self.ex("if 2==True 1 else False", AkiTypeException)
        self.ex("if 2==2 1 else False", AkiTypeException)
