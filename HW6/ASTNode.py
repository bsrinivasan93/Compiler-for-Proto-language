#Balaji Srinivasan      -   04/28/15
#ASTNode.py             -   Module representing the Abstract Syntax Tree in the Compiler
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw5.html
#usage                  -   python protoplasm5.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

import copy
import re
from IRCode import IRCode

#Symbol table
sym_tab = []
#Global variables to keep track of temporaries, labels generated
temp_count = 0
label_count = 0
#List of argument and result registers
argument_registers = ['$a0', '$a1', '$a2', '$a3']
result_registers = ['$v0', '$v1']
#Patterns of arrays, dimensions, datatypes
array_type_pattern = re.compile('int\[\]|bool\[\]|void\[\]')
array_dim_pattern = re.compile('\[\]')
int_type_pattern = re.compile('int')
bool_type_pattern = re.compile('bool')
void_type_pattern = re.compile('void')

#Helper functions
#Print the symbol table
def print_symtab():
    print "symtab: ", sym_tab

#Find the number of functions and their names
def find_numfunc():
    num_proc = 0
    res_list = []
    for i in range(len(sym_tab)):
        temp_dict = sym_tab[i][1]
        if temp_dict['type'] == 'proc':
            num_proc += 1
            res_list.append(sym_tab[i][0])
    return num_proc, res_list

#Return the list of symbols in the program
def getSymList():
    temp_list = []
    for i in range(len(sym_tab)):
        temp_list.append(sym_tab[i][0])
    return temp_list

#Return the symbol table dictionary corr. to a symbol
def getSymTabDict(sym_name):
    for i in range(len(sym_tab)-1,-1,-1):
        if sym_tab[i][0] == sym_name:
            return i, sym_tab[i][1]

#Set the symbol table dictionary corr. to a symbol
def setSymTabDict(index, sym_name, sym_dict):
    assert sym_tab[index][0] == sym_name
    sym_tab[index][1] = sym_dict

#Find the base type of an array symbol datatype
def findArrayType(type_str):
    if int_type_pattern.match(type_str) is not None:
        return 'int'
    elif bool_type_pattern.match(type_str) is not None:
        return 'bool'
    elif void_type_pattern.match(type_str) is not None:
        return 'void'
    else:
        print "PROTO ERROR: Array declaration of unknown type", type_str
        exit(1)

#Check if the symbol is already declared
def checkIfDeclared(symbol):
    for i in range(len(sym_tab)-1, -1, -1):
        if sym_tab[i][0] == symbol:
            return 1
        elif sym_tab[i][0] == None:
            return 0
    return 0

#Refactor types.ex:int[][]--->array_array_int
def refactorType(symbol):
    #For normal variables
    if symbol in ['int', 'bool', 'void']:
        return symbol
    #For array variables
    elif array_type_pattern.match(symbol) is not None:
        n_dim = len(array_dim_pattern.findall(symbol))
        arr_type = ''
        for i in range(n_dim):
            arr_type += 'array_'
        arr_type += findArrayType(symbol)
        return arr_type

#Generate new temporary
def gen_temp():
    global temp_count
    temp_name = 'x'+str(temp_count)
    temp_count += 1
    return temp_name

#Generate new label
def gen_label():
    global label_count
    label_name =  "label_"+str(label_count)
    label_count += 1
    return label_name



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

        self.sym_tab = []
        self.dtype = ''
        self.t = ''
        self.at = ''
        self.code = []
        self.lcode = []
        self.rcode = []
        self.formalsOpt_type = []
        self.formalsOpt_id = []
        self.fun_flag = 0
        self.return_list = []

    #Helper method to display the whole AST recursively
    def display(self):
        print "Node(", hex(id(self)), "):", self.type, self.children, self.leaves, self.dtype, self.return_list#, self.sym_tab, len(self.sym_tab), "\n"
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.children[i].display()

    #Get the formal return type of the current function
    def getFormalRetType(self):
        for i in range(len(self.sym_tab)-1, -1, -1):
            symbol = self.sym_tab[i][0]
            sym_dict = self.sym_tab[i][1]
            if sym_dict != {} and sym_dict['type'] == 'proc':
                ret_type = sym_dict['dtype'][1]
                ret_type = refactorType(ret_type)
                return ret_type

    #Recursive method to check static semantics
    def checkStaticSemantics(self):
        global sym_tab
        symtab_backup = []

        self.sym_tab = copy.deepcopy(sym_tab)

        if self.type in ['type_int']:
            self.dtype = 'int'

        elif self.type in ['type_bool']:
            self.dtype = 'bool'

        elif self.type in ['type_void']:
            self.dtype = 'void'

        elif self.type in ['formalsOpt_empty']:
            self.dtype = []

        elif self.type in ['varlist_multi']:
            assert len(self.children) == 1
            assert len(self.leaves) == 1
            assert self.dtype is not ''
            self.children[0].dtype = self.dtype
            temp_dict = {}
            if checkIfDeclared(self.leaves[0]) == 1:
                print "PROTO ERROR: Static semantic check failed: Symbol ", self.leaves[0], "declared more than once within the same scope"
                exit(1)
            else:
                #For normal variables
                if self.dtype in ['int', 'bool', 'void']:
                    temp_dict = {'type':'var', 'dtype':self.dtype, 'sym_state':'UNINIT', 'sym_dimensions':[], 'sym_value':[], 'proc_attr':[]}
                #For array variables
                elif array_type_pattern.match(self.dtype) is not None:
                    n_dim = len(array_dim_pattern.findall(self.dtype))
                    arr_type = ''
                    for i in range(n_dim):
                        arr_type += 'array_'
                    arr_type += findArrayType(self.dtype)
                    temp_dict = {'type':'var_array', 'dtype':arr_type, 'sym_state':'UNINIT', 'sym_dimensions':[n_dim], 'sym_value':[], 'proc_attr':[]}
                temp_list = [self.leaves[0], temp_dict]
                sym_tab.append(temp_list)

        elif self.type in ['varlist_single']:
            assert len(self.leaves) == 1
            assert self.dtype is not ''
            temp_dict = {}
            if checkIfDeclared(self.leaves[0]) == 1:
                print "PROTO ERROR: Static semantic check failed: Symbol ", self.leaves[0], "declared more than once within the same scope"
                exit(1)
            else:
                #For normal variables
                if self.dtype in ['int', 'bool', 'void']:
                    temp_dict = {'type':'var', 'dtype':self.dtype, 'sym_state':'UNINIT', 'sym_dimensions':[], 'sym_value':[], 'proc_attr':[]}
                #For array variables
                elif array_type_pattern.match(self.dtype) is not None:
                    n_dim = len(array_dim_pattern.findall(self.dtype))
                    arr_type = ''
                    for i in range(n_dim):
                        arr_type += 'array_'
                    arr_type += findArrayType(self.dtype)
                    temp_dict = {'type':'var_array', 'dtype':arr_type, 'sym_state':'UNINIT', 'sym_dimensions':[n_dim], 'sym_value':[], 'proc_attr':[]}
                temp_list = [self.leaves[0], temp_dict]
                sym_tab.append(temp_list)

        elif self.type in ['lhs_id']:
            assert len(self.leaves) == 1
            sym_list = getSymList()
            if self.leaves[0] not in sym_list:
                print "PROTO ERROR: Symbol", self.leaves[0], "defined/used before declaration"
                exit(1)
            temp_index, temp_dict = getSymTabDict(self.leaves[0])
            self.dtype = temp_dict['dtype']

        elif self.type in ['primary_id']:
            assert len(self.leaves) == 1
            temp_dict = {}
            sym_list = getSymList()
            temp_index, temp_dict = getSymTabDict(self.leaves[0])
            if self.leaves[0] not in sym_list:
                print "PROTO ERROR: Symbol", self.leaves[0], "defined/used before declaration"
                exit(1)
            elif temp_dict['sym_state'] == 'UNINIT':
                print "PROTO ERROR: Symbol", self.leaves[0], "used before definition"
                exit(1)
            self.dtype = temp_dict['dtype']

        elif self.type in ['primary_intconst']:
            assert len(self.leaves) == 1
            self.dtype = 'int'

        elif self.type in ['primary_true', 'primary_false']:
            assert len(self.leaves) == 1
            self.dtype = 'bool'

        elif self.type in ['primary_input']:
            self.dtype = 'input'

        elif self.type in ['stmt_block']:
            symtab_backup = copy.deepcopy(sym_tab)
            if self.fun_flag == 0:
                sym_tab.append([None,{}])


        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.children[i].checkStaticSemantics()
                if self.type == 'vardecl':
                    assert len(self.children) == 2
                    self.children[1].dtype = self.children[0].dtype

                elif self.type in ['se_assign']:
                    assert len(self.children) == 2
                    assert self.children[0].type in ['lhs_id', 'lhs_arrayAccess']
                    if self.children[0].type == 'lhs_id':
                        assert len(self.children[0].leaves) == 1
                        symbol = self.children[0].leaves[0]
                        temp_dict = {}
                        sym_list = getSymList()
                        if symbol not in sym_list:
                            print "PROTO ERROR: Symbol ", symbol, " defined before declaration"
                            exit(1)
                        else:
                            temp_index, temp_dict = getSymTabDict(symbol)
                            if temp_dict['sym_state'] == 'UNINIT':
                                temp_dict['sym_state'] = 'INIT'
                            setSymTabDict(temp_index, symbol, temp_dict)

                elif self.type in ['fundecl'] and i == 1:
                    assert len(self.children) == 3
                    assert len(self.leaves) == 1
                    assert len(self.children[0].leaves) == 1
                    self.formalsOpt_id.extend(self.children[1].formalsOpt_id)
                    self.formalsOpt_type.extend(self.children[1].formalsOpt_type)
                    assert len(self.formalsOpt_id) == len(self.formalsOpt_type)
                    symbol = self.leaves[0]
                    temp_rtype = self.children[0].leaves[0]

                    temp_dtype = (tuple(self.formalsOpt_type), temp_rtype)

                    temp_dict = {'type':'proc', 'dtype': temp_dtype, 'sym_state':'INIT', 'sym_dimensions':'', 'sym_value':'', 'proc_attr':[self.formalsOpt_id, self.formalsOpt_type]}
                    temp_list = [symbol, temp_dict]
                    sym_tab.append(temp_list)
                    #Store the symtab to restore at the exit of the function
                    symtab_backup = copy.deepcopy(sym_tab)

                    #Add all the formal arguments to the symbol table as initialized symbols
                    sym_tab.append([None,{}])
                    if len(self.formalsOpt_type) == 1 and self.formalsOpt_type[0] == None:
                        pass
                    else:
                        for i in range(len(self.formalsOpt_type)):
                            #For normal variables
                            if self.formalsOpt_type[i] in ['int', 'bool', 'void']:
                                temp_dict = {'type':'var_fargs', 'dtype':self.formalsOpt_type[i], 'sym_state':'INIT', 'sym_dimensions':[], 'sym_value':[argument_registers[i]], 'proc_attr':[]}
                            #For array variables
                            elif array_type_pattern.match(self.formalsOpt_type[i]) is not None:
                                n_dim = len(array_dim_pattern.findall(self.formalsOpt_type[i]))
                                arr_type = ''
                                for j in range(n_dim):
                                    arr_type += 'array_'
                                arr_type += findArrayType(self.formalsOpt_type[i])
                                temp_dict = {'type':'var_fargs', 'dtype':arr_type, 'sym_state':'INIT', 'sym_dimensions':[n_dim], 'sym_value':[argument_registers[i]], 'proc_attr':[]}
                            temp_list = [self.formalsOpt_id[i], temp_dict]
                            sym_tab.append(temp_list)
                    self.children[2].fun_flag = 1


        if self.type in ['type_array']:
            assert len(self.children) == 1
            self.dtype = self.children[0].dtype + '[]'
            self.leaves = [self.children[0].dtype + '[]']

        elif self.type in ['stmt_block']:
            sym_tab = symtab_backup

        elif self.type in ['formals_single']:
            assert len(self.children) == 1
            assert len(self.leaves) == 1
            assert len(self.children[0].leaves) == 1
            self.formalsOpt_id.append(self.leaves[0])
            self.formalsOpt_type.append(self.children[0].leaves[0])

        elif self.type in ['formals_multi']:
            assert len(self.children) == 2
            assert len(self.leaves) == 1
            assert len(self.children[0].leaves) == 1
            self.formalsOpt_id.append(self.leaves[0])
            self.formalsOpt_type.append(self.children[0].leaves[0])
            self.formalsOpt_id.extend(self.children[1].formalsOpt_id)
            self.formalsOpt_type.extend(self.children[1].formalsOpt_type)

        elif self.type in ['formalsOpt']:
            assert len(self.children) == 1
            self.formalsOpt_id.extend(self.children[0].formalsOpt_id)
            self.formalsOpt_type.extend(self.children[0].formalsOpt_type)

        elif self.type in ['formalsOpt_empty']:
            assert len(self.children) == 0
            assert len(self.leaves) == 1
            self.formalsOpt_id = self.leaves
            self.formalsOpt_type = self.leaves

        elif self.type in ['fundecl']:
            sym_tab = symtab_backup


    #Recursive function to perform type checking
    def typeCheck(self):
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.children[i].typeCheck()
        #Type checking for program
        if self.type in ['pgm']:
            assert len(self.children) == 1
            assert self.dtype == ''
            if self.children[0].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                print "PROTO ERROR: TypeError: Program is not well-typed because the functions are not all well-typed"
                exit(1)

        elif self.type in ['decl_vardecl', 'declstar_empty']:
            assert self.dtype == ''
            self.dtype = 'TYPE_WELL'

        elif self.type in ['decl_fundecl']:
            assert len(self.children) == 1
            assert self.dtype == ''
            assert self.children[0].dtype != 'TYPE_ERROR'
            if self.children[0].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'

        elif self.type in ['declstar']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype == 'TYPE_WELL'
            assert self.children[1].dtype ==  'TYPE_WELL'
            self.dtype = 'TYPE_WELL'

        #Typechecking for function
        elif self.type in ['fundecl']:
            assert len(self.children) == 3
            assert len(self.leaves) == 1
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[2].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                print "PROTO ERROR: TypeError: Function ", self.leaves[0], "'s statement body is not well-typed"
                exit(1)

        #Typechecking for statements
        elif self.type in ['stmt_se']:
            assert len(self.children) == 1
            assert self.dtype == ''
            assert self.children[0].dtype != 'TYPE_ERROR'
            self.dtype = 'TYPE_WELL'

        elif self.type in ['stmt_print']:
            assert len(self.children) == 1
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[0].dtype == 'int':
                self.dtype = 'TYPE_WELL'
            else:
                print "PROTO ERROR: TypeError: Print statement associated with non-integer(", self.children[0].dtype, ") expression"
                exit(1)

        elif self.type in ['stmt_block']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[1].dtype == 'TYPE_WELL'
            self.dtype = 'TYPE_WELL'

        elif self.type in ['stmtstar_empty']:
            assert len(self.children) == 0
            assert len(self.leaves) == 1
            assert self.dtype == ''
            self.dtype = 'TYPE_WELL'

        elif self.type in ['stmtstar']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != '' or self.children[1].type == 'TYPE_WELL'
            self.dtype = 'TYPE_WELL'

        elif self.type in ['stmt_if']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[0].dtype == 'bool' and self.children[1].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                if self.children[0].dtype != 'bool':
                    print "PROTO ERROR: TypeError: If then statement's expression is of non-boolean(", self.children[0].dtype, ") type"
                    exit(1)
                else:
                    print "PROTO ERROR: TypeError: If then statement's statement is not well-typed(", self.children[1].dtype, ")"
                    exit(1)

        elif self.type in ['stmt_if_else']:
            assert len(self.children) == 3
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[0].dtype == 'bool' and self.children[1].dtype == 'TYPE_WELL' and self.children[2].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                if self.children[0].dtype != 'bool':
                    print "PROTO ERROR: TypeError: If then else statement's expression is of non-boolean(", self.children[0].dtype, ") type"
                    exit(1)
                elif self.children[1].dtype == 'TYPE_WELL':
                    print "PROTO ERROR: TypeError: If then statement's then-statement is not well-typed(", self.children[1].dtype, ")"
                    exit(1)
                else:
                    print "PROTO ERROR: TypeError: If then statement's else-statement is not well-typed(", self.children[1].dtype, ")"
                    exit(1)

        elif self.type in ['stmt_while']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[0].dtype == 'bool' and self.children[1].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                if self.children[0].dtype != 'bool':
                    print "PROTO ERROR: TypeError: While statement's expression is of non-boolean(", self.children[0].dtype, ") type"
                    exit(1)
                else:
                    print "PROTO ERROR: TypeError: While statement's statement is not well-typed(", self.children[1].dtype, ")"
                    exit(1)

        elif self.type in ['stmt_do_while']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[1].dtype != ''
            if self.children[1].dtype == 'bool' and self.children[0].dtype == 'TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                if self.children[1].dtype != 'bool':
                    print "PROTO ERROR: TypeError: Do-While statement's expression is of non-boolean(", self.children[1].dtype, ") type"
                    exit(1)
                else:
                    print "PROTO ERROR: TypeError: Do-While statement's statement is not well-typed(", self.children[0].dtype, ")"
                    exit(1)

        elif self.type in ['stmt_for']:
            assert len(self.children) == 4
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            assert self.children[2].dtype != ''
            assert self.children[3].dtype != ''
            if self.children[0].dtype != 'TYPE_ERROR' and self.children[2].dtype != 'TYPE_ERROR' and self.children[1].dtype == 'bool' and self.children[3].dtype =='TYPE_WELL':
                self.dtype = 'TYPE_WELL'
            else:
                if self.children[0].dtype == 'TYPE_ERROR' or self.children[2].dtype == 'TYPE_ERROR':
                    print "PROTO ERROR: TypeError: For statement's init / update expressions are of error type"
                    exit(1)

                elif self.children[1].dtype != 'bool':
                    print "PROTO ERROR: TypeError: For statement's guard expression is of non-boolean(", self.children[1].dtype, ") type"
                    exit(1)

                elif self.children[3].dtype !='TYPE_WELL':
                    print "PROTO ERROR: TypeError: For statement's body statement is not well-typed(", self.children[3].dtype, ")"
                    exit(1)

        elif self.type in ['stmt_return']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            formal_ret_type = self.getFormalRetType()
            actual_ret_type = self.children[0].dtype
            if formal_ret_type == actual_ret_type:
                self.dtype = 'TYPE_WELL'
            elif formal_ret_type == 'void' and actual_ret_type == 'TYPE_WELL' and self.children[0].type == 'AEOpt_empty':
                self.dtype = 'TYPE_WELL'
            else:
                print "PROTO ERROR: TypeError: Return statement's expression type(", actual_ret_type, ") is not the same as the enclosing function's return type(", formal_ret_type, ")"
                exit(1)

        #Typechecking for SEOpt, AEOpt
        elif self.type in ['SEOpt', 'AEOpt']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        elif self.type in ['SEOpt_empty', 'AEOpt_empty']:
            assert len(self.children) == 0
            assert len(self.leaves) == 1
            assert self.dtype == ''
            self.dtype = 'TYPE_WELL'

        #Typechecking for Statement Expressions
        elif self.type in ['se_assign']:
            assert len(self.children) == 2
            assert len(self.leaves) == 1
            assert self.dtype == ''
            #print "inside se_assign", self.children[0].dtype, self.children[1].dtype
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            if self.children[0].dtype == self.children[1].dtype:
                self.dtype = self.children[1].dtype
            elif self.children[1].dtype == 'input':
                self.dtype = self.children[1].dtype
            else:
                print "PROTO ERROR: TypeError: Assignment performed on different-typed(", self.children[0].dtype, "=", self.children[1].dtype, ") arithmetic expressions"
                exit(1)

        elif self.type in ['se_preinc', 'se_predec', 'se_postinc', 'postdec']:
            assert len(self.children) == 1
            assert self.dtype == ''
            assert len(self.children[0].leaves) == 1
            if self.children[0].dtype == 'int':
                self.dtype = 'int'
            else:
                print "PROTO ERROR: TypeError: Post/Pre Increment/Decrement operator performed on a non-integer type symbol", self.children[0].leaves[0]
                exit(1)

        #Typechecking for Arithmetic Expressions
        elif self.type in ['ae_binop']:
            assert len(self.children) == 2
            assert len(self.leaves) == 1
            #print "inside ae_binop", self.children[0].dtype, self.children[1].dtype
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            #Arithmetic operators
            if self.leaves[0] in ['+','-','*','/','%']:
                if self.children[0].dtype == 'int' and self.children[1].dtype == 'int':
                    self.dtype = 'int'
                else:
                    print "PROTO ERROR: TypeError: Binary arithmetic operator ", self.leaves[0], "performed on non-integer(", self.children[0].dtype, " and ", self.children[1].dtype, ") arithmetic expressions"
                    exit(1)
            #Equality comparison operators
            elif self.leaves[0] in ['==','!=']:
                if self.children[0].dtype == 'int' and self.children[1].dtype == 'int':
                    self.dtype = 'bool'
                elif self.children[0].dtype == 'bool' and self.children[1].dtype == 'bool':
                    self.dtype = 'bool'
                else:
                    print "PROTO ERROR: TypeError: Binary equality comparison operator ", self.leaves[0], "performed on different typed(", self.children[0].dtype, " and ", self.children[1].dtype, ") arithmetic expressions"
                    exit(1)
            #Inequality comparison operators
            elif self.leaves[0] in ['<','<=','>','>=']:
                if self.children[0].dtype == 'int' and self.children[1].dtype == 'int':
                    self.dtype = 'bool'
                else:
                    print "PROTO ERROR: TypeError: Binary inequality comparison operator ", self.leaves[0], "performed on non-integer(", self.children[0].dtype, " and ", self.children[1].dtype, ") arithmetic expressions"
                    exit(1)
            #Logical operators
            elif self.leaves[0] in ['&&','||']:
                if self.children[0].dtype == 'bool' and self.children[1].dtype == 'bool':
                    self.dtype = 'bool'
                else:
                    print "PROTO ERROR: TypeError: Logical operator ", self.leaves[0], "performed on non-boolean(", self.children[0].dtype, " and ", self.children[1].dtype, ") arithmetic expressions"
                    exit(1)

        elif self.type in ['ae_unop']:
            assert len(self.children) == 1
            assert len(self.leaves) == 1
            assert self.dtype == ''
            if self.leaves[0] == '-':
                if self.children[0].dtype == 'int':
                    self.dtype = self.children[0].dtype
                else:
                    print "PROTO ERROR: TypeError: Unary minus operator performed on a non-integer type symbol", self.children[0].leaves[0]
                    exit(1)
            elif self.leaves[0] == '!':
                if self.children[0].dtype == 'bool':
                    self.dtype = self.children[0].dtype
                else:
                    print "PROTO ERROR: TypeError: Unary not operator performed on a non-boolean type symbol", self.children[0].leaves[0]
                    exit(1)

        elif self.type in ['ae_primary']:
            assert len(self.children) == 1
            assert self.dtype == ''
            if self.children[0].type in ['primary_intconst', 'primary_true', 'primary_false', 'primary_input', 'primary_group', 'primary_id', 'primary_arrayAccess', 'primary_functionCall']:
                self.dtype = self.children[0].dtype

        elif self.type in ['ae_se']:
            assert len(self.children) == 1
            assert self.dtype == ''
            if self.children[0].dtype != 'TYPE_ERROR':
                self.dtype = self.children[0].dtype

        elif self.type in ['ae_newArray']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        #Typechecking for primary and lhs statements
        elif self.type in ['primary_group']:
            assert len(self.children) == 1
            assert self.dtype == ''
            self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        elif self.type in ['primary_arrayAccess', 'lhs_arrayAccess']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        elif self.type in ['primary_functionCall']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        #Typechecking for arrayAccess
        elif self.type in ['arrayAccess']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            if self.children[1].dtype == 'int' and str(self.children[0].dtype).startswith('array_') == True:
                self.dtype = str(self.children[0].dtype).lstrip('array_')
            else:
                if self.children[1].dtype != 'int':
                    print "PROTO ERROR: TypeError: ArrayAccess with non-integer(", self.children[1].dtype, ") index value"
                    exit(1)
                elif str(self.children[0].dtype).startswith('array_') != True:
                    print "PROTO ERROR: TypeError: ArrayAccess with non-array(", self.children[0].dtype, ") base element"
                    exit(1)

        #Typechecking for functionCall
        elif self.type in ['functionCall']:
            assert len(self.children) == 1
            assert len(self.leaves) == 1
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            sym_index, sym_dict = getSymTabDict(self.leaves[0])
            assert sym_dict['type'] == 'proc'
            formal_arg_list = []
            farg_list = sym_dict['proc_attr'][1]
            if farg_list != [None]:
                for i in range(len(farg_list)):
                    farg = farg_list[i]
                    #Array variables
                    if array_type_pattern.match(farg) is not None:
                        n_dim = len(array_dim_pattern.findall(farg))
                        arr_type = ''
                        for i in range(n_dim):
                            arr_type += 'array_'
                        arr_type += findArrayType(farg)
                        formal_arg_list.append(arr_type)
                    else:
                        formal_arg_list.append(farg)
            else:
                formal_arg_list = farg_list
            formal_ret_type = sym_dict['dtype'][1]
            if array_type_pattern.match(formal_ret_type) is not None:
                n_dim = len(array_dim_pattern.findall(formal_ret_type))
                arr_type = ''
                for i in range(n_dim):
                    arr_type += 'array_'
                arr_type += findArrayType(formal_ret_type)
                formal_ret_type = arr_type

            #Calculate actual arguments type list
            actual_arg_list = self.children[0].dtype
            if formal_arg_list == actual_arg_list:
                self.dtype = formal_ret_type
            else:
                print "PROTO ERROR: TypeError: Function call arguments(", actual_arg_list, ") doesnt match the function declaration arguments(", formal_arg_list, ")"
                exit(1)

        #Typechecking for newArray
        elif self.type in ['newArray']:
            assert len(self.children) == 3
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            if self.children[1].dtype == 'int':
                self.dtype = self.children[2].dtype + 'array_'+ self.children[0].dtype
            else:
                print "PROTO ERROR: TypeError: newArray expression with non-integer(", self.children[1].dtype, ") dimension expression"
                exit(1)

        #Typechecking for dim expressions, dimstar, dim
        elif self.type in ['dimexpr']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = self.children[0].dtype

        elif self.type in ['dimstar_empty']:
            assert len(self.children) == 0
            assert len(self.leaves) == 1 and self.leaves[0] == None
            assert self.dtype == ''

        elif self.type in ['dim']:
            assert len(self.children) == 0
            assert len(self.leaves) == 0
            assert self.dtype == ''
            self.dtype = 'array_'

        elif self.type in ['dimstar']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            if self.children[1].type != 'dimstar_empty':
                assert self.children[1].dtype != ''
            self.dtype += self.children[0].dtype + self.children[1].dtype

        #Typechecking for args
        elif self.type in ['args_single']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            self.dtype = [self.children[0].dtype]

        elif self.type in ['args_multi']:
            assert len(self.children) == 2
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            assert self.children[1].dtype != ''
            temp_list = self.children[1].dtype
            temp_list.append(self.children[0].dtype)
            self.dtype = temp_list

        elif self.type in ['argsOpt']:
            assert len(self.children) == 1
            assert len(self.leaves) == 0
            assert self.dtype == ''
            assert self.children[0].dtype != ''
            temp_list = self.children[0].dtype
            temp_list.reverse()
            self.dtype = temp_list

        elif self.type in ['argsOpt_empty']:
            assert len(self.children) == 0
            assert len(self.leaves) == 1
            assert self.dtype == ''
            self.dtype = [None]


    #Recursive method to check if every control flow in a function has a return statement
    def checkControlFlowReturn(self):
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.return_list.append(self.children[i].checkControlFlowReturn())

        if self.type in ['stmt_return']:
            return 1

        elif self.type in ['stmt_if', 'stmt_for', 'stmt_while']:
            return 0

        elif self.type in ['stmtstar']:
            assert len(self.return_list) == 2
            if 1 in self.return_list:
                return 1
            else:
                return 0

        elif self.type in ['stmtstar_empty']:
            return 0

        elif self.type in ['stmt_if_else']:
            assert len(self.return_list) == 3
            if self.return_list == [None, 1, 1]:
                return 1
            else:
                return 0

        elif self.type in ['stmt_block']:
            assert len(self.return_list) == 2
            if self.return_list[1] == 1:
                return 1
            else:
                return 0

        elif self.type in ['fundecl']:
            assert len(self.leaves[0])
            assert len(self.return_list) == 3
            if self.return_list[2] == 1:
                #All control paths in the function have a return statement
                pass
            else:
                print "PROTO ERROR: Returns check failed: Function ", self.leaves[0], "() does have a return statement in every control path"
                exit(1)


    #Helper method to identify the children of a node
    def findpos(self, ircode):
        for i in range(self.prev_ircode_length, len(ircode.ircode_list), 1):
            if ircode.ircode_list[i] == [None]:
                return i
        return -1

    #Helper method to resolve arguments in a functionCall statement
    def resolveArgs(self, symbol):
        temp_dict = {}
        for i in range(len(self.sym_tab)-1,-1,-1):
            if self.sym_tab[i][0] == symbol:
                temp_dict = self.sym_tab[i][1]
                break
        if temp_dict['sym_state'] == 'INIT' and temp_dict['type'] == 'var_fargs':
            assert temp_dict['sym_value'] != ''
            return temp_dict['sym_value'][0]
        else:
            return symbol

    #Helper method to get the type dict of the enclosing function
    def getEnclosingFunction(self):
        temp_dict = {}
        for i in range(len(self.sym_tab)-1,-1,-1):
            temp_dict = self.sym_tab[i][1]
            if temp_dict != {}:
                if temp_dict['type'] == 'proc':
                    return temp_dict

    #Recursive method to generate intermediate code for the program
    def gencode(self, ircode):
        global sym_tab
        node_icode_list = []
        copy_sym_tab = []
        self.prev_ircode_length = len(ircode.ircode_list)

        if self.type in ['fundecl']:
            assert len(self.leaves) == 1
            if ircode.func_name != self.leaves[0]:
                return
            else:
                #Generate the intermed code for the function rooted at this node
                ircode.ircode_list = []
                self.code = ['func_'+self.leaves[0], ':']
                ircode.ircode_list.append(self.code)
                if ircode.func_name!='main':
                    ircode.ircode_list.append(['func_pushregisters',':'])

        #[None] is used to identify the transition from one child to the next child
        elif self.type in ['stmt_while', 'stmt_do_while']:
            ircode.ircode_list.append([None])


        #Recursive calls to generate intermediate code in all the children
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                node_icode_list.append(self.children[i].gencode(ircode))
                if self.type in ['stmt_if', 'stmt_if_else', 'stmt_while', 'stmt_do_while', 'stmt_for']:
                    ircode.ircode_list.append([None])



        #Adding epilogue to the function
        if self.type in ['fundecl']:
            if ircode.func_name!='main':
                ircode.ircode_list.append(['func_popregisters',':'])
                ircode.ircode_list.append(['jr', '$ra'])
            pass

        #gencode for the statements
        elif self.type in ['stmt_se']:
            pass

        elif self.type in ['stmt_print']:
            assert len(node_icode_list) == 1
            node_icode_list.insert(0, 'print')
            ircode.ircode_list.append(node_icode_list)

        elif self.type in ['stmt_block']:
            sym_tab = copy.deepcopy(copy_sym_tab)

        elif self.type in ['stmt_if_else']:
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            ircode.ircode_list[self.findpos(ircode)] = ['beq', node_icode_list[0], 0, self.label_list[0]]
            end_of_then_block = self.findpos(ircode)
            ircode.ircode_list[end_of_then_block] = ['b', self.label_list[1]]
            ircode.ircode_list.insert(end_of_then_block+1, [self.label_list[0],':'])
            ircode.ircode_list[self.findpos(ircode)] = [self.label_list[1], ':']

        elif self.type in ['stmt_if']:
            self.label_list.append(gen_label())
            ircode.ircode_list[self.findpos(ircode)] = ['beq', node_icode_list[0], 0, self.label_list[0]]
            ircode.ircode_list[self.findpos(ircode)] = [self.label_list[0], ':']

        elif self.type in ['stmt_while']:
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            ircode.ircode_list[self.findpos(ircode)] = [self.label_list[0], ':']
            ircode.ircode_list[self.findpos(ircode)] = ['beq', node_icode_list[0], 0, self.label_list[1]]
            end_of_do_block = self.findpos(ircode)
            ircode.ircode_list[end_of_do_block] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_do_block+1, [self.label_list[1], ':'])

        elif self.type in ['stmt_for']:
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            ircode.ircode_list[self.findpos(ircode)] = [self.label_list[0], ':']
            end_of_aeopt = self.findpos(ircode)
            ircode.ircode_list[end_of_aeopt] = ['beq', node_icode_list[1], 0, self.label_list[3]]
            ircode.ircode_list.insert(end_of_aeopt+1, ['b', self.label_list[1]])
            ircode.ircode_list.insert(end_of_aeopt+2, [self.label_list[2], ':'])
            end_of_seopt = self.findpos(ircode)
            ircode.ircode_list[end_of_seopt] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_seopt+1, [self.label_list[1], ':'])
            end_of_stmt = self.findpos(ircode)
            ircode.ircode_list[end_of_stmt] = ['b', self.label_list[2]]
            ircode.ircode_list.insert(end_of_stmt+1, [self.label_list[3], ':'])
            #print node_icode_list, len(node_icode_list), ircode.ircode_list, len(ircode.ircode_list)

        elif self.type in ['stmt_do_while']:
            self.label_list.append(gen_label())
            self.label_list.append(gen_label())
            ircode.ircode_list[self.findpos(ircode)] = [self.label_list[0], ':']
            ircode.ircode_list.pop(self.findpos(ircode))
            end_of_ae = self.findpos(ircode)
            ircode.ircode_list[end_of_ae] = ['beq', node_icode_list[1], 0, self.label_list[1]]
            ircode.ircode_list.insert(end_of_ae+1, ['b', self.label_list[0]])
            ircode.ircode_list.insert(end_of_ae+2, [self.label_list[1], ':'])

        elif self.type in ['stmt_return']:
            temp_dict = self.getEnclosingFunction()
            if temp_dict['dtype'][1] != 'void':
                assert node_icode_list != [None]
                ircode.ircode_list.append(['$v0', '=', node_icode_list[0]])

        #gencode for SEOpt,AEOpt
        elif self.type in ['SEOpt']:
            return node_icode_list[0]

        elif self.type in ['AEOpt']:
            assert len(node_icode_list) == 1
            #print "inside AEOpt", node_icode_list
            return node_icode_list[0]

        #gencode for statement expressions
        elif self.type in ['se_assign']:
            assert(len(node_icode_list) == 2)
            if self.children[0].type == 'lhs_id':
                node_icode_list.insert(1, '=')
                ircode.ircode_list.append(node_icode_list)
                return node_icode_list[2]

            elif self.children[0].type == 'lhs_arrayAccess':
                temp1 = node_icode_list[0]
                temp2 = node_icode_list[1]
                ircode.ircode_list.append(['sw', temp2, '(', temp1, ')'])
                return temp2

        elif self.type in ['se_postinc']:
            assert(len(node_icode_list) == 1)
            temp = gen_temp()
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '+', 1])
            return temp

        elif self.type in ['se_postdec']:
            assert(len(node_icode_list) == 1)
            temp = gen_temp()
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '-', 1])
            return temp

        elif self.type in ['se_preinc']:
            assert(len(node_icode_list) == 1)
            temp = gen_temp()
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '+', 1])
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            return temp

        elif self.type in ['se_predec']:
            assert(len(node_icode_list) == 1)
            temp = gen_temp()
            ircode.ircode_list.append([node_icode_list[0], '=', node_icode_list[0], '-', 1])
            ircode.ircode_list.append([temp, '=', node_icode_list[0]])
            return temp

        #gencode for lhs
        elif self.type in ['lhs_id']:
            assert(len(self.leaves) == 1)
            return self.resolveArgs(self.leaves[0])

        elif self.type in ['lhs_arrayAccess']:
            assert len(node_icode_list) == 1
            temp_list = node_icode_list[0]
            temp1 = self.children[0].t
            temp2 = self.children[0].at
            size = 4
            ircode.ircode_list.append([temp1, '=', temp_list[1], '*', size])
            ircode.ircode_list.append([temp2, '=', temp_list[0], '+', temp1])
            return temp2

        #gencode for arrayAccess
        elif self.type in ['arrayAccess']:
            assert(len(node_icode_list) == 2)
            temp1 = gen_temp()
            temp2 = gen_temp()
            self.t = temp1
            self.at = temp2
            return node_icode_list

        #gencode for arithmetic expressions
        elif self.type in ['ae_binop']:
            assert(len(node_icode_list) == 2)
            assert(len(self.leaves) == 1)
            temp = gen_temp()
            self.t = temp
            node_icode_list.insert(1, self.leaves[0])
            node_icode_list.insert(0, '=')
            node_icode_list.insert(0, temp)
            self.code = node_icode_list
            ircode.ircode_list.append(self.code)
            return self.t

        elif self.type in ['ae_unop']:
            assert len(node_icode_list) == 1
            assert len(self.leaves) == 1
            temp =gen_temp()
            node_icode_list.insert(0, self.leaves[0])
            node_icode_list.insert(0, '=')
            node_icode_list.insert(0, temp)
            ircode.ircode_list.append(node_icode_list)
            return temp

        elif self.type in ['ae_primary']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['ae_se']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['ae_newArray']:
            assert node_icode_list != [None]
            return node_icode_list[0]

        #gencode for primary
        elif self.type in ['primary_intconst']:
            assert len(self.leaves) == 1
            temp = gen_temp()
            self.t = temp
            self.code = [temp, '=', self.leaves[0]]
            ircode.ircode_list.append(self.code)
            return self.t

        elif self.type in ['primary_true']:
            assert len(self.leaves) == 1
            temp = gen_temp()
            ircode.ircode_list.append([temp, '=', 1])
            return temp

        elif self.type in ['primary_false']:
            assert len(self.leaves) == 1
            temp = gen_temp()
            ircode.ircode_list.append([temp, '=', 0])
            return temp

        elif self.type in ['primary_input']:
            temp = gen_temp()
            ircode.ircode_list.append([temp, '=', 'input'])
            return temp

        elif self.type in ['primary_group']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['primary_id']:
            assert len(node_icode_list) == 0
            assert len(self.leaves) == 1
            temp = self.resolveArgs(self.leaves[0])
            return temp

        elif self.type in ['primary_arrayAccess']:
            assert len(node_icode_list) == 1
            temp_list = node_icode_list[0]
            temp1 = self.children[0].t
            temp2 = self.children[0].at
            size = 4
            ircode.ircode_list.append([temp1, '=', temp_list[1], '*', size])
            ircode.ircode_list.append([temp2, '=', temp_list[0], '+', temp1])
            ircode.ircode_list.append(['lw', temp1, '(', temp2, ')'])
            return temp1

        elif self.type in ['primary_functionCall']:
            #print "inside primary_functionCall", node_icode_list
            assert node_icode_list != [None]
            return node_icode_list[0]

        #gencode for functionCall
        elif self.type in ['functionCall']:
            assert node_icode_list != [None]
            assert len(self.leaves) == 1
            #print "inside functionCall", node_icode_list[0]
            temp_list = node_icode_list[0]
            for i in range(len(temp_list)):
                ircode.ircode_list.append([argument_registers[i], '=', temp_list[i]])
            ircode.ircode_list.append(['jal', 'func_'+self.leaves[0]])
            return '$v0'

        #gencode for args
        elif self.type in ['argsOpt']:
            assert node_icode_list != [None]
            return node_icode_list[0]

        elif self.type in ['argsOpt_empty']:
            return []

        elif self.type in ['args_multi']:
            assert node_icode_list[0] != [None]
            assert node_icode_list[1] != [None]
            temp_list = []
            temp_list.append(node_icode_list[0])
            temp_list.extend(node_icode_list[1])
            return temp_list

        elif self.type in ['args_single']:
            assert node_icode_list != [None]
            return node_icode_list

        #gencode for newArray
        elif self.type in ['newArray']:
            assert len(node_icode_list) == 3
            temp = gen_temp()
            temp1 = gen_temp()
            ircode.ircode_list.append([temp1, '=', node_icode_list[1], '*', node_icode_list[0]])
            ircode.ircode_list.append(['halloc', temp, temp1])
            return temp

        #gencode for dimexpr,dimstar
        elif self.type in ['dimexpr']:
            assert len(node_icode_list) == 1
            return node_icode_list[0]

        elif self.type in ['dimstar']:
            pass

        #gencode for types
        elif self.type in ['type_int']:
            return 4

        elif self.type in ['type_bool']:
            return 4