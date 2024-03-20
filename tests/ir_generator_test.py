import unittest

from src.compiler import ast
from src.compiler.ast import Continue, Break
from src.compiler.ir import Call, LoadIntConst, IRvar, Label, Jump, Copy, CondJump, LoadBoolConst
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_binary_op_addition(self):
        source_code = "1"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1'))]

    def test_binary_op_addition(self):
        source_code = "1 + 2"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))]

        source_code = "1 + 2 * 3"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   LoadIntConst(value=3, dest=IRvar('x3')),
                                   Call(fun=IRvar('*'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x4')], dest=IRvar('x5')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x5')], dest=IRvar('x6'))]

    def test_binary_if_then_else1(self):
        source_code = "if 1 < 2 then 3 else 4"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('<'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   CondJump(cond=IRvar('x3'), then_label=Label(name='L1'), else_label=Label(name='L2')),
                                   Label(name='L1'),
                                   LoadIntConst(value=3, dest=IRvar('x4')),
                                   Copy(source=IRvar('x4'), dest=IRvar('x5')),
                                   Jump(label=Label(name='L3')),
                                   Label(name='L2'),
                                   LoadIntConst(value=4, dest=IRvar('x6')),
                                   Copy(source=IRvar('x6'), dest=IRvar('x5')),
                                   Label(name='L3'),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x5')], dest=IRvar('x7'))]

    def test_binary_if_then_else2(self):
        source_code = "1 + if 2 < 3 then 4 * 5 else 6 * 7"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)

        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   LoadIntConst(value=3, dest=IRvar('x3')),
                                   Call(fun=IRvar('<'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   CondJump(cond=IRvar('x4'), then_label=Label(name='L1'), else_label=Label(name='L2')),
                                   Label(name='L1'),
                                   LoadIntConst(value=4, dest=IRvar('x5')),
                                   LoadIntConst(value=5, dest=IRvar('x6')),
                                   Call(fun=IRvar('*'), args=[IRvar('x5'), IRvar('x6')], dest=IRvar('x7')),
                                   Copy(source=IRvar('x7'), dest=IRvar('x8')),
                                   Jump(label=Label(name='L3')),
                                   Label(name='L2'),
                                   LoadIntConst(value=6, dest=IRvar('x9')),
                                   LoadIntConst(value=7, dest=IRvar('x10')),
                                   Call(fun=IRvar('*'), args=[IRvar('x9'), IRvar('x10')], dest=IRvar('x11')),
                                   Copy(source=IRvar('x11'), dest=IRvar('x8')),
                                   Label(name='L3'),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x8')], dest=IRvar('x12')),
                                   Call(fun=IRvar('print_int'),args=[IRvar('x12')], dest=IRvar('x13'))]

    def test_binary_if_then_else3(self):
        source_code = "1 + if 2 < 3 then 4 * 5 "
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        print(ir_instructions)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   LoadIntConst(value=3, dest=IRvar('x3')),
                                   Call(fun=IRvar('<'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   CondJump(cond=IRvar('x4'), then_label=Label(name='L1'), else_label=Label(name='L2')),
                                   Label(name='L1'),
                                   LoadIntConst(value=4, dest=IRvar('x5')),
                                   LoadIntConst(value=5, dest=IRvar('x6')),
                                   Call(fun=IRvar('*'), args=[IRvar('x5'), IRvar('x6')], dest=IRvar('x7')),
                                   Copy(source=IRvar('x7'), dest=IRvar('x8')),
                                   Jump(label=Label(name='L2')),
                                   Label(name='L2'),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x8')], dest=IRvar('x9')),
                                   Call(fun=IRvar('print_int'),args=[IRvar('x9')], dest=IRvar('x10'))]

class IRGeneratorTestCase(unittest.TestCase):
    def test_literal_int(self):
        source_code = "42"

        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)

        for i in ir_instructions:
            print(i)
        self.assertIsInstance(ir_instructions[0], LoadIntConst)
        self.assertEqual(ir_instructions[0].value, 42)

    def test_literal_bool(self):
        source_code = "true"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=True, dest=IRvar('x1')),
                                   Call(fun=IRvar('print_bool'), args=[IRvar('x1')], dest=IRvar('x2'))]

    def test_binary_op_addition(self):
        source_code = "1 + 2"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x4'))]

    def test_var_decl_with_assignment(self):
        source_code = "{ var x: Int = 42 ; x}"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [Copy(source=42, dest=IRvar('x1')),
                                   Copy(source=IRvar('x1'), dest=IRvar('x2')),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x2')], dest=IRvar('x3'))]

    def test_if_true_then_42_else_43(self):
        source_code = "if true then 42 else 43"
        ast_root = parse(tokenize(source_code))
        print(ast_root)
        ir_instructions = generate_ir(ast_root)
        print(ir_instructions)
        assert ir_instructions == [LoadIntConst(value=True, dest=IRvar('x1')),
                                   CondJump(cond=IRvar('x1'), then_label=Label(name='L1'),else_label=Label(name='L2')),
                                   Label(name='L1'),
                                   LoadIntConst(value=42, dest=IRvar('x2')),
                                   Copy(source=IRvar('x2'), dest=IRvar('x3')),
                                   Jump(label=Label(name='L3')),
                                   Label(name='L2'),
                                   LoadIntConst(value=43, dest=IRvar('x4')),
                                   Copy(source=IRvar('x4'), dest=IRvar('x3')),
                                   Label(name='L3'),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x3')], dest=IRvar('x5'))]


class TestIRGeneratorScopes(unittest.TestCase):
    def test_nested_scope_var_decl_with_assignment(self):

        source_code = "{ var x: Int = 42 ; { var x: Int = 1 ;} x}"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions ==[Copy(source=42, dest=IRvar('x1')),
                                  Copy(source=1, dest=IRvar('x2')),
                                  Copy(source=IRvar('x3'), dest=IRvar('x4')),
                                  Call(fun=IRvar('print_int'), args=[IRvar('x4')], dest=IRvar('x5'))]

class TestIRGenerator(unittest.TestCase):
    def test_binary_op_addition(self):
        source_code = """
        fun main() : Int {
            1 + 2
        }
        main()
        """
        module_ast = parse(tokenize(source_code))
        print(module_ast)
        ir_map = generate_ir(module_ast)
        assert ir_map == [LoadIntConst(value=1, dest=IRvar('x1')),
                          LoadIntConst(value=2, dest=IRvar('x2')),
                          Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                          Copy(source=None, dest=IRvar('x3')),
                          Call(fun=
                               ast.Block(expressions=[],
                                     result_expression=ast.BinaryOp(left=ast.Literal(value=1), op='+', right=ast.Literal(value=2))),
                                     args=[],
                                     dest=IRvar('x4')),
                          Call(fun=IRvar('print_int'), args=[IRvar('x4')], dest=IRvar('x5'))]


class TestIRGenerator(unittest.TestCase):
    def test_loop_with_break_and_continue(self):
        # Create a simple looping AST node with break and continue.
        loop = ast.WhileExpr(
            condition=ast.Literal(True),
            body=ast.Block(
                expressions=[Continue(), Break()],
                result_expression=None
            )
        )
        instructions = generate_ir(loop)

        # Check if the generated IR contains a jump instruction
        self.assertTrue(any(isinstance(inst, Jump) for inst in instructions))
        self.assertTrue(any(isinstance(inst, CondJump) for inst in instructions))
        # Add more assertions as needed to verify the correctness of the IR

if __name__ == '__main__':
    unittest.main()
