
from typing import Generic, TypeVar, Dict, Any, List

from src.compiler import types, ast
from src.compiler.types import Int, Bool, FunctionType, Unit, Type

# Create a type variable for the SymTab class
T = TypeVar('T')

class SymTab(Generic[T]):
    def __init__(self, parent: 'SymTab[T]' = None):
        self.parent = parent
        self.symbols: Dict[str, T] = {}
        self.scopes = [{}]


    def enter_scope(self):
        self.scopes.append({})

    def leave_scope(self):
        self.scopes.pop()

    def lookup_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                value = scope[name]
                if str(type(value)) == "<class 'tuple'>":
                    return scope[name][0]
                else:
                    return scope[name]
        raise KeyError(f"Variable '{name}' not found.")

    def update_variable(self, name, value):
        # 在现有作用域中更新变量的值，如果变量存在
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        raise KeyError(f"Variable '{name}' not defined.")

    def define_variable(self, name, value, var_type):
        self.scopes[-1][name] = (value, var_type)

    def lookup_variable_type(self, name):
        for scope in reversed(self.scopes):

            if name in scope:
                _, var_type = scope[name]
                return var_type
        raise KeyError(f"Type for variable '{name}' not found.")



    def define_function(self, name: str, params: List[Type], return_type: Type, body: Any = None):
        """
        Define a new function in the current scope.

        :param name: The name of the function
        :param params: A list of parameter types
        :param return_type: The return type of the function
        :param body: The body of the function (optional, used for interpreted execution)
        """
        func_type = FunctionType(params, return_type)
        self.define_variable(name, (func_type, body), func_type)

def add_builtin_symbols(symtab: SymTab):

    symtab.define_variable("Int", "Int", Int())
    symtab.define_variable("Bool","Bool", Bool())

    symtab.define_variable("true", True, types.Bool())
    symtab.define_variable("false", False, types.Bool())

    symtab.define_variable("+", lambda a, b: a + b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("-", lambda a, b: a - b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("*", lambda a, b: a * b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("/", lambda a, b: a / b, FunctionType([Int(), Int()], Int()))
    symtab.define_variable("%", lambda a, b: a % b, FunctionType([Int(), Int()], Int()))

    symtab.define_variable("==", lambda a, b: a == b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable("!=", lambda a, b: a != b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable("<", lambda a, b: a < b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable("<=", lambda a, b: a <= b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable(">", lambda a, b: a > b, FunctionType([Int(), Int()], Bool()))
    symtab.define_variable(">=", lambda a, b: a >= b, FunctionType([Int(), Int()], Bool()))

    symtab.define_variable("and", lambda a, b: a and b, FunctionType([Bool(), Bool()], Bool()))
    symtab.define_variable("or", lambda a, b: a or b, FunctionType([Bool(), Bool()], Bool()))
    symtab.define_variable("unary_not", lambda a: not a, FunctionType([Bool()], Bool()))
    symtab.define_variable("unary_-", lambda a: -a, FunctionType([Int()], Int()))
    symtab.define_variable("print_int", print, FunctionType([Int()], Unit()))
