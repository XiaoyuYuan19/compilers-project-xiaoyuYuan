import unittest

from src.model import ast
from src.model.SymTab import SymTab, add_builtin_symbols
from src.compiler.interpreter import interpret, BreakException
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)
    def test_interpret_op(self):
        assert interpret(parse(tokenize("1 + 2")),self.symtab) == 3
        assert interpret(parse(tokenize("1 + 2 * 3")),self.symtab) == 7
    def test_interpret_prior(self):
        assert interpret(parse(tokenize("( 1 + 2 ) * 3")),self.symtab) == 9
    def test_interprete_if_then_else(self):
        assert interpret(parse(tokenize("if 1 < 2 then 3 else 4")),self.symtab) == 3
        assert interpret(parse(tokenize("if 2 < 1 then 3 else 4")),self.symtab) == 4
        assert interpret(parse(tokenize("10 + if 2 < 1 then 3 else 4")),self.symtab) == 14
    def test_arithmetic_operations(self):
        # 测试基本的算术运算
        source_code = "3 + 4 * 2 - 1"
        tokens = tokenize(source_code)
        ast = parse(tokens)
        result = interpret(ast, self.symtab)
        self.assertEqual(result, 10)

    def test_variable_declaration_and_use(self):
        # 测试变量声明和使用
        source_code = "{ var x = 5; x * 2 }"
        tokens = tokenize(source_code)
        ast = parse(tokens)
        result = interpret(ast, self.symtab)
        self.assertEqual(result, 10)

    def test_conditional_logic(self):
        # 测试条件逻辑
        source_code = "if true then 42 else 0"
        tokens = tokenize(source_code)
        ast = parse(tokens)
        result = interpret(ast, self.symtab)
        self.assertEqual(result, 42)

    def test_arithmetic_operators(self):
        tests = [
            ("1 + 2", 3),
            ("4 - 2", 2),
            ("6 * 2", 12),
            ("8 / 2", 4),
            ("10 % 3", 1),
        ]
        for source_code, expected in tests:
            with self.subTest(source_code=source_code):
                block = parse(tokenize(source_code))
                result = interpret(block, self.symtab)
                print(result)
                self.assertEqual(result, expected)

    def test_comparison_operators(self):
        tests = [
            ("1 == 1", True),
            ("2 != 1", True),
            ("3 < 4", True),
            ("5 <= 5", True),
            ("6 > 5", True),
            ("7 >= 7", True),
        ]
        for source_code, expected in tests:
            with self.subTest(source_code=source_code):
                block = parse(tokenize(source_code))
                result = interpret(block, self.symtab)
                self.assertEqual(result, expected)

    def test_logical_operators(self):
        tests = [
            ("true and false", False),
            ("true or false", True),
            ("not true", False),
        ]
        for source_code, expected in tests:
            with self.subTest(source_code=source_code):
                block = parse(tokenize(source_code))
                result = interpret(block, self.symtab)
                # print(result)
                self.assertEqual(result, expected)

    def test_variable_scope(self):
        source_code = "{var x = 10; {var x = 20;} x}"
        block = parse(tokenize(source_code))
        result = interpret(block, self.symtab)
        self.assertEqual(result, 10)

    def test_if_statement(self):
        tests = [
            ("if true then 42 else 0", 42),
            ("if false then 42 else 0", 0),
        ]
        for source_code, expected in tests:
            with self.subTest(source_code=source_code):
                block = parse(tokenize(source_code))
                result = interpret(block, self.symtab)
                self.assertEqual(result, expected)

    def test_while_loop(self):
        source_code = "{var x = 0; while x < 5 do  x = x + 1;  x}"
        block = parse(tokenize(source_code))
        print(block)
        result = interpret(block, self.symtab)
        self.assertEqual(result, 5)

    def test_short_circuit_logic(self):
        # 测试'or'的短路行为
        source_code = """{
        var evaluated_right_hand_side = false;
        true or { evaluated_right_hand_side = true; true };
        evaluated_right_hand_side}# expect be false
        """
        block = parse(tokenize(source_code))
        result = interpret(block, self.symtab)
        self.assertEqual(result, False)

        # 测试'and'的短路行为
        source_code = """{
        var evaluated_right_hand_side = false;
        false and { evaluated_right_hand_side = true; false };
        evaluated_right_hand_side} #应该为false
        """
        block = parse(tokenize(source_code))
        result = interpret(block, self.symtab)
        self.assertEqual(result, False)

    def test_if_then_else(self):
        source_code = """{
        var x = 10;
        if x > 5 then { x = 2; } else { x = 3; }
        x }  # 应该为2
        """
        block = parse(tokenize(source_code))
        result = interpret(block, self.symtab)
        self.assertEqual(result, 2)

class test_interprete_funcdel(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)
    def test_function_definition(self):
        module_code = """
        fun square(x: Int): Int {
            return x * x;
        }
        square(2)
        """
        tokens = tokenize(module_code)
        module = parse(tokens)
        print(module)
        result = interpret(module, self.symtab)
        self.assertEqual(result, 4)

    def test_function_definition_and_call(self):
        source_code = """
        fun square(x: Int): Int {
            return x * x;
        }
        fun add(a: Int, b: Int): Int {
            return a + b;
        }
        square(add(2, 3))
        """
        result = interpret(parse(tokenize(source_code)), self.symtab)
        self.assertEqual(result, 25)

    def test_module_with_functions(self):
        source_code = """
        fun double(x: Int): Int {
            return x * 2;
        }
        double(4)
        """
        result = interpret(parse(tokenize(source_code)), self.symtab)
        self.assertEqual(result, 8)

class TestInterpreterFunctions(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)
    def test_function_call(self):
        source_code = """
        fun add(x: Int, y: Int): Int {
            return x + y;
        }
        add(2, 3)
        """
        module = parse(tokenize(source_code))
        result = interpret(module, self.symtab)
        self.assertEqual(result, 5)

    def test_function_definition_and_Recursion (self):
        source_code = """
        fun square(x: Int): Int {
            return x * x;
        }
        fun square_sum(a: Int, b: Int): Int {
            return square(a) + square(b);
        }
        square_sum(2,3)
        """
        result = interpret(parse(tokenize(source_code)), self.symtab)
        self.assertEqual(result, 13)

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()

    def test_break_in_loop(self):
        loop = ast.WhileExpr(
            condition=ast.Literal(True),  # 无限循环条件
            body=ast.Block(expressions=[ast.Break()], result_expression=None)  # 循环体中立即 break
        )
        # 期望循环能够被 break 打断，不抛出异常
        try:
            interpret(loop, self.symtab)
        except BreakException:
            self.fail("BreakException should not escape the loop.")


if __name__ == '__main__':
    unittest.main()
