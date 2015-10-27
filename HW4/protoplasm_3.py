#Balaji Srinivasan      -   04/14/15
#protoplasm2.py         -   Program that compiles a Proto source program and generates a .asm file of the same name
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw4.html
#usage                  -   python protoplasm2.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

from proto_lex import tokens
from proto_lex import keywords
import proto_lex
import ply.lex as lex
import ply.yacc as yacc
from sets import Set
import re
import copy
import sys

#Tuple that denotes the precedence and associativity of various tokens in the grammar
precedence=(
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
    'pgm : decl_seq stmt_seq'
    print "matched pgm: decl_seq stmt_seq", [p[i] for i in range(len(p))]
    p[0] = Node('pgm', [p[1], p[2]], [])

def p_stmt_seq(p):
    '''stmt_seq : stmt stmt_seq
                | empty
    '''
    if p[1] is not None:
        print "matched stmt_seq : stmt stmt_seq", [p[i] for i in range(len(p))]
        p[0] = Node('stmtseq', [p[1],p[2]], [])
    else:
        print "matched stmt_seq : empty", [p[i] for i in range(len(p))]
        p[0] = Node('stmtseq_empty', [], [p[1]])

def p_stmt_se(p):
    'stmt : SE SEMICOLON'
    print "matched stmt: SE SEMICOLON ",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_se', [p[1]], [])

def p_stmt_print(p):
    'stmt : PRINT LPAREN AE RPAREN SEMICOLON'
    print "matched stmt: PRINT LPAREN AE RPAREN SEMICOLON",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_print', [p[3]], [])

def p_stmt_block(p):
    'stmt :  LBRACE decl_seq stmt_seq RBRACE'
    print "matched stmt: LBRACE decl_seq stmt_seq RBRACE",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_block', [p[2], p[3]], [])

def p_stmt_if_else(p):
    'stmt : IF AE THEN stmt ELSE stmt'
    print "matched stmt: IF AE THEN stmt ELSE stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_if_else', [p[2], p[4], p[6]], [])

def p_stmt_if(p):
    'stmt :  IF AE THEN stmt'
    print "matched stmt: IF AE THEN stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_if', [p[2], p[4]], [])

def p_stmt_while(p):
    'stmt : WHILE AE DO stmt'
    print "matched stmt: WHILE AE DO stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_while', [p[2], p[4]], [])

def p_stmt_for(p):
    'stmt : FOR LPAREN SEOpt SEMICOLON AEOpt SEMICOLON SEOpt RPAREN stmt'
    print "matched stmt: FOR LPAREN SEOpt SEMICOLON AEOpt SEMICOLON SEOpt RPAREN stmt",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_for', [p[3], p[5], p[7], p[9]], [])

def p_stmt_do_while(p):
    'stmt : DO stmt WHILE AE SEMICOLON'
    print "matched stmt: DO stmt WHILE AE SEMICOLON ",[p[i] for i in range(len(p))]
    p[0] = Node('stmt_do_while', [p[2], p[4]], [])

def p_SEOpt(p):
    '''SEOpt : SE
             | empty
    '''
    if p[1] is not None:
        print "matched SEOpt: SE", [p[i] for i in range(len(p))]
        p[0] = Node('seopt', [p[1]], [])
    else:
        print "matched SEOpt: empty", [p[i] for i in range(len(p))]
        p[0] = Node('seopt_empty', [], [p[1]])

def p_AEOpt(p):
    '''AEOpt : AE
             | empty
    '''
    if p[1] is not None:
        print "matched AEOpt: AE", [p[i] for i in range(len(p))]
        p[0] = Node('aeopt', [p[1]], [])
    else:
        print "matched AEOpt: empty", [p[i] for i in range(len(p))]
        p[0] = Node('aeopt_empty', [], [p[1]])

def p_decl_seq(p):
    '''decl_seq : decl decl_seq
                | empty
    '''
    if p[1] is not None:
        print "matched decl_seq: decl decl_seq", [p[i] for i in range(len(p))]
        p[0] = Node('declseq', [p[1], p[2]], [])

    else:
        print "matched decl_seq: empty", [p[i] for i in range(len(p))]
        p[0] = Node('declseq_empty', [], [p[1]])

def p_decl(p):
    'decl : type varlist SEMICOLON'
    print "matched decl : type varlist SEMICOLON", [p[i] for i in range(len(p))]
    p[0] = Node('decl', [p[1], p[2]], [])

def p_type_int(p):
    'type : INT'
    print "matched type : INT", [p[i] for i in range(len(p))]
    p[0] = Node('type_int', [], [p[1]])

def p_type_bool(p):
    'type : BOOL'
    print "matched type : BOOL", [p[i] for i in range(len(p))]
    p[0] = Node('type_bool', [], [p[1]])

def p_varlist_multi(p):
    'varlist : var COMMA varlist'
    print "matched varlist : var COMMA varlist", [p[i] for i in range(len(p))]
    p[0] = Node('varlist', [p[1], p[3]], [])

def p_varlist_single(p):
    'varlist : var'
    print "matched varlist : var", [p[i] for i in range(len(p))]
    p[0] = Node('varlist', [p[1]], [])

def p_var(p):
    'var : IDENTIFIER dimstar'
    print "matched var : IDENTIFIER dimstar", [p[i] for i in range(len(p))]
    p[0] = Node('var', [p[2]], [p[1]])

def p_SE_assign(p):
    'SE : lhs EQUALS AE'
    print "matched SE : lhs EQUALS AE", [p[i] for i in range(len(p))]
    p[0] = Node('se_assign', [p[1], p[3]], [p[2]])

def p_SE_postinc(p):
    'SE : lhs INCREMENT'
    print "matched SE : lhs INCREMENT", [p[i] for i in range(len(p))]
    p[0] = Node('se_postinc', [p[1]], [p[2]])

def p_SE_postdec(p):
    'SE : lhs DECREMENT'
    print "matched SE : lhs DECREMENT", [p[i] for i in range(len(p))]
    p[0] = Node('se_postdec', [p[1]], [p[2]])

def p_SE_preinc(p):
    'SE : INCREMENT lhs'
    print "matched SE : INCREMENT lhs", [p[i] for i in range(len(p))]
    p[0] = Node('se_preinc', [p[2]], [p[1]])

def p_SE_predec(p):
    'SE : DECREMENT lhs'
    print "matched SE : DECREMENT lhs", [p[i] for i in range(len(p))]
    p[0] = Node('se_predec', [p[2]], [p[1]])

def p_lhs(p):
    '''lhs : IDENTIFIER
           | lhs LSQUARE AE RSQUARE
    '''
    if len(p) == 2:
        print "matched lhs : IDENTIFIER", [p[i] for i in range(len(p))]
        p[0] = Node('lhs_id', [], [p[1]])

    elif len(p) == 5:
        print "matched lhs: lhs LSQUARE AE RSQUARE", [p[i] for i in range(len(p))]
        p[0] = Node('lhs_ae', [p[1], p[3]], [])

def p_AE_binop(p):
    'AE : AE binop AE'
    print "matched AE: AE binop AE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_AE_unop(p):
    'AE : unop AE %prec UMINUS'
    print "matched AE: unop AE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_unop', [p[2]], [p[1]])

def p_AE_lhs(p):
    'AE : lhs'
    print "matched AE: lhs", [p[i] for i in range(len(p))]
    p[0] = Node('ae_lhs', [p[1]], [])

def p_AE_se(p):
    'AE : SE'
    print "matched AE: SE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_se', [p[1]], [])

def p_AE_ae(p):
    'AE : LPAREN AE RPAREN'
    print "matched AE: LPAREN AE RPAREN", [p[i] for i in range(len(p))]
    p[0] = Node('ae_group', [p[2]], [])

def p_AE_input(p):
    'AE : INPUT LPAREN RPAREN'
    print "matched AE: INPUT LPAREN RPAREN", [p[i] for i in range(len(p))]
    p[0] = Node('ae_input', [], [])

def p_AE_intconst(p):
    'AE : INTCONST'
    print "matched AE: INTCONST", [p[i] for i in range(len(p))]
    p[0] = Node('ae_intconst', [], [p[1]])

def p_AE_true(p):
    'AE : TRUE'
    print "matched AE: TRUE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_true', [], [p[1]])

def p_AE_false(p):
    'AE : FALSE'
    print "matched AE: FALSE", [p[i] for i in range(len(p))]
    p[0] = Node('ae_false', [], [p[1]])

def p_AE_new(p):
    'AE : NEW type dimexpr dimstar'
    print "matched AE: NEW type dimexpr dimstar", [p[i] for i in range(len(p))]
    p[0] = Node('ae_new', [p[2], p[3], p[4]], [])

def p_dimexpr(p):
    'dimexpr : LSQUARE AE RSQUARE'
    print "matched dimexpr : LSQUARE AE RSQUARE", [p[i] for i in range(len(p))]
    p[0] = Node('dimexpr', [p[2]], [])

def p_dimstar(p):
    '''dimstar : LSQUARE RSQUARE dimstar
               | empty
    '''
    if p[1] is not None:
        print "matched dimstar : LSQUARE RSQUARE dimstar", [p[i] for i in range(len(p))]
        p[0] = Node('dimstar', [p[3]], [])

    else:
        print "matched dimstar : empty",  [p[i] for i in range(len(p))]
        p[0] = Node('dimstar_empty', [], [p[1]])

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
    print "matched binop: PLUS| MINUS| ...|GTHANEQ",  [p[i] for i in range(len(p))]
    #p[0] = Node('binop', [], [p[1]])
    p[0] = p[1]

def p_unop(p):
    '''unop : MINUS
            | NOT
    '''
    print "matched unop: MINUS | NOT",  [p[i] for i in range(len(p))]
    #p[0] = Node('unop', [], [p[1]])
    p[0] = p[1]

def calc_column(token_lexpos):
    nline_index = test_file_input.rfind('\n', 0, token_lexpos)
    return token_lexpos - nline_index

def p_error(p):
    print "Syntax error at line ", lexer.line_count, " column ", calc_column(p.lexpos), " Offending token:", p
    exit(1)

def p_empty(p):
    'empty  :   '
    #p[0] = Node('empty', [], [])
    p[0] = None



#Class representing an Interference Graph
#interference_dict          : Key = Vertex v
#                           : Value = List of vertices interfering with v
#spill_vertex_exception_list: List that contains the exceptions to choice of spill_vertex. Used to fully color the graph
class Interference_Graph:
    interference_dict={}
    spill_vertex_exception_list=[]

    #Initializes the interference_dict using in_list, and spill_exception_list
    def __init__(self, in_list, spill_vertex_exception_list):
        vertex_list=[]
        neighbor_list=[]
        for i in in_list:
            for j in i:
                self.interference_dict[j] = []
        for i in in_list:
            #self.interference_dict[i]
            vertex_list = list(i)
            for j in vertex_list:
                neighbor_list=[x for x in vertex_list if x!=j]
                for k in neighbor_list:
                    dict_val = self.interference_dict[j]
                    if k not in dict_val:
                        dict_val.append(k)
                    self.interference_dict[j] = dict_val
        self.spill_vertex_exception_list = spill_vertex_exception_list
        #print "init: ", self.interference_dict, self.spill_vertex_exception_list

    #Remove the vertex and all edges corresponding to the vertex from the interference_dict
    def remove_vertex(self, dict, vertex):
        neighbor_list = []
        for key, value in dict.iteritems():
            if vertex in value:
                neighbor_list = value
                neighbor_list.remove(vertex)
                dict[key] = neighbor_list
        del dict[vertex]
        return dict

    #Select a spill vertex based on degree of vertices. Selects the highest degree vertex not in spill_vertex_exception_list
    def select_spill_vertex(self, dict):
        max_value_length = -1
        for key, value  in dict.iteritems():
            if len(value) > max_value_length and key not in self.spill_vertex_exception_list:
                max_key = key
                max_value_length = len(value)
        return max_key

    #Allocates registers to temporaries using a stack. Performs spilling if necessary
    #register_alloc_dict    :   Key     =   variable or vertex in interference graph
    #                           Value   =   register allocated to the variable
    def allocate_registers(self, num_registers):
        stack = []
        spill_vertex_list = []
        registers_list = temp_registers[:num_registers]
        register_alloc_dict={}
        k = len(registers_list)
        dict_copy = copy.deepcopy(self.interference_dict)
        #1) Keep removing nodes from the graph until atleast one of the vertices has degree<k
        #2) If no such node exists, choose a spill node and try to remove nodes with degree<k
        #Removed nodes are pushed into a stack
        #Continue 1) and 2) until all nodes are in the stack
        length = len(self.interference_dict)
        while(len(stack) != length):
            main_copy = copy.deepcopy(dict_copy)
            flag = 0
            for key, value in main_copy.iteritems():
                if key in dict_copy and len(value) < k:
                    flag += 1
                    stack.append(key)
                    dict_copy = self.remove_vertex(dict_copy, key)
            #No vertex exists with degree < k. Need to spill
            if flag == 0:
                spill_vertex_list.append(self.select_spill_vertex(dict_copy))
                stack.append(spill_vertex_list[len(spill_vertex_list)-1])
                dict_copy = self.remove_vertex(dict_copy, spill_vertex_list[len(spill_vertex_list)-1])
                #self.interference_dict = dict_copy

        #print dict_copy, self.interference_dict, stack, spill_vertex_list, self.spill_vertex_exception_list
        # Stack contains variables in the order of register allocation
        # Pop variables from stack and allocate a register that is not a register of a neighbor variable
        for key in self.interference_dict:
            register_alloc_dict[key] = ""
        while(len(stack)>0):
            var = stack.pop()
            if var in spill_vertex_list:
                continue
            for i in registers_list:
                count = 0
                register_alloc_dict[var] = i
                for neighbor in self.interference_dict[var]:
                    if register_alloc_dict[var] != register_alloc_dict[neighbor]:
                        count += 1
                #Cannot allocate register to this variable. Need to spill from and to memory
                if(count != len(self.interference_dict[var])):
                    register_alloc_dict[var] = ""
                #Allocation of register i to variable var successful
                if(count == len(self.interference_dict[var])):
                    break
        #print register_alloc_dict, spill_vertex_list
        return register_alloc_dict, spill_vertex_list

    #Checks if register allocation is complete
    #If either the variable has a register in register_alloc_dict or the variable is in spill_vertex_list, the graph is colored successfully
    def isColoredFully(self, register_alloc_dict, spill_vertex_list):
        for key, value in register_alloc_dict.iteritems():
            if value != '':
                continue
            elif value == '' and key in spill_vertex_list:
                continue
            else:
                return 0
        return 1



#Class representing intermediate code for the input program
#ircode_list            =   list representing the intermediate code for the program
#defined_list            =   list of define(s) sets for each statement s
#used_list               =   list of use(s) sets for each statement s
#succ_list              =   successor list for all statements in program
#pred_list              =   predecessor list for all sttements in program
#label_table            =   dictionary containing (label_name, successor_statement_to_label_name) pairs
#in_list                =   list of in(s) sets for each statement s
#out_list               =   list of out(s) sets for each statement s
#register_alloc_dict    =   map of variable to register allocated
#spill_vertex_list      =   list of spill vertices
#optimized_ircode_list  =   ircode_list, with variables either replaced by their allocated registers or spilled/restored from memory
#sc_label_counter       =   counter for the short-circuit labels. Used in AND(&&), OR(||) and NOT(!) statements
class IRCode:
    ircode_list = []
    defined_list = []
    used_list =[]
    succ_list = []
    pred_list = []
    label_table = {}
    in_list = []
    out_list = []
    register_alloc_dict = {}
    spill_vertex_list = []
    optimized_ircode_list = []
    sc_label_counter = 0

    def __init__(self):
        pass

    def display(self):
            print self.ircode_list

    #Make defined_list, used_list, succ_list of the same length
    def make_llengths_equal(self):
        for i in range(len(self.ircode_list)):
            self.defined_list.append([])
            self.used_list.append([])
            self.succ_list.append([])
            self.pred_list.append([])


    #Utility function to stringify the intermediate code in string
    def stringify(self):
        for i in range(len(self.ircode_list)):
            for j in range(len(self.ircode_list[i])):
                self.ircode_list[i][j] = str(self.ircode_list[i][j])

    #Get the defined variables in a statement(ircode_list)
    def getDefinedVars(self, ircode_list):
        if ircode_list[1] == '=':
            return [ircode_list[0]]

        elif ircode_list[0] == 'halloc':
            assert len(ircode_list) == 3
            return [ircode_list[1]]

        return []

    #Get the used variables in a statement(ircode_list)
    def getUsedVars(self, ircode_list):
        res_list = []
        label_pattern = re.compile('label_[0-9]+')
        number_pattern = re.compile('[0-9]+')

        #halloc statement
        if ircode_list[0] == 'halloc':
            #print "inside getUsedVars:", ircode_list
            assert len(ircode_list) == 3
            return [ircode_list[2]]

        #lw and sw statements
        if ircode_list[0] == 'lw' or ircode_list[0] =='sw':
            print ircode_list
            if len(ircode_list) == 5:
                assert ircode_list[2]=='(' and ircode_list[4]==')'
                return [ircode_list[1], ircode_list[3]]

        #Assignment statement
        if ircode_list[1] == '=':
            if ircode_list[2] == 'input':
                return []
            elif len(ircode_list)==3 and number_pattern.match(ircode_list[2]) is None and label_pattern.match(ircode_list[2]) is None:
                res_list.append(ircode_list[2])
            elif len(ircode_list)==4:
                assert(ircode_list[2]=='-' or ircode_list[2]=='!')
                res_list.append(ircode_list[3])
            elif(len(ircode_list)==5) :
                if number_pattern.match(ircode_list[2]) is None:
                    res_list.append(ircode_list[2])
                if number_pattern.match(ircode_list[4]) is None:
                    res_list.append(ircode_list[4])
            return res_list
        #Print statement
        elif ircode_list[0] == 'print':
            assert len(ircode_list) == 2
            return [ircode_list[1]]
        #Unconditional branch statement
        elif ircode_list[0] == 'b':
            label_pattern = re.compile('label_[0-9]+')
            assert(label_pattern.match(ircode_list[1]) is not None)
            return []
        #Conditiona branch statement
        elif ircode_list[0] == 'beq':
            if number_pattern.match(ircode_list[1]) is None:
                res_list.append(ircode_list[1])
            if number_pattern.match(ircode_list[2]) is None:
                res_list.append(ircode_list[2])
            assert(label_pattern.match(ircode_list[3]) is not None)
            return res_list

        #Generate label successor table
        elif label_pattern.match(ircode_list[0]) is not None:
            val = self.ircode_list.index(ircode_list)+1
            self.label_table[ircode_list[0]] = val
            return []
        #Default return value
        return []

    def getSuccHelper(self, index, res_list):
        print index, len(self.ircode_list) #self.label_table, self.ircode_list[index]
        label_pattern = re.compile('label_[0-9]+')
        number_pattern = re.compile('[0-9]+')

        if index == len(self.ircode_list):
            res_list.append(index)
            return

        if self.ircode_list[index][0] == 'b' or self.ircode_list[index][0] == 'beq':
            if self.ircode_list[index][0] == 'b' and label_pattern.match(self.ircode_list[index][1]) is not None:
                self.getSuccHelper(self.label_table[self.ircode_list[index][1]], res_list)

            elif self.ircode_list[index][0] == 'beq' and label_pattern.match(self.ircode_list[index][3]) is not None:
                self.getSuccHelper(self.label_table[self.ircode_list[index][3]], res_list)
                self.getSuccHelper(index+1, res_list)

        elif label_pattern.match(self.ircode_list[index][0]) is not None and self.ircode_list[index][1]==':':
            self.getSuccHelper(self.label_table[self.ircode_list[index][0]], res_list)

        else:
            if res_list == []:
                res_list.append(index+1)
            else:
                res_list.append(index)


    #Get the successor statements for a statement indexed by index
    def getSucc(self, index):
        res_list = []
        #print index, len(self.ircode_list) #, self.label_table, self.ircode_list[index]
        '''
        #the current statement is a label definition
        if label_pattern.match(self.ircode_list[index][0]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index][0]])
        #the current statement is a unconditional branch
        elif self.ircode_list[index][0] == 'b' and label_pattern.match(self.ircode_list[index][1]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index][1]])
        #the current statement is a conditional branch
        elif self.ircode_list[index][0] == 'beq' and label_pattern.match(self.ircode_list[index][3]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index][3]])
            if label_pattern.match(self.ircode_list[index+1][0]) is not None:
                self.succ_list[index].append(self.label_table[self.ircode_list[index+1][0]])
            else:
                self.succ_list[index].append(index+1)
        else:
            if index!=len(self.ircode_list)-1 and label_pattern.match(self.ircode_list[index+1][0]) is not None:
                self.succ_list[index].append(self.label_table[self.ircode_list[index+1][0]])
            else:
                self.succ_list[index].append(index+1)

        if index!= len(self.ircode_list)-1 and self.ircode_list[index][0] != 'b' and self.ircode_list[index][0] != 'beq' and self.ircode_list[index+1][0] == 'b' and label_pattern.match(self.ircode_list[index+1][1]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index+1][1]])
        #the current statement is a conditional branch
        elif index!= len(self.ircode_list)-1 and self.ircode_list[index][0] != 'b' and self.ircode_list[index][0] != 'beq' and self.ircode_list[index+1][0] == 'beq' and label_pattern.match(self.ircode_list[index+1][3]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index+1][3]])
        '''
        if index != len(self.ircode_list)-1:
            self.getSuccHelper(index, res_list)
        self.succ_list[index] = res_list


    #Check the 'define-before-use' property for all statements
    def doStaticSemanticsCheck(self):
        for i in range(0, len(self.used_list), 1):
            for j in self.used_list[i]:
                flag = 0
                for k in range(i):
                    if j in self.defined_list[k]:
                        flag = 1
                        break
                if flag == 0:
                    print "Line ", i+1, ": Static semantic check failed: Symbol", j, "used before definition"
                    exit(1)
        '''
        print len(self.ircode_list), len(self.succ_list), len(self.pred_list)
        for i in range(len(self.ircode_list)):
            for j in range(len(self.succ_list[i])):
                print i, self.ircode_list[i], self.defined_list[i], self.used_list[i], self.succ_list[i], j
                self.pred_list[self.succ_list[i][j]].append(i)

        print len(self.succ_list), len(self.pred_list)
        for i in range(len(self.defined_list)):
            print i, self.ircode_list[i], self.defined_list[i], self.used_list[i], self.succ_list[i], self.pred_list[i]
        '''

    #Check if the program represented by the ircode_list is well-formed
    def check_if_wellformed(self):
        self.make_llengths_equal()
        self.stringify()
        for i in range(len(self.ircode_list)):
            #print self.getDefinedVars(self.ircode_list[i]), self.getUsedVars(self.ircode_list[i])
            self.defined_list[i]=self.getDefinedVars(self.ircode_list[i])
            self.used_list[i]=self.getUsedVars(self.ircode_list[i])
            #print i, self.ircode_list[i], self.defined_list[i], self.used_list[i]

        print "len(ircodelist):", len(self.ircode_list)
        for i in range(len(self.ircode_list)):
            print i, self.ircode_list[i]
        print "label table :", self.label_table
        #Generate successor lists for all statements
        for i in range(len(self.ircode_list)-1,-1,-1):
            self.getSucc(i)
        #print self.label_table
        #print self.defined_list, len(self.defined_list), self.used_list, len(self.used_list), self.succ_list, len(self.succ_list)

        print "\tircode:def, use, succ"
        for i in range(len(self.ircode_list)):
            print i, self.ircode_list[i], self.defined_list[i], self.used_list[i], self.succ_list[i]

        #Perform a static semantic check
        #self.doStaticSemanticsCheck()

        #Calculate in and out lists for all statements
        self.defined_list.append([])
        self.used_list.append([])
        for i in range(len(self.defined_list)):
            self.in_list.append(Set())
            self.out_list.append(Set())
        #for i in range(len(self.ircode_list)):
        #    print i, self.ircode_list[i], self.defined_list[i], self.used_list[i], self.succ_list[i], self.in_list[i], self.out_list[i]
        #print len(self.defined_list), len(self.used_list), len(self.succ_list), len(self.in_list), len(self.out_list)
        #for i in range(len(self.defined_list)):
        #    print i, self.defined_list[i], self.used_list[i], self.in_list[i], self.out_list[i]

        #Do backward passes till the least fixed point is reached
        while(1):
            in_list_dup = self.in_list
            out_list_dup = self.out_list

            for i in range(len(self.ircode_list)-1, -1, -1):
                for j in range(len(self.succ_list[i])):
                    self.out_list[i] = self.out_list[i].union(self.in_list[self.succ_list[i][j]])
                self.in_list[i] = Set(self.used_list[i]).union(self.out_list[i].difference(Set(self.defined_list[i])))

            if in_list_dup == self.in_list and out_list_dup == self.out_list:
                break

        print "\tircode: def, use, in, out"
        for i in range(len(self.ircode_list)):
            print i, self.ircode_list[i], self.defined_list[i], self.used_list[i],  self.in_list[i], self.out_list[i]

    #Performs liveness analysis on the statements in the program
    #1)Calculates in_list and out_list for all statements in the program
    #2)Checks if the graph can be fully colored with the given num_registers by selecting different spill vertex in each iteration
    def performLivenessAnalysis(self):
        register_alloc_dict = {}
        spill_vertex_list = []
        spill_vertex_exception_list = []
        is_colored = 0
        num_tries = 0
        max_num_tries = 10
        while is_colored != 1:
            i_graph = Interference_Graph(self.in_list, spill_vertex_exception_list)
            if spill_vertex_exception_list == i_graph.interference_dict.keys() or num_tries>max_num_tries:
                print "Register allocation not possible for this program"
                exit(1)
            else:
                register_alloc_dict, spill_vertex_list = i_graph.allocate_registers(num_registers)
                is_colored = i_graph.isColoredFully(register_alloc_dict, spill_vertex_list)
                if len(spill_vertex_list) != 0:
                    spill_vertex_exception_list.append(spill_vertex_list[0])
                num_tries+=1
        self.register_alloc_dict, self.spill_vertex_list = register_alloc_dict, spill_vertex_list
        print "register_alloc_dict:", self.register_alloc_dict, "spill_vertex_list:", self.spill_vertex_list

    #Get a free register that is not used in the statement indexed by index
    def getFreeReg(self, index):
        #print self.ircode_list[index]
        reg_list = temp_registers[:num_registers]
        for i in self.ircode_list[index]:
            if i in reg_list:
                reg_list.remove(i)
        if len(reg_list)==0:
            print "Register allocation not possible for spilled variables"
            exit(1)
        return reg_list[0]

    #Replaces the variable names with allocated register names from register_alloc_dict
    #Replaces occurrences of spill variables with load and store statements. Uses only register t9 for this purpose
    def optimize(self):
        label_pattern = re.compile('label_[0-9]+')
        #print "defined_list:", self.defined_list, "used_list:", self.used_list
        #print "inside optimize:", "ircode_list", self.ircode_list, "register_alloc_dict:", self.register_alloc_dict, "spill_vertex_list:", self.spill_vertex_list
        optimized_ircode_list = []
        for j in range(len(self.ircode_list)):
            #print self.ircode_list[j], self.defined_list[j], self.used_list[j], self.in_list[j], self.out_list[j]

            if self.ircode_list[j][1] == '=' and self.ircode_list[j][0] not in self.register_alloc_dict.keys():
                continue


            for i in self.ircode_list[j]:
                #Special handling for branch statements
                if self.ircode_list[j][0] == 'b' and label_pattern.match(self.ircode_list[j][1]) is not None:
                    break

                elif self.ircode_list[j][0] == 'beq' and label_pattern.match(self.ircode_list[j][3]) is not None:
                    if self.ircode_list[j][1] in self.register_alloc_dict.keys() and self.register_alloc_dict[self.ircode_list[j][1]]!='':
                        self.ircode_list[j][1] = self.register_alloc_dict[self.ircode_list[j][1]]
                    break
                #Replace the variable names with allocated registers from register_alloc_dict
                elif i in self.register_alloc_dict.keys() and self.register_alloc_dict[i]!='':
                    index = self.ircode_list[j].index(i)
                    self.ircode_list[j][index] = self.register_alloc_dict[i]
                    #print self.ircode_list[j]

            #Special handling of branch statements
            if self.ircode_list[j][0] == 'b' and label_pattern.match(self.ircode_list[j][1]) is not None:
                optimized_ircode_list.append((self.ircode_list[j]))

            elif self.ircode_list[j][0] == 'beq' and label_pattern.match(self.ircode_list[j][3]) is not None:
                optimized_ircode_list.append((self.ircode_list[j]))

            #Check if the statement can be dropped and
            else:
                flag = 0
                for i in self.ircode_list[j]:
                    if i not in self.used_list[j] and i not in self.defined_list[j]:
                        flag += 1
                if flag == len(self.ircode_list[j]):
                    optimized_ircode_list.append(self.ircode_list[j])
            #optimized_ircode_list.append(self.ircode_list[j])
            '''for key,value in self.register_alloc_dict.iteritems():
                if key in self.ircode_list[j] and value!='':
                    index = self.ircode_list[j].index(key)
                    self.ircode_list[j][index] = value
                    optimized_ircode_list.append(self.ircode_list[j])'''

            #print self.ircode_list[j], self.used_list[j], self.defined_list[j]

            #If the spilled variable is on the rhs, restore from memory
            for i in self.used_list[j]:
                if i in self.spill_vertex_list:
                        treg = self.getFreeReg(j)
                        optimized_ircode_list.append(['lw',treg,i])
                        index = self.ircode_list[j].index(i)
                        self.ircode_list[j][index] = treg
                        optimized_ircode_list.append(self.ircode_list[j])

            #If the spilled variable is on the lhs, store to memory
            for i in self.defined_list[j]:
                if i in self.spill_vertex_list:
                        treg = self.getFreeReg(j)
                        index = self.ircode_list[j].index(i)
                        self.ircode_list[j][index] = treg
                        optimized_ircode_list.append(self.ircode_list[j])
                        optimized_ircode_list.append(['sw', treg, i])

        self.optimized_ircode_list = optimized_ircode_list
        #print "optimized ircode:"
        #for i in range(len(optimized_ircode_list)):
        #    print " ".join(optimized_ircode_list[i])


    #Generates MIPS code from intermediate code for each statement arg_list
    def genASMstatement(self, ircode_list):
        #print "stmt:", ircode_list
        result = ""
        number_pattern = re.compile('[+-]?[0-9]+')
        label_pattern = re.compile('label_[0-9]+')
        register_pattern = re.compile(r'\$t[0-9]+')
        #Simply propagate branch statements with minor changes
        if ircode_list[0] == 'b' or label_pattern.match(ircode_list[0]) is not None:
            result = " ".join(ircode_list)

        elif ircode_list[0] == 'beq':
            assert(len(ircode_list)==4)
            result += "beq "+ircode_list[1]+", "+ircode_list[2]+", "+ircode_list[3]

        #Print the contents of register and also print a new line
        elif ircode_list[0] == 'print':
            #print "inside print"
            result += "move $a0, "+ircode_list[1]+"\n\t"
            result += "li $v0, 1\n\t"
            result += "syscall\n\t"
            result += 'la $a0, new_line\n\t'
            result += 'li $v0, 4\n\t'
            result += 'syscall'

        #Get input from console
        elif ircode_list[1] == '=' and ircode_list[2] == 'input':
            result += "li $v0, 5\n\t"
            result += "syscall\n\t"
            result += "move "+ircode_list[0]+", $v0"

        #load or store statements
        elif ircode_list[0] == 'lw' or ircode_list[0] == 'sw':
            assert(len(ircode_list) == 3 or len(ircode_list) == 5)
            if len(ircode_list) == 3:
                result += ircode_list[0]+" "+ircode_list[1]+", "+ircode_list[2]
            elif len(ircode_list) == 5:
                result += ircode_list[0]+" "+ircode_list[1]+", "+ircode_list[2]+ircode_list[3]+ircode_list[4]

        elif ircode_list[0] == 'halloc':
            #print "inside genASM statement:halloc", ircode_list
            result += "li $v0, 9\n\t"
            result += "move $a0, "+ircode_list[2]+'\n\t'
            result += "syscall\n\t"
            result += "move "+ ircode_list[1]+ ", $v0"

        #Assignment statements
        elif ircode_list[1] == '=':
            #print ircode_list
            assert(register_pattern.match(ircode_list[0]) is not None)

            #Simple assignment statements
            if len(ircode_list) == 3:
                if number_pattern.match(ircode_list[2]) is not None:
                    result += "li "+ircode_list[0]+", "+ircode_list[2]
                elif register_pattern.match(ircode_list[2]) is not None:
                    result += "move "+ircode_list[0]+", "+ircode_list[2]

            #Statements involving Unary operators
            elif len(ircode_list) == 4:
                operand1 = ircode_list[0]
                operand2 = ircode_list[3]
                operator = ircode_list[2]
                if operator == '-':
                    result += "neg "+ operand1+ ", "+ operand2
                #Generate short-circuit MIPS code for ! operator
                elif operator == '!':
                    sc_label_list = ['sc_label_'+str(self.sc_label_counter), 'sc_label_'+str(self.sc_label_counter+1)]
                    self.sc_label_counter += 2
                    result += "bne "+ operand2+ ", 0, "+ sc_label_list[0]+"\n\t"
                    result += "li "+ operand1+ ", 1\n\t"
                    result += "b "+ sc_label_list[1]+ "\n"
                    result += sc_label_list[0]+ ":\n\t"
                    result += "li "+ operand1+ ", 0\n"
                    result += sc_label_list[1]+ ":"

            #Statements involving Binary operators
            elif len(ircode_list) == 5:
                operand1 = ircode_list[0]
                operator = ircode_list[3]
                if register_pattern.match(ircode_list[2]) is not None:
                    operand2 = ircode_list[2]
                    operand3 = ircode_list[4]
                else:
                    operand2 = ircode_list[4]
                    operand3 = ircode_list[2]

                if number_pattern.match(operand2) is not None:
                    result += 'li $t9, '+ operand2+ '\n\t'
                    operand2 = '$t9'

                #Generate MIPS code depending on if the operator is a +,-,*,/,%
                if operator == '+':
                    result += "add "+operand1+", "+operand2+", "+operand3
                elif operator == '-':
                    result += "sub "+operand1+", "+operand2+", "+operand3
                elif operator == '*':
                    result += "mul "+operand1+", "+operand2+", "+operand3
                elif operator == '/':
                    result += "divu "+operand1+", "+operand2+", "+operand3
                elif operator == '%':
                    result += "li $t9, "+operand3+"\n\t"
                    result += "divu "+ operand2+", $t9\n\t"
                    result += "mfhi "+operand1

                #Generate MIPS code depending on if the operator is a ==,!=,>,>=,<,<=
                elif operator == '==':
                    result += 'seq '+operand1+', '+operand2+', '+operand3
                elif operator == '!=':
                    result += 'sne '+operand1+', '+operand2+', '+operand3
                elif operator == '>':
                    result += 'sgt '+operand1+', '+operand2+', '+operand3
                elif operator == '>=':
                    result += 'sge '+operand1+', '+operand2+', '+operand3
                elif operator == '<':
                    result += 'slt '+operand1+', '+operand2+', '+operand3
                elif operator == '<=':
                    result += 'sle '+operand1+', '+operand2+', '+operand3

                #Generate short-circuit MIPS code for && operator
                elif operator == '&&':
                    sc_label_list = ['sc_label_'+str(self.sc_label_counter), 'sc_label_'+str(self.sc_label_counter+1)]
                    self.sc_label_counter += 2
                    result += 'beq '+ operand2+ ', 0, '+ sc_label_list[0]+'\n\t'
                    if number_pattern.match(operand3) is not None:
                        result+= 'li '+ operand1+ ', '+operand3+'\n\t'
                    else:
                        result+= 'move '+ operand1+ ', '+operand3+'\n\t'
                    result += 'b '+ sc_label_list[1]+'\n'
                    result += sc_label_list[0]+ ':\n\t'
                    result += 'li '+ operand1+', 0\n'
                    result += sc_label_list[1]+ ':'

                #Generate short-circuit MIPS code for || operator
                elif operator == '||':
                    sc_label_list = ['sc_label_'+str(self.sc_label_counter), 'sc_label_'+str(self.sc_label_counter+1)]
                    self.sc_label_counter += 2
                    result += 'bne '+ operand2+ ', 0, '+ sc_label_list[0]+'\n\t'
                    if number_pattern.match(operand3) is not None:
                        result+= 'li '+ operand1+ ', '+operand3+'\n\t'
                    else:
                        result+= 'move '+ operand1+ ', '+operand3+'\n\t'
                    result += 'b '+ sc_label_list[1]+'\n'
                    result += sc_label_list[0]+ ':\n\t'
                    if number_pattern.match(operand2) is not None:
                        result+= 'li '+ operand1+ ', '+operand2+'\n'
                    else:
                        result+= 'move '+ operand1+ ', '+operand2+'\n'
                    result += sc_label_list[1]+ ':'

        else:
            print "Unhandled stmt in genASMstatement:", ircode_list
            exit(1)

        result+='\n'
        return result

    #Generates MIPS code from intermediate code for the whole program
    def genASM(self):
        #Create the output .asm file
        output_file_name = str(test_file_name).strip(".proto")+".asm"
        output_file = open(output_file_name, "a")

        #Add $ to the registers in the intermediate code
        register_pattern = re.compile('t[0-9]+')
        for i in range(len(self.optimized_ircode_list)):
            for j in range(len(self.optimized_ircode_list[i])):
                if register_pattern.match(self.optimized_ircode_list[i][j]) is not None:
                    self.optimized_ircode_list[i][j] = '$'+self.optimized_ircode_list[i][j]

        #Write data section
        #data_section contains new_line string("\n") and all spill variables are allocated a word in memory
        output_file.write(".data\n\n")
        output_file.write("new_line:	.asciiz \""+"\\n\"\n")
        for vertex in self.spill_vertex_list:
            output_file.write("\t"+vertex+" :\t.word 0\n")
        #Write text section starting form main label
        output_file.write("\n\n")
        output_file.write(".text\n\nmain:\n")
        for line in range(len(self.optimized_ircode_list)):
            output_file.write("\t"+self.genASMstatement(self.optimized_ircode_list[line]))
        #Write exit label
        output_file.write("exit:\n\tli $v0, 10\n\tsyscall\n")
        output_file.close()



#Class representing the Abstract Syntax Node in the AST
#type       =   Type of the AST node(binop, unop, if_stmt, while_stmt,etc)
#children   =   Children of the AST node(Non-terminal symbols used by the node)
#leaves     =   Leaves of the AST node(Terminal symbols used by the node)
#define_list=   define_list at the node
#used_list  =   used_list at the node
class Node:

    def __init__(self, ntype, children=[], leaves=[]):
        self.type = ntype
        self.children = children
        self.leaves = leaves
        self.temp_index = ''
        self.label_list = []
        self.define_list = []
        self.used_list = []
        self.node_ircode = []
        self.prev_ircode_length = 0

        self.sib_list = []
        self.param = {}

    #Helper method to display the whole AST recursively
    def display(self):
        print "Node(", hex(id(self)), "):", self.type, self.children, self.leaves, self.sib_list, self.param
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.children[i].display()

    '''def checkForStaticSemantics(self, sib_list):
        global sym_deflist
        print "Node(", hex(id(self)), "):", self.type, self.children, self.leaves, self.sib_list, sym_deflist
        self.sib_list = sib_list

        if self.type == 'var':
            if self.leaves[0] not in symtab:
                symtab[self.leaves[0]] = ['']
            else:
                symtab[self.leaves[0]].append('')

        if self.type == 'se_assign':
            sym_deflist.append(self.children[0].leaves[0])

        if self.type == 'lhs_id':
            if self.leaves[0] not in symtab:
                print self.leaves[0], symtab
                print "Static Semantic check failed : Symbol", self.leaves[0], "defined/used before definition"
                exit(1)
            if self.leaves[0] not in sym_deflist:
                print self.leaves[0], sym_deflist
                print "Static semantic check failed : Symbol", self.leaves[0], "used before definition"
                exit(1)
            return self.leaves[0]

        if self.type == 'stmt_block':
            sym_index = len(sym_deflist)
            sym_deflist.append('None')

        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                ret = self.children[i].checkForStaticSemantics(self.children)

        if self.type == 'stmt_block':
            sym_deflist = sym_deflist[:sym_index]
    '''

    def updateParam(self, param):
        #print "inside param of ", "Node(", hex(id(self)), ")", self.param
        self.param = param
        #print "inside param of ", "Node(", hex(id(self)), ")", self.param

    def buildTypeDict(self, sib_list, param):
        self.sib_list = sib_list
        for key, value in param.iteritems():
            self.param[key] = param[key]

        #print "buildTypeDict : Node(", hex(id(self)), "):", self.type, self.children, self.leaves, self.sib_list, self.param, sym_deflist

        if self.type == 'type_int':
            if self.sib_list[0].type == 'varlist':
                assert len(self.sib_list)==1
                self.sib_list[0].updateParam({'type':'int'})

        if self.type == 'type_bool':
            if self.sib_list[0].type == 'varlist':
                assert len(self.sib_list)==1
                self.sib_list[0].updateParam({'type':'bool'})

        if self.type == 'var':
            if len(self.param) != 0:
                type_dict[self.leaves[0]] = self.param['type']

        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                ret = self.children[i].buildTypeDict(self.children[i+1:], self.param)
                if self.type == 'var' and ret == {'isArray':1}:
                    array_list.append(self.leaves[0])

        if self.type == 'dimstar':
            return {'isArray':1}

    def checkForStaticSemantics(self):
        global sym_deflist

        #print "Node(", hex(id(self)), "):", self.type, self.children, self.leaves, self.sib_list, self.param, sym_deflist

        if self.type == 'var':
            if self.leaves[0] not in symtab:
                symtab[self.leaves[0]] = ['']
            else:
                symtab[self.leaves[0]].append('')



        #if self.type == 'varlist':
        #    print "\t inside varlist", self.param

        elif self.type == 'lhs_ae':
            if 'valtype' not in self.param.keys():
                self.param.update({'valtype':'rval'})

        elif self.type == 'se_assign':
            #for i in range(len(self.children)):
            #    print i, self.children[i].type, self.children[i].children, self.children[i].leaves
            if self.children[0].type == 'lhs_id':
                sym_deflist.append(self.children[0].leaves[0])
            elif self.children[0].type == 'lhs_ae' and self.children[0].children[0].type == 'lhs_id':
                self.children[0].param.update({'valtype':'lval'})

        elif self.type == 'lhs_id':
            if self.leaves[0] not in symtab:
                print self.leaves[0], symtab
                print "Static Semantic check failed : Symbol", self.leaves[0], "defined/used before definition"
                exit(1)
            if self.leaves[0] not in sym_deflist:
                print self.leaves[0], sym_deflist
                print "Static semantic check failed : Symbol", self.leaves[0], "used before definition"
                exit(1)
            return self.leaves[0]

        elif self.type == 'stmt_block':
            sym_index = len(sym_deflist)
            sym_deflist.append('None')

        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                ret = self.children[i].checkForStaticSemantics()

        if self.type == 'stmt_block':
            sym_deflist = sym_deflist[:sym_index]

    #Helper method to generate labels
    def gen_label(self):
        global label_count
        label_name =  "label_"+str(label_count)
        label_count += 1
        return label_name

    #Helper method to identify the children of a node
    def findpos(self):
        global ircode
        for i in range(self.prev_ircode_length, len(ircode.ircode_list), 1):
            if ircode.ircode_list[i] == [None]:
                return i
        return -1

    def gen_temp(self):
        global temp_count
        temp_name = 'x'+str(temp_count)
        temp_count += 1
        return temp_name

    def gencode(self):
        global ircode
        global symtab
        node_icode_list = []
        copy_symtab = {}
        self.prev_ircode_length = len(ircode.ircode_list)

        if self.type in ['declseq', 'declseq_empty']:
            return

        #print ircode.ircode_list, len(ircode.ircode_list), self.type

        elif self.type in ['stmt_block']:
            copy_symtab = copy.deepcopy(symtab)

        #[None] is used to identify the transition from one child to the next child
        elif self.type in ['stmt_while', 'stmt_do_while']:
            ircode.ircode_list.append([None])


        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                node_icode_list.append(self.children[i].gencode())
                if self.type in ['stmt_if', 'stmt_if_else', 'stmt_while', 'stmt_do_while', 'stmt_for']:
                    ircode.ircode_list.append([None])
            #print ircode.ircode_list

        if self.type in ['stmt_se']:
            pass

        elif self.type in ['stmt_print']:
            assert len(node_icode_list) == 1
            node_icode_list.insert(0, 'print')
            ircode.ircode_list.append(node_icode_list)

        elif self.type in ['stmt_block']:
            symtab = copy.deepcopy(copy_symtab)

        elif self.type in ['stmt_if_else']:
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = ['beq', node_icode_list[0], 0, self.label_list[0]]
            end_of_then_block = self.findpos()
            ircode.ircode_list[end_of_then_block] = ['b', self.label_list[1]]
            ircode.ircode_list.insert(end_of_then_block+1, [self.label_list[0],':'])
            ircode.ircode_list[self.findpos()] = [self.label_list[1], ':']
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['stmt_while']:
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            ircode.ircode_list[self.findpos()] = ['beq', node_icode_list[0], 0, self.label_list[1]]
            end_of_do_block = self.findpos()
            ircode.ircode_list[end_of_do_block] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_do_block+1, [self.label_list[1], ':'])
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['stmt_if']:
            self.label_list.append(self.gen_label())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = ['beq', node_icode_list[0], 0, self.label_list[0]]
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['stmt_for']:
            #print "\tPrev ircode ", ircode.ircode_list, "prev_ircode_length", self.prev_ircode_length, "node_icode_list", node_icode_list
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            end_of_aeopt = self.findpos()
            ircode.ircode_list[end_of_aeopt] = ['beq', node_icode_list[1], 0, self.label_list[3]]
            ircode.ircode_list.insert(end_of_aeopt+1, ['b', self.label_list[1]])
            ircode.ircode_list.insert(end_of_aeopt+2, [self.label_list[2], ':'])
            end_of_seopt = self.findpos()
            ircode.ircode_list[end_of_seopt] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_seopt+1, [self.label_list[1], ':'])
            end_of_stmt = self.findpos()
            ircode.ircode_list[end_of_stmt] = ['b', self.label_list[2]]
            ircode.ircode_list.insert(end_of_stmt+1, [self.label_list[3], ':'])
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['stmt_do_while']:

            #print "\tPrev ircode ", ircode.ircode_list, "prev_ircode_length", self.prev_ircode_length, "node_icode_list", node_icode_list
            self.label_list.append(self.gen_label())
            self.label_list.append(self.gen_label())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            ircode.ircode_list.pop(self.findpos())
            end_of_ae = self.findpos()
            ircode.ircode_list[end_of_ae] = ['beq', node_icode_list[1], 0, self.label_list[1]]
            ircode.ircode_list.insert(end_of_ae+1, ['b', self.label_list[0]])
            ircode.ircode_list.insert(end_of_ae+2, [self.label_list[1], ':'])
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['seopt']:
            return node_icode_list[0]

        elif self.type in ['aeopt']:
            return node_icode_list[0]

        elif self.type in ['se_assign']:
            assert(len(node_icode_list) == 2)
            #print "\t"
            if node_icode_list[0] not in symtab:
                symtab[node_icode_list[0]]=[node_icode_list[1]]
            else:
                symtab[node_icode_list[0]].append(node_icode_list[1])

            if self.children[0].type == 'lhs_id':
                node_icode_list.insert(1, '=')
                ircode.ircode_list.append(node_icode_list)
                return node_icode_list[2]

            elif self.children[0].type == 'lhs_ae':
                print "in lhs_ae: ", node_icode_list
                temp1 = node_icode_list[0]
                temp2 = node_icode_list[1]
                ircode.ircode_list.append(['sw', temp2, '(', temp1, ')'])
                return temp2
            #print "symtab", symtab
            #print "sym_deflist", sym_deflist



        elif self.type in ['se_postinc']:
            assert(len(node_icode_list) == 1)
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '+', 1])
            return temp

        elif self.type in ['se_postdec']:
            assert(len(node_icode_list) == 1)
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '-', 1])
            return temp

        elif self.type in ['se_preinc']:
            assert(len(node_icode_list) == 1)
            temp = self.gen_temp()
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '+', 1])
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            return temp

        elif self.type in ['se_predec']:
            assert(len(node_icode_list) == 1)
            temp = self.gen_temp()
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '-', 1])
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            return temp

        elif self.type in ['lhs_id']:
            assert(len(self.leaves) == 1)
            return self.leaves[0]

        elif self.type in ['lhs_ae']:
            assert(len(node_icode_list) == 2)
            #print "in gencode:lhs_ae:node_icode_list:", node_icode_list, "self.param", self.param
            temp1 = self.gen_temp()
            temp2 = self.gen_temp()
            assert node_icode_list[0] in type_dict

            if type_dict[node_icode_list[0]] == 'int':
                size = 4
            elif type_dict[node_icode_list[0]] == 'bool':
                size = 1

            if self.param['valtype'] == 'lval':
                #print "before: ", ircode.ircode_list
                ircode.ircode_list.append([temp1, '=', node_icode_list[1], '*', size])
                ircode.ircode_list.append([temp2, '=', node_icode_list[0], '+', temp1])
                #print "after: ", ircode.ircode_list
                return temp2

            if self.param['valtype'] == 'rval':
                #print "before: ", ircode.ircode_list
                ircode.ircode_list.append([temp1, '=', node_icode_list[1], '*', size])
                ircode.ircode_list.append([temp2, '=', node_icode_list[0], '+', temp1])
                if type_dict[node_icode_list[0]] == 'int':
                    ircode.ircode_list.append(['lw', temp1, '(', temp2, ')'])
                if type_dict[node_icode_list[0]] == 'bool':
                    ircode.ircode_list.append(['lw', temp1, '(', temp2, ')'])
                #print "after: ", ircode.ircode_list
                return temp1


        elif self.type in ['ae_binop']:
            assert(len(node_icode_list) == 2)
            assert(len(self.leaves) == 1)
            temp = self.gen_temp()
            node_icode_list.insert(1, self.leaves[0])
            node_icode_list.insert(0, '=')
            node_icode_list.insert(0, temp)
            ircode.ircode_list.append(node_icode_list)
            return temp

        elif self.type in ['ae_unop']:
            assert len(node_icode_list) == 1
            assert  len(self.leaves) == 1
            temp =self.gen_temp()
            node_icode_list.insert(0, self.leaves[0])
            node_icode_list.insert(0, '=')
            node_icode_list.insert(0, temp)
            ircode.ircode_list.append(node_icode_list)
            return temp

        elif self.type in ['ae_lhs']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['ae_se']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['ae_group']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['ae_input']:
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', 'input'])
            return temp
            #return 'input'

        elif self.type in ['ae_intconst']:
            assert len(self.leaves) == 1
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', self.leaves[0]])
            return temp
            #return self.leaves[0]

        elif self.type in ['ae_true']:
            assert len(self.leaves) == 1
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', 1])
            return temp
            #return 1

        elif self.type in ['ae_false']:
            assert len(self.leaves) == 1
            temp = self.gen_temp()
            ircode.ircode_list.append([temp, '=', 0])
            return temp
            #return 0

        elif self.type in ['ae_new']:
            #print "inside ae_new", node_icode_list
            assert len(node_icode_list) == 3
            temp = self.gen_temp()
            temp1 = self.gen_temp()

            if node_icode_list[0] == 'sizeof_int':
                node_icode_list[0] = 4
            elif node_icode_list[0] == 'sizeof_bool':
                node_icode_list[0] = 1

            ircode.ircode_list.append([temp1, '=', node_icode_list[1], '*', node_icode_list[0]])
            ircode.ircode_list.append(['halloc', temp, temp1])
            return temp

        elif self.type in ['dimexpr']:
            assert  len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['dimstar']:
            pass

        elif self.type in ['type_int']:
            return 'sizeof_int'

        elif self.type in ['type_bool']:
            return 'sizeof_bool'

    '''
    #Generate intermediate code for the statements in the program
    def gencode(self):
        global temp_count
        global ircode
        node_icode_list = []
        self.prev_ircode_length = len(ircode.ircode_list)

        #print ircode.ircode_list, len(ircode.ircode_list), self.type

        #[None] is used to identify the transition from one child to the next child
        if self.type in ['stmt_while']:
            ircode.ircode_list.append([None])

        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                node_icode_list.append(self.children[i].gencode())
                if self.type in ['if_stmt', 'if_else_stmt', 'while_stmt']:
                    ircode.ircode_list.append([None])

        #Generate code depending upon the type of the AST node
        if self.type == 'assign_stmt':
            node_icode_list.insert(0, '=')
            node_icode_list.insert(0, self.leaves[0])
            ircode.ircode_list.append(node_icode_list)

        elif self.type == 'print_stmt':
            node_icode_list.insert(0, 'print')
            ircode.ircode_list.append(node_icode_list)

        elif self.type == 'block_stmt':
            pass

        elif self.type == 'if_stmt':
            self.label_list.append(self.genlabel())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = ['beq',node_icode_list[0], 0, self.label_list[0]]
            ircode.ircode_list[self.findpos()] = [self.label_list[0],':']
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type == 'if_else_stmt':
            self.label_list.append(self.genlabel())
            self.label_list.append(self.genlabel())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = ['beq',node_icode_list[0], 0, self.label_list[0]]
            end_of_then_block = self.findpos()
            ircode.ircode_list[end_of_then_block] = ['b',self.label_list[1]]
            ircode.ircode_list.insert(end_of_then_block+1, [self.label_list[0],':'])
            ircode.ircode_list[self.findpos()] =  [self.label_list[1],':']
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type == 'while_stmt':
            self.label_list.append(self.genlabel())
            self.label_list.append(self.genlabel())
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            ircode.ircode_list[self.findpos()] = ['beq', node_icode_list[0], 0, self.label_list[1]]
            end_of_do_block = self.findpos()
            ircode.ircode_list[end_of_do_block] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_do_block+1, [self.label_list[1], ':'])
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)


        elif self.type == 'rhs_ae':
            return node_icode_list[0]

        elif self.type == 'rhs_input':
            return 'input'

        elif self.type == 'ae_group':
            return node_icode_list[0]

        elif self.type == 'ae_binop':
            assert(len(node_icode_list)==2)
            node_icode_list.insert(1, self.leaves[0])
            node_icode_list.insert(0, '=')
            self.temp_index = 'x'+str(temp_count)
            node_icode_list.insert(0, self.temp_index)
            temp_count += 1
            ircode.ircode_list.append(node_icode_list)
            return self.temp_index

        elif self.type == 'ae_unop':
            assert(len(node_icode_list)==1)
            node_icode_list.insert(0, self.leaves[0])
            node_icode_list.insert(0, '=')
            self.temp_index = 'x'+str(temp_count)
            node_icode_list.insert(0, self.temp_index)
            temp_count += 1
            ircode.ircode_list.append(node_icode_list)
            return self.temp_index

        elif self.type == 'ae_identifier' or self.type == 'ae_intconst':
            return self.leaves[0]

        #print node_icode_list, self.type, self.define_list, self.used_list
        '''


#Name and number of registers that can be used by the compiler. Change only num_registers variable
temp_registers = ['t0', 't1','t2','t3','t4','t5','t6','t7','t8']
num_registers = 9
#Global variables to keep track of temporaries, labels generated and the intermediate code of the program
temp_count = 0
label_count = 0
global_define_list = []
global_used_list = []
ircode = IRCode()
symtab = {}
sym_deflist = []
type_dict = {}
array_list = []

#Test files for the program. Specify a test file in the command-line or specify here
tes_files = []
test_file_name = sys.argv[1]
f = open(test_file_name,'r')
test_file_input = f.read()

#Build the lexer and input the lexer with the program to identify undefined tokens
lexer = lex.lex(module=proto_lex)
lexer.line_count = 1
lexer.input(test_file_input)
for token in lexer:
    print token

#Build the parser and input the parser with the program to parse the statements in the program
parser = yacc.yacc()
res = parser.parse(test_file_input)
assert(res is not None)
#res.display

res.checkForStaticSemantics()
res.display()

res.buildTypeDict([], {})

#res.display()

print "type_dict:", type_dict
print "array_list", array_list

print "symtab", symtab
print "sym_deflist", sym_deflist

for key, value in symtab.iteritems():
    symtab[key] = []
sym_deflist = []

res.gencode()
#ircode.display()

print "symtab", symtab
print "sym_deflist", sym_deflist

ircode.check_if_wellformed()


ircode.performLivenessAnalysis()

ircode.optimize()

print "\toptimized ircode:"
for i in range(len(ircode.optimized_ircode_list)):
    print i, ircode.optimized_ircode_list[i]

print "symtab", symtab
print "sym_deflist", sym_deflist

ircode.genASM()