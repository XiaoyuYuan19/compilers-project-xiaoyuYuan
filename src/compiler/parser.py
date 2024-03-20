from src.compiler import ast
from src.compiler.tokenizer import Token
from src.compiler.types import Int, Bool, Type

precedence_levels = [
    ['='],
    ['or'],
    ['and'],
    ['==', '!='],
    ['<', '<=', '>', '>='],
    ['+', '-', '%'],
    ['*', '/'],
    ['not'],  # 一元操作符的优先级
]

def parse(tokens: list[Token], right_associative=False) -> ast.Expression:

    # This keeps track of which token we're looking at.

    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type="end", text="")

    def consume(expected:  str | list[str] | None = None) -> Token:
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f'{token}: expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token}: expected one of: {comma_separated}')
        pos += 1
        return token


    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal' :
            raise Exception(f'{peek()}: expected an integer literal')
        token = consume()
        return ast.Literal(value=int(token.text))

    def parse_bool_literal() -> ast.Literal:
        if peek().type != 'bool_literal':
            raise Exception(f'{peek().loc}: expected an integer literal')
        token = consume()
        if 'rue' in token.text:
            value = True
        else:
            value = False
        return ast.Literal(value=value)

    def parse_identifier() -> ast.Identifier:
        if peek().type != 'identifier':
            raise Exception(f'{peek().loc}: expected an identifier')
        token = consume()
        return ast.Identifier(name=token.text)

    def parse_term() -> ast.Expression:
        # 处理乘法和除法
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(left=left, op=operator, right=right)
        return left

    def parse_binary_expression(level=0) -> ast.Expression:
        if level == len(precedence_levels):
            return parse_unary_expression()

        left_expr = parse_binary_expression(level + 1)
        while peek().text in precedence_levels[level]:
            op_token = consume()
            if op_token.text == '=':
                # Special handling for right associativity of assignment
                right_expr = parse_binary_expression(level)  # Use the same level for right associativity
            else:
                right_expr = parse_binary_expression(level + 1)
            left_expr = ast.BinaryOp(left=left_expr,op=op_token.text, right=right_expr)

        return left_expr

    def parse_unary_expression() -> ast.Expression:
        if peek().text == 'not':
            op_token = consume('not')
            expr = parse_unary_expression()  # 递归以支持链式一元操作符
            return ast.UnaryOp(operator=op_token.text, operand=expr)
        else:
            return parse_factor()

    def parse_factor() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == '{':
            return parse_block()
        elif peek().text == 'if':
            return parse_if_expr()
        elif peek().text == 'while':
            return parse_while_expr()
        elif peek().type == 'identifier':
            next_pos = pos + 1
            if next_pos < len(tokens) and tokens[next_pos].text == '(':
                return parse_function_call()
            else:
                return parse_identifier()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        else:
            raise Exception(f'{peek()}: unexpected token "{peek().text}"')


    def parse_block() -> ast.Block:
        # consume('{')
        opening_brace_token = consume('{')
        # opening_brace_location = opening_brace_token.loc
        expressions = []
        result_expression = None

        while not peek().text == '}':
            if peek().text == 'return':
                consume('return')
                result_expression = parse_expression()
                # expressions.append(result_expression)
                if peek().text == ';':
                    consume(';')
            elif peek().text in ['if', 'while', '{']:  # Starting a new block or control structure
                expr = parse_expression()
                expressions.append(expr)
                # Check if next token is '}', in which case, this block/expression might be the result_expression
                if peek().text == '}':
                    result_expression = expressions.pop()  # Last expression is result_expression
                elif peek().text == ';':  # Optional semicolon after a block/control structure
                    consume(';')
            else:
                if peek().text == 'var':
                    expr = parse_var_decl()
                else:
                    expr = parse_expression()
                if peek().text == ';':
                    consume(';')
                    expressions.append(expr)
                elif peek().text == '}':
                    result_expression = expr  # Last expression is result_expression
                elif peek().text in ['if', 'while', '{']:  # No semicolon required before these
                    expressions.append(expr)

                else:
                    raise Exception(f"{peek()}: Expected ';' or '}}' but found '{peek().text}'")

        consume('}')
        # return BlockExpr(expressions, result_expression)
        return ast.Block(expressions=expressions, result_expression=result_expression)

    def parse_function_call() -> ast.Expression:
        # name = parse_identifier()
        name_token = consume()
        consume('(')
        arguments = []
        if peek().text != ')':
            while True:
                arg = parse_expression()
                arguments.append(arg)
                if peek().text == ',':
                    consume(',')
                else:
                    break
        consume(')')
        return ast.FunctionCall(name=name_token.text, arguments=arguments)

    def parse_if_expr() -> ast.Expression:
        name_token = consume('if')  # Consume the function name token, capturing the function name
        # function_location = name_token.loc
        condition = parse_expression()
        consume('then')
        then_branch = parse_expression()
        else_branch = None
        if peek().text == 'else':
            consume('else')
            else_branch = parse_expression()
        return ast.IfExpression(condition, then_branch, else_branch)

    def parse_while_expr() -> ast.Expression:
        name_token = consume('while')  # Consume the 'while' keyword
        # function_location = name_token.loc
        condition = parse_expression()
        consume('do')  # Consume the 'do' keyword
        body = parse_expression()
        return ast.WhileExpr(condition=condition, body=body)


    def parse_parenthesized() -> ast.Expression:
        consume('(')
        # Recursively call the top level parsing function
        # to parse whatever is inside the parentheses.
        expr = parse_expression()
        consume(')')
        return expr

    def parse_expression_right() -> ast.Expression:
        left = parse_term()

        if peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text

            # 通过递归调用 `parse_expression` 来解析右边的表达式，
            # 实现右结合性
            right = parse_expression()

            # 构建并返回一个二元操作的AST节点，左边是`left`，右边是`right`的结果
            return ast.BinaryOp(left=left,op=operator,right=right)
        else:
            return left


    # 根据 right_associative 参数选择解析函数
    def parse_expression() -> ast.Expression:
        if right_associative:
            return parse_expression_right()
        else:
            return parse_binary_expression(0)


    # 右结合解析逻辑
    def parse_expression_right() -> ast.Expression:
        # 之前的 parse_expression_right() 代码
        left = parse_term()
        if peek().text in ['+', '-']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_expression()  # 注意这里递归调用 parse_expression()
            return ast.BinaryOp(left=left, op=operator, right=right)
        else:
            return left

    def parse_type_expr(token: Token) -> ast.Expression:
        print('token',token.text)
        if token.text == "Int":
            return Int()
        elif token.text == "Bool":
            return Bool()
        else:
            raise Exception(f"Unknown type: {token.text}")

    def parse_var_decl() -> ast.VarDecl:
        name_token = consume('var')  # Consume the function name token, capturing the function name
        # function_location = name_token.loc
        name = consume().text
        type_annotation = None
        if peek().text == ":":
            consume(":")
            type_annotation = parse_type_expr(consume())
        else:
            type_annotation = None
        consume("=")
        value = parse_expression().value
        # bool or int
        return ast.VarDecl(name=name,  value=value,type_annotation=type_annotation)

    def parse_function_definition() -> ast.FunctionDef:
        """
        Parses a function definition from the token list.
        A function definition consists of the 'fun' keyword, followed by the function name,
        a parameter list, a return type, and a block of code as the function body.
        """
        consume('fun')  # Consume the 'fun' keyword
        name = consume().text  # Function name
        consume('(')
        params = []
        while peek().text != ')':
            param_name = consume().text  # Parameter name
            consume(':')
            param_type = parse_type_expr(consume())  # Parameter type
            params.append((param_name, param_type))
            if peek().text == ',':
                consume(',')
        consume(')')
        if peek().text == ':':
            consume(':')
            return_type = parse_type_expr(consume())  # Return type
        else:
            return_type = None
        body = parse_block()  # Function body
        return ast.FunctionDef(name=name, params=params, return_type=return_type, body=body)

    def parse_module() -> ast.Module:
        """
        Parses a module from the token list. A module can contain multiple function
        definitions and optionally a top-level expression.
        """
        functions = []
        while peek().text == 'fun':
            function_def = parse_function_definition()  # Parse each function definition
            functions.append(function_def)
        expression = None
        if peek().type != 'end':  # If there are tokens left, parse the top-level expression
            expression = parse_expression()
        return ast.Module(functions=functions, expression=expression)

    res = parse_module()
    if peek().text == ';':
        consume(';')
    if peek().type != 'end':
        raise Exception(f"Unexpected token at {peek()}: '{peek().text}'")

    return res

