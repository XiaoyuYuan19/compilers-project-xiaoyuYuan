import re
from dataclasses import dataclass
from typing import List, Literal

TokenType = Literal["int_literal", "identifier", "operator", "parenthesis", "end"]

@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str

def tokenize(source_code: str) -> List[Token]:
    token_specs = [
        ("address_of", re.compile(r'&')),  # Add address fetch operator
        ("multiline_comment", re.compile(r'/\*.*?\*/', re.DOTALL)),  # Skip multi-line comments
        ("singleline_comment", re.compile(r'//.*?\n')),  # Skip single-line comments
        ("singleline_comment_alt", re.compile(r'#.*?\n')),  # Skip single-line comments (alternate)
        ("whitespace", re.compile(r'\s+')),  # Skip whitespace
        ("bool_literal", re.compile(r'True|true|False|false')),
        ("int_literal", re.compile(r'\b[0-9]+\b')),
        ("identifier", re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')),
        # Longer operators must be before shorter ones that are their substrings
        ("operator", re.compile(r':|==|!=|<=|>=|<<|>>|\+\+|--|\+=|-=|\*=|/=|&&|\|\||[%+\-*/=<>]')),
        ("parenthesis", re.compile(r'[{}()\[\],;]')),
    ]

    position = 0
    result: List[Token] = []

    while position < len(source_code):
        match = None
        for token_type, pattern in token_specs:
            match = pattern.match(source_code, position)
            if match:
                text = match.group(0)
                if token_type not in ["whitespace", "singleline_comment", "singleline_comment_alt", "multiline_comment"]:  # Skip certain types
                    result.append(Token(type=token_type, text=text))
                position = match.end()
                break
        else:  # If no pattern matches
            raise Exception(f'Tokenization failed near "{source_code[position:position + 10]}"...')

    return result
