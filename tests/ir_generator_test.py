import unittest

from src.compiler.ir import Call, LoadIntConst, IRvar, Label, Jump, Copy, CondJump
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
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3'))]

        source_code = "1 + 2 * 3"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   LoadIntConst(value=3, dest=IRvar('x3')),
                                   Call(fun=IRvar('*'), args=[IRvar('x2'), IRvar('x3')], dest=IRvar('x4')),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x4')], dest=IRvar('x5'))]

    def test_binary_if_then_else(self):
        source_code = "if 1 < 2 then 3 else 4"
        ast_root = parse(tokenize(source_code))
        ir_instructions = generate_ir(ast_root)
        assert ir_instructions == [LoadIntConst(value=1, dest=IRvar('x1')),
                                   LoadIntConst(value=2, dest=IRvar('x2')),
                                   Call(fun=IRvar('<'), args=[IRvar('x1'), IRvar('x2')], dest=IRvar('x3')),
                                   CondJump(cond=IRvar('x3'), then_label=Label(name='L1'), else_label=Label(name='L2')),
                                   Label(name='L1'),
                                   LoadIntConst(value=3, dest=IRvar('x4')),
                                   Jump(label=Label(name='L3')),
                                   Label(name='L2'),
                                   LoadIntConst(value=4, dest=IRvar('x5')),
                                   Copy(source=IRvar('x5'), dest=IRvar('x4')),
                                   Label(name='L3'),
                                   Call(fun=IRvar('print_int'), args=[IRvar('x4')], dest=IRvar('x6'))]

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
                                   Jump(label=Label(name='L3')),
                                   Label(name='L2'),
                                   LoadIntConst(value=6, dest=IRvar('x8')),
                                   LoadIntConst(value=7, dest=IRvar('x9')),
                                   Call(fun=IRvar('*'), args=[IRvar('x8'), IRvar('x9')], dest=IRvar('x10')),
                                   Copy(source=IRvar('x10'), dest=IRvar('x7')),
                                   Label(name='L3'),
                                   Call(fun=IRvar('+'), args=[IRvar('x1'), IRvar('x7')], dest=IRvar('x11')),
                                   Call(fun=IRvar('print_int'),args=[IRvar('x11')], dest=IRvar('x12'))]


if __name__ == '__main__':
    unittest.main()
