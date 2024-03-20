from typing import Any

from src.compiler import ast

Value = int | bool | None

def interpret(node: ast.Expression) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            a: Any = interpret(node.left)
            b: Any = interpret(node.right)
            if node.op == '+':
                return a + b
            elif node.op == '-':
                return a - b
            elif node.op == '*':
                return a * b
            elif node.op == '/':
                return a / b
            elif node.op == '<':
                return a < b
            else:
                raise Exception(f'Unsupported operator "{node.op}"')

        case ast.IfExpression():
            if interpret(node.cond):
                return interpret(node.then_clause)
            else:
                if node.else_clause is not None:
                    return interpret(node.else_clause)
                else:
                    return None

        case _:
            raise Exception(f'Unsupported AST node: "{node}"')