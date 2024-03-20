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
            Token(type='identifier',text='+'),
            Token(type='identifier',text='-'),
            Token(type='int_literal',text='5'),
        ]
        assert tokenize(" 3 + -( 1 + 2 )") == [
            Token(type='int_literal', text='3'),
            Token(type='identifier', text='+'),
            Token(type='identifier', text='-'),
            Token(type='parenthesis', text='('),
            Token(type='int_literal', text='1'),
            Token(type='identifier', text='+'),
            Token(type='int_literal', text='2'),
            Token(type='parenthesis', text=')'),
        ]
        assert tokenize(" 3-1 ") == [
            Token(type='int_literal', text='3'),
            Token(type='identifier', text='-'),
            Token(type='int_literal', text='1')
        ]


if __name__ == '__main__':
    unittest.main()

