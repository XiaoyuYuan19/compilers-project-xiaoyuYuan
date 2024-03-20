import unittest

from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck
from src.compiler.types import Int, Bool, Unit


def assert_fails_typecheck(code: str) -> None:
    failed = False
    expr = parse(tokenize(code))
    try:
        typecheck(expr)
    except Exception:
        failed = True
    assert failed, f"Type-checking succeeded for: {code}"

class MyTestCase(unittest.TestCase):
    def test_something(self):
        assert typecheck(parse(tokenize("1 + 2 "))) == Int
        assert typecheck(parse(tokenize("1 + 2 < 3"))) == Bool

        assert_fails_typecheck(" ( 1 < 2 ) + 3")
    def test_type_check_if_then_else(self):
        assert typecheck(parse(tokenize("if 1 < 2 then 3"))) == Unit
        assert typecheck(parse(tokenize("if 1 < 2 then 3 else 4"))) == Int

        assert_fails_typecheck("if 1 then 3 else 4 < 5")
        assert_fails_typecheck("if 1 < 2 then 3 else 4 < 5")


if __name__ == '__main__':
    unittest.main()
