import re
from dataclasses import dataclass
from typing import Literal


TokenType = Literal["ini_literal", "identifier","parenthesis","end"]

@dataclass(frozen = True)
class Token:
    type: TokenType
    text: str

def tokenize(source_code: str) -> list[Token]:
    whitespace_re = re.compile(r'\s+')
    integer_re = re.compile(r'[0-9]+')
    identifier_re = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    operator_re = re.compile(r'[<*/+-]')
    paren_re = re.compile(r'[()]')

    position = 0
    result: list[Token] = []

    while position < len(source_code):
        match = whitespace_re.match(source_code, position)
        if match is not None:
            position += match.end() - position
            continue

        match = identifier_re.match(source_code, position)
        if match is not None:
            result.append(Token(
                type='identifier',
                text=source_code[position:match.end()]
            ))
            position = match.end()
            continue

        match = integer_re.match(source_code, position)
        if match is not None:
            result.append(Token(
                type='int_literal',
                text=source_code[position:match.end()]
            ))
            position = match.end()
            continue

        match = operator_re.match(source_code, position)
        if match is not None:
            result.append(Token(
                type='identifier',# change oit to operater later
                text=source_code[position:match.end()]
            ))
            position = match.end()
            continue

        match = paren_re.match(source_code, position)
        if match is not None:
            result.append(Token(
                type='parenthesis',# change oit to operater later
                text=source_code[position:match.end()]
            ))
            position = match.end()
            continue

        raise Exception(f'Tokenization failed near {source_code[position:{position + 10}]}...')

        # Todo(me): 简化结构

    return result