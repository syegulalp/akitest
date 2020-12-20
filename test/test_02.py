from utils import BaseTest
from errors import AkiTypeException


class TestExpressions(BaseTest):
    def test_int_if(self):
        self.eq("if 2==2 1 else 0", 1)
        self.eq("if 2!=2 1 else 0", 0)

    def test_bool_if(self):
        self.eq("if True 1 else 0", 1)
        self.eq("if False 1 else 0", 0)

    def test_bool_coercion_when_clause(self):
        self.eq("when 32 1 else 0", 1)
        self.eq("when -32 1 else 0", 1)
        self.eq("when 0 1 else 0", 0)

    def test_float_coercion_if(self):
        self.eq("if 1.0 1 else 0", 1)
        self.eq("if 0.0 1 else 0", 0)
        self.eq("if 1.0_F 1 else 0", 1)
        self.eq("if 0.0_F 1 else 0", 0)

    def test_illegal_if(self):
        self.ex("if 2==True 1 else 0", AkiTypeException)
        self.ex("if 2==True 1 else False", AkiTypeException)
        self.ex("if 2==2 1 else False", AkiTypeException)

    def test_when_expr(self):
        self.eq("when 2==2 32 else 64", 32)
    
    def test_illegal_when(self):
        self.ex("when 2==2 1 else False", AkiTypeException)
        self.ex("when 32 1 else False", AkiTypeException)
