import unittest


from src.compiler import ast
from src.compiler.parser import parse
from src.compiler.tokenizer import tokenize


class MyTestCase(unittest.TestCase):
    def test_parser(self):
        assert parse(tokenize('1')) == ast.Literal(1)
        print(parse(tokenize('1')))
        assert parse(tokenize(" 1 + 2 ")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.Literal(2),
        )
    def test_parser_iteration(self):
        assert parse(tokenize("1 + 2 - 3")) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(1),
                op='+',
                right=ast.Literal(2),
            ),
            op='-',
            right=ast.Literal(3),
        )
    def test_parser_ops(self):
        assert parse(tokenize("1 + 2 * 3")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='*',
                right=ast.Literal(3),
            ),
        )
        assert parse(tokenize("1 * 5 + 2 * 3")) == ast.BinaryOp(
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
        assert parse(tokenize("1 * ( 2 + 3 )")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='*',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            )
        )
        assert parse(tokenize(" ( 2 + 3 )+ 4 ")) == ast.BinaryOp(
            left=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            ),
            op='+',
            right=ast.Literal(4)
        )
        assert parse(tokenize(" 1 * ( 2 + 3 ) / 4 ")) == ast.BinaryOp(
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
        assert parse(tokenize("1 < ( 2 + 3 )")) == ast.BinaryOp(
            left=ast.Literal(1),
            op='<',
            right=ast.BinaryOp(
                left=ast.Literal(2),
                op='+',
                right=ast.Literal(3),
            )
        )
    def test_parse_if_then_else(self):
        assert parse(tokenize("if 1 then 2")) == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.Literal(2),
            else_clause=None,
        )
        assert parse(tokenize("if 1 then 2 else 3")) == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.Literal(2),
            else_clause=ast.Literal(3),
        )
        assert parse(tokenize("if 1 then 2 * 3 else 3 / 4")) == ast.IfExpression(
            cond=ast.Literal(1),
            then_clause=ast.BinaryOp(ast.Literal(2),'*',ast.Literal(3)),
            else_clause=ast.BinaryOp(ast.Literal(3),'/',ast.Literal(4)),
        )
        assert parse(tokenize("0 + if 1 then 2 else 3")) == ast.BinaryOp(
            left=ast.Literal(0),
            op='+',
            right=ast.IfExpression(
                cond=ast.Literal(1),then_clause=ast.Literal(2),else_clause=ast.Literal(3),
                )
        )
        assert parse(tokenize("0 + if 1 then 2 else 3 + 2")) == ast.BinaryOp(
            left=ast.Literal(0),
            op='+',
            right=ast.IfExpression(
                cond=ast.Literal(1),then_clause=ast.Literal(2),else_clause=ast.BinaryOp(
                    left=ast.Literal(3),op='+',right=ast.Literal(2)),
                )
        )

    def test_parse_right_associativity(self):
        assert parse(tokenize("2 + 3 + 4"),right_associative=True) == ast.BinaryOp(
            left=ast.Literal(2),
            op='+',
            right=ast.BinaryOp(
                left=ast.Literal(3),
                op='+',
                right=ast.Literal(4),
            )
        )

    def test_parse_function_call(self):
        # 假设tokenize和Token类已正确处理并识别函数调用和参数
        tokens = tokenize("f ( x, y + z )")
        parsed_expression = parse(tokens)
        assert parsed_expression == ast.FunctionCall(
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
        assert parsed_block == ast.Block(
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

if __name__ == '__main__':
    unittest.main()
