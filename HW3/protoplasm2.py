#Balaji Srinivasan      -   03/24/15
#protoplasm2.py        -   Program that compiles a Proto source program and generates a .asm file of the same name
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw3.html
#usage                  -   python protoplasm2.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

from proto_lex import tokens
import proto_lex
import ply.lex as lex
import ply.yacc as yacc
import re
from sets import Set
import copy
import sys

#Variable that denotes the precedence and associativity of various tokens in the grammar
precedence=(
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQUAL','NEQUAL','LTHAN','LTHANEQ','GTHAN','GTHANEQ'),
    ('left', 'PLUS','MINUS'),
    ('left', 'STAR','DIV','MOD'),
    ('right', 'NOT'),
    ('right', 'UMINUS'),
)
#Name and number of registers that can be used by the compiler. Change only num_registers variable
temp_registers = ['t0', 't1','t2','t3','t4','t5','t6','t7','t8']
num_registers = 9

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
            vertex_list = list(i)
            for j in vertex_list:
                neighbor_list=[x for x in vertex_list if x!=j]
                for k in neighbor_list:
                    dict_val = self.interference_dict[j]
                    if k not in dict_val:
                        dict_val.append(k)
                    self.interference_dict[j] = dict_val
        self.spill_vertex_exception_list = spill_vertex_exception_list

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

    #Utility function to stringify the intermediate code in string
    def stringify(self):
        for i in range(len(self.ircode_list)):
            for j in range(len(self.ircode_list[i])):
                self.ircode_list[i][j] = str(self.ircode_list[i][j])

    #Get the defined variables in a statement(ircode_list)
    def getDefinedVars(self, ircode_list):
        if ircode_list[1] == '=':
            return [ircode_list[0]]
        return []

    #Get the used variables in a statement(ircode_list)
    def getUsedVars(self, ircode_list):
        res_list = []
        label_pattern = re.compile('label_[0-9]+')
        number_pattern = re.compile('[0-9]+')
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

    #Get the successor statements for a statement indexed by index
    def getSucc(self, index):
        label_pattern = re.compile('label_[0-9]+')
        number_pattern = re.compile('[0-9]+')
        if label_pattern.match(self.ircode_list[index][0]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index][0]])
        elif self.ircode_list[index][0] == 'b' and label_pattern.match(self.ircode_list[index][1]) is not None:
            self.succ_list[index].append(self.label_table[self.ircode_list[index][1]])
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
                    exit()

    #Check if the program represented by the ircode_list is well-formed
    def check_if_wellformed(self):
        self.make_llengths_equal()
        self.stringify()
        for i in range(len(self.ircode_list)):
            self.defined_list[i]=self.getDefinedVars(self.ircode_list[i])
            self.used_list[i]=self.getUsedVars(self.ircode_list[i])

        #Perform a static semantic check
        self.doStaticSemanticsCheck()

        #Generate successor lists for all statements
        for i in range(len(self.ircode_list)-1,-1,-1):
            self.getSucc(i)

        #Calculate in and out lists for all statements
        self.defined_list.append([])
        self.used_list.append([])
        for i in range(len(self.defined_list)):
            self.in_list.append(Set())
            self.out_list.append(Set())

        #Do two backward passes to generate the correct in_list and out_list
        for k in range(2):
            for i in range(len(self.ircode_list)-1, -1, -1):
                for j in range(len(self.succ_list[i])):
                    self.out_list[i] = self.out_list[i].union(self.in_list[self.succ_list[i][j]])
                self.in_list[i] = Set(self.used_list[i]).union(self.out_list[i].difference(Set(self.defined_list[i])))
        
    #Perform liveness analysis on the statements in the program
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

    #Get a free register that is not used in the statement indexed by index
    def getFreeReg(self, index):
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
        optimized_ircode_list = []
        for j in range(len(self.ircode_list)):
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


    #Generates MIPS code from intermediate code for each statement arg_list
    def genASMstatement(self, ircode_list):
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
            result += "move "+ircode_list[0]+", $a0"

        #load or store statements
        elif ircode_list[0] == 'lw' or ircode_list[0] == 'sw':
            assert(len(ircode_list) == 3)
            result += ircode_list[0]+" "+ircode_list[1]+", "+ircode_list[2]

        #Assignment statements
        else:
            assert(ircode_list[1] == '=')
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

        result+='\n'
        return result

    #Generates MIPS code from intermediate code for the whole program
    def genASM(self):
        #Create the output .asm file
        output_file_name = str(test_file_name).strip(".proto")+".asm"
        output_file = open(output_file_name, "a")

        #Prepend $ symbol to the registers in the intermediate code
        register_pattern = re.compile('t[0-9]+')
        for i in range(len(self.optimized_ircode_list)):
            for j in range(len(self.optimized_ircode_list[i])):
                if register_pattern.match(self.optimized_ircode_list[i][j]) is not None:
                    self.optimized_ircode_list[i][j] = '$'+self.optimized_ircode_list[i][j]

        #Write the data section
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

#Global variables to keep track of temporaries, labels generated and the intermediate code of the program
temp_count = 0
label_count = 0
ircode = IRCode()


#Class representing the Abstract Syntax Node in the AST
#type       =   Type of the AST node(binop, unop, if_stmt, while_stmt,etc)
#children   =   Children of the AST node(Non-terminal symbols used by the node)
#leaves     =   Leaves of the AST node(Terminal symbols used by the node)
class Node:

    def __init__(self, ntype, children=[], leaves=[]):
        self.type = ntype
        self.children = children
        self.leaves = leaves
        self.temp_index = ''
        self.label_list = []
        self.prev_ircode_length = 0

    #Helper method to display the whole AST recursively
    def display(self):
        print "Node(", hex(id(self)), "):", self.type, self.children, [type(self.children[i]) for i in range(len(self.children))], self.leaves, [type(self.leaves[i]) for i in range(len(self.leaves))]
        for i in range(len(self.children)):
            if isinstance(self.children[i] , self.__class__)==True:
                self.children[i].display()

    #Helper method to generate labels
    def genlabel(self):
        global label_count
        label_name =  "label_"+str(label_count)
        label_count += 1
        return  label_name

    #Helper method to identify the children of a node
    def findpos(self):
        global ircode
        for i in range(self.prev_ircode_length, len(ircode.ircode_list), 1):
            if ircode.ircode_list[i] == [None]:
                return i

    #Generate intermediate code for the statements in the program
    def gencode(self):
        global temp_count
        global ircode
        node_icode_list = []
        self.prev_ircode_length = len(ircode.ircode_list)
        if self.type in ['while_stmt']:
            ircode.ircode_list.append([None])
        #[None] is used to identify the transition from one child to the next child
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
            ircode.ircode_list[self.findpos()] = ['beq',node_icode_list[0], 0, self.label_list[0]]
            ircode.ircode_list[self.findpos()] = [self.label_list[0],':']

        elif self.type == 'if_else_stmt':
            self.label_list.append(self.genlabel())
            self.label_list.append(self.genlabel())
            ircode.ircode_list[self.findpos()] = ['beq',node_icode_list[0], 0, self.label_list[0]]
            end_of_then_block = self.findpos()
            ircode.ircode_list[end_of_then_block] = ['b',self.label_list[1]]
            ircode.ircode_list.insert(end_of_then_block+1, [self.label_list[0],':'])
            ircode.ircode_list[self.findpos()] =  [self.label_list[1],':']

        elif self.type == 'while_stmt':
            self.label_list.append(self.genlabel())
            self.label_list.append(self.genlabel())
            ircode.ircode_list[self.findpos()] = [self.label_list[0], ':']
            ircode.ircode_list[self.findpos()] = ['beq', node_icode_list[0], 0, self.label_list[1]]
            end_of_do_block = self.findpos()
            ircode.ircode_list[end_of_do_block] = ['b', self.label_list[0]]
            ircode.ircode_list.insert(end_of_do_block+1, [self.label_list[1], ':'])


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

#Yacc methods(p_) to identify the grammar in the program
#start  =   start symbol in the grammar
start='pgm'

def p_pgm(p):
    'pgm : stmt_seq'
    p[0] = Node('pgm', [p[1]], [])

def p_stmt_seq(p):
    '''stmt_seq : stmt stmt_seq
                | stmt'''
    if len(p) == 3:
        p[0] = Node('stmt_seq', [p[1],p[2]], [])
    elif len(p) == 2:
        p[0] = Node('stmt_seq', [p[1]], [])

def p_stmt(p):
    '''stmt : assign_stmt
            | print_stmt
            | block_stmt
            | if_stmt
            | while_stmt'''
    p[0] = Node('stmt', [p[1]], [])

def p_assign_stmt(p):
    'assign_stmt : IDENTIFIER EQUALS rhs SEMICOLON'
    p[0] = Node('assign_stmt', [p[3]], [p[1]])

def p_print_stmt(p):
    'print_stmt : PRINT LPAREN arith_expr RPAREN SEMICOLON'
    p[0] = Node('print_stmt', [p[3]], [])

def p_block_stmt(p):
    'block_stmt : LBRACE stmt_seq RBRACE'
    p[0] = Node('block_stmt', [p[2]], [])

def p_if_else_stmt(p):
    'if_stmt : IF arith_expr THEN stmt ELSE stmt'
    p[0] = Node('if_else_stmt', [p[2],p[4],p[6]], [])

def p_if_stmt(p):
    'if_stmt : IF arith_expr THEN stmt'
    p[0] = Node('if_stmt', [p[2],p[4]], [])

def p_while_stmt(p):
    'while_stmt : WHILE arith_expr DO stmt'
    p[0] = Node('while_stmt', [p[2],p[4]], [])

def p_rhs_input(p):
    'rhs : INPUT LPAREN RPAREN'
    p[0] = Node('rhs_input', [], [])

def p_rhs_arith_expr(p):
    'rhs : arith_expr'
    p[0] = Node('rhs_ae', [p[1]], [])

def p_arith_expr_bin_plus(p):
    'arith_expr : arith_expr PLUS arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_minus(p):
    'arith_expr : arith_expr MINUS arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_star(p):
    'arith_expr : arith_expr STAR arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_div(p):
    'arith_expr : arith_expr DIV arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_mod(p):
    'arith_expr : arith_expr MOD arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_and(p):
    'arith_expr : arith_expr AND arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_or(p):
    'arith_expr : arith_expr OR arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_equal(p):
    'arith_expr : arith_expr EQUAL arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_nequal(p):
    'arith_expr : arith_expr NEQUAL arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_lthan(p):
    'arith_expr : arith_expr LTHAN arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_lthaneq(p):
    'arith_expr : arith_expr LTHANEQ arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_gthan(p):
    'arith_expr : arith_expr GTHAN arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_bin_gthaneq(p):
    'arith_expr : arith_expr GTHANEQ arith_expr'
    p[0] = Node('ae_binop', [p[1], p[3]], [p[2]])

def p_arith_expr_un_not(p):
    'arith_expr : NOT arith_expr'
    p[0] = Node('ae_unop', [p[2]], [p[1]])

def p_arith_expr_un_minus(p):
    'arith_expr : MINUS arith_expr %prec UMINUS'
    p[0] = Node('ae_unop', [p[2]], [p[1]] )

def p_arith_group_expr(p):
    'arith_expr : LPAREN arith_expr RPAREN'
    p[0] = Node('ae_group', [p[2]], [p[1], p[3]])

def p_arith_intconst_expr(p):
    'arith_expr : INTCONST'
    p[0] = Node('ae_intconst', [], [p[1]])

def p_arith_id_expr(p):
    'arith_expr : IDENTIFIER'
    p[0] = Node('ae_identifier', [], [p[1]])

#Calculate column number of a token for specifying the error_token
def calc_column(token_lexpos):
    nline_index = test_file_input.rfind('\n', 0, token_lexpos)
    return token_lexpos - nline_index

def p_error(p):
    print "Syntax error at line ", lexer.line_count, " column ", calc_column(p.lexpos), " Offending token:", p
    exit(1)

#Test files for the program. Specify a test file in the command-line or choose from here
test_files = ['test.proto','simple_and_or_not_neg.proto', 'example2.proto','nested_while.proto','nested_if_else.proto','nested_if_else.proto','test.proto','simple_assign.proto','simple_print.proto','simple_block.proto', 'simple_if_then.proto', 'simple_while.proto']
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
res.gencode()
ircode.check_if_wellformed()
ircode.performLivenessAnalysis()
ircode.optimize()
ircode.genASM()