# -*- coding: utf-8 -*-
import ply.lex as lex

#Tabla de símbolos
identifier_list = {}

#Palabras reservadas para cambiar si se encuentran como identificador
reserved_words = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'print': 'PRINT',
    'void': 'VOID',
    'main': 'MAIN',
    'program': 'PROGRAM',
    'var': 'VAR',
    'end': 'END',
    'int': 'INTEGER',
    'float': 'FLOAT',
    'string': 'STRING', 
}

#Lista de tokens aceptados
tokens = [
    'const_int',
    'const_float',
    'const_string',
    'identifier',
    'comment',
    'op_assign',
    'semicol',
    'op_plus',
    'op_minus',
    'op_mult',
    'op_div',
    'opening_par',
    'closing_par',
    'opening_anglbrack',
    'closing_anglbrack',
    'opening_brack',
    'closing_brack',
    'op_more_than',
    'op_morethan_equal',
    'op_lesser_than',
    'op_lessthan_equal',
    'op_not_equal',
    'op_equals',
    'twopoint',
    'comma',
] + list(reserved_words.values())

# Los tokens simples tienen solo una expresion regular
# Se asignan en variables que inician con t_
# Deben coincidir con lo definido en la lista tokens

t_const_string = r"\"\s?.*\""
t_comment = r"@\s?.*"
t_op_assign = r"="
t_semicol = r";"
t_op_plus = r"\+"
t_op_minus = r"\-"
t_op_mult = r"\*"
t_op_div = r"/"
t_opening_par = r"\("
t_closing_par = r"\)"
t_opening_anglbrack = r"\{"
t_closing_anglbrack = r"\}"
t_opening_brack = r"\["
t_closing_brack = r"\]"
t_op_more_than = r">"
t_op_morethan_equal = r">="
t_op_lesser_than = r"<"
t_op_lessthan_equal = r"<="
t_op_not_equal = r"!="
t_op_equals = r"=="
t_twopoint = r":"
t_comma = r","

# Los tokens que requieran alguna accion adicional, se definen en funciones
# La primer linea es la expresion regular del token
# Luego, van las acciones, por ejemplo, convertir cadenas en enteros


def t_const_float(t):
    r"[0-9]+\.[0-9]+\b"
    t.value = float(t.value)
    return t


def t_const_int(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_identifier(t):
    r'[a-zA-Z]\w*\b'
    #Buscamos si el identificador es una palabra reservada para cambiarlo
    if t.value in reserved_words:
        t.type = reserved_words.get(t.value, 'identifier')
    else:
        #Agregamos a tabla de símbolos con su línea respectiva en la que se encontró
        if t.value in identifier_list:
            identifier_list[t.value]['lines_found'].append(t.lineno)
            identifier_list[t.value]['lexpos'].append(t.lexpos)
        else:
            identifier_list[t.value] ={
                'lines_found' : [t.lineno],
                'lexpos': [t.lexpos],

            } 
    return t


# Numeros de linea, espacios y errores:  no son parte de tokens


# Numeros de linea.
# Hay un contador dentro la clase, aqui se incrementa
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Esto especifica que simbolos se ignoran, tipicamente espacios y tabs
t_ignore = ' \t'


# Muestra errores y sigue avanzando (con skip)
def t_error(t):
    print("\nLEXICAL ERROR !!! UNKNOWN SYMBOL '%s' !!!" % t.value[0], " on line ", t.lineno, " and lexpos ", t.lexpos)
    t.lexer.skip(1)


# Construye el objeto lexer
# La libreria 'sabe' que debe usar las funciones y variables que definimos arriba
# Definición del lexer
lexer = lex.lex()


# Una clase tokens basica...
class Tokens:
  # Atributos
  tokens = []       # una lista de tokens
  pos = 0           # un indice para el token actual

  # Constructor de la clase...
  def __init__(self, lista):
    self.tokens = lista
    self.pos = 0

  # Devuelve el token actual
  def current(self):
    return self.tokens[self.pos]

  # Consume un token, avanzando al siguiente
  def avanza(self):
    self.pos += 1
    return self.tokens[self.pos]

# Guarda errores en una lista
def addError(errors, expected, token, index):
  #print(  f"ERROR index {index}: esperaba {expected}, recibio {token}"  )
  errors.append( f"ERROR en index {index}: esperaba {expected}, recibio {token}"  )
  

#Tabla de parseo para la gramática
parse_table = {
    'ASSIGN': {
        'identifier': ['identifier', 'op_assign', 'EXPRESSION', 'semicol'],
    },
    'EXPRESSION': {
        'identifier': ['EXP', 'REL_OPT'],
        'opening_par': ['EXP', 'REL_OPT'],
        'op_plus': ['EXP', 'REL_OPT'],
        'op_minus': ['EXP', 'REL_OPT'],
        'const_int': ['EXP', 'REL_OPT'],
        'const_float': ['EXP', 'REL_OPT'],
    },
    'REL_OPT': {
        'op_more_than': ['REL_OP', 'EXP'],
        'op_lesser_than': ['REL_OP', 'EXP'],
        'op_morethan_equal': ['REL_OP', 'EXP'],
        'op_lesserthan_equal': ['REL_OP', 'EXP'],
        'op_not_equal': ['REL_OP', 'EXP'],
        'op_equals': ['REL_OP', 'EXP'],
        'semicol': [],     # ε
        'closing_par': [],     # ε
    },
    'REL_OP': {
        'op_more_than': ['op_more_than'],
        'op_lesser_than': ['op_lesser_than'],
        'op_morethan_equal': ['op_morethan_equal'],
        'op_lesserthan_equal': ['op_lesserthan_equal'],
        'op_not_equal': ['op_not_equal'],
        'op_equals': ['op_equals'],
    },
    'EXP': {
        'identifier': ['TERM', 'EXP_PRIME'],
        'opening_par': ['TERM', 'EXP_PRIME'],
        'op_plus': ['TERM', 'EXP_PRIME'],
        'op_minus': ['TERM', 'EXP_PRIME'],
        'const_int': ['TERM', 'EXP_PRIME'],
        'const_float': ['TERM', 'EXP_PRIME'],
    },
    'EXP_PRIME': {
        'op_plus': ['op_plus', 'TERM', 'EXP_PRIME'],
        'op_minus': ['op_minus', 'TERM', 'EXP_PRIME'],
        'op_more_than': [],     # ε
        'op_lesser_than': [],     # ε
        'op_morethan_equal': [],    # ε
        'op_lesserthan_equal': [],    # ε
        'op_not_equal': [],    # ε
        'op_equals': [],    # ε
        'semicol': [],     # ε
        'closing_par': [],     # ε
    },
    'TERM': {
        'identifier': ['FACTOR', 'TERM_PRIME'],
        'opening_par': ['FACTOR', 'TERM_PRIME'],
        'op_plus': ['FACTOR', 'TERM_PRIME'],
        'op_minus': ['FACTOR', 'TERM_PRIME'],
        'const_int': ['FACTOR', 'TERM_PRIME'],
        'const_float': ['FACTOR', 'TERM_PRIME'],
    },
    'TERM_PRIME': {
        'op_mult': ['op_mult', 'FACTOR', 'TERM_PRIME'],
        'op_div': ['op_div', 'FACTOR', 'TERM_PRIME'],
        'op_plus': [],     # ε
        'op_minus': [],     # ε
        'op_more_than': [],     # ε
        'op_lesser_than': [],     # ε
        'op_morethan_equal': [],    # ε
        'op_lesserthan_equal': [],    # ε
        'op_not_equal': [],    # ε
        'op_equals': [],    # ε
        'semicol': [],     # ε
        'closing_par': [],     # ε
    },
    'FACTOR': {
        'opening_par': ['opening_par', 'EXPRESSION', 'closing_par'],
        'op_plus': ['FACTOR_PRIME'],
        'op_minus': ['FACTOR_PRIME'],
        'identifier': ['FACTOR_PRIME'],
        'const_int': ['FACTOR_PRIME'],
        'const_float': ['FACTOR_PRIME'],
    },
    'FACTOR_PRIME': {
        'op_plus': ['SIGN', 'ATOM'],
        'op_minus': ['SIGN', 'ATOM'],
        'identifier': ['ATOM'],
        'const_int': ['ATOM'],
        'const_float': ['ATOM'],
    },
    'SIGN': {
        'op_plus': ['op_plus'],
        'op_minus': ['op_minus'],
    },
    'ATOM': {
        'identifier': ['identifier'],
        'const_int': ['const_int'],
        'const_float': ['const_float'],
    }
}

#Tabla de alias para cuando obtenemos un error
token_aliases = {
    'op_plus': "'+'",
    'op_minus': "'-'",
    'op_mult': "'*'",
    'op_div': "'/'",
    'op_assign': "'='",
    'op_equals': "'=='",
    'op_not_equal': "'!='",
    'op_more_than': "'>'",
    'op_lesser_than': "'<'",
    'op_morethan_equal': "'>='",
    'op_lesserthan_equal': "'<='",
    'identifier': "identificador",
    'const_int': "entero",
    'const_float': "flotante",
    'opening_par': "'('",
    'closing_par': "')'",
    'semicol': "';'",
}

#Función de análisis sintáctico
def assign(tokens, errors, stack):
   
   #Seguimos con el stack hasta que encontremos un error o esté vacío
   while  len(stack) > 0:
      #obtenemos el tope del stack y el token actual
      top = stack[-1]
      current_token = tokens.current()[0]
      #Si nuestro stack no tiene nada, es una línea válida (ej. si la línea está vacía no debería marcar error)
      if top == "$" and current_token == "EOL":
        stack.pop()
        break
      
      #revisamos si top es un token y no una expresión de la gramátical y es el token actual
      elif top == current_token:
        stack.pop()
        tokens.avanza()
      
      #revisamos si top es una expresión gramatical válida
      elif top in parse_table:
        prod = parse_table[top].get(current_token)

        if prod is not None:
          stack.pop()
          #subtituimos el top por lo que hay en 
          for symbol in reversed(prod):
            if symbol != "":
              stack.append(symbol)
        else:
          expected_tokens = list(parse_table[top].keys())
          expected_str = ', '.join([token_aliases.get(tok, tok) for tok in expected_tokens])
          received_token = token_aliases.get(current_token, current_token)
          addError(errors, f"uno de: {expected_str}", received_token, tokens.pos)
          break
      
      else:
        expected_tokens = list(parse_table[top].keys())
        expected_str = ', '.join([token_aliases.get(tok, tok) for tok in expected_tokens])
        received_token = token_aliases.get(current_token, current_token)
        addError(errors, f"uno de: {expected_str}", received_token, tokens.pos)
        break
      



lineas = []

input_program = ""

# Abrimos el archivo y lo leemos 
with open("test.ld") as f:
  input_program = f.read()

# Generamos los tokens del programa
lexer.input(input_program)

input_string = input_program.split('\n')

print("Lexer section")

current_line = 1
print(f"\nLine {current_line}: {input_string[current_line - 1].lstrip()}")
#Agregamos la primera línea a nuestra lista de líneas

lineas.append([])


while True:
  #Obtenemos el token
  tok = lexer.token()
  if not tok:
      break
  
  #Avanzamos de línea mientras el token encontrado sea diferente a la línea actual en la que se encuentra current_line
  while tok.lineno > current_line:
      lineas[current_line-1].append(["EOL", ""])
      current_line += 1
      print(f"\nLine {current_line}: {input_string[current_line - 1].lstrip()}")
      lineas.append([])

  #Agregamos el token válido a la línea actual.
  lineas[current_line-1].append([tok.type, tok.value])
  print(tok.type, " value:", tok.value, " lexpos: ", tok.lexpos)

lineas[current_line-1].append(["EOL", ""])

stack = []

current_line = 0
print("\nParser section")
for linea in lineas:
  print("\n","--line", current_line+1, "--")
  
  #Creamos el stack
  stack = ["$", "ASSIGN"]

  tokens = Tokens(linea)
  errors = []
  if len(linea) > 1:
    print("\n",input_string[current_line])
    print("\n",linea)

    # Revisa si la linea es una expresion valida
    assign(tokens, errors, stack)  
  
    if tokens.pos < len(tokens.tokens)-1:       #   Si no se consumio toda la linea, hubo algun token inesperado
      addError( errors, "operador", tokens.current()[1] , tokens.pos )
  
    #Revisamos si existen más de 3 errores.
    if len(errors) == 0 :
      print("EVERYTHING IS OKAY AND GOOD TO GO")
    else:
      for e in errors:
        print(e)

  current_line += 1
