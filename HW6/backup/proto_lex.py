#Balaji Srinivasan      -   04/28/15
#proto_lex.py           -   Module that tokenizes a Proto source program
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw5.html
#usage                  -   python protoplasm5.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

import ply.lex as lex

#List of keywords in Proto(4)
keywords = {
    'return':'RETURN',
    'void':'VOID',
    'new':'NEW',
    'for':'FOR',
    'int':'INT',
    'bool':'BOOL',
    'true':'TRUE',
    'false':'FALSE',
    'input':'INPUT',
    'print':'PRINT',
    'if':'IF',
    'then':'THEN',
    'else':'ELSE',
    'while':'WHILE',
    'do':'DO'
}

#List of tokens in Proto(2)
tokens = ['INCREMENT',
          'DECREMENT',
          'LSQUARE',
          'RSQUARE',
          'COMMA',
          'SCOMMENT',
          'PLUS',
          'MINUS',
          'STAR',
          'DIV',
          'MOD',
          'AND',
          'OR',
          'EQUAL',
          'NEQUAL',
          'LTHAN',
          'LTHANEQ',
          'GTHAN',
          'GTHANEQ',
          'NOT',
          'INTCONST',
          'IDENTIFIER',
          'LPAREN',
          'RPAREN',
          'EQUALS',
          'SEMICOLON',
          'LBRACE',
          'RBRACE',
          'NEWLINE',
          'UMINUS'
        ] + list(keywords.values())


#Token rules for the tokens defined above
def t_INCREMENT(t):
    r'\+\+'
    return t

def t_DECREMENT(t):
    r'--'
    return t

def t_LSQUARE(t):
    r'\['
    return t

def t_RSQUARE(t):
    r'\]'
    return t

def t_COMMA(t):
    r','
    return t

def t_SCOMMENT(t):
    r'//.*'
    pass

def t_PLUS(t):
    r'\+'
    return t

def t_MINUS(t):
    r'-'
    return t

def t_STAR(t):
    r'\*'
    return t

def t_DIV(t):
    r'\/'
    return t

def t_MOD(t):
    r'%'
    return t

def t_AND(t):
    r'&&'
    return t

def t_OR(t):
    r'\|\|'
    return t

def t_EQUAL(t):
    r'=='
    return t

def t_NEQUAL(t):
    r'!='
    return t

def t_LTHANEQ(t):
    r'<='
    return t

def GTHANEQ(t):
    r'>='
    return t

def t_LTHAN(t):
    r'<'
    return t

def t_GTHAN(t):
    r'>'
    return t

def t_NOT(t):
    r'[!]'
    return t

def t_INTCONST(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z][A-Za-z0-9]*'
    if t.value in keywords.keys():
        t.type = keywords[t.value]
    return t

def t_LPAREN(t):
    r'\('
    return t

def t_RPAREN(t):
    r'\)'
    return t

def t_EQUALS(t):
    r'='
    return t

def t_SEMICOLON(t):
    r';'
    return t

def t_LBRACE(t):
    r'\{'
    return t

def t_RBRACE(t):
    r'\}'
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.line_count += 1

def t_error(t):
    print "PROTO_ERROR : Tokenizer error at line ", t.lexer.line_count, ": Invalid token at '%s'" % t.value[0]
    exit(1)

t_ignore = ' \t'