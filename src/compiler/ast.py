
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Expression:
    "Base class for expression AST nodes"

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: int


@dataclass
class UnaryOp(Expression):
    operator: str
    operand: Expression

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None

@dataclass
class FunctionCall(Expression):
    name: Expression  # Normally is an Identifier
    arguments: list[Expression]

@dataclass
class Block(Expression):
    expressions: List[Expression]
    result_expression: Expression = None


@dataclass
class VarDecl(Expression):
    name: str
    value: Expression
    type_annotation: type | None

@dataclass
class WhileExpr(Expression):
    condition: Expression
    body: Expression

@dataclass
class CaseClause:
    pattern: Expression
    expression: Expression

@dataclass
class CaseExpr(Expression):
    value: Expression
    clauses: List[CaseClause]
    default: Optional[Expression] = None