from lexer import tokens, lexer, input_program
from semantic_cube import semantic_cube
from semantic_structures import program_functions, objects
import ply.yacc as yacc

start = 'programa'


syntax_error = 0
error_list = []

Scopes = program_functions()

Ds = objects()

#PROGRAMA ::= 'program' 'id' ';' VARS? FUNCS* 'main' BODY 'end'
def p_programa(t):
    'programa : PROGRAM create_program semicol vars funcs complete_main body elim_program'
    t[0] = ('programa', t[2], t[5], t[6], t[8])

def p_create_program(t):
    'create_program : identifier'
    Scopes.create_function('program', t[1])
    Ds.create_main()

def p_complete_main(t):
    'complete_main : MAIN'
    Ds.complete_main()

def p_elim_program(t):
    'elim_program : END'
    Scopes.eliminate_function()

#Error en definir el nombre del programa
# def p_programa_id_error(t):
#     'programa : PROGRAM error semicol vars funcs MAIN body END'
#     global error_list
#     error_list.append("At program: Incorrect program name")
#     t[0] = ('programa', 'default', t[4], t[5], t[7])

#VARS     ::= 'var' ( 'id' ( ',' 'id' )* ':' TYPE ';' )+
def p_vars(t):
    'vars : VAR var_definition'
    t[0] = t[2]

def p_vars_empty(t):
    'vars : '
    t[0] = []

def p_definition(t):
    'var_definition : id_list twopoint type semicol var_definition'
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), False)
    t[0] = [('var_decl', t[1], t[3])] + t[5]
    
def p_definition_once(t):
    'var_definition : id_list twopoint type semicol'
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), False)
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
    Scopes.create_function('Void', t[1])

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
    Scopes.declare_vars_in_scope(t[1], t[3], t.lineno(2), True)

#Error al definir func
# def p_func_error(t):
#     'func : VOID identifier opening_par error closing_par opening_brack vars body closing_brack semicol'
#     global error_list
#     error_list.append("At function creation: Bad list of parameters")
    
#     t[0] = []

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
        Ds.add_assignation(t[1], Scopes.scope_stack)

def p_assign_string(t):
    'assign : identifier op_assign const_string semicol'
    if not Scopes.error_found:
        Ds.add_to_operand_stack(t[3], 'string', 1)
        Ds.add_assignation(t[1], Scopes.scope_stack)

#error en asignación normal, expresiones inválidas
# def p_assign_error(t):
#     "assign : identifier op_assign error semicol" 
#     global error_list
#     error_list.append("At asignation: Incorrect expression")

# EXPRESSION ::= EXP ( ( '>' | '<' | '>=' | '<=' | '!=' | '==' ) EXP )?
def p_expression(t):
    'expression : exp'
    
def p_expression_less(t):
    'expression : exp op_lesser_than exp'
    Ds.add_to_quad_list("<")

def p_expression_more(t):
    'expression : exp op_more_than exp'
    Ds.add_to_quad_list(">")

def p_expression_less_equal(t):
    'expression : exp op_lessthan_equal exp'
    Ds.add_to_quad_list("<=")

def p_expression_more_equal(t):
    'expression : exp op_morethan_equal exp'
    Ds.add_to_quad_list(">=")

def p_expression_equals(t):
    'expression : exp op_equals exp'
    Ds.add_to_quad_list("==")

def p_expression_not_equal(t):
    'expression : exp op_not_equal exp'
    Ds.add_to_quad_list("!=")

#EXP      ::= TERM ( ( '+' | '-' ) TERM )*
def p_exp_suma(t):
    'exp : exp op_plus term'
    Ds.add_to_quad_list("+")

def p_exp_minus(t):
    'exp : exp op_minus term'
    # t[0] = t[1] - t[3]
    Ds.add_to_quad_list("-")

def p_exp_term(t):
    'exp : term'
    
#TERM     ::= FACTOR ( ( '*' | '/' ) FACTOR )*
def p_term_mult(t):
    'term : term op_mult factor'
    Ds.add_to_quad_list("*")

def p_term_div(t):
    'term : term op_div factor'
    Ds.add_to_quad_list("/")

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
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1)
        else:
            Ds.add_to_operand_stack(name, 'error', 0)
            error = "Variable " + name + " Does not exist in scope or has not been defined"
            Ds.errors_found.append(error)
            Ds.error_found = True
        Ds.add_single_to_quad("+")

def p_factor_plus_cte(t):
    'factor : op_plus cte'
    Ds.add_single_to_quad("+")

def p_factor_minus_id(t):
    'factor : op_minus identifier'
    if not Scopes.error_found:
        name = t[2]
        var = name in Scopes.scope_stack[-1]['var_table']
        if (var and Scopes.scope_stack[-1]['var_table'][name]['is_null'] == False):
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1)
        else:
            Ds.add_to_operand_stack(name, 'error', 0)
            error = "Variable " + name + " Does not exist in scope"
            Ds.errors_found.append(error)
            Ds.error_found = True
        Ds.add_single_to_quad("-")

def p_factor_minus_cte(t):
    'factor : op_minus cte'
    Ds.add_single_to_quad("-")

def p_factor_id(t):
    'factor : identifier'
    if not Scopes.error_found:
        name = t[1]
        var = name in Scopes.scope_stack[-1]['var_table']
        if (var and Scopes.scope_stack[-1]['var_table'][name]['is_null'] == False):
            Ds.add_to_operand_stack(name, Scopes.scope_stack[-1]['var_table'][name]["type"], 1)
        else:
            Ds.add_to_operand_stack(name, 'error', 0)
            error = "Variable " + name + " Does not exist in scope"
            Ds.errors_found.append(error)
            Ds.error_found = True

def p_factor_cte(t):
    'factor : cte'

#CTE      ::= 'cte_int' | 'cte_float'
def p_cte_int(t):
    'cte : const_int'
    Ds.add_to_operand_stack(t[1], "int", 1)
    
def p_cte_float(t):
    'cte : const_float'
    Ds.add_to_operand_stack(t[1], "float", 1)

#F_CALL   ::= 'id' '(' ( EXPRESSION ( ',' EXPRESSION )* )? ')' ';'
def p_f_call(t):
    'f_call : check_function opening_par arguments closing_par make_call_quads'

    t[0] = ('call', t[1], t[3])

def p_check_function(t):
    'check_function : identifier'
    if not Scopes.error_found:
        if (t[1] in Scopes.function_directory):
            Scopes.name_called = t[1]
        else:
            error = "Function " + t[1] + " Does not exist"
            Ds.errors_found.append(error)
            Ds.error_found = True
            Scopes.error_found = True

def p_make_call_quads(t):
    'make_call_quads : semicol'
    if not Scopes.error_found:
        Ds.fcallquads(Scopes)

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

#Error de malos arguments
# def p_f_call_error(t):
#     'f_call : identifier opening_par error closing_par semicol'
    
#     global error_list
#     error_list.append("At Function call: bad arguments")
#     t[0] = []

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
        Ds.add_to_operand_stack(t[1], 'string', 1)
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
        Ds.add_cycle()

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
    Ds.add_gotof()

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
    with open('output.txt', 'w') as f:
        for tupla in Ds.quad_list:
            f.write(str(tupla) + '\n')

    print("--Symbol Table--")

    for scope in Scopes.function_directory:
        print(scope)
        for var in Scopes.function_directory[scope]['var_table']:
            print ( var ,Scopes.function_directory[scope]['var_table'][var])
else:
    print("--Errors Found--")
    for x in Ds.errors_found:
        print (x)
    for x in Scopes.errors:
        print(x)