from dataclasses import dataclass


@dataclass(frozen=True)
class Type:
    "Nase class for yupes."


@dataclass(frozen=True)
class BasicType(Type):
    name: str


Int = BasicType('Int')
Bool = BasicType('Bool')
Unit = BasicType('Unit')
