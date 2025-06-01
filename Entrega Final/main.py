from lexer import tokens, lexer, input_program
from semantic_cube import semantic_cube
from semantic_structures import program_functions, objects
from memory import MemoryManager, ConstantTable, get_segment
import ply.yacc as yacc

start = 'programa'


syntax_error = 0
error_list = []

Scopes = program_functions()
Ds = objects()
mem_manager = MemoryManager()
const_table = ConstantTable(mem_manager)

#PROGRAMA ::= 'program' 'id' ';' VARS? FUNCS* 'main' BODY 'end'
def p_programa(t):
    'programa : PROGRAM create_program semicol vars funcs complete_main body elim_program'
    t[0] = ('programa', t[2], t[5], t[6], t[8])

def p_create_program(t):
    'create_program : identifier'
    Scopes.create_function('program', t[1], mem_manager, t.lineno(1))
    Ds.create_main()

def p_complete_main(t):
    'complete_main : MAIN'
    Ds.complete_main()

def p_elim_program(t):
    'elim_program : END'
    Scopes.eliminate_function()

#VARS     ::= 'var' ( 'id' ( ',' 'id' )* ':' TYPE ';' )+
def p_vars(t):
    'vars : VAR var_definition'
    t[0] = t[2]

def p_vars_empty(t):
    'vars : '
    t[0] = []

def p_definition(t):
    'var_definition : id_list twopoint type semicol var_definition'
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), False, Scopes.scope_stack[-1]["addresses"])
    t[0] = [('var_decl', t[1], t[3])] + t[5]
    
def p_definition_once(t):
    'var_definition : id_list twopoint type semicol'
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), False, Scopes.scope_stack[-1]["addresses"])
    t[0] = [('var_decl', t[1], t[3])]

def p_id_list(t):
    'id_list : identifier comma id_list'
    t[0] = [t[1]] + t[3]
    Scopes.n_local+=1

def p_id_list_once(t):
    'id_list : identifier'
    t[0] = [t[1]]
    Scopes.n_local+=1

#Error en listar las variables
def p_definition_error(t):
    'var_definition : error twopoint type semicol var_definition'
    global error_list
    error_list.append("At variable definition: bad identifier list")
    t[0]=[]

def p_definition_once_error(t):
    'var_definition : error twopoint type semicol'
    global error_list
    error_list.append("At variable definition: bad identifier list")
    t[0] = []

#TYPE     ::= 'int' | 'float' | 'string'
def p_type_int(t):
    'type : INTEGER'
    t[0] = 'int'

def p_type_float(t):
    'type : FLOAT'
    t[0] = 'float'

def p_type_string(t):
    'type : STRING'
    t[0] = 'string'

# FUNCS    ::= 'void' 'id' '(' ( 'id' ':' TYPE ( ',' 'id' ':' TYPE )* )? ')' '[' VARS? BODY ']' ';'

def p_funcs(t):
    'funcs : func funcs'
    t[0] = [t[1]] + t[2]

def p_funcs_empty(t):
    'funcs : '
    t[0] = []

def p_func(t):
    'func : VOID create_function opening_par param_list closing_par opening_brack create_func_quad body closing_brack end_function'
    t[0] = ('func', t[2], t[4], t[7], t[8]) 

def p_create_function(t):
    'create_function : identifier'
    Scopes.current_name = t[1]
    Scopes.create_function('Void', t[1], mem_manager, t.lineno(1))

def p_create_func_quad(t):
    'create_func_quad : vars'
    Scopes.update_vars()
    Ds.create_function(Scopes)

def p_end_function(t):
    'end_function : semicol'
    Ds.create_function_quad(Scopes)
    Scopes.eliminate_function()

def p_param_list(t):
    'param_list : param_list comma param'
    t[0] = t[1] + [t[3]]

def p_param_list_once(t):
    'param_list : param'
    t[0] = [t[1]]

def p_param_list_empty(t):
    'param_list : '
    t[0] = []

def p_param(t):
    'param : identifier twopoint type'
    t[0] = (t[1], t[3])
    Scopes.n_params+=1
    Scopes.param_order.append(t[3])
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), True, Scopes.scope_stack[-1]["addresses"])

#BODY     ::= '{' STATEMENT* '}'
def p_body(t):
    'body : opening_anglbrack statements closing_anglbrack'
    t[0] = ('body', t[2])

def p_statements(t):
    'statements : statements statement'
    t[0] = t[1] + [t[2]]

def p_statements_single(t):
    'statements : statement'
    t[0] = [t[1]]

def p_statements_empty(t):
    'statements :'
    t[0] = []
    
#STATEMENT ::= ASSIGN | CONDITION | CYCLE | F_CALL | PRINT

def p_statement_assign(t):
    'statement : assign'
    t[0] = t[1]
    

def p_statement_condition(t):
    'statement : condition'
    t[0] = t[1]

def p_statement_cycle(t):
    'statement : cycle'
    t[0] = t[1]

def p_statement_f_call(t):
    'statement : f_call'
    t[0] = t[1]

def p_statement_print(t):
    'statement : print_statement'
    t[0] = t[1]

# ASSIGN   ::= 'id' '=' (EXPRESSION | 'cte_string' ) ';'
def p_assign(t):
    'assign : identifier op_assign expression semicol'
    if not Scopes.error_found:
        Ds.add_assignation(t[1], Scopes.scope_stack, t.lineno(1))

def p_assign_string(t):
    'assign : identifier op_assign const_string semicol'
    if not Scopes.error_found:
        addr = const_table.get_or_add(t[3], "string")
        Ds.add_to_operand_stack(t[3], 'string', 1, addr)
        Ds.add_assignation(t[1], Scopes.scope_stack, t.lineno(1))

# EXPRESSION ::= EXP ( ( '>' | '<' | '>=' | '<=' | '!=' | '==' ) EXP )?
def p_expression(t):
    'expression : exp'
    
def p_expression_less(t):
    'expression : exp op_lesser_than exp'
    if not Scopes.error_found:
        Ds.add_to_quad_list("<", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_expression_more(t):
    'expression : exp op_more_than exp'
    #agregar validación
    if not Scopes.error_found:
        Ds.add_to_quad_list(">", Scopes.scope_stack[-1]["addresses"], t.lineno(2))


def p_expression_less_equal(t):
    'expression : exp op_lessthan_equal exp'
    if not Scopes.error_found:
        Ds.add_to_quad_list("<=", Scopes.scope_stack[-1]["addresses"], t.lineno(2))


def p_expression_more_equal(t):
    'expression : exp op_morethan_equal exp'
    if not Scopes.error_found:
        Ds.add_to_quad_list(">=", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_expression_equals(t):
    'expression : exp op_equals exp'
    if not Scopes.error_found:
        Ds.add_to_quad_list("==", Scopes.scope_stack[-1]["addresses"], t.lineno(2))


def p_expression_not_equal(t):
    'expression : exp op_not_equal exp'
    if not Scopes.error_found:
        Ds.add_to_quad_list("!=", Scopes.scope_stack[-1]["addresses"], t.lineno(2))


#EXP      ::= TERM ( ( '+' | '-' ) TERM )*
def p_exp_suma(t):
    'exp : exp op_plus term'
    if not Scopes.error_found:
        Ds.add_to_quad_list("+", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_exp_minus(t):
    'exp : exp op_minus term'
    # t[0] = t[1] - t[3]
    if not Scopes.error_found:
        Ds.add_to_quad_list("-", Scopes.scope_stack[-1]["addresses"], t.lineno(2))
    

def p_exp_term(t):
    'exp : term'
    
#TERM     ::= FACTOR ( ( '*' | '/' ) FACTOR )*
def p_term_mult(t):
    'term : term op_mult factor'
    if not Scopes.error_found:
        Ds.add_to_quad_list("*", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_term_div(t):
    'term : term op_div factor'
    if not Scopes.error_found:
        Ds.add_to_quad_list("/", Scopes.scope_stack[-1]["addresses"], t.lineno(2))


def p_term_factor(t):
    'term : factor'
    

# FACTOR   ::= '(' EXPRESSION ')' | ( '+' | '-' )? ( 'id' | CTE )

def p_factor_expression(t):
    'factor : opening_par expression closing_par'

def p_factor_plus_id(t):
    'factor : op_plus identifier'
    if not Scopes.error_found:
        name = t[2]
        var = name in Scopes.scope_stack[-1]['var_table']
        if (var and Scopes.scope_stack[-1]['var_table'][name]['is_null'] == False):
            address = Scopes.scope_stack[-1]['var_table'][name]["address"]
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1, address)
        else:
            Ds.add_to_operand_stack(name, 'error', 0, None)
            error = "Variable " + name + " Does not exist in scope or has not been defined at line " + str(t.lineno(2)) 
            Ds.errors_found.append(error)
            Ds.error_found = True
        # Ds.add_single_to_quad("+", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_factor_plus_cte(t):
    'factor : op_plus cte'
    # if not Scopes.error_found:
    #     Ds.add_single_to_quad("+", Scopes.scope_stack[-1]["addresses"], t.lineno(1))


def p_factor_minus_id(t):
    'factor : op_minus identifier'
    if not Scopes.error_found:
        name = t[2]
        var = name in Scopes.scope_stack[-1]['var_table']
        if (var and Scopes.scope_stack[-1]['var_table'][name]['is_null'] == False):
            address = Scopes.scope_stack[-1]['var_table'][name]["address"]
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1, address)
        else:
            Ds.add_to_operand_stack(name, 'error', 0)
            error = "Variable " + name + " Does not exist in scope at line " + str(t.lineno(2))
            Ds.errors_found.append(error)
            Ds.error_found = True
        Ds.add_single_to_quad("-", Scopes.scope_stack[-1]["addresses"], t.lineno(2))

def p_factor_minus_cte(t):
    'factor : op_minus cte'
    if not Scopes.error_found:
        Ds.add_single_to_quad("-", Scopes.scope_stack[-1]["addresses"], t.lineno(1))

def p_factor_id(t):
    'factor : identifier'
    if not Scopes.error_found:
        name = t[1]
        var = name in Scopes.scope_stack[-1]['var_table']
        if (var and Scopes.scope_stack[-1]['var_table'][name]['is_null'] == False):
            address = Scopes.scope_stack[-1]['var_table'][name]["address"]
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1, address)
        else:
            Ds.add_to_operand_stack(name, 'error', 0, None)
            error = "Variable " + name + " Does not exist in scope at line " + str(t.lineno(1))
            Ds.errors_found.append(error)
            Ds.error_found = True

def p_factor_cte(t):
    'factor : cte'

#CTE      ::= 'cte_int' | 'cte_float'
def p_cte_int(t):
    'cte : const_int'
    addr = const_table.get_or_add(t[1], "int")
    Ds.add_to_operand_stack(t[1], "int", 1, addr)
    
def p_cte_float(t):
    'cte : const_float'
    addr = const_table.get_or_add(t[1], "float")
    Ds.add_to_operand_stack(t[1], "float", 1, addr)


#F_CALL   ::= 'id' '(' ( EXPRESSION ( ',' EXPRESSION )* )? ')' ';'
def p_f_call(t):
    'f_call : check_function opening_par arguments closing_par make_call_quads'

    t[0] = ('call', t[1], t[3])

def p_check_function(t):
    'check_function : identifier'
    if not Scopes.error_found:
        if (t[1] in Scopes.function_directory):
            Scopes.name_called = t[1]
            Ds.quad_list.append(("sub", Scopes.function_directory[t[1]]["address"], None, None, None))
        else:
            error = "Function " + t[1] + " Does not exist at line " + str(t.lineno(1))
            Ds.errors_found.append(error)
            Ds.error_found = True
            Scopes.error_found = True

def p_make_call_quads(t):
    'make_call_quads : semicol'
    if not Scopes.error_found:
        Ds.fcallquads(Scopes, t.lineno(1))

def p_arguments_mult(t):
    'arguments : arguments comma expression'
    t[0] = t[1] + [t[3]]
    Ds.addParam()

def p_arguments_single(t):
    'arguments : expression'
    t[0] = [t[1]]
    Ds.addParam()


def p_arguments_empty(t):
    'arguments : '
    t[0] = []

#PRINT    ::= 'print' '(' ( 'cte.string' | EXPRESSION ) ( ',' ( 'cte.string' | EXPRESSION ) )* ')' ';'
def p_print_statement(t):
    'print_statement : PRINT opening_par print_args closing_par last_print'

def p_print_args(t):
    'print_args : print_args comma print_arg'

def p_print_args_single(t):
    'print_args : print_arg'

def p_print_arg_expression(t):
    'print_arg : expression'
    if not Scopes.error_found:
        Ds.addPrint()
    
def p_print_arg_string(t):
    'print_arg : const_string'
    if not Scopes.error_found:
        addr = const_table.get_or_add(t[1], "string")
        Ds.add_to_operand_stack(t[1], 'str', 1, addr)
        Ds.addPrint()


def p_last_print(t):
    'last_print : semicol'
    if not Scopes.error_found:
        Ds.addLast_print()


def p_last_print_dummy(t):
    'last_print_dummy : semicol'

#Error dentro de expresión de string
def p_print_error(t):
    'print_statement : PRINT opening_par error closing_par last_print_dummy'
    global error_list
    error_list.append("At Print call: bad expression")
    

#CYCLE    ::= 'do' BODY 'while' '(' EXPRESSION ')' ';'
def p_cycle(t):
    'cycle : start_cycle body WHILE opening_par expression end_cycle semicol'
    
def p_start_cycle(t):
    'start_cycle : DO'
    Ds.start_cycle()

def p_start_cycle_dummy(t):
    'start_cycle_dummy : DO'

def p_end_cycle(t):
    'end_cycle : closing_par'
    if not Scopes.error_found:
        Ds.add_cycle(t.lineno(1))

    
def p_end_cycle_dummy(t):
    'end_cycle_dummy : closing_par'

#Error de expresión
def p_cycle_error(t):
    'cycle : start_cycle_dummy body WHILE opening_par error end_cycle_dummy semicol'
    global error_list
    error_list.append("At cycle definition: Bad expression")
    

#CONDITION ::= 'if' '(' EXPRESSION ')' BODY ( 'else' BODY )? ';'

def p_condition(t):
    'condition : IF opening_par expression gotof body check_else last_goto'

def p_gotof(t):
    'gotof : closing_par'
    if not Scopes.error_found:
        Ds.add_gotof(t.lineno(1))

def p_gotof_dummy(t):
    'gotof_dummy : closing_par'

def p_check_else(t):
    'check_else : else_goto body' 
    
#revisar con dummy y errores sintácticos
def p_else_goto(t):
    'else_goto : ELSE '
    if not Scopes.error_found:
        Ds.add_goto()

def p_last_goto(t):
    'last_goto : semicol'
    if not Scopes.error_found:
        Ds.end_goto()

def p_last_goto_dummy(t):
    'last_goto_dummy : semicol'

def p_check_else_empty(t):
    'check_else : '
    t[0] = None

#Error de expresión
def p_condition_error(t):
    'condition : IF opening_par error gotof_dummy body check_else last_goto_dummy'
    global error_list
    error_list.append("At If creation: Bad expression")

    t[0] = []


#Error general
def p_error(t):
    global syntax_error
    syntax_error+=1
    if not t:
        print("❌ Syntax error: unexpected end of file")
        return
    print(f"❌ Syntax error at line {t.lineno}, lexpos {t.lexpos}, unexpected token '{t.value}'.")
    Ds.error_found = True
    Scopes.error_found = True


parser = yacc.yacc()

print("\n--SYNTAX ANALYSIS--")

lexer.lineno = 1

result = parser.parse(input_program, lexer=lexer)
if syntax_error > 0:
    print("\nAmount of syntactical errors found: ",syntax_error)
    for x in error_list:
        print(x)
    if (syntax_error != len (error_list)):
        print("Unknown error also detected that stopped analysis abruptly")
else:
    print("\nNO SYNTAX ERRORS FOUND ")

print("\n--SEMANTICAL ANALYSIS--")
print("-Quadruples-")

if(not Ds.error_found and not Scopes.error_found and syntax_error == 0):
    print("Number/Operator/Left/Right/result/result_type")
    count = 1
    for quad in Ds.quad_list:
        print(count, quad[0], quad[1], quad[2], quad[3], quad[4])
        count+=1
    
    global_counts = {}
    for segment, base in mem_manager.counters.items():
        start = {
            'global_int': 1000,
            'global_float': 2000,
            'global_string': 3000,
            'global_void': 4000,
            'local_int': 7000,
            'local_float': 8000,
            'local_string': 9000,
            'temp_int': 12000,
            'temp_float': 13000,
            'temp_bool': 14000,
            'cte_int': 17000,
            'cte_float': 18000,
            'cte_string': 19000,
        }[segment]
        used = base - start
        global_counts[segment] = used

    # Obtenemos contadores de las variables de cada función, sumando los valores de main a nuestros datos globales
    for x in Scopes.function_directory:
        print(x, Scopes.function_directory[x]["address"])
        y = Scopes.function_directory[x]["addresses"]

        for segment, base in y.counters.items():
            start = {
                'global_int': 1000,
                'global_float': 2000,
                'global_string': 3000,
                'global_void': 4000,
                'local_int': 7000,
                'local_float': 8000,
                'local_string': 9000,
                'temp_int': 12000,
                'temp_float': 13000,
                'temp_bool': 14000,
                'cte_int': 17000,
                'cte_float': 18000,
                'cte_string': 19000,
            }[segment]
            used = base - start
            if Scopes.function_directory[x]["return_type"] == "program":
                global_counts[segment] += used
            else:
                Scopes.function_directory[x]["addresses"].counters[segment] = used

    
    # Imprimimos contadores de las variables por función
    print("\nFunction Addresses:")
    for x in Scopes.function_directory:
        if (Scopes.function_directory[x]["return_type"] != "program"):
            print(x, Scopes.function_directory[x]["address"])
            print("params", Scopes.function_directory[x]["n_params"])
            print("local_int", Scopes.function_directory[x]["addresses"].counters["local_int"])
            print("local_float", Scopes.function_directory[x]["addresses"].counters["local_float"])
            print("local_string", Scopes.function_directory[x]["addresses"].counters["local_string"])
            print("temp_int", Scopes.function_directory[x]["addresses"].counters["temp_int"])
            print("temp_float", Scopes.function_directory[x]["addresses"].counters["temp_float"])
            print("temp_bool", Scopes.function_directory[x]["addresses"].counters["temp_bool"])
        else:
            print(x, Scopes.function_directory[x]["address"])
            for y in global_counts:
                print(y, global_counts[y])
        
        print("")

    for x in const_table.table:
        print(x, const_table.table[x])    

    # print("--Symbol Table--")

    # for scope in Scopes.function_directory:
    #     print(scope)
    #     for var in Scopes.function_directory[scope]['var_table']:
    #         print ( var ,Scopes.function_directory[scope]['var_table'][var])

    #Pasamos los datos necesarios de la memoria a el output
     
    with open('output.txt', 'w') as f:
        # for tupla in Ds.quad_list:
        #     f.write(str(tupla) + '\n')
        
        #pasamos constantes
        for x in const_table.table:
            f.write(str(x) +" " + str(const_table.table[x]) + '\n')  
        
        #pasamos variables de funciones
        f.write('\n') 
        for x in Scopes.function_directory:
            if (Scopes.function_directory[x]["return_type"] != "program"):
                f.write( str(Scopes.function_directory[x]["address"]) + "\n")
                f.write("params" + " " + str(Scopes.function_directory[x]["n_params"]) + "\n" )
                f.write("local_int" + " " + str(Scopes.function_directory[x]["addresses"].counters["local_int"]) + "\n")
                f.write("local_float" + " " + str(Scopes.function_directory[x]["addresses"].counters["local_float"]) + "\n")
                f.write("local_string" + " " + str( Scopes.function_directory[x]["addresses"].counters["local_string"]) + "\n")
                f.write("temp_int" + " " + str(Scopes.function_directory[x]["addresses"].counters["temp_int"]) + "\n" )
                f.write("temp_float" + " " + str(Scopes.function_directory[x]["addresses"].counters["temp_float"]) + "\n")
                f.write("temp_bool"+ " " + str(Scopes.function_directory[x]["addresses"].counters["temp_bool"]) + "\n")
            else:
                # f.write( str(x) + " " + str(Scopes.function_directory[x]["address"]) + "\n")
                for y in global_counts:
                    f.write(str(y) + " " + str(global_counts[y]) + "\n")
            f.write('\n') 
        
        #Pasamos los cuádruplos
        count = 1
        for tupla in Ds.quad_list:
            f.write(str(count) + " ")
            for item in range(len(tupla)-1):
                if tupla[item] == None:
                    f.write( "-1 ")
                else:
                    f.write( str(tupla[item])  + " ")
            f.write("\n")
            count +=1

    
else:
    print("--Errors Found--")
    #Por si acaso, sólo imprimimos el primer error ya que es el más relevante
    if( Ds.error_found):
        print(Ds.errors_found[0])
    if(Scopes.error_found):
        print(Scopes.errors[0])

# print(const_table.table)
