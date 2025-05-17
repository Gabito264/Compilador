from semantic_cube import semantic_cube
class program_functions:
    function_directory = {}
    scope_stack = []
    errors = []
    error_found = False

    def __init__(self):
        self.function_directory = {}
        self.scope_stack = []
        self.errors = []
        self.error_found = False
    
    def create_function(self, return_type, name ,n_params):
        if name not in self.function_directory:
            self.function_directory[name] ={
                'return_type' : return_type,
                'n_params' : n_params,
                'var_table' : {}
            }
            self.scope_stack.append(self.function_directory[name]['var_table'])
        else:
            error = "Error, function " + name + " already exists"
            self.errors.append(error)
            self.error_found = True

    def eliminate_function(self):
        self.scope_stack.pop()

    def declare_vars_in_scope(self, id_list, var_type, lineno):
        current_scope = self.scope_stack[-1]
        for name in id_list:
            if name in current_scope:
                self.errors.append(f"Variable '{name}' already declared in current scope (line {lineno})")
            else:
                current_scope[name] = {
                    'scope' : 'global',
                    'type': var_type,
                    'value': None,
                    'declared_line': lineno,
                    'is_null' : True
                }



class objects:
    t_count = 0
    #quad = (op, left, right, result)
    quad_list = []
    #operand = (name, type, not_null)
    operand_stack = []
    # (gotof, arg1, None, lineno )
    pending_jumps = []
    #por si encontramos un error
    errors_found = []
    #Lista separada para ciclos (por si acaso)
    cycle_index_list = []

    def __init__(self):
        self.t_count = 0
        self.quad_list = []
        self.operand_stack = []
        self.pending_jumps = []
        self.errors_found = []
        self.cycle_index_list = []

    #checar si el stack de operandos tiene una entrada válida
    def checkOperandStack(self):
        if len(self.operand_stack > 0):
            return True
        else:
            return False
    #tomamos el nombre, el tipo, y si el valor no es nulo o si sí existe
    def add_to_operand_stack(self, name, type, not_null):
        self.operand_stack.append((name, type, not_null))
        # print(self.operand_stack)

    #Cuando entramos en una gramática con sólo expresión queda un leftover
    def add_to_quad_list(self, operator):
        right, r_type, r_valid = self.operand_stack.pop()
        left, l_type, l_valid= self.operand_stack.pop()
        result = semantic_cube[l_type][operator][r_type]
        if (l_valid and r_valid and result != "error"):
            self.t_count +=1
            
            temp = "t_" + str(self.t_count)
            self.operand_stack.append((temp, result, 1))
            self.quad_list.append((operator, left, right, temp, result))
        else:
            #print("Invalid operation between " , l_type," and " ,r_type)
            error = "Invalid operation between " + str(l_type) + " and " + str(r_type)
            self.errors_found.append(error)
            self.operand_stack.append(("error_token", "error", 0))
    
    
    def add_assignation(self, name, scope_stack):
        last, last_type, is_valid = self.operand_stack.pop()
        
        if( name in scope_stack[-1] and is_valid):
            #variable existe, verificamos que sea válida la asignación
            var = scope_stack[-1][name]
            if (last_type != 'bool' and semantic_cube[var['type']]['='][last_type] != 'error'):
                scope_stack[-1][name]['is_null'] = False
                result = ('=', last, None, name, semantic_cube[var['type']]['='][last_type])
                self.quad_list.append(result)
            else:
                #print("Invalid assignment, ", var['type'], "cannot be", last_type)
                error = "Invalid assignment, " + str(var['type']) + " cannot be "+ str(last_type)
                self.errors_found.append(error)
        else:
            #print("Invalid assignment to variable ", name, ". It does not exist or expression is not valid")
            error = "Invalid assignment to variable " + str(name) + ". It does not exist or expression is not valid"
            self.errors_found.append(error)

    def add_single_to_quad(self, operator):
        last, last_type, is_valid = self.operand_stack.pop()
        result = semantic_cube[''][operator][last_type]
        if(is_valid and result != 'error'):
            self.t_count+=1
            temp = "t_" + str(self.t_count)
            self.operand_stack.append((temp, result, 1))
            self.quad_list.append((operator, last, None, temp, result))
        else:
            #print("Invalid operation to ", last_type)
            error = "Invalid operation to " +  str(last_type)
            self.errors_found.append(error)
            self.operand_stack.append(("error_token", "error", 0))

    #if
    def add_gotof(self):
        last, last_type, is_valid = self.operand_stack.pop()
        if (last_type == 'bool'):
            temp = ['gotof', last, None, 0, None]
            index = len(self.quad_list)
            self.quad_list.append(temp)
            self.pending_jumps.append(index)
        else:
            error = "Condition is not a boolean condition"
            self.errors_found.append(error)
            temp = ['gotof', last, None, 0, None]
            index = len(self.quad_list)
            self.quad_list.append(temp)
            self.pending_jumps.append(index)
    
    #else
    def add_goto(self):
        gotof_index = self.pending_jumps.pop()
        gottof = self.quad_list[gotof_index]

        temp = ['goto', None, None, 0, None]
        index = len(self.quad_list)
        self.quad_list.append(temp)
        self.pending_jumps.append(index)
        
        self.quad_list[gotof_index] = (gottof[0], gottof[1], gottof[2], len(self.quad_list)+1, None)

    #cerramos último índice que había
    def end_goto(self):
        index = self.pending_jumps.pop()
        temp = self.quad_list[index]
        self.quad_list[index] = (temp[0], temp[1], temp[2], len(self.quad_list)+1, None)
        
    def addPrint(self):
        if (self.checkOperandStack):
            last, last_type, is_valid = self.operand_stack.pop()
            if is_valid:
                self.quad_list.append(('print', last, None, None, last_type))

    def addLast_print(self):
        self.quad_list.append(("print", "\\n", None, None, "string"))
    
    def start_cycle(self):
        self.cycle_index_list.append(len(self.quad_list)+1)

    def add_cycle(self):
        if (self.checkOperandStack):
            last, last_type, is_valid = self.operand_stack.pop()
            index = self.cycle_index_list.pop()
            if last_type == 'bool':
                self.quad_list.append(('gotoV', last, None, index, last_type))
            else:
                error = "Condition does not give a boolean result in cycle"
                self.errors_found.append(error)
