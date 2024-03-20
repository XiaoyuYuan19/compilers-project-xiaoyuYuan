import unittest

from src.model import types, ast
from src.model.SymTab import SymTab, add_builtin_symbols
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck
from src.model.types import Int, Bool, Unit


def assert_fails_typecheck(code: str) -> None:
    failed = False
    expr = parse(tokenize(code))
    try:
        typecheck(expr)
    except Exception:
        failed = True
    assert failed, f"Type-checking succeeded for: {code}"

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)
    def test_something(self):
        assert str(typecheck(parse(tokenize("1 + 2 ")).expression,self.symtab)) == 'Int'
        assert str(typecheck(parse(tokenize("1 + 2 < 3")).expression,self.symtab)) == 'Bool'

        assert_fails_typecheck(" ( 1 < 2 ) + 3")
    def test_type_check_if_then_else(self):
        # assert str(typecheck(parse(tokenize("if 1 < 2 then 3")),self.symtab)) == 'Unit'
        assert str(typecheck(parse(tokenize("if 1 < 2 then 3 else 4")).expression,self.symtab)) == 'Int'

        assert_fails_typecheck("if 1 then 3 else 4 < 5")
        assert_fails_typecheck("if 1 < 2 then 3 else 4 < 5")


class TestTypeChecker(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)

    def test_int_literal(self):
        node = parse(tokenize("42")).expression
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_bool_literal(self):
        node = parse(tokenize("True")).expression
        self.assertIsInstance(typecheck(node, self.symtab), types.Bool)

    def test_binary_op_ints(self):
        node = parse(tokenize("42 + 1")).expression
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_binary_op_type_mismatch(self):
        node = parse(tokenize("42 + True")).expression
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)

    def test_variable_lookup(self):
        self.symtab.define_variable("x", 10, types.Int())
        node = ast.Identifier(name="x")
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_if_expr(self):
        node = parse(tokenize("if True then 42 else 1")).expression
        self.assertIsInstance(typecheck(node, self.symtab), types.Int)

    def test_if_expr_type_mismatch(self):
        node = parse(tokenize("if True then 42 else False")).expression
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)


class TestUnitTypeChecker(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        # 添加内置符号，如果有的话

    # def test_if_then_no_else(self):
    #     source_code = "if true then { 1 }"
    #     node = parse(tokenize(source_code))
    #     print(typecheck(node, self.symtab))
    #     self.assertIsInstance(typecheck(node, self.symtab), Unit)


class TestTypeCheckerWithFunctionTypes(unittest.TestCase):
    def setUp(self):
        # 在每个测试用例开始前初始化符号表和添加内置符号
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)  # 确保你已经实现了这个函数

    def test_function_call_with_correct_types(self):
        source_code = "print_int(42)"
        node = parse(tokenize(source_code)).expression
        self.assertIsInstance(typecheck(node, self.symtab), Unit)

    def test_binary_op_with_correct_types(self):
        source_code = "42 + 1"
        node = parse(tokenize(source_code)).expression
        self.assertIsInstance(typecheck(node, self.symtab), Int)

    def test_function_call_with_incorrect_argument_type(self):
        source_code = "print_int(True)"
        node = parse(tokenize(source_code)).expression
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)

class TestUnaryOpTypeCheck(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        # 假设 add_builtin_symbols 已经定义，用于添加内置类型和函数
        add_builtin_symbols(self.symtab)

    def test_not_operator_with_bool(self):
        source_code = "not true"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)

    def test_not_operator_with_int(self):
        source_code = "not 42"
        node = parse(tokenize(source_code)).expression
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)

class TestBlockTypeCheck(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)

    def test_empty_block(self):
        source_code = "{}"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Unit)

    def test_block_with_last_expression_int(self):
        source_code = "{ true; 42 }"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Int)

    def test_block_with_last_expression_bool(self):
        source_code = "{ 42; false }"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)

    def test_block_with_variable_declaration(self):
        source_code = "{ var x : Bool = true; x }"
        self.symtab.define_variable("x","x", Bool())  # 在测试中显式定义变量类型
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Bool)


class TestBlockExpr(unittest.TestCase):
    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)

    def test_empty_block(self):
        source_code = "{}"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Unit)

    def test_block_with_multiple_statements(self):
        source_code = "{var x: Int = 42; var y: Bool = true; x }"
        node = parse(tokenize(source_code)).expression
        result_type = typecheck(node, self.symtab)
        self.assertIsInstance(result_type, Int)

    def test_block_with_type_mismatch(self):
        source_code = "{var z : Int = 42; z = true}"
        node = parse(tokenize(source_code)).expression
        print(node)
        with self.assertRaises(TypeError):
            typecheck(node, self.symtab)

class TestTypes(unittest.TestCase):
    def test_int_type(self):
        int_type = Int()
        self.assertIsInstance(int_type, Int)

    def test_bool_type(self):
        bool_type = Bool()
        self.assertIsInstance(bool_type, Bool)

    def test_unit_type(self):
        unit_type = Unit()
        self.assertIsInstance(unit_type, Unit)

    def test_type_equality(self):
        int_type1 = Int()
        int_type2 = Int()
        bool_type = Bool()
        self.assertEqual(str(int_type1), str(int_type2))
        self.assertNotEqual(int_type1, bool_type)

class test_type_check_funcdel(unittest.TestCase):

    def setUp(self):
        self.symtab = SymTab()
        add_builtin_symbols(self.symtab)
    # def test_function_call_type_check(self):
    #     source_code = """
    #             fun double(x: Int): Int {
    #                 return x * 2;
    #             }
    #             double(4)
    #             """
    #     result_type = typecheck(parse(tokenize(source_code)), self.symtab)
    #     self.assertEqual(result_type, Int())

if __name__ == '__main__':
    unittest.main()
