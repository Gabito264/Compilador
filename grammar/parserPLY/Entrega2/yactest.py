from lexer import tokens, lexer, input_program
import ply.yacc as yacc

start = 'x'
names = {}
def p_x(t):
    'x : opening_anglbrack program closing_anglbrack'
    t[0] = t[1]

def p_program(t):
    'program : program assign'
    t[0] = ('program', t[1], t[2])

def p_program_once(t):
    'program : assign'
    t[0] = ('program', t[1])

# ASSIGN   ::= 'id' '=' (EXPRESSION | 'cte_string' ) ';'
def p_assign(t):
    'assign : identifier op_assign expression semicol'
    names[t[1]] = t[3]
    t[0] = names[t[1]]

def p_assign_string(t):
    'assign : identifier op_assign const_string semicol'
    names[t[1]] = t[3]
    t[0] = names[t[1]]

# EXPRESSION ::= EXP ( ( '>' | '<' | '>=' | '<=' | '!=' | '==' ) EXP )?
def p_expression(t):
    'expression : exp'
    t[0] = t[1]

def p_expression_less(t):
    'expression : exp op_lesser_than exp'
    t[0] = t[1] < t[3]

def p_expression_more(t):
    'expression : exp op_more_than exp'
    t[0] = t[1] > t[3]

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
    t[0] = t[1] + t[3]

def p_exp_minus(t):
    'exp : exp op_minus term'
    t[0] = t[1] - t[3]

def p_exp_term(t):
    'exp : term'
    t[0] = t[1]

#TERM     ::= FACTOR ( ( '*' | '/' ) FACTOR )*
def p_term_mult(t):
    'term : term op_mult factor'
    t[0] = t[1] * t[3]

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
    try:
        t[0] = +names[t[2]]
    except LookupError:
        #print("undefined variable '%s'" % t[2]) 
        t[0] = 0

def p_factor_plus_cte(t):
    'factor : op_plus cte'
    t[0] = + t[2]

def p_factor_minus_id(t):
    'factor : op_minus identifier'
    try:
        t[0] = -names[t[2]]
    except LookupError:
        #print("undefined variable '%s'" % t[2]) 
        t[0] = 0

def p_factor_minus_cte(t):
    'factor : op_minus cte'
    t[0] = - t[2]

def p_factor_id(t):
    'factor : identifier'
    try:
        t[0] = names[t[1]]
    except LookupError:
        #print("undefined variable '%s'" % t[1]) 
        t[0] = 0

def p_factor_cte(t):
    'factor : cte'
    t[0] = t[1]

#CTE      ::= 'cte_int' | 'cte_float'
def p_cte_int(t):
    'cte : const_int'
    t[0] = int(t[1])

def p_cte_float(t):
    'cte : const_float'
    t[0] = float(t[1]) 

def p_error(t):
    if not t:
        print("❌ Error de sintaxis: fin inesperado del archivo.")
        return

    print(f"❌ Error de sintaxis en línea {t.lineno}, token inesperado '{t.value}'.")

    # while True:
    #     tok = parser.token()
    #     if not tok or tok.type == 'semicol':
    #         break
        
    # parser.errok()

parser = yacc.yacc()

print("\n--Análisis de sintaxis--")

lexer.lineno = 1

result = parser.parse(input_program, lexer=lexer)