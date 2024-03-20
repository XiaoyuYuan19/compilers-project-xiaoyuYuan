from src.compiler import ast, types
from src.compiler.SymTab import SymTab
from src.compiler.types import Type, Int, Bool, Unit, FunctionType

def typecheck_var_decl(node: ast.VarDecl, symtab: SymTab) -> types.Type:
    value_type = typecheck(node.value, symtab)
    annotated_type = 0
    if node.type_annotation:
        # Map AST type expression to type checker's type
        annotated_type = node.type_annotation
        if type(value_type) != type(annotated_type):
            raise TypeError(f"Type of initializer does not match variable type annotation in declaration of '{node.name}'")
    symtab.define_variable(node.name,node.value, annotated_type)
    return types.Unit()

def map_ast_type_expr_to_type(type_expr: ast.Expression) -> types.Type:
    if str(type_expr) == 'Bool':
        return types.Bool()
    elif str(type_expr) == 'Int':
        return types.Int()
    else:
        raise Exception("Unknown type expression")

def typecheck(node: ast.Expression, symtab: SymTab) -> Type:
    match node:
        # First bool, then True
        case bool():
            return types.Bool()
        case int():
            return types.Int()
        case ast.Literal(value=bool()):
            return types.Bool()
        case ast.Literal(value=int()):
            return types.Int()
        case ast.Identifier():
            # print('idn',node)
            var_type = symtab.lookup_variable_type(node.name)
            if var_type is None:
                raise TypeError(f"Variable '{node.name}' is not defined")
            return var_type

        case ast.UnaryOp():
            operand_type = typecheck(node.operand, symtab)
            op_type = symtab.lookup_variable_type(f"unary_{node.operator}")

            if isinstance(op_type, FunctionType) and str(operand_type) == str(op_type.param_types[0]):
                return op_type.return_type
            else:
                raise TypeError(f"Unsupported unary operation: {node.operator} for {operand_type}")

        case ast.BinaryOp():
            if node.op == "=":
                if isinstance(node.left, ast.Identifier):
                    value = typecheck(node.right, symtab)
                    # print('ini',symtab.lookup_variable_type(node.left.name),value)
                    if str(symtab.lookup_variable_type(node.left.name)) != str(value):
                        # if not isinstance(symtab.lookup_variable_type(node.left.name),value):
                        raise TypeError("Left side of assignment must be isinstance with right side")
                    symtab.update_variable(node.left.name, value)
                    return value
                else:
                    raise TypeError("Left side of assignment must be an identifier.")
            op_func = symtab.lookup_variable(node.op)
            op_type = symtab.lookup_variable_type(node.op)
            left_type = typecheck(node.left, symtab)
            right_type = typecheck(node.right, symtab)

            if isinstance(op_type, FunctionType):
                # Validate operand types
                if [type(left_type), type(right_type)] != [type(t) for t in op_type.param_types]:
                    raise TypeError(f"Operand type mismatch for operator '{node.op}'")
                return op_type.return_type

            else:
                raise TypeError(f"Operator '{node.op}' not defined")
        case ast.IfExpression():

            cond_type = typecheck(node.cond, symtab)

            # print('in if', node.condition,cond_type)
            if not isinstance(cond_type, types.Bool):
                raise TypeError("Condition in 'if' must be a Bool")
            then_type = typecheck(node.then_clause, symtab)
            if node.else_clause is None:
                else_type = None
            #
            #     # if not isinstance(then_type, types.Unit):
            #     #     raise TypeError("Then branch of 'if' without 'else' must not produce a value")
            #     return types.Unit()
            else:
                else_type = typecheck(node.else_clause, symtab)
                if type(then_type) != type(else_type):
                    raise TypeError("'then' and 'else' branches must have the same type")
            return then_type

        case ast.FunctionCall():
            func_type = symtab.lookup_variable_type(node.name)
            if not isinstance(func_type, FunctionType):
                raise TypeError(f"{node.name} is not a function")

            if len(node.arguments) != len(func_type.param_types):
                raise TypeError("Incorrect number of arguments")

            for arg, param_type in zip(node.arguments, func_type.param_types):
                arg_type = typecheck(arg, symtab)
                if type(arg_type) != type(param_type):
                    raise TypeError("Argument type mismatch")

            return func_type.return_type
        case ast.Block():
            symtab.enter_scope()

            # for expr in node.expressions[:-1]:
            for expr in node.expressions:
                typecheck(expr, symtab)  # Discard types of non-final expressions
            result_type = types.Unit() if not node.result_expression else typecheck(node.result_expression, symtab)
            symtab.leave_scope()
            return result_type

        case ast.VarDecl():
            return typecheck_var_decl(node, symtab)

        case ast.WhileExpr():
            cond_type = typecheck(node.condition, symtab)
            print('con', cond_type)
            if not isinstance(cond_type, types.Bool):
                raise TypeError("Condition in 'while' must be a Bool")
            body_type = typecheck(node.body, symtab)
            print('body', body_type)
            # if not isinstance(body_type, types.Unit):
            #     raise TypeError("Body of 'while' must not produce a value")
            return types.Unit()

        case ast.Module():
            for func in node.functions:
                symtab.define_variable(func.name, func.body, typecheck(func,symtab))
                print(symtab.lookup_variable(func.name))

        case ast.FunctionDef():
            params_types = []
            for p in node.params:
                params_types.append(p[1])
            return FunctionType(params_types,node.return_type)

        case ast.Break(value):
            if value:
                value_type = typecheck(value, symtab)
                # Ensure that the value_type matches the expected return type of the loop
            return Unit()

        case ast.Continue():
            return Unit()

        case ast.AddressOf(expr):
            expr_type = typecheck(expr, symtab)
            return ast.PointerType(expr_type)
        case ast.Dereference(expr):
            expr_type = typecheck(expr, symtab)
            if isinstance(expr_type, ast.PointerType):
                return expr_type.base_type
            else:
                raise TypeError("Dereference of a non-pointer type")

        case _:
            raise Exception(f'Unsupported AST node: {node}.')
