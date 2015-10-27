#Balaji Srinivasan      -   04/28/15
#protoplasm4.py         -   Program that compiles a Proto source program and generates a .asm file of the same name
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw5.html
#usage                  -   python protoplasm4.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

from proto_lex import tokens
from proto_lex import keywords
from ASTNode import *
from IRCode import *

import proto_lex
import ply.lex as lex
import ply.yacc as yacc
from sets import Set
import re
import copy
import sys

#Tuple that denotes the precedence and associativity of various tokens in the grammar
precedence=(
    ('right', 'EQUALS'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQUAL','NEQUAL'),
    ('nonassoc', 'LTHAN','LTHANEQ','GTHAN','GTHANEQ'),
    ('left', 'PLUS','MINUS'),
    ('left', 'STAR','DIV','MOD'),
    ('right', 'NOT', 'UMINUS')
)


#Yacc methods(p_) to identify the grammar in the program
#start  =   start symbol in the grammar
start='pgm'

def p_pgm(p):
    'pgm  :   decl_star'
    #print "matched pgm  :   decl_star", [p[i] for i in range(len(p))]
    p[0] = Node('pgm', [p[1]], [])

def p_decl_star(p):
    '''decl_star    :   decl decl_star
                    |   empty
    '''
    if p[1] is not None:
        #print "matched decl_star    :   decl decl_star", [p[i] for i in range(len(p))]
        p[0] = Node('declstar', [p[1], p[2]], [])
    else:
        #print "matched decl_star    :   empty", [p[i] for i in range(len(p))]
        p[0] = Node('declstar_empty', [], [p[1]])

def p_decl_vardecl(p):
    'decl   :   vardecl'
    #print "matched decl :   vardecl", [p[i] for i in range(len(p))]
    p[0] = Node('decl_vardecl', [p[1]], [])

def p_decl_fundecl(p):
    'decl   :   fundecl'
    #print "matched decl : fundecl", [p[i] for i in range(len(p))]
    p[0] = Node('decl_fundecl', [p[1]], [])

def p_vardecl(p):
    'vardecl    :   type varlist SEMICOLON'
    #print "matched vardecl : type varlist SEMICOLON", [p[i] for i in range(len(p))]
    p[0] = Node('vardecl', [p[1], p[2]], [])

def p_fundecl(p):
    'fundecl   :   type IDENTIFIER LPAREN formalsOpt RPAREN stmt'
    #print "matched fundecl : type IDENTIFIER LPAREN formalsOpt RPAREN stmt", [p[i] for i in range(len(p))]
    p[0] = Node('fundecl', [p[1], p[4], p[6]], [p[2]])

def p_formalsOpt(p):
    '''formalsOpt   :   formals
                    |   empty
    '''
    if p[1] is not None:
        #print "matched formalsOpt   :   formals", [p[i] for i in range(len(p))]
        p[0] = Node('formalsOpt', [p[1]], [])
    else:
        #print "matched formalsOpt   :   empty", [p[i] for i in range(len(p))]
        p[0] = Node('formalsOpt_empty', [], [p[1]])

def p_type_int(p):
    'type   :   INT'
    #print "matched type : INT", [p[i] for i in range(len(p))]
    p[0] = Node('type_int', [], [p[1]])

def p_type_bool(p):
    'type   :   BOOL'
    #print "matched type : BOOL", [p[i] for i in range(len(p))]
    p[0] = Node('type_bool', [], [p[1]])

def p_type_void(p):
    'type   :   VOID'
    #print "matched type : VOID", [p[i] for i in range(len(p))]
    p[0] = Node('type_void', [], [p[1]])

def p_type_array(p):
    'type   :   type LSQUARE RSQUARE'
    #print "matched type : type LSQUARE RSQUARE", [p[i] for i in range(len(p))]
    p[0] = Node('type_array', [p[1]], [])

def p_varlist_multi(p):
    'varlist    :   IDENTIFIER COMMA varlist'
    #print "matched varlist : IDENTIFIER COMMA varlist",  [p[i] for i in range(len(p))]
    p[0] = Node('varlist_multi', [p[3]], [p[1]])

def p_varlist_single(p):
    'varlist    :   IDENTIFIER'
    #print "matched varlist    :   IDENTIFIER", [p[i] for i in range(len(p))]
    p[0] = Node('varlist_single', [], [p[1]])

def p_formals(p):
    '''formals      :   type IDENTIFIER COMMA formals
                    |   type IDENTIFIER
    '''
    if len(p) == 5:
        #print "matched formals      :   type IDENTIFIER COMMA formals", [p[i] for i in range(len(p))]
        p[0] = Node('formals_multi', [p[1], p[4]], [p[2]])
    elif len(p) == 3:
        #print "matched formals      :   type IDENTIFIER", [p[i] for i in range(len(p))]
        p[0] = Node('formals_single', [p[1]], [p[2]])

def p_stmt_SE(p):
    'stmt   :   SE SEMICOLON'
    #print "matched stmt   :   SE SEMICOLON", [p[i] for i in range(len(p))]
    p[0] = Node('stmt_se', [p[1]], [])

def p_stmt_print(p):
    'stmt   :   PRINT LPAREN AE RPAREN SEMICOLON'
    #print "matched stmt   :   PRINT LPAREN AE RPAREN SEMICOLON", [p[i] for i in range(len(p))]
    p[0] = Node('stmt_print', [p[3]], [])

def p_stmt_block(p):
    'stmt   :   LBRACE vardecl_star stmt_star RBRACE'
    #print "matched stmt   :   LBRACE vardecl_star stmt_star RBRACE", [p[i] for i in range(len(p))]
    p[0] = Node('stmt_block', [p[2], p[3]], [])
    
def p_vardecl_star(p):
    '''vardecl_star     :   vardecl vardecl_star
                        |   empty
    '''
    if p[1] is not None:
        #print "matched vardecl_star    :   vardecl vardecl_star", [p[i] for i in range(len(p))]
        p[0] = Node('vardeclstar', [p[1], p[2]], [])
    else:
        #print "matched vardecl_star    :   empty", [p[i] for i in range(len(p))]
        p[0] = Node('vardeclstar_empty', [], [p[1]])

def p_stmt_star(p):
    '''stmt_star    :   stmt stmt_star
                    |   empty
    '''
    if p[1] is not None:
        #print "matched stmt_star    :   stmt stmt_star", [p[i] for i in range(len(p))]
        p[0] = Node('stmtstar', [p[1], p[2]], [])
    else:
        #print "matched stmt_star    :   empty", [p[i] for i in range(len(p))]
        p[0] = Node('stmtstar_empty', [], [p[1]])

def p_stmt_if_else(p):
    'stmt : IF AE THEN stmt ELSE stmt'
    #print "matched stmt: IF AE THEN stmt ELSE stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_if_else', [p[2], p[4], p[6]], [])

def p_stmt_if(p):
    'stmt :  IF AE THEN stmt'
    #print "matched stmt: IF AE THEN stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_if', [p[2], p[4]], [])

def p_stmt_while(p):
    'stmt : WHILE AE DO stmt'
    #print "matched stmt: WHILE AE DO stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_while', [p[2], p[4]], [])

def p_stmt_for(p):
    'stmt : FOR LPAREN SEOpt SEMICOLON AEOpt SEMICOLON SEOpt RPAREN stmt'
    #print "matched stmt: FOR LPAREN SEOpt SEMICOLON AEOpt SEMICOLON SEOpt RPAREN stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_for', [p[3], p[5], p[7], p[9]], [])

def p_SEOpt(p):
    '''SEOpt : SE
             | empty
    '''
    if p[1] is not None:
        #print "matched SEOpt: SE", [p[i] for i in range(len(p))]
        p[0] = Node('SEOpt', [p[1]], [])
    else:
        #print "matched SEOpt: empty", [p[i] for i in range(len(p))]
        p[0] = Node('SEOpt_empty', [], [p[1]])

def p_AEOpt(p):
    '''AEOpt : AE
             | empty
    '''
    if p[1] is not None:
        #print "matched AEOpt: AE", [p[i] for i in range(len(p))]
        p[0] = Node('AEOpt', [p[1]], [])
    else:
        #print "matched AEOpt: empty", [p[i] for i in range(len(p))]
        p[0] = Node('AEOpt_empty', [], [p[1]])


def p_stmt_do_while(p):
    'stmt : DO stmt WHILE AE SEMICOLON'
    #print "matched stmt: DO stmt WHILE AE SEMICOLON ",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_do_while', [p[2], p[4]], [])

def p_stmt_return(p):
    'stmt   :   RETURN AEOpt SEMICOLON'
    #print "matched stmt   :   RETURN AEOpt SEMICOLON",  [p[i] for i in range(len(p))]
    p[0] = Node('stmt_return', [p[2]], [])

def p_SE_assign(p):
    'SE : lhs EQUALS AE'
    #print "matched SE : lhs EQUALS AE", [p[i] for i in range(len(p))]
    p[0] = Node('se_assign', [p[1], p[3]], [p[2]])

def p_SE_postinc(p):
    'SE : lhs INCREMENT'
    #print "matched SE : lhs INCREMENT", [p[i] for i in range(len(p))]
    p[0] = Node('se_postinc', [p[1]], [p[2]])

def p_SE_postdec(p):
    'SE : lhs DECREMENT'
    #print "matched SE : lhs DECREMENT", [p[i] for i in range(len(p))]
    p[0] = Node('se_postdec', [p[1]], [p[2]])

def p_SE_preinc(p):
    'SE : INCREMENT lhs'
    #print "matched SE : INCREMENT lhs", [p[i] for i in range(len(p))]
    p[0] = Node('se_preinc', [p[2]], [p[1]])

def p_SE_predec(p):
    'SE : DECREMENT lhs'
    #print "matched SE : DECREMENT lhs", [p[i] for i in range(len(p))]
    p[0] = Node('se_predec', [p[2]], [p[1]])

def p_lhs_id(p):
    'lhs    :   IDENTIFIER'
    #print "matched lhs    :   IDENTIFIER",  [p[i] for i in range(len(p))]
    p[0] = Node('lhs_id', [], [p[1]])

def p_lhs_arrayAccess(p):
    'lhs    :   arrayAccess'
    #print "matched lhs    :   arrayAccess",  [p[i] for i in range(len(p))]
    p[0] = Node('lhs_arrayAccess', [p[1]], [])

def p_AE_binop(p):
    'AE : AE binop AE'
    #print "matched AE: AE binop AE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_AE_unop(p):
    'AE : unop AE %prec UMINUS'
    #print "matched AE: unop AE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_unop', [p[2]], [p[1]])

def p_AE_primary(p):
    'AE :   primary'
    #print "matched AE :   primary",  [p[i] for i in range(len(p))]
    p[0] = Node('ae_primary', [p[1]], [])

def p_AE_SE(p):
    'AE : SE'
    #print "matched AE: SE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_se', [p[1]], [])

def p_AE_newArray(p):
    'AE :   newArray'
    #print "matched AE :   newArray",  [p[i] for i in range(len(p))]
    p[0] = Node('ae_newArray', [p[1]], [])

def p_primary_intconst(p):
    'primary    :   INTCONST'
    #print "matched primary    :   intconst",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_intconst', [], [p[1]])

def p_primary_true(p):
    'primary    :   TRUE'
    #print "matched primary    :   TRUE",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_true', [], [p[1]])

def p_primary_false(p):
    'primary    :   FALSE'
    #print "matched primary  :   FALSE",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_false', [], [p[1]])

def p_primary_input(p):
    'primary    :   INPUT LPAREN RPAREN'
    #print "matched primary    :   INPUT LPAREN RPAREN",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_input', [], [])

def p_primary_group(p):
    'primary    :   LPAREN AE RPAREN'
    #print "matched primary    :   LPAREN AE RPAREN",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_group', [p[2]], [])

def p_primary_id(p):
    'primary    :   IDENTIFIER'
    #print "matched primary  :   IDENTIFIER",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_id', [], [p[1]])

def p_primary_arrayAccess(p):
    'primary    :   arrayAccess'
    #print "matched primary    :   arrayAccess",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_arrayAccess', [p[1]], [])

def p_primary_functionCall(p):
    'primary    :   functionCall'
    #print "matched primary    :   functionCall",  [p[i] for i in range(len(p))]
    p[0] = Node('primary_functionCall', [p[1]], [])

def p_arrayAccess(p):
    'arrayAccess    :   primary LSQUARE AE RSQUARE'
    #print "matched arrayAccess    :   primary LSQUARE AE RSQUARE",  [p[i] for i in range(len(p))]
    p[0] = Node('arrayAccess', [p[1], p[3]], [])

def p_functionCall(p):
    'functionCall   :   IDENTIFIER LPAREN argsOpt RPAREN'
    #print "matched functionCall   :   IDENTIFIER LPAREN argsOpt RPAREN",  [p[i] for i in range(len(p))]
    p[0] = Node('functionCall', [p[3]], [p[1]])

def p_argsOpt(p):
    '''argsOpt  : args
                | empty
    '''
    if p[1] is not None:
        #print "matched argsOpt: args", [p[i] for i in range(len(p))]
        p[0] = Node('argsOpt', [p[1]], [])
    else:
        #print "matched argsOpt: empty", [p[i] for i in range(len(p))]
        p[0] = Node('argsOpt_empty', [], [p[1]])

def p_args(p):
    '''args :   AE COMMA args
            |   AE
    '''
    if len(p) == 4:
        #print "matched args :   AE COMMA args",  [p[i] for i in range(len(p))]
        p[0] = Node('args_multi', [p[1], p[3]], [])
    elif len(p) == 2:
        #print "matched args :   AE",  [p[i] for i in range(len(p))]
        p[0] = Node('args_single', [p[1]], [])

def p_newArray(p):
    'newArray   :   NEW type dimexpr dim_star'
    #print "matched newArray   :   NEW type dimexpr dim_star",  [p[i] for i in range(len(p))]
    p[0] = Node('newArray', [p[2], p[3], p[4]], [])

def p_dimstar(p):
    '''dim_star :   dim dim_star
                |   empty
    '''
    if len(p) == 3 and p[1] is not None:
        #print "matched dim_star :   dim dim_star",  [p[i] for i in range(len(p))]
        p[0] = Node('dimstar', [p[1], p[2]], [])
    elif p[1] is None:
        #print "matched dim_star :   empty",  [p[i] for i in range(len(p))]
        p[0] = Node('dimstar_empty', [], [p[1]])

def p_dimexpr(p):
    'dimexpr    :   LSQUARE AE RSQUARE'
    #print "matched dimexpr    :   LSQUARE AE RSQUARE",  [p[i] for i in range(len(p))]
    p[0] = Node('dimexpr', [p[2]], [])

def p_dim(p):
    'dim    :   LSQUARE RSQUARE'
    #print "matched dim    :   LSQUARE RSQUARE",  [p[i] for i in range(len(p))]
    p[0] = Node('dim', [], [])


def p_binop(p):
    '''binop : PLUS
             | MINUS
             | STAR
             | DIV
             | MOD
             | AND
             | OR
             | EQUAL
             | NEQUAL
             | LTHANEQ
             | LTHAN
             | GTHANEQ
             | GTHAN
    '''
    #print "matched binop: PLUS| MINUS| ...|GTHANEQ",  [p[i] for i in range(len(p))]
    p[0] = p[1]

def p_unop(p):
    '''unop : MINUS
            | NOT
    '''
    #print "matched unop: MINUS | NOT",  [p[i] for i in range(len(p))]
    p[0] = p[1]

def calc_column(token_lexpos):
    nline_index = test_file_input.rfind('\n', 0, token_lexpos)
    return token_lexpos - nline_index

def p_error(p):
    print "PROTO_ERROR : Parser error at line ", lexer.line_count, " column ", calc_column(p.lexpos), " Offending token:", p.value
    exit(1)

def p_empty(p):
    'empty  :   '
    p[0] = None




#Global variables denoting the intermediate code of the functions in the program
func_list = []
func_ircode_list = []

#Test files for the program. Specify a test file in the command-line or specify here
tes_files = []
test_file_name = sys.argv[1]
f = open(test_file_name,'r')
test_file_input = f.read()

#Build the lexer and input the lexer with the program to identify undefined tokens
lexer = lex.lex(module=proto_lex)
lexer.line_count = 1
lexer.input(test_file_input)

#Build the parser and input the parser with the program to parse the statements in the program
parser = yacc.yacc()
res = parser.parse(test_file_input)
assert(res is not None)
print "\n\tbefore checkStaticSemantics()"
res.display()

res.checkStaticSemantics()
print "\n\tafter checkStaticSemantics()"
res.display()

res.typeCheck()
print "\n\tafter typeCheck()"
res.display()
print "sym_tab"
print_symtab()

res.checkControlFlowReturn()
print "\n\tafter control flow return check"
res.display()
print_symtab()

num_func, func_list = find_numfunc()
if 'main' not in func_list:
    print "PROTO  ERROR: main() function not defined in the program"
    exit(1)

for i in range(num_func):
    func_ircode_list.append(IRCode(func_list[i]))
    res.gencode(func_ircode_list[i])

print "\n\tafter intermediate codegen"
for i in range(num_func):
    print "\n\t", func_ircode_list[i].func_name, "\tfunc_ircode_list", i
    func_ircode_list[i].display()

print "\n\tafter generating def, use, in, out"
for i in range(num_func):
    func_ircode_list[i].check_if_wellformed()

print "\n\tafter performing liveness analysis"
for i in range(num_func):
    func_ircode_list[i].performLivenessAnalysis()

print "\n\tafter optimizing gencode"
for i in range(num_func):
    func_ircode_list[i].optimize()

print "\n\tafter generating ASM code"
if num_func == 1:
    for i in range(num_func):
        func_ircode_list[i].genASM()
else:
    bigger_optimized_ircode_list = []
    bigger_spill_vertex_list = []
    for i in range(num_func):
        bigger_optimized_ircode_list.extend(func_ircode_list[i].optimized_ircode_list)
        bigger_optimized_ircode_list.extend(func_ircode_list[i].spill_vertex_list)
    big_ircode = IRCode('main')
    big_ircode.optimized_ircode_list = bigger_optimized_ircode_list
    big_ircode.spill_vertex_list = bigger_spill_vertex_list
    big_ircode.genASM()
