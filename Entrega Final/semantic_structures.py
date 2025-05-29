from semantic_cube import semantic_cube
from memory import get_segment

class program_functions:
    function_directory = {}
    scope_stack = []
    errors = []
    error_found = False
    n_params = 0
    n_local = 0
    param_order = []
    name_called = ""
    current_name = ""

    def __init__(self):
        self.function_directory = {}
        self.scope_stack = []
        self.errors = []
        self.error_found = False
        self.n_params = 0
        self.n_local = 0
        self.param_order = []
        self.name_called = ""
        self.current_name = ""
    
    def create_function(self, return_type, name):
        #Técnicamente ya tenemos hecho lo de los parámetros, sólo hay que modificar un poco como lo mostramos y darle memoria cuando es un void.
        self.n_params = 0
        self.n_local = 0
        self.param_order = []
        if name not in self.function_directory:
            self.function_directory[name] ={
                'return_type' : return_type,
                'n_params' : 0,
                'n_local_vars' : 0,
                'var_table' : {},
                'param_order' : [],
                'start_quad' : -1,
                'address' : None,
            }
            self.scope_stack.append(self.function_directory[name])
        else:
            error = "Error, function " + name + " already exists"
            self.errors.append(error)
            self.error_found = True

    def eliminate_function(self):
        if (not self.error_found):
            self.scope_stack.pop()

    def declare_vars_in_scope(self, id_list, var_type, lineno, is_param, mem_manager):
        if not self.error_found:
            current_scope = self.scope_stack[-1]['var_table']
            for name in id_list:
                if name in current_scope:
                    self.errors.append(f"Variable '{name}' already declared in current scope (line {lineno})")
                    self.error_found = True
                else:
                    if self.current_name != "":
                        segment = get_segment("local", var_type)
                    else:
                        segment = get_segment("global", var_type)
                    
                    address = mem_manager.allocate(segment)
                    current_scope[name] = {
                        'scope' : 'local',
                        'type': var_type,
                        'value': None,
                        'declared_line': lineno,
                        'is_null' : True,
                        'is_param' : is_param,
                        'address' : address,
                    }
                    if is_param:
                        current_scope[name]['is_null'] = False 

    def update_vars(self):
        if (not self.error_found):
            current_scope = self.scope_stack[-1]
            current_scope['n_params'] = self.n_params
            current_scope['n_local_vars'] = self.n_local
            current_scope['param_order'] = self.param_order
        
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
    #flag para ver si realizamos el proceso
    error_found =False
    #para llamada de funciones
    param_stack = []

    def __init__(self):
        self.t_count = 0
        self.quad_list = []
        self.operand_stack = []
        self.pending_jumps = []
        self.errors_found = []
        self.cycle_index_list = []
        self.param_stack = []
        self.error_found = False

    #checar si el stack de operandos tiene una entrada válida
    def checkOperandStack(self):
        if not self.error_found:
            if len(self.operand_stack > 0):
                return True
            else:
                return False
    #tomamos el nombre, el tipo, y si el valor no es nulo o si sí existe
    def add_to_operand_stack(self, name, type, not_null, address=None):
        if not self.error_found:
            self.operand_stack.append((address if address is not None else name, type, not_null))
        # print(self.operand_stack)

    #Cuando entramos en una gramática con sólo expresión queda un leftover
    def add_to_quad_list(self, operator, mem_manager):
        if not self.error_found:
            right, r_type, r_valid = self.operand_stack.pop()
            left, l_type, l_valid= self.operand_stack.pop()
            result = semantic_cube[l_type][operator][r_type]
            if (l_valid and r_valid and result != "error"):
                self.t_count +=1
                
                temp_addr = mem_manager.allocate(get_segment("temp", result)) + 1
                self.operand_stack.append((temp_addr, result, 1))
                self.quad_list.append((operator, left, right, temp_addr, result))
            else:
                #print("Invalid operation between " , l_type," and " ,r_type)
                error = "Invalid operation between " + str(l_type) + " and " + str(r_type)
                self.errors_found.append(error)
                self.error_found = True
                self.operand_stack.append(("error_token", "error", 0))
        
    
    def add_assignation(self, name, scope_stack):
        if not self.error_found:
            last, last_type, is_valid = self.operand_stack.pop()
            if( name in scope_stack[-1]['var_table'] and is_valid):
                #variable existe, verificamos que sea válida la asignación
                var = scope_stack[-1]['var_table'][name]
                var_address = var['address']
                if (last_type != 'bool' and semantic_cube[var['type']]['='][last_type] != 'error'):
                    scope_stack[-1]['var_table'][name]['is_null'] = False
                    result = ('=', last, None, var_address, semantic_cube[var['type']]['='][last_type])
                    self.quad_list.append(result)
                else:
                    #print("Invalid assignment, ", var['type'], "cannot be", last_type)
                    error = "Invalid assignment, " + str(var['type']) + " cannot be "+ str(last_type)
                    self.errors_found.append(error)
                    self.error_found = True
            else:
                #print("Invalid assignment to variable ", name, ". It does not exist or expression is not valid")
                error = "Invalid assignment to variable " + str(name) + ". It does not exist or expression is not valid"
                self.errors_found.append(error)
                self.error_found = True

    def add_single_to_quad(self, operator):
        if not self.error_found:
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
                self.error_found = True
                self.operand_stack.append(("error_token", "error", 0))

    #if
    def add_gotof(self):
        if not self.error_found:
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
                self.error_found = True
    
    #else
    def add_goto(self):
        if not self.error_found:
            gotof_index = self.pending_jumps.pop()
            gottof = self.quad_list[gotof_index]

            temp = ['goto', None, None, 0, None]
            index = len(self.quad_list)
            self.quad_list.append(temp)
            self.pending_jumps.append(index)
            
            self.quad_list[gotof_index] = (gottof[0], gottof[1], gottof[2], len(self.quad_list)+1, None)

    #cerramos último índice que había
    def end_goto(self):
        if not self.error_found:
            index = self.pending_jumps.pop()
            temp = self.quad_list[index]
            self.quad_list[index] = (temp[0], temp[1], temp[2], len(self.quad_list)+1, None)
        
    def addPrint(self):
        if not self.error_found:
            if (self.checkOperandStack):
                last, last_type, is_valid = self.operand_stack.pop()
                if is_valid:
                    self.quad_list.append(('print', last, None, None, last_type))

    def addLast_print(self):
        if not self.error_found:
            self.quad_list.append(("print", "\\n", None, None, "string"))
    
    def start_cycle(self):
        if not self.error_found:
            self.cycle_index_list.append(len(self.quad_list)+1)

    def add_cycle(self):
        if not self.error_found:
            if (self.checkOperandStack):
                last, last_type, is_valid = self.operand_stack.pop()
                index = self.cycle_index_list.pop()
                if last_type == 'bool':
                    self.quad_list.append(('gotoV', last, None, index, last_type))
                else:
                    error = "Condition does not give a boolean result in cycle"
                    self.errors_found.append(error)
                    self.error_found=True

    def create_function(self, Scopes):
        if not self.error_found:
            if not Scopes.error_found:
                Scopes.scope_stack[-1]['start_quad'] = len(self.quad_list)+1

    def create_function_quad(self, Scopes):
        if not self.error_found:
            if not Scopes.error_found:
                self.quad_list.append(('endfun', None, None, None, None))

    def create_main(self):
        if not self.error_found:
            quad = ['gotomain', None, None , None, None]
            self.quad_list.append(quad)

    def complete_main(self):
        if not self.error_found:
            temp = ('gotomain', None, None, len(self.quad_list)+1, None)
            #reemplazamos main
            self.quad_list[0] = temp

    def addParam(self):
        if not self.error_found:
            last, last_type, is_valid = self.operand_stack.pop()
            self.param_stack.append([last, last_type, is_valid])

    def fcallquads(self, Scopes):
        if not self.error_found:
            name = Scopes.name_called
            our_stack = self.param_stack
            types = Scopes.function_directory[name]['param_order']
            if len(our_stack) != len(types):
                error = "Wrong amount of parameters for function " + name
                self.error_found = True
                self.errors_found.append(error)
            else:
                for x in range(len(types)):
                    if types[x] == 'int' or types[x] == 'float':
                        if  our_stack[x][1] != 'string':
                            self.quad_list.append(('param', our_stack[x][0], None, None, None))
                        else:
                            error = "At function call, parameters do not match types"
                            self.error_found = True
                            self.errors_found.append(error)

                    elif types[x] == 'string':
                        if  our_stack[x][1] == 'string':
                            self.quad_list.append(('param', our_stack[x][0], None, None, None))
                        else:
                            error = "At function call, parameters do not match types"
                            self.error_found = True
                            self.errors_found.append(error)    

                if not self.error_found:
                    sq = Scopes.function_directory[name]['start_quad']
                    self.quad_list.append(('gosub', name, None, sq, None))

        self.param_stack = []
        
#Técnicamente ya tenemos hecho lo de los parámetros, sólo hay que modificar un poco como lo mostramos y darle memoria. Agregar Sub?