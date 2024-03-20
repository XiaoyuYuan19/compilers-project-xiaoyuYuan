from src.compiler import ast
from src.compiler.types import Type, Int, Bool, Unit


def typecheck(node: ast.Expression) -> Type:
    match node:
        case ast.Literal():
            if isinstance(node.value, int):
                return Int
            else:raise Exception(f'Don\'t know type of literal: "{node.value}"')

        case ast.BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.op in ['+','-','*','/']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expected 2 Ints, got {t1} and {t2}.')
                return Int
            elif node.op in ['<']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Operator {node.op} expected 2 Ints, got {t1} and {t2}.')
                return Bool
            else:
                raise Exception(f'Unknown operatior {node.op}.')

        case ast.IfExpression():
            t1 = typecheck(node.cond)
            if t1 is not Bool:
                raise Exception(f'"if" condition was {t1}')
            t2 = typecheck(node.then_clause)
            if node.else_clause is None:
                return Unit
            else:
                t3 = typecheck(node.else_clause)
                if t2 != t3:
                    raise Exception(f'"then" and "else" had different types: {t2} and {t3}')
                return t2

        case _:
            raise Exception(f'Unsupported AST node: {node}.')
