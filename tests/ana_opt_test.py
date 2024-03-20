import unittest

from src.compiler.ana_opt import split_into_basic_blocks, build_flowgraph
from src.model.ir import CondJump
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_case1(self):
        source_code = "1 + 2"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        # Assuming `instructions` is a list of your IR instructions
        basic_blocks = split_into_basic_blocks(ir_instructions)

        # Now you have a list of BasicBlocks, which you can further process
        for block in basic_blocks:
            print(f"Basic Block {block.label}:")
            for instruction in block.instructions:
                print(instruction)


    def test_case2(self):
        source_code = "if 1 < 2 then 2 + 2 else 3 * 3"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        # Assuming `instructions` is a list of your IR instructions
        basic_blocks = split_into_basic_blocks(ir_instructions)

        # Now you have a list of BasicBlocks, which you can further process
        for block in basic_blocks:
            print(f"Basic Block {block.label}:")
            for instruction in block.instructions:
                print(instruction)

    def test_basic_block_splitting(self):
        source_code = "if 1 < 2 then 2 + 2 else 3 * 3"
        tokens = tokenize(source_code)
        ast_root = parse(tokens)
        ir_instructions = generate_ir(ast_root)
        basic_blocks = split_into_basic_blocks(ir_instructions)

        # Now you have a list of BasicBlocks, which you can further process
        for block in basic_blocks:
            print(f"Basic Block {block.label}:")
            for instruction in block.instructions:
                print(instruction)

        # Example assertions (customize these based on the expected IR and basic blocks)
        self.assertEqual(len(basic_blocks), 4, "Expected 4 basic blocks")
        # Ensure the first block is the conditional check
        self.assertTrue(isinstance(basic_blocks[0].instructions[-1], CondJump), "Expected a conditional jump at the end of the first block")
        # Further assertions can be made based on the content of each block


class TestFlowGraph(unittest.TestCase):
    class TestFlowGraphWithNewCase(unittest.TestCase):
        def test_flowgraph_with_conditional_expression(self):
            source_code = """
        if 1 < 2 then
            x = 2 + 2;
        else
            x = 3 * 3;
        end
        """
            tokens = tokenize(source_code)
            ast_root = parse(tokens)
            ir_instructions = generate_ir(ast_root)
            basic_blocks = split_into_basic_blocks(ir_instructions)
            flowgraph = build_flowgraph(basic_blocks)



if __name__ == '__main__':
    unittest.main()
