import unittest

from src.compiler.tokenizer import tokenize, Token


class test_tokenizer(unittest.TestCase):
    def test_1token(self):
        assert tokenize("hello") == [
            Token(type='identifier', text='hello')
        ]
        assert tokenize("   \n  hi      \n\n") == [
            Token(type='identifier',text='hi')
        ]
    def testMultoken(self):
        assert tokenize(" hi number 1 ") == [
            Token(type='identifier', text='hi'),
            Token(type='identifier',text='number'),
            Token(type='int_literal',text='1'),
        ]
        assert tokenize(" 3 + -5 ") == [
            Token(type='int_literal', text='3'),
            Token(type='operator',text='+'),
            Token(type='operator',text='-'),
            Token(type='int_literal',text='5'),
        ]
        print(tokenize(" 3 + -( 1 + 2 )"))
        assert tokenize(" 3 + -( 1 + 2 )") == [
            Token(type='int_literal', text='3'),
            Token(type='operator', text='+'),
            Token(type='operator', text='-'),
            Token(type='parenthesis', text='('),
            Token(type='int_literal', text='1'),
            Token(type='operator', text='+'),
            Token(type='int_literal', text='2'),
            Token(type='parenthesis', text=')'),
        ]
        assert tokenize(" 3 - 1 ") == [
            Token(type='int_literal', text='3'),
            Token(type='operator', text='-'),
            Token(type='int_literal', text='1')
        ]

    def test_tokenizer_lines(self):
        assert tokenize(" 3 - \n1 ") == [
            Token(type='int_literal', text='3'),
            Token(type='operator', text='-'),
            Token(type='int_literal', text='1')
        ]

    def test_tokenizer_multi_character_operators(self):
        assert tokenize("a == b != c <= d >= e") == [
            Token(type='identifier', text='a'),
            Token(type='operator', text='=='),
            Token(type='identifier', text='b'),
            Token(type='operator', text='!='),
            Token(type='identifier', text='c'),
            Token(type='operator', text='<='),
            Token(type='identifier', text='d'),
            Token(type='operator', text='>='),
            Token(type='identifier', text='e')
        ]

    def test_tokenizer_punctuation(self):
        print(tokenize("func(a, b); {return a + b;}"))
        assert tokenize("func(a, b); {return a + b;}") == [
            Token(type='identifier', text='func'),
            Token(type='parenthesis', text='('),
            Token(type='identifier', text='a'),
            Token(type='parenthesis', text=','),
            Token(type='identifier', text='b'),
            Token(type='parenthesis', text=')'),
            Token(type='parenthesis', text=';'),
            Token(type='parenthesis', text='{'),
            Token(type='identifier', text='return'),
            Token(type='identifier', text='a'),
            Token(type='operator', text='+'),
            Token(type='identifier', text='b'),
            Token(type='parenthesis', text=';'),
            Token(type='parenthesis', text='}'),
        ]

    def test_tokenizer_single_line_comments(self):
        assert tokenize("// This is a comment\na = b + 1;") == [
            Token(type='identifier', text='a'),
            Token(type='operator', text='='),
            Token(type='identifier', text='b'),
            Token(type='operator', text='+'),
            Token(type='int_literal', text='1'),
            Token(type='parenthesis', text=';')
        ]

    def test_tokenizer_multi_line_comments(self):
        print(tokenize("/* This is a \nmulti-line comment */\na = b + 1;"))
        assert tokenize("/* This is a \nmulti-line comment */\na = b + 1;") == [
            Token(type='identifier', text='a'),
            Token(type='operator', text='='),
            Token(type='identifier', text='b'),
            Token(type='operator', text='+'),
            Token(type='int_literal', text='1'),
            Token(type='parenthesis', text=';')
        ]


if __name__ == '__main__':
    unittest.main()

