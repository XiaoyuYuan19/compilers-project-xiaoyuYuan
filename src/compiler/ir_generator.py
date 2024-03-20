from src.compiler import ast, ir
from src.compiler.ir import IRvar


def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:

    next_var_number = 1
    next_label_number = 1

    def new_var() -> IRvar:
        nonlocal next_var_number
        var = IRvar(f'x{next_var_number}')
        next_var_number += 1
        return var

    def new_label() -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(f'L{next_label_number}')
        next_label_number += 1
        return label


    instructions: list[ir.Instruction] = []
    def visit(node: ast.Expression) -> IRvar:
        match node:
            case ast.Literal():
                var = new_var()
                instructions.append(ir.LoadIntConst(node.value,var))
                return var

            case ast.BinaryOp():
                var_left = visit(node.left)
                var_right = visit(node.right)
                var_result = new_var()
                instructions.append(ir.Call(
                    fun=IRvar(node.op),
                    args=[var_left,var_right],
                    dest=var_result,
                ))
                return var_result

            case ast.IfExpression():
                if node.else_clause is None:
                    raise Exception('TODO: elseless ifs')
                else:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()

                    var_cond = visit(node.cond)
                    instructions.append(ir.CondJump(var_cond,l_then,l_else))

                    instructions.append(l_then)
                    var_result = visit(node.then_clause)
                    instructions.append(ir.Jump(l_end))

                    instructions.append(l_else)
                    var_else_result = visit(node.else_clause)
                    instructions.append(ir.Copy(var_else_result, var_result))

                    instructions.append(l_end)
                    return var_result
            case _:
                raise Exception(f"Unsupported ASTnode: {node}")

    var_result = visit(root_node)

    # TODO(me): handle boolean and unit results
    instructions.append(ir.Call(
        IRvar('print_int'),
        [var_result],
        new_var()
    ))


    return instructions