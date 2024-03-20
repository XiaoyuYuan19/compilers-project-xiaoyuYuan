from typing import Any

from src.model import ast
from src.model.SymTab import SymTab
from src.compiler.type_checker import typecheck

Value = int | bool | None

class BreakException(Exception):
    def __init__(self, value=None):
        self.value = value

class ContinueException(Exception):
    pass

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
            # Variable declarations should only define new variables in the current scope
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

        case ast.WhileExpr(condition, body):
            while True:
                try:
                    cond_value = interpret(condition, symtab)
                    if not cond_value:
                        break
                    try:
                        interpret(body, symtab)
                    except ContinueException:
                        continue
                except BreakException as e:
                    # If break carries a return value, the return value is processed
                    if e.value is not None:
                        return e.value
                    break
            return None

        case ast.Module(functions, expression):
            # First process all function definitions, adding them to the symbol table
            for func in functions:
                # The function is bound to a special handler function for subsequent calls
                symtab.define_variable(func.name, (func, "function"), func.return_type)
                print(symtab.lookup_variable(func.name))
            # Process top-level expressions
            if expression is not None:
                return interpret(expression, symtab)
            return None

        case ast.FunctionDef(name, params, return_type, body):
            # FunctionDef nodes should be processed during Module processing and should not be called directly by interpret
            raise RuntimeError(f"Unexpected FunctionDef node in interpret: {name}")

        case ast.FunctionCall(name, arguments):
            func, func_type = symtab.lookup_variable(name)
            if func_type != "function":
                raise TypeError(f"{name} is not a function")
            # Create a new scope for function calls
            symtab.enter_scope()
            # Bind the parameter value to the new scope
            for param, arg in zip(func.params, arguments):
                arg_value = interpret(arg, symtab)
                symtab.define_variable(param[0], arg_value, arg)
            # Execute function body
            result = interpret(func.body, symtab)
            symtab.leave_scope()
            return result

        case ast.Break(value):
            # if break has value, return optional value
            raise BreakException(interpret(value, symtab) if value else None)
        case ast.Continue():
            raise ContinueException()

        case _:
            raise Exception(f'Unsupported AST node: "{node}"')
