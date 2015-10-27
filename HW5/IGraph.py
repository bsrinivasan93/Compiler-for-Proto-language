#Balaji Srinivasan      -   04/28/15
#IGraph.py              -   Module representing the interference graph
#For grammar, refer to http://www3.cs.stonybrook.edu/~cram/cse504/Spring15/Homeworks/hw5.html
#usage                  -   python protoplasm4.py <source_code>.proto
#                       -   generates <source_code>.asm in the same directory
__author__ = 'bsrinivasan'

import copy

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