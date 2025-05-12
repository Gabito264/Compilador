from lexer import tokens, lexer, input_program
from semantic_cube import semantic_cube
import ply.yacc as yacc

start = 'programa'

current_program = 'program'
function_directory = {}
scope_stack=[]

operator_stack = []
operand_stack = []

syntax_error = 0
error_list = []

class objects:
    t_count = 0
    quad_list = []
    def __init__(self):
        self.t_count = 0
        self.quad_list = []

Ds = objects()

def declare_vars_in_scope(id_list, var_type, lineno):
    current_scope = scope_stack[-1]
    for name in id_list:
        if name in current_scope:
            error_list.append(f"Variable '{name}' already declared in current scope (line {lineno})")
        else:
            if (current_program == 'program'):
                current_scope[name] = {
                    'scope' : 'global',
                    'type': var_type,
                    'value': None,
                    'declared_line': lineno,
                    'is_null' : True
                }
            else:
                current_scope[name] = {
                    'scope' : 'local',
                    'type': var_type,
                    'value': None,
                    'declared_line': lineno,
                    'is_null' : True
                }

#PROGRAMA ::= 'program' 'id' ';' VARS? FUNCS* 'main' BODY 'end'
def p_programa(t):
    'programa : PROGRAM identifier create_program semicol vars funcs MAIN body END elim_program'
    t[0] = ('programa', t[2], t[5], t[6], t[8])

def p_create_program(t):
    'create_program : '
    function_directory[t[-1]] = {
            'return_type' : 'program',
            'n_params' : 0,
            'var_table' : {}
        }
    scope_stack.append(function_directory[t[-1]]['var_table'])

def p_elim_program(t):
    'elim_program : '
    #próximamente
    scope_stack.pop()

#Error en definir el nombre del programa
def p_programa_id_error(t):
    'programa : PROGRAM error semicol vars funcs MAIN body END'
    global error_list
    error_list.append("At program: Incorrect program name")
    t[0] = ('programa', 'default', t[4], t[5], t[7])

#VARS     ::= 'var' ( 'id' ( ',' 'id' )* ':' TYPE ';' )+
def p_vars(t):
    'vars : VAR var_definition'
    t[0] = t[2]

def p_vars_empty(t):
    'vars : '
    t[0] = []

def p_definition(t):
    'var_definition : id_list twopoint type semicol var_definition'
    declare_vars_in_scope(t[1], t[3], t.lineno(3))
    t[0] = [('var_decl', t[1], t[3])] + t[5]
    

def p_definition_once(t):
    'var_definition : id_list twopoint type semicol'
    declare_vars_in_scope(t[1], t[3], t.lineno(3))
    t[0] = [('var_decl', t[1], t[3])]

def p_id_list(t):
    'id_list : identifier comma id_list'
    t[0] = [t[1]] + t[3]

def p_id_list_once(t):
    'id_list : identifier'
    t[0] = [t[1]]

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
    'func : VOID identifier opening_par param_list closing_par opening_brack vars body closing_brack semicol'
    t[0] = ('func', t[2], t[4], t[7], t[8]) 

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

#Error al definir func
def p_func_error(t):
    'func : VOID identifier opening_par error closing_par opening_brack vars body closing_brack semicol'
    global error_list
    error_list.append("At function creation: Bad list of parameters")
    
    t[0] = []

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
    last, last_type, is_valid = operand_stack.pop()
    if(scope_stack[-1][t[1]]):
        scope_stack[-1][t[1]]["is_Null"] = False
        result = ('=', last, None, t[1])
        print(result)

def p_assign_string(t):
    'assign : identifier op_assign const_string semicol'
    # names[t[1]] = t[3]
    # t[0] = names[t[1]]

#error en asignación normal, expresiones inválidas
def p_assign_error(t):
    "assign : identifier op_assign error semicol" 
    global error_list
    error_list.append("At asignation: Incorrect expression")

# EXPRESSION ::= EXP ( ( '>' | '<' | '>=' | '<=' | '!=' | '==' ) EXP )?
def p_expression(t):
    'expression : exp'
    t[0] = t[1]

def p_expression_less(t):
    'expression : exp op_lesser_than exp'
    # t[0] = t[1] < t[3]

def p_expression_more(t):
    'expression : exp op_more_than exp'
    # t[0] = t[1] > t[3]

def p_expression_less_equal(t):
    'expression : exp op_lessthan_equal exp'
    t[0] = t[1] <= t[3]

def p_expression_more_equal(t):
    'expression : exp op_morethan_equal exp'
    t[0] = t[1] >= t[3]

def p_expression_equals(t):
    'expression : exp op_equals exp'
    t[0] = t[1] == t[3]

def p_expression_not_equal(t):
    'expression : exp op_not_equal exp'
    t[0] = t[1] != t[3]

#EXP      ::= TERM ( ( '+' | '-' ) TERM )*
def p_exp_suma(t):
    'exp : exp op_plus term'
    # t[0] = t[1] + t[3]
    right, r_type, r_valid = operand_stack.pop()
    left, l_type, l_valid= operand_stack.pop()
    result = semantic_cube[l_type]["+"][r_type]
    if (result != "error"):
        Ds.t_count +=1
        
        temp = "t_" + str(Ds.t_count)
        operand_stack.append((temp, result, 1))
        print("+ ", left, right, temp)
    else:
        print("Invalid sum operation between " , l_type," and " ,r_type)

def p_exp_minus(t):
    'exp : exp op_minus term'
    # t[0] = t[1] - t[3]

def p_exp_term(t):
    'exp : term'
    t[0] = t[1]

#TERM     ::= FACTOR ( ( '*' | '/' ) FACTOR )*
def p_term_mult(t):
    'term : term op_mult factor'
    # t[0] = t[1] * t[3]

def p_term_div(t):
    'term : term op_div factor'
    t[0] = t[1] / t[3]

def p_term_factor(t):
    'term : factor'
    t[0] = t[1]

# FACTOR   ::= '(' EXPRESSION ')' | ( '+' | '-' )? ( 'id' | CTE )

def p_factor_expression(t):
    'factor : opening_par expression closing_par'
    t[0] = t[2]

def p_factor_plus_id(t):
    'factor : op_plus identifier'
    # try:
    #     t[0] = scope_stack[-1][t[2]]
    # except LookupError:
    #     #print("undefined variable '%s'" % t[2]) 
    #     t[0] = 0

def p_factor_plus_cte(t):
    'factor : op_plus cte'
    t[0] = t[2]

def p_factor_minus_id(t):
    'factor : op_minus identifier'
    try:
        t[0] = -scope_stack[-1][t[1]]
    except LookupError:
        #print("undefined variable '%s'" % t[2]) 
        t[0] = 0

def p_factor_minus_cte(t):
    'factor : op_minus cte'
    t[0] = - t[2]

def p_factor_id(t):
    'factor : identifier'
    name = t[1]
    var = scope_stack[-1].get(name)
    if (var):
        operand_stack.append((name, var["type"], 1))
    else:
        print("Inexistent identifier ", name, " in scope")
        operand_stack.append((name, "None", 0))



def p_factor_cte(t):
    'factor : cte'
    t[0] = t[1]


#CTE      ::= 'cte_int' | 'cte_float'
def p_cte_int(t):
    'cte : const_int'
    value = t[1]
    operand_stack.append((t[1], "int", 1))
    t[0] = value
    

def p_cte_float(t):
    'cte : const_float'
    value = t[1]
    operand_stack.append((t[1], "float", 1))
    t[0] = value 

#F_CALL   ::= 'id' '(' ( EXPRESSION ( ',' EXPRESSION )* )? ')' ';'
def p_f_call(t):
    'f_call : identifier opening_par arguments closing_par semicol'
    t[0] = ('call', t[1], t[3])

def p_arguments_mult(t):
    'arguments : arguments comma expression'
    t[0] = t[1] + [t[3]]

def p_arguments_single(t):
    'arguments : expression'
    t[0] = [t[1]]

def p_arguments_empty(t):
    'arguments : '
    t[0] = []

#Error de malos arguments
def p_f_call_error(t):
    'f_call : identifier opening_par error closing_par semicol'
    
    global error_list
    error_list.append("At Function call: bad arguments")
    t[0] = []

#PRINT    ::= 'print' '(' ( 'cte.string' | EXPRESSION ) ( ',' ( 'cte.string' | EXPRESSION ) )* ')' ';'
def p_print_statement(t):
    'print_statement : PRINT opening_par print_args closing_par semicol'
    t[0] = ('print', t[3])

def p_print_args(t):
    'print_args : print_args comma print_arg'
    t[0] = t[1] + [t[3]]

def p_print_args_single(t):
    'print_args : print_arg'
    t[0] = [t[1]]

def p_print_arg_expression(t):
    'print_arg : expression'
    t[0] = t[1]

def p_print_arg_string(t):
    'print_arg : const_string'
    t[0] = t[1][1:-1] 

#Error dentro de expresión de string
def p_print_error(t):
    'print_statement : PRINT opening_par error closing_par semicol'
    global error_list
    error_list.append("At Print call: bad expression")
    

#CYCLE    ::= 'do' BODY 'while' '(' EXPRESSION ')' ';'
def p_cycle(t):
    'cycle : DO body WHILE opening_par expression closing_par semicol'
    t[0] = ('cycle', t[2], t[5])

#Error de expresión
def p_cycle_error(t):
    'cycle : DO body WHILE opening_par error closing_par semicol'
    global error_list
    error_list.append("At cycle definition: Bad expression")
    t[0] = []

#CONDITION ::= 'if' '(' EXPRESSION ')' BODY ( 'else' BODY )? ';'

def p_condition(t):
    'condition : IF opening_par expression closing_par body check_else semicol'
    if t[5] and t[6]:  # hay un else
        t[0] = ('if_else', t[3], t[5], t[6])
    else:
        t[0] = ('if', t[3], t[5])

def p_check_else(t):
    'check_else : ELSE body' 
    t[0] = t[2]

def p_check_else_empty(t):
    'check_else : '
    t[0] = None

#Error de expresión
def p_condition_error(t):
    'condition : IF opening_par error closing_par body check_else semicol'
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
    print("\nNO ERRORS FOUND ")

print(operand_stack)
#print(function_directory)