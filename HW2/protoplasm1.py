#Balaji Srinivasan  -   02/027/15
#protoplasm1.py     -   Program that compiles a Proto source program and generates a .asm file of the same name
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw2.html
#usage              -   python protoplasm1.py <source_code>.proto
#                   -   generates <source_code>.asm in the same directory
import sys
import tokenize
import token
import cStringIO
from sets import Set
import copy
import re

#Class representing the grammar of Proto
class Proto_Grammar:
    operator = ['+','-','*','/','%']
    punctuation = [';']
    parenthesis = ['(',')']
    keywords = ['print', 'input']
    variable = re.compile('[a-zA-Z][a-zA-Z0-9]*')
    integer_constant = re.compile('[0-9]+')

    #Checks if a string is a valid variable name
    def match_variable(self, string):
        res = self.variable.match(string)
        if res != None:
            return [True]
        else:
            return [False, "Invalid variable name", string]

    #Checks if a string is a valid integer constant
    def match_integer_constant(self, string):
        res = self.integer_constant.match(string)
        if res != None:
            return [True]
        else:
            return[False, "Invalid integer constant", string]

    #Checks if a string is a valid keyword
    def match_keyword(self, string):
        if string in self.keywords:
            return [True]
        else:
            return [False]

    #Checks if a string is a valid operand----A
    def match_operand(self, string):
        if self.match_variable(string)==[True] or self.match_integer_constant(string)==[True]:
            return [True]
        else:
            return [False, "Invalid operand", string]

    #Checks if a string is a valid operator------op
    def match_operator(self, string):
        #print "match_operator:", string
        if string in self.operator:
            return [True]
        else:
            return [False, "Invalid operator", string]

    #Checks if expression whose tokens are in arg_list is a valid arithmetic expression----A op A | A
    def match_arithmetic_expression(self, arg_list):
        #print "match_arithmetic expression:",arg_list
        if len(arg_list)==1:
            return self.match_operand(arg_list[0])
        elif len(arg_list)==3:
            is_operand1 = self.match_operand(arg_list[0])
            is_operator = self.match_operator(arg_list[1])
            is_operand2 = self.match_operand(arg_list[2])
            if is_operand1==[True] and is_operator==[True] and is_operand2==[True]:
                return [True]
            elif is_operand1 != [True]:
                return is_operand1
            elif is_operator != [True]:
                return is_operator
            elif is_operand2 != [True]:
                return is_operand2
        else:
            return[False, "Invalid expression", arg_list]

    #Checks if tokens represented by arg_list is a valid RHS------input() or AE
    def match_rhs(self, arg_list):
        #print "match_rhs:",arg_list
        if arg_list[0] == "input":
            if arg_list[1]==self.parenthesis[0] and arg_list[2]==self.parenthesis[1]:
                return [True]
            else:
                if arg_list[1]!=self.parenthesis[0]:
                    return[False, "Invalid input statement: opening parenthesis missing", arg_list[1]]
                elif arg_list[2]!=self.parenthesis[1]:
                    return[False, "Invalid input statement: closing parenthesis missing", arg_list[2]]
        #RHS not an input() statement. RHS is an arithmetic expression
        else:
            return self.match_arithmetic_expression(arg_list)

    #Checks if tokens represented by arg_list is a valid print statement----print(AE)
    def match_print(self, arg_list):
        #print "match_print:",arg_list
        is_arith_expr = self.match_arithmetic_expression(arg_list[2:len(arg_list)-2])
        if arg_list[0] == self.keywords[0] and arg_list[1] == self.parenthesis[0] and is_arith_expr == [True] and arg_list[len(arg_list)-2] == self.parenthesis[1] and arg_list[len(arg_list)-1] == self.punctuation[0]:
            return [True]
        else:
            if arg_list[0] != self.keywords[0]:
                return[False, "Invalid print statement: print misspelled", arg_list[0]]
            elif arg_list[1] != self.parenthesis[0]:
                return[False, "Invalid print statement: opening parenthesis missing", arg_list[1]]
            elif is_arith_expr !=[True]:
                return is_arith_expr
            elif arg_list[len(arg_list)-2] != self.parenthesis[1]:
                return[False, "Invalid print statement: closing parenthesis missing", arg_list[len(arg_list)-2]]
            elif arg_list[len(arg_list)-1] != self.punctuation[0]:
                return[False, "Invalid print statement: semicolon missing", arg_list[len(arg_list)-1]]

    #Checks if tokens represented by arg_list is a valid assignment statement------var = RHS
    def match_assign(self, arg_list):
        #print "match_assign:", arg_list
        is_variable = self.match_variable(arg_list[0])
        is_rhs = self.match_rhs(arg_list[2:len(arg_list)-1])
        if is_variable==[True] and arg_list[1]=="=" and is_rhs==[True] and arg_list[len(arg_list)-1]==self.punctuation[0]:
            return [True]
        else:
            if is_variable!=[True]:
                return is_variable
            elif arg_list[1]!="=":
                return[False, "Invalid assignment statement: Missing = symbol", arg_list[1]]
            elif arg_list[len(arg_list)-1]!=self.punctuation[0]:
                return[False, "Invalid assignment statement: Missing semicolon", arg_list[len(arg_list)-1]]
            elif is_rhs != [True]:
                return is_rhs

    #Checks if tokens represented by arg_list is a valid statement------print | assign
    def match_statement(self, arg_list):
        #print "match_statement:", arg_list
        is_print = self.match_print(arg_list)
        is_assign = self.match_assign(arg_list)
        if is_print==[True] or is_assign==[True]:
            return [True]
        else:
            if "print" not in arg_list and is_assign!=[True]:
                return is_assign
            elif is_print!=[True]:
                return is_print


#Class representing Abstract Syntax List for a set of statements
class Abstract_Syntax_List:
    #syntax_list contains list of all tokens in statements
    #correct_syntax_list contains list of all tokens in well-defined statements
    #wellformed indicates if the program is wellformed or not
    syntax_list=[]
    correct_syntax_list=[]
    wellformed = 0

    #Add the line to the ASL
    def add(self, line):
        self.syntax_list.append((line))

    #Display the list of all tokens
    def display(self):
        print self.syntax_list

    #Display the list of all wellformed tokens
    def displayCorrectASL(self):
        print self.correct_syntax_list

    #Checks the ASL for syntax correctness. If not correct, indicates the first occurrence of the line number and the reason and bad token for the error
    def doSyntaxCheck(self):
        pg = Proto_Grammar()
        result_list=[]
        for line in self.syntax_list:
            result_list = pg.match_statement(line)
            #print result_list
            if result_list == [True]:
                self.correct_syntax_list.append(line)
            elif len(result_list)==3:
                result, reason, bad_token = result_list
                print "Line number:", self.syntax_list.index(line)+1,", Syntax error:", reason, ",bad_token:", bad_token
                exit()
        return 1

    #Checks the ASL for static semantics. If not correct, indicates the first occurrence of the line number and the reason and bad token for the error
    def doStaticSemanticsCheck(self, define_list, use_list):
        for i in range(0, len(use_list), 1):
            for j in use_list[i]:
                flag = 0
                for k in range(i):
                    if j in define_list[k]:
                        flag = 1
                        break
                if flag == 0:
                    print "Line ", i+1, ": Static semantic check failed: Symbol", j, "used before definition"
                    exit()
        return 1

    #Checks if the program represented by the ASL is wellformed or not, and sets the wellformed field if it the program is wellformed
    def isWellFormed(self):
        define_list = []
        use_list = []
        is_syntax_correct = self.doSyntaxCheck()
        define_list, use_list = self.generate_def_and_use()
        is_static_semantics_correct = self.doStaticSemanticsCheck(define_list, use_list)
        if  is_syntax_correct== 1 and  is_static_semantics_correct== 1:
            print "Program syntactically correct!"
            print "Program's static semantics are correct!"
            self.wellformed = 1
            return 1, define_list, use_list
        return 0

    #Generates the intermediate code corresponding to tokens in correct_syntax_list
    def gencode(self):
        for line in self.correct_syntax_list:
            #If the statement is print, move the argument to a0, call syscall with v0 = 1
            if 'print' in line:
                index = self.correct_syntax_list.index(line)
                line[0] = 'a0';
                line[1] = '=';
                line.remove(')')
                self.correct_syntax_list.insert(index+1, ['v0', '=', '1', ';'])
                self.correct_syntax_list.insert(index+2, ['syscall'])
            #If the statement is input, call syscall with v0 = 5 and move the input from v0 to the LHS variable
            elif 'input' in line:
                index = self.correct_syntax_list.index(line)
                line[2] = 'v0';
                line.remove('(')
                line.remove(')')
                self.correct_syntax_list.insert(index, ['syscall'])
                self.correct_syntax_list.insert(index, ['v0', '=', '5', ';'])
        return self.correct_syntax_list

    #Generate define(s) and use(s) for each statement s
    #bigger_define_list = list of define(s) and bigger_use_list = list of use(s)
    def generate_def_and_use(self):
        pg = Proto_Grammar()
        bigger_define_list=[]
        bigger_use_list=[]
        for i in range(len(self.correct_syntax_list)):
            define_list = []
            use_list = []
            seen_equal_flag = 0
            #variables on the left side of an = or print token are in define_list
            #other variables are in use_list
            for j in self.correct_syntax_list[i]:
                if j == 'print':
                    seen_equal_flag = 1
                if seen_equal_flag==0 and pg.match_variable(j) == [True] and pg.match_keyword(j)==[False]:
                    define_list.append(j)
                elif j == '=':
                    seen_equal_flag = 1
                elif seen_equal_flag==1 and pg.match_variable(j) == [True] and pg.match_keyword(j)==[False]:
                    use_list.append(j)
            bigger_define_list.append(define_list)
            bigger_use_list.append(use_list)

        #Convert the elements of bigger_define_list and bigger_use_list to sets
        for i in range(len(bigger_define_list)):
            define_set = Set(bigger_define_list[i])
            bigger_define_list[i] = define_set
        for i in range(len(bigger_use_list)):
            use_set = Set(bigger_use_list[i])
            bigger_use_list[i] = use_set
        return bigger_define_list, bigger_use_list


#Global function that tokenizes the input program, creates Abstract Syntax List from the tokens, checks for wellformedness, generates the intermediate code
def parse():
    asl = Abstract_Syntax_List();
    token_list=[]
    input_file_name = sys.argv[1]
    input_file_handle = open(input_file_name,"r")
    input_string = input_file_handle.read()
    token_generator_object = tokenize.generate_tokens(cStringIO.StringIO(input_string).readline)
    for (token_name, token_string, (srow,scol), (erow,ecol), token_line) in token_generator_object:
        line_buffer = ""
        token_list.append(token_string)
        if token.tok_name[token_name]=="NEWLINE":
            token_list.pop()
            asl.add(token_list)
            token_list=[]

    define_list = []
    use_list = []
    wellFormed , define_list, use_list = asl.isWellFormed()

    intermed_code_list = []
    intermed_code_list = asl.gencode()
    return define_list, use_list, intermed_code_list


#Class representing an Interference Graph
#interference_dict: Key = Vertex v
#                   Value = List of vertices interfering with v
#temp_registers   : List of temporary registers
class Interference_Graph:
    interference_dict={}
    spill_vertex_exception_list=[]
    temp_registers = ['t0', 't1','t2','t3','t4','t5','t6','t7','t8']

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
        self.spill_vertex_exception_list = []

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
        registers_list = self.temp_registers[:num_registers]
        register_alloc_dict={}
        k = len(registers_list)
        dict_copy = copy.deepcopy(self.interference_dict)
        #1) Keep removing nodes from the graph until atleast one of the vertices has degree<k
        #2) If no such node exists, choose a spill node and try to remove nodes with degree<k
        #Removed nodes are pushed into a stack
        #Continue 1) and 2) until all nodes are in the stack
        while(len(stack) != len(self.interference_dict)):
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
            elif value == ''  and key in spill_vertex_list:
                continue
            else:
                return 0
        return 1

#Class representing intermediate code for the input program
#define_list    =   define list for all statements in program
#use_list       =   use list for all statements in program
#intermediate_code+list =   list representing the intermediate code for the program
#num_registers  =   number of registers the program can use
class Intermediate_Code:
    define_list = []
    use_list = []
    intermediate_code_list = []
    num_registers = 0

    def __init__(self, define_list, use_list, intermed_code_list, num_registers):
        self.define_list = define_list
        self.use_list = use_list
        self.intermediate_code_list = intermed_code_list
        self.num_registers = num_registers

    #Helper method
    def displayAll(self):
        print "define_list:", self.define_list
        print "use_list:", self.use_list
        print "intermediate_code_list:", self.intermediate_code_list

    #Performs liveness analysis on the statements in the program
    #1)Calculates in_list and out_list for all statements in the program
    #2)Checks if the graph can be fully colored with the given num_registers by selecting different spill vertex in each iteration
    def performLivenessAnalysis(self):
        in_list=[]
        out_list=[]
        length_list=len(self.define_list)
        for i in range(length_list):
            in_list.append(Set())
            out_list.append(Set())
        out_list[length_list-1]=Set([])
        in_list[length_list-1]=self.use_list[length_list-1].union(out_list[length_list-1].difference(self.define_list[length_list-1]))
        for i in range(length_list-2,-1,-1):
            out_list[i]=in_list[i+1]
            in_list[i]=self.use_list[i].union(out_list[i].difference(self.define_list[i]))

        register_alloc_dict = {}
        spill_vertex_list = []
        spill_vertex_exception_list = []
        is_colored = 0
        while is_colored != 1:
            i_graph = Interference_Graph(in_list, spill_vertex_exception_list)
            register_alloc_dict, spill_vertex_list = i_graph.allocate_registers(self.num_registers)
            is_colored = i_graph.isColoredFully(register_alloc_dict, spill_vertex_list)
            if len(spill_vertex_list) != 0:
                spill_vertex_exception_list.append(spill_vertex_list[0])
        return register_alloc_dict, spill_vertex_list

    #Replaces the variable names with allocated register names from register_alloc_dict
    #Replaces occurrences of spill variables with load and store statements. Uses only register t9 for this purpose
    def optimize(self, register_alloc_dict, spill_vertex_list, intermed_code_list):
        spill_vertex_dict = {}
        line_index = 0
        special = { '+':1, '-':1, '/':1, '=':1 , ';':1, '*':1, '%':1, '(':1 , ')':1, 'a0':1, 'v0':1}
        temp = []
        while line_index < len(intermed_code_list):
            lexeme_index = 0
            skip = False
            R = copy.deepcopy(intermed_code_list[line_index])
            temp.append(R)
            while lexeme_index < len(intermed_code_list[line_index]):
                if intermed_code_list[line_index][lexeme_index] == 'syscall':
                    break
                lexeme = intermed_code_list[line_index][lexeme_index]
                if lexeme in spill_vertex_list:
                    if lexeme not in spill_vertex_dict:
                        temp_vertex_name = lexeme + "1"
                        spill_vertex_dict[lexeme] = [temp_vertex_name]
                    else:
                        temp_vertex_name = lexeme + str(len(spill_vertex_dict[lexeme])+1)
                        spill_vertex_dict[lexeme].append(temp_vertex_name)
                    intermed_code_list[line_index][lexeme_index] = temp_vertex_name
                    if intermed_code_list[line_index].index(temp_vertex_name) < intermed_code_list[line_index].index('='):
                        intermed_code_list[line_index][lexeme_index] = 't9'
                        intermed_code_list.insert(line_index+1, ['sw',' ', '$t9', ',', lexeme])
                        temp.append([])
                        skip = True
                    else:
                        intermed_code_list[line_index][lexeme_index] = 't9'
                        intermed_code_list.insert(line_index, ['lw',' ', '$t9', ',', lexeme])
                        temp.append([])
                        line_index += 1
                else:
                    if lexeme in register_alloc_dict:
                        intermed_code_list[line_index][lexeme_index] = register_alloc_dict[lexeme]
                    else:
                        t = intermed_code_list[line_index][lexeme_index]
                        digit_pattern = re.compile('[0-9]+')
                        if t not in special and digit_pattern.match(t) is None:
                            del intermed_code_list[line_index]
                            line_index -= 1
                            break
                lexeme_index += 1
            if skip:
                line_index += 2
            else:
                line_index += 1
        return temp, spill_vertex_dict


    #Generates MIPS code from intermediate code for each statement arg_list
    #prev_arg_list is used to insert a new line after every print statement
    def genASMstatement(self, arg_list, prev_arg_list=[]):
        number_pattern = re.compile('[+-]?[0-9]+')
        result = ""
        #If current statement is syscall
        if(arg_list[0] == 'syscall'):
            result += 'syscall'
            #If current syscall is a print syscall, generate MIPS code to insert a new line
            if prev_arg_list == ['v0', '=', '1', ';']:
                result+="\n\t"
                result += 'la $a0, new_line\n\t'
                result += 'li $v0, 4\n\t'
                result += 'syscall'
        #If current statement is a load or store operation
        elif(arg_list[0] == 'lw' or arg_list[0] == 'sw'):
            for i in range(len(arg_list)):
                result+=arg_list[i]
        #If current statement is a two-operand operation(move or load immediate)
        elif(len(arg_list) == 4):
            operand1 = "$"+arg_list[0]
            operator1 = arg_list[1]
            if number_pattern.match(arg_list[2]):
                operand2 = arg_list[2]
                result += "li "+ operand1+ ","+ operand2
            else:
                operand2 = "$"+arg_list[2]
                result += "move "+operand1+ ","+ operand2
        #If current statement is a three-operand operation----operand1<operator1>operand2<operator2>operand3
        elif(len(arg_list) == 6):
            operand1 = "$"+arg_list[0]
            operator1 = arg_list[1]
            operand2 = "$"+arg_list[2]
            operator2 = arg_list[3]
            if number_pattern.match(arg_list[4]):
                operand3 = arg_list[4]
            else:
                operand3 = "$"+arg_list[4]
            #Generate MIPS code depending on if the operator2 is a +,-,*,/,%
            if operator2 == '+':
                result += "addu "+operand1+", "+operand2+", "+operand3
            elif operator2 == '-':
                result += "subu "+operand1+", "+operand2+", "+operand3
            elif operator2 == '*':
                result += "mul "+operand1+", "+operand2+", "+operand3
            elif operator2 == '/':
                result += "divu "+operand1+", "+operand2+", "+operand3
            elif operator2 == '%':
                result += "li $t9, "+operand3+"\n\t"
                result += "divu "+ operand2+", $t9\n\t"
                result += "mfhi "+operand1
        result+='\n'
        return result

    #Generates MIPS code from intermediate code for the whole program
    def genASM(self, intermed_code_list, spill_vertex_list):
        #Create the output .asm file
        output_file_name = str(sys.argv[1]).strip(".proto")+".asm"
        output_file = open(output_file_name, "a")
        #Write data section
        #data_section contains new_line string("\n") and all spill variables are allocated a word in memory
        output_file.write(".data\n\n")
        output_file.write("new_line:	.asciiz \""+"\\n\"\n")
        for vertex in spill_vertex_list:
            output_file.write("\t"+vertex+" :\t.word 0\n")
        #Write text section starting form main label
        output_file.write("\n\n")
        output_file.write(".text\n\nmain:\n")
        for line in range(len(intermed_code_list)):
            if line == 0:
                output_file.write("\t"+self.genASMstatement(intermed_code_list[line]))
            else:
                output_file.write("\t"+self.genASMstatement(intermed_code_list[line], intermed_code_list[line-1]))
        #Write exit label
        output_file.write("exit:\n\tli $v0, 10\n\tsyscall\n")
        output_file.close()


#Driver routine
#define_list    =   list of define(s) sets for each statement s
#use_list       =   list of use(s) sets for each statement s
#intermed_code_list     =   list of intermediate code statements in the program
#register_alloc_dict    =   map of variable to register allocated
#spill_vertex_list      =   list of spill vertices
#spill_vertex_dict      =   map of spill vertex to instances of the vertex.eg: {a:['a1', 'a2', 'a3', 'a4', 'a5']} if spill_vertex_list=[a]
#NUM_REGISTERS          =   number of registers the program can use. Can be controlled by changing here
if __name__== "__main__":
    define_list = []
    use_list =[]
    intermed_code_list = []
    register_alloc_dict = {}
    spill_vertex_list = []
    spill_vertex_dict = {}
    NUM_REGISTERS = 3
    define_list, use_list, intermed_code_list = parse()

    icode = Intermediate_Code(define_list, use_list, intermed_code_list, NUM_REGISTERS)
    register_alloc_dict, spill_vertex_list = icode.performLivenessAnalysis()

    temp = copy.deepcopy(intermed_code_list)
    temp, spill_vertex_dict = icode.optimize(register_alloc_dict, spill_vertex_list, intermed_code_list)

    icode.genASM(intermed_code_list, spill_vertex_list)