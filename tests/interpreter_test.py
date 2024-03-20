import unittest

from src.compiler.interpreter import interpret
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_interpret_op(self):
        assert interpret(parse(tokenize("1 + 2"))) == 3
        assert interpret(parse(tokenize("1 + 2 * 3"))) == 7
    def test_interpret_prior(self):
        assert interpret(parse(tokenize("( 1 + 2 ) * 3"))) == 9
    def test_interprete_if_then_else(self):
        assert interpret(parse(tokenize("if 1 < 2 then 3 else 4"))) == 3
        assert interpret(parse(tokenize("if 2 < 1 then 3 else 4"))) == 4
        assert interpret(parse(tokenize("10 + if 2 < 1 then 3 else 4"))) == 14


if __name__ == '__main__':
    unittest.main()
