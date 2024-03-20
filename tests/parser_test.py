import unittest


from src.model import ast
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize
from src.model.types import Int


class MyTestCase(unittest.TestCase):
    def test_parser(self):
        assert parse(tokenize('1')).expression == ast.Literal(1)
        assert parse(tokenize(" 1 + 2 ")).expression == ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.Literal(2),
        )
    def test_parser_iteration(self):
        assert parse(tokenize("1 + 2 - 3")).expression == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='+',
                right=ast.Literal(2),
            ),
            op='-',
            right=ast.Literal(3),
        )
    def test_parser_ops(self):
        assert parse(tokenize("1 + 2 * 3")).expression == ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='*',
                right=ast.Literal(3),
            ),
        )
        assert parse(tokenize("1 * 5 + 2 * 3")).expression == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='*',
                right=ast.Literal(5),
            ),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='*',
                right=ast.Literal(3),
            ),
        )
    def test_parser_brace(self):
        assert parse(tokenize("1 * ( 2 + 3 )")).expression == ast.BinaryOp(
            left=ast.Literal(1),
            op='*',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            )
        )
        assert parse(tokenize(" ( 2 + 3 )+ 4 ")).expression == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            ),
            op='+',
            right=ast.Literal(4)
        )
        assert parse(tokenize(" 1 * ( 2 + 3 ) / 4 ")).expression == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='*',
                right=ast.BinaryOp(
                    left=ast.Literal(2),
                    op='+',
                    right=ast.Literal(3),
                ),
            ),
            op='/',
            right=ast.Literal(4)
        )

    def test_parse_compare(self):
        assert parse(tokenize("1 < ( 2 + 3 )")).expression == ast.BinaryOp(
            left=ast.Literal(1),
            op='<',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            )
        )
    def test_parse_if_then_else(self):
        assert parse(tokenize("if 1 then 2")).expression == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.Literal(2),
            else_clause=None,
        )
        assert parse(tokenize("if 1 then 2 else 3")).expression == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.Literal(2),
            else_clause=ast.Literal(3),
        )
        assert parse(tokenize("if 1 then 2 * 3 else 3 / 4")).expression == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.BinaryOp(ast.Literal(2),'*',ast.Literal(3)),
            else_clause=ast.BinaryOp(ast.Literal(3),'/',ast.Literal(4)),
        )
        assert parse(tokenize("0 + if 1 then 2 else 3")).expression == ast.BinaryOp(
            left=ast.Literal(0),
            op='+',
            right=ast.IfExpression(
                cond=ast.Literal(1),then_clause=ast.Literal(2),else_clause=ast.Literal(3),
                )
        )
        assert parse(tokenize("0 + if 1 then 2 else 3 + 2")).expression == ast.BinaryOp(
            left=ast.Literal(0),
            op='+',
            right=ast.IfExpression(
                cond=ast.Literal(1),then_clause=ast.Literal(2),else_clause=ast.BinaryOp(
                    left=ast.Literal(3),op='+',right=ast.Literal(2)),
                )
        )

    def test_parse_right_associativity(self):
        assert parse(tokenize("2 + 3 + 4"),right_associative=True).expression == ast.BinaryOp(
            left=ast.Literal(2),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(3),
                op='+',
                right=ast.Literal(4),
            )
        )

    def test_parse_function_call(self):
        tokens = tokenize("f ( x, y + z )")
        parsed_expression = parse(tokens)
        assert parsed_expression.expression == ast.FunctionCall(
            name='f',
            arguments=[
                ast.Identifier(name='x'),
                ast.BinaryOp(
                    left=ast.Identifier(name='y'),
                    op='+',
                    right=ast.Identifier(name='z')
                )
            ]
        )

    def test_parse_block(self):
        tokens = tokenize("{ f(a); x = y; f(x) }")
        parsed_block = parse(tokens)
        print(parsed_block)

        assert parsed_block.expression == ast.Block(
            expressions=[
                ast.FunctionCall(
                    name='f',
                    arguments=[ast.Identifier(name='a')]
                ),
                ast.BinaryOp(
                    left=ast.Identifier(name='x'),
                    op='=',
                    right=ast.Identifier(name='y')
                )
            ],
            result_expression=ast.FunctionCall(
                name='f',
                arguments=[ast.Identifier(name='x')]
            )
        )

class test_parser_funcdel(unittest.TestCase):
    def test_parse_function_definition(self):
        source_code = """
        fun square(x: Int): Int {
            return x * x;
        }
        """
        tokens = tokenize(source_code)
        parsed_module = parse(tokens)
        print(parsed_module)
        parsed_module = ast.Module(functions=
        ast.FunctionDef(
            name='square',
            params=[('x', Int())],
            return_type=Int(),
            body=ast.Block(expressions=[],
                       result_expression=ast.BinaryOp(left=ast.Identifier(name='x'),
                                                  op='*',
                                                  right=ast.Identifier(name='x'))
                           )
        ),
            expression=None)

    def test_parse_module_with_functions_and_expression(self):
        source_code = """
        fun square(x: Int): Int {
            return x * x;
        }
    
        fun print_int_twice(x: Int) {
            print_int(x);
            print_int(x);
        }
    
        print_int_twice(square(3))
        """
        tokens = tokenize(source_code)
        parsed_module = parse(tokens)
        print(parsed_module)

class TestPointerFeatures_parse(unittest.TestCase):
    def test_token_dereference(self):
        tokens = tokenize("{ var x: Int* = &y; }")
        print(tokens)
        par = parse(tokens)
        assert par == ast.Module(functions=[],
                                 expression=ast.Block(
                                     expressions=[ast.VarDecl(name='x', value=ast.Identifier(name='y'),
                                                              type_annotation=ast.PointerType(base_type='Int'))],
                                                  result_expression=None))


if __name__ == '__main__':
    unittest.main()
