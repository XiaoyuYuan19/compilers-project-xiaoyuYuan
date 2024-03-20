
from src.compiler.tokenizer import Token
from src.compiler import ast

def parse(tokens: list[Token], right_associative=False) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='')

    def consume(expected: str | None = None) -> Token:
        token = peek()
        if expected is not None and token.text != expected:
            raise Exception(f'Expected "{expected}", got "{token.text}"')
        nonlocal pos
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text))
        else:
            raise Exception(f'Excepted literal, found "{token.text}"')

    def parse_expression() -> ast.Expression:

        if right_associative:
            return parse_expression_right_assoc()
        else:
            left = parse_polynomial() # implement more operator
            while peek().text in ['<']:
                op_token = consume()
                right = parse_polynomial()
                left = ast.BinaryOp(left,op_token.text,right)
            return left

    def parse_polynomial() -> ast.Expression:
        left = parse_term() # implement more operator
        while peek().text in ['+','-']:
            op_token = consume()
            right = parse_term()
            left = ast.BinaryOp(left,op_token.text,right)
        return left

    # Implement more operator
    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ['*','/']:
            op_token = consume()
            right = parse_factor()
            left = ast.BinaryOp(left,op_token.text,right)
        return left

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized_expression()
        elif peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            return parse_literal()
        else:
            raise Exception(f'Unexpected "{peek().text}')

    def parse_if_expression() -> ast.Expression:
        consume('if')
        cond = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None
        return ast.IfExpression(cond, then_clause, else_clause)

    def parse_parenthesized_expression() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_expression_right_assoc() -> ast.Expression:
        left = parse_term()
        if peek().type == 'operator':
            operator_token = consume()
            # 递归调用parse_expression_right_assoc以保证右关联性
            right = parse_expression_right_assoc()
            return ast.BinaryOp(left, operator_token.text, right)
        return left

    return parse_expression()