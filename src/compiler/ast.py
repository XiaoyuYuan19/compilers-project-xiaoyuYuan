
from dataclasses import dataclass


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
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class IfExpression(Expression):
    cond: Expression
    then_clause: Expression
    else_clause: Expression | None