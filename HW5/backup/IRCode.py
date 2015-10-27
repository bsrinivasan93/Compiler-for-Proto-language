__author__ = 'bsrinivasan'

import re
from sets import Set
import sys

from IGraph import Interference_Graph

#Name and number of registers that can be used by the compiler. Change only num_registers variable
temp_registers = ['t0', 't1','t2','t3','t4','t5','t6','t7','t8']
num_registers = 9
arg_registers_pattern = re.compile('\$a[0123]')
res_registers_pattern = re.compile('\$v[01]')
function_label_pattern = re.compile('func_[A-Za-z][a-zA-Z0-9]*')
number_pattern = re.compile('[+-]?[0-9]+')
label_pattern = re.compile('label_[0-9]+')
register_pattern = re.compile(r'\$t[0-9]+|\$a[0123]|\$v[01]')


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
    func_name = ''
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

    def __init__(self, fname):
        self.func_name = fname

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
            if arg_registers_pattern.match(ircode_list[0]) is None and res_registers_pattern.match(ircode_list[0]) is None:
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
            #print ircode_list
            if len(ircode_list) == 5:
                assert ircode_list[2]=='(' and ircode_list[4]==')'
                return [ircode_list[1], ircode_list[3]]

        #Assignment statement
        if ircode_list[1] == '=':
            if ircode_list[2] == 'input':
                return []
            elif len(ircode_list)==3 and number_pattern.match(ircode_list[2]) is None and label_pattern.match(ircode_list[2]) is None:
                if arg_registers_pattern.match(ircode_list[2]) is None and res_registers_pattern.match(ircode_list[2]) is None:
                    res_list.append(ircode_list[2])
            elif len(ircode_list)==4:
                assert(ircode_list[2]=='-' or ircode_list[2]=='!')
                if arg_registers_pattern.match(ircode_list[3]) is None and res_registers_pattern.match(ircode_list[3]) is None:
                    res_list.append(ircode_list[3])
            elif(len(ircode_list)==5) :
                if number_pattern.match(ircode_list[2]) is None:
                    if arg_registers_pattern.match(ircode_list[2]) is None and res_registers_pattern.match(ircode_list[2]) is None:
                        res_list.append(ircode_list[2])
                if number_pattern.match(ircode_list[4]) is None:
                    if arg_registers_pattern.match(ircode_list[4]) is None and res_registers_pattern.match(ircode_list[4]) is None:
                        res_list.append(ircode_list[4])
            return res_list
        #Print statement
        elif ircode_list[0] == 'print':
            assert len(ircode_list) == 2
            if arg_registers_pattern.match(ircode_list[1]) is None and res_registers_pattern.match(ircode_list[1]) is None:
                return [ircode_list[1]]
        #Unconditional branch statement
        elif ircode_list[0] == 'b':
            label_pattern = re.compile('label_[0-9]+')
            assert(label_pattern.match(ircode_list[1]) is not None) or function_label_pattern.match(ircode_list[1]) is not None
            return []
        #Conditiona branch statement
        elif ircode_list[0] == 'beq':
            if number_pattern.match(ircode_list[1]) is None:
                if arg_registers_pattern.match(ircode_list[1]) is None and res_registers_pattern.match(ircode_list[1]) is None:
                    res_list.append(ircode_list[1])
            if number_pattern.match(ircode_list[2]) is None:
                if arg_registers_pattern.match(ircode_list[2]) is None and res_registers_pattern.match(ircode_list[2]) is None:
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
        #print index, len(self.ircode_list) #self.label_table, self.ircode_list[index]
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

        #print "len(ircodelist):", len(self.ircode_list)
        #for i in range(len(self.ircode_list)):
        #    print i, self.ircode_list[i]
        #print "label table :", self.label_table
        #Generate successor lists for all statements
        for i in range(len(self.ircode_list)-1,-1,-1):
            self.getSucc(i)
        #print self.label_table
        #print self.defined_list, len(self.defined_list), self.used_list, len(self.used_list), self.succ_list, len(self.succ_list)

        #print "\tircode:def, use, succ"
        #for i in range(len(self.ircode_list)):
        #    print i, self.ircode_list[i], self.defined_list[i], self.used_list[i], self.succ_list[i]

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

        #print "\tircode: def, use, in, out"
        #for i in range(len(self.ircode_list)):
        #    print i, self.ircode_list[i], self.defined_list[i], self.used_list[i],  self.in_list[i], self.out_list[i]

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
        #print "register_alloc_dict:", self.register_alloc_dict, "spill_vertex_list:", self.spill_vertex_list

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

            if self.ircode_list[j][1] == '=' and self.ircode_list[j][0] not in self.register_alloc_dict.keys() and register_pattern.match(self.ircode_list[j][0]) is None:
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

        if ircode_list[0] == 'func_pushregisters':
            result += 'sub $sp, $sp, 60\n\t'
            result += 'sw $t0, ($sp)\n\t'
            result += 'sw $t1, 4($sp)\n\t'
            result += 'sw $t2, 8($sp)\n\t'
            result += 'sw $t3, 12($sp)\n\t'
            result += 'sw $t4, 16($sp)\n\t'
            result += 'sw $t5, 20($sp)\n\t'
            result += 'sw $t6, 24($sp)\n\t'
            result += 'sw $t7, 28($sp)\n\t'
            result += 'sw $t8, 32($sp)\n\t'
            result += 'sw $t9, 36($sp)\n\t'
            result += 'sw $a0, 40($sp)\n\t'
            result += 'sw $a1, 44($sp)\n\t'
            result += 'sw $a2, 48($sp)\n\t'
            result += 'sw $a3, 52($sp)\n\t'
            #result += 'sw $v0, 56($sp)\n\t'
            #result += 'sw $v1, 60($sp)\n\t'
            result += 'sw $ra, 56($sp)\n\t'

        elif ircode_list[0] == 'func_popregisters':
            result += 'lw $t0, ($sp)\n\t'
            result += 'lw $t1, 4($sp)\n\t'
            result += 'lw $t2, 8($sp)\n\t'
            result += 'lw $t3, 12($sp)\n\t'
            result += 'lw $t4, 16($sp)\n\t'
            result += 'lw $t5, 20($sp)\n\t'
            result += 'lw $t6, 24($sp)\n\t'
            result += 'lw $t7, 28($sp)\n\t'
            result += 'lw $t8, 32($sp)\n\t'
            result += 'lw $t9, 36($sp)\n\t'
            result += 'lw $a0, 40($sp)\n\t'
            result += 'lw $a1, 44($sp)\n\t'
            result += 'lw $a2, 48($sp)\n\t'
            result += 'lw $a3, 52($sp)\n\t'
            #result += 'lw $v0, 56($sp)\n\t'
            #result += 'lw $v1, 60($sp)\n\t'
            result += 'lw $ra, 56($sp)\n\t'
            result += 'add $sp, $sp, 60'


        #Simply propagate branch statements with minor changes
        elif ircode_list[0] == 'b' or label_pattern.match(ircode_list[0]) is not None or function_label_pattern.match(ircode_list[0]) is not None:
            result = " ".join(ircode_list)

        elif ircode_list[0] in ['jal','jr']:
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
        output_file_name = str(sys.argv[1]).strip(".proto")+".asm"
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
        output_file.write(".text\n\nmain:\nb func_main\n")
        for line in range(len(self.optimized_ircode_list)):
            output_file.write("\t"+self.genASMstatement(self.optimized_ircode_list[line]))
        #Write exit label
        output_file.write("exit:\n\tli $v0, 10\n\tsyscall\n")
        output_file.close()