from typing import Any

from src.compiler import ast
from src.compiler.SymTab import SymTab
from src.compiler.type_checker import typecheck

Value = int | bool | None

def interpret(node: ast.Expression, symtab: SymTab) -> Value:
    match node:
        case ast.Literal():
            return node.value

        case ast.BinaryOp():
            if node.op == "=":
                # 确保左侧是标识符
                if isinstance(node.left, ast.Identifier):
                    # 计算右侧表达式的值
                    value = interpret(node.right, symtab)
                    # 更新现有变量的值
                    symtab.update_variable(node.left.name, value)
                    return value
                else:
                    raise TypeError("Left side of assignment must be an identifier.")
            if node.op == 'and':
                left_value = interpret(node.left, symtab)
                if not left_value:  # 如果左侧为假，则不需要评估右侧
                    return False
                return interpret(node.right, symtab)
            elif node.op == 'or':
                left_value = interpret(node.left, symtab)
                if left_value:  # 如果左侧为真，则不需要评估右侧
                    return True
                return interpret(node.right, symtab)
            else:
                a: Value = interpret(node.left, symtab)
                b: Value = interpret(node.right, symtab)
                op_func = symtab.lookup_variable(node.op)
                return op_func(a, b)

        case ast.IfExpression():
            if interpret(node.cond,symtab):
                return interpret(node.then_clause,symtab)
            else:
                if node.else_clause is not None:
                    return interpret(node.else_clause,symtab)
                else:
                    return None

        case ast.UnaryOp():
            a: Value = interpret(node.operand, symtab)
            op_func = symtab.lookup_variable(f"unary_{node.operator}")
            return op_func(a)

        case ast.IfExpression():
            if interpret(node.condition,symtab):
                return interpret(node.then_branch,symtab)
            else:
                return interpret(node.else_branch,symtab)
        # Handle Literal, BinaryOp, and IfExpression as before
        # Add new cases for variable declaration and block expression


        case ast.VarDecl():
            # 变量声明应该只在当前作用域中定义新变量
            # value = interpret(node.value, symtab)
            symtab.define_variable(node.name, node.value,typecheck(node.value,symtab))
            return node.value

        case ast.Identifier():
            return symtab.lookup_variable(node.name)

        case ast.Block():
            symtab.enter_scope()
            for expr in node.expressions:
                interpret(expr, symtab)
            if node.result_expression is not None:
                result = interpret(node.result_expression, symtab)
            else:
                result = None
            symtab.leave_scope()
            return result

        case ast.WhileExpr():
            while interpret(node.condition, symtab):
                interpret(node.body, symtab)
            return None
        case _:
            raise Exception(f'Unsupported AST node: "{node}"')