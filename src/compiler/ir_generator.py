import types

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
    def visit(node: ast.Expression,loop_start : ir.Label= None, loop_end: ir.Label = None) -> IRvar:
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
                if node.expressions == []:
                    exp_var = None
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

            case ast.Module():
                # 首先处理所有函数定义，将它们添加到符号表中
                for func in node.functions:
                    # 函数被绑定到一个特殊的处理函数上，以便后续调用
                    # symtab.define_variable(func.name, (func, "function"),func.return_type)

                    # symtab.define_variable(func.name, (func, "function"), func.return_type)
                    symtab.define_variable(func.name, func.body, typecheck(func, symtab))
                    print(symtab.lookup_variable(func.name))

                # 处理顶级表达式
                if node.expression is not None:
                    return visit(node.expression)
                return None

            case ast.FunctionDef(name, params, return_type, body):
                func_symtab = SymTab(parent=symtab)  # Create a new symbol table for the function scope
                for param_name, param_type in params:
                    param_var = ir.IRvar(param_name)
                    func_symtab.define_variable(param_name, param_var, param_type)
                # Process function body in the function scope
                for expr in body:
                    visit(expr)
                # Note: Add the function to the parent symbol table if needed

            case ast.FunctionCall(name, arguments):
                # Look up the function and its type
                func_var, func_type = symtab.lookup_variable(name,True)
                visit(func_var)
                print('fuva',func_var,func_type)
                arg_vars = [visit(arg) for arg in arguments]
                result_var = new_var(func_type.return_type)
                instructions.append(ir.Call(fun=func_var, args=arg_vars, dest=result_var))
                return result_var

            case ast.WhileExpr(condition, body):
                start_label = new_label()
                end_label = new_label()
                continue_label = new_label()  # Optional: To handle continue statements

                # Jump to the conditional judgment before the loop starts
                instructions.append(ir.Jump(label=start_label))
                instructions.append(continue_label)  # continue statement jumps here

                cond_var = visit(condition)
                # Break out of the loop when the condition is false
                instructions.append(ir.CondJump(cond=cond_var, then_label=start_label, else_label=end_label))

                # Loop body
                visit(body, loop_start=start_label, loop_end=end_label)

                # After the loop ends, jump to the beginning of the loop and continue with the next iteration
                instructions.append(ir.Jump(label=continue_label))
                instructions.append(start_label)  # The position where the loop starts

                # End of loop
                instructions.append(end_label)
                return None

            case ast.Break(value):
                if value:
                    value_var = visit(value, symtab, instructions, loop_start, loop_end)
                    instructions.append(ir.Copy(source=value_var, dest=value_var))  # 假设有 loop_result_var
                instructions.append(ir.Jump(label=loop_end))
            case ast.Continue():
                instructions.append(ir.Jump(label=loop_start))


    var_result = visit(root_node)
    print(var_result,var_types)
    if var_result != None:
        if str(var_types[var_result]) == 'Int':
            instructions.append(ir.Call(IRvar('print_int'),[var_result],new_var(Int())))
        if str(var_types[var_result]) == 'Bool':
            instructions.append(ir.Call(IRvar('print_bool'),[var_result],new_var(Int())))


    return instructions