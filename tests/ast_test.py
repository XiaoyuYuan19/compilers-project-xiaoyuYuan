import unittest

from src.model import ast
from src.model.ast import Break, Continue, WhileExpr, Literal
from src.model.types import Int


class TestASTNodes(unittest.TestCase):
    def test_break_node(self):
        # 测试不带返回值的 break
        break_node = Break()
        self.assertIsNone(break_node.value)

        # 测试带返回值的 break
        break_with_value = Break(value=Literal(42))
        self.assertIsNotNone(break_with_value.value)
        self.assertEqual(break_with_value.value.value, 42)

    def test_continue_node(self):
        continue_node = Continue()
        self.assertIsInstance(continue_node, Continue)


if __name__ == '__main__':
    unittest.main()
