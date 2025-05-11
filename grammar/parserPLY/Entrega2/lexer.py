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

def t_comment(t):
    r'@\s?.*'
    pass

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

#lineas = []

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

#lineas.append([])


while True:
  #Obtenemos el token
  tok = lexer.token()
  if not tok:
      break
  
  #Avanzamos de línea mientras el token encontrado sea diferente a la línea actual en la que se encuentra current_line
  while tok.lineno > current_line:
      #lineas[current_line-1].append(["EOL", ""])
      current_line += 1
      print(f"\nLine {current_line}: {input_string[current_line - 1].lstrip()}")
      #lineas.append([])

  #Agregamos el token válido a la línea actual.
  #lineas[current_line-1].append([tok.type, tok.value])
  print(tok.type, " value:", tok.value, " lexpos: ", tok.lexpos)

#lineas[current_line-1].append(["EOL", ""])

print("\n--------Symbol table--------")
for simbolo in identifier_list:
    print("\nsymbol: ", simbolo, " found in:")
    for x in range(len(identifier_list[simbolo]['lines_found'])):
        print("line ", identifier_list[simbolo]['lines_found'][x], "lexpos ",
              identifier_list[simbolo]['lexpos'][x])
