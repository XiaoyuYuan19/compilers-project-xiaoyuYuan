import unittest

from src.compiler.assembler import assemble
from src.compiler.assembly_generator import generate_assembly
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_load_bool_const_true(self):
        source_code = "1 + 2"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        assembly_code = generate_assembly(ir_instructions)
        print(assembly_code)
    def test_if_then_else(self):
        source_code = "if 1 < 2 then 2 + 2 else 3 * 3"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        assembly_code = generate_assembly(ir_instructions)
        print(assembly_code)


if __name__ == '__main__':
    unittest.main()
