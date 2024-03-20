from src.compiler import ast, ir
from src.compiler.SymTab import SymTab, add_builtin_symbols
from src.compiler.ir import IRvar
from src.compiler.type_checker import typecheck
from src.compiler.types import Type, Unit, Int, Bool


def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:

    next_var_number = 1
    next_label_number = 1

    symtab = SymTab()
    add_builtin_symbols(symtab)

    var_types: dict[IRvar, Type] = {}
    var_types = {}
    var_unit = IRvar("unit")
    var_types[var_unit] = Unit()

    def new_var(t: Type) -> IRvar:
        nonlocal next_var_number, var_types
        var = IRvar(f'x{next_var_number}')
        next_var_number += 1
        new_ir_var = var
        var_types[new_ir_var] = t
        return var

    def new_label() -> ir.Label:
        nonlocal next_label_number
        label = ir.Label(f'L{next_label_number}')
        next_label_number += 1
        return label


    instructions: list[ir.Instruction] = []
    def visit(node: ast.Expression) -> IRvar:
        nonlocal symtab
        var_type = typecheck(node, symtab)

        match node:
            case ast.Literal():
                var = new_var(var_type)
                instructions.append(ir.LoadIntConst(node.value,var))
                return var
            case ast.Identifier():
                return new_var(symtab.lookup_variable_type(node.name))

            case ast.BinaryOp():
                var_left = visit(node.left)
                var_right = visit(node.right)
                var_result = new_var(var_type)
                instructions.append(ir.Call(
                    fun=IRvar(node.op),
                    args=[var_left,var_right],
                    dest=var_result,
                ))
                return var_result

            case ast.IfExpression():

                cond_var = visit(node.cond)

                then_label = new_label()
                else_label = new_label() if node.else_clause else None
                end_label = new_label()

                instructions.append(
                    ir.CondJump(cond=cond_var, then_label=then_label,
                                else_label=else_label if else_label else end_label))

                instructions.append(then_label)
                then_result_var = visit(node.then_clause)  # Visit the then branch and get the result variable

                result_var = new_var(var_type)  # Assume that the IfExpr node has a type attribute
                instructions.append(
                    ir.Copy(source=then_result_var,
                            dest=result_var))  # Copy the result of the then branch to result_var
                instructions.append(
                    ir.Jump(label=end_label))  # Jump to the end label to avoid executing the else branch

                if else_label:
                    instructions.append(else_label)
                    else_result_var = visit(node.else_clause)  # Visit the else branch and get the result variable
                    instructions.append(
                        ir.Copy(source=else_result_var,
                                dest=result_var))  # Copy the result of else branch to result_var

                instructions.append(end_label)

                return result_var  # Return the IR variable storing the final result

            case ast.Block():
                symtab.enter_scope()  # Enter a new scope
                for expr in node.expressions:
                    exp_var = visit(expr)  # Generate IR code for each expression in the block
                    print(exp_var)
                if node.result_expression:
                    result_var = visit(node.result_expression)  # Generate IR code for the result expression and obtain its result variable
                    instructions.append(ir.Copy(source=exp_var, dest=result_var))
                else:
                    result_var = new_var(Unit())  # If the block has no result expression, the default is Unit type
                symtab.leave_scope()  # Leave the scope
                return result_var

            case ast.VarDecl():
                nonlocal var_types
                symtab.define_variable(node.name, node.value, node.type_annotation)
                result_var = new_var(var_type)
                instructions.append(ir.Copy(source=node.value, dest=result_var))
                return result_var

            case ast.FunctionCall():
                args_vars = [visit(arg)[1] for arg in node.arguments]  # Generate IR code for each parameter
                if node.name in ["print_int", "print_bool"]:  # Assume these functions are already defined
                    func_var = IRvar(node.name)  # Special processing built-in function
                    result_var = new_var(Unit())  # Assume these functions have no return value
                    instructions.append(ir.Call(fun=func_var, args=args_vars, dest=result_var))
                else:
                    # For user-defined functions, additional processing logic needs to be added
                    pass
                return result_var

            case _:
                    raise Exception(f"Unsupported ASTnode: {node}")

    var_result = visit(root_node)
    print(var_result,var_types)
    if str(var_types[var_result]) == 'Int':
        instructions.append(ir.Call(IRvar('print_int'),[var_result],new_var(Int())))
    if str(var_types[var_result]) == 'Bool':
        instructions.append(ir.Call(IRvar('print_bool'),[var_result],new_var(Int())))


    return instructions