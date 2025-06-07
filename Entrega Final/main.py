# -*- coding: utf-8 -*-
from syntax_n_semantics import program_is_ok
import re
# clase para poder guardar la dirección de una función (poder copiarla)
class Func:
  def __init__(self, memov, type):
    self.memov = {}
    self.return_quad = None
    self.start_quad = None
    for key in memov:
      #Si es main hacemos una copia como tal nueva
      if type == "main":
        self.memov[key] = memov[key]
      #Si es una función, entonces sólo copiamos las constantes globales
      elif int(key) >= 17000:
        self.memov[key] = memov[key]
      

if program_is_ok:

  print("Executing code... \n")

  input_program = "output.txt"

  with open(input_program) as f:
      input_program = f.read()

  #print(input_program)

  # info sobre los indices de cada region para simular la memoria
  regions = { "global_int"	  :	[1000]	,
        "global_float"	  :	[2000]	,
        "global_str"	  :	[3000]	,
        "global_void"	  :	[4000]	,
        "local_int"	  :	[7000]	,
        "local_float" :	[8000]	,
        "local_str"	  :	[9000]	,
        "temp_int"	  :	[12000]	,
        "temp_float"  :	[13000]	,
        "temp_bool"	  :	[14000]	,
        "cte_int"	  :	[17000]	,
        "cte_float"	  :	[18000]	,
        "cte_str"	  :	[19000]	 }

  memov = {}

  class Quad:
    op = -1
    arg1 = -1
    arg2 = -1
    destino = -1

    def __init__(self, lista):
      self.op = lista[0]
      self.arg1 = lista[1]
      self.arg2 = lista[2]
      self.destino = lista[3]

  seccion = 0
  lineas = input_program.split('\n')
  lista_quads = {}

  for i in lineas:
    linea  = re.findall(r'"[^"]*"|\S+', i)
    longitud = len(linea)

    # print(linea, len(linea))

    if (longitud == 0):
      seccion = seccion + 1
    elif (seccion == 0 and longitud == 2):
      if linea[1] >= "17000" and linea[1] <= "17999":
        memov[linea[1]] = int(linea[0]) # Guarda las constantes y su dir
      elif(linea[1] >= "18000" and linea[1] <= "18999"):
        memov[linea[1]] = float(linea[0])
      elif linea[1] >= "19000":
        memov[linea[1]] = linea[0].strip('"') # Quita los valores de " del principio y final del string
    #Es una función que hay que agregar a la memoria
    elif (seccion > 1 and longitud ==1):
      memov[linea[0]] = {}
    elif (longitud == 5):
      quadTemp = Quad(linea[1:])
      lista_quads[int(linea[0])] = quadTemp

  call_stack = []

  new_main = Func(memov, "main")

  call_stack.append(new_main)

  param_buffer = [] #guardamos los valores que le queremos meter a la función

  #En el call stack, el primer valor siempre es el main
  cur_fun = call_stack[-1]

  n_quads = len(lista_quads)
  current = 1
  newFun = None

  print('\n\nEmpieza analisis')
  while (current <= n_quads):
    current_quad = lista_quads[current]
    #Error de call_stack, se nos acabó la memoria virtual
    if (len(call_stack) > 1000):
      print("Runtime Error: Too many function calls! exceeded 1000 calls")
      break
    if (current_quad.op == 'gotomain'):
      current = int(current_quad.destino)
    #vamos a crear una nueva función
    elif(current_quad.op == 'sub'):
      #generamos una subfunción nueva
      newFun = Func(cur_fun.memov, "fun")
      current += 1
      #Para cada parámetro, guardamos el valor que metimos
    elif(current_quad.op == 'param'):
      param_buffer.append(cur_fun.memov[current_quad.arg1])
      current+=1
      #Sabiendo que los parámetros siempre son locales, generamos las direcciones iniciales de nuestra memoria de función
    elif(current_quad.op == 'gosub'):
      newFun.return_quad = current+1
      newFun.start_quad = int(current_quad.destino)
      start_int = 7000
      start_float = 8000
      start_string = 9000
      for x in param_buffer:
        if isinstance(x, int):
          newFun.memov[str(start_int)] = x
          start_int+=1
        elif isinstance(x, float):
          newFun.memov[str(start_float)] = x
          start_float+=1
        elif isinstance(x, str):
          newFun.memov[str(start_string)] = x
          start_string+=1
      call_stack.append(newFun)
      param_buffer = []
      cur_fun = call_stack[-1]
      current = cur_fun.start_quad
      #Al terminar con una función, regresamos a donde estábamos
    elif(current_quad.op == 'endfun'):
      current = cur_fun.return_quad
      call_stack.pop()
      cur_fun = call_stack[-1]
    elif (current_quad.op == 'gotof'):
      if cur_fun.memov[current_quad.arg1]:
        current += 1
      else:
        current = int(current_quad.destino)
    elif (current_quad.op == 'goto'):
      current = int(current_quad.destino)
    elif (current_quad.op == 'gotoV'):
      if cur_fun.memov[current_quad.arg1]:
        current = int(current_quad.destino)
      else:
        current += 1
    elif (current_quad.op == '='):
      #Checamos para ver si truncamos si hay una asignación a un int local o global
      if ( int(current_quad.destino) >= 1000 and int(current_quad.destino) < 2000) or (int(current_quad.destino) >=7000 and int(current_quad.destino) < 8000):
        cur_fun.memov[current_quad.destino] = int(cur_fun.memov[current_quad.arg1])
      elif (int(current_quad.destino) >= 8000 and int(current_quad.destino) < 9000) or (int(current_quad.destino) >=2000 and int(current_quad.destino) < 3000):
        cur_fun.memov[current_quad.destino] = float(cur_fun.memov[current_quad.arg1])
      else:
        cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1]
      current += 1
    elif (current_quad.op == '+'):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] + cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '-'):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] - cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == 'uminus'):
      cur_fun.memov[current_quad.destino] = - cur_fun.memov[current_quad.arg1]
      current+=1
    elif (current_quad.op == '/'):
      if cur_fun.memov[current_quad.arg2] != 0:
        cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] / cur_fun.memov[current_quad.arg2]
      else:
        print(f"Runtime Error: Trying to divide by 0 at quad #{current}, ending analysis")
        break
      current += 1
    elif (current_quad.op == '*'):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] * cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '>='):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] >= cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '>'):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] > cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '<='):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] <= cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '<'):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] < cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '!='):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] != cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == '=='):
      cur_fun.memov[current_quad.destino] = cur_fun.memov[current_quad.arg1] == cur_fun.memov[current_quad.arg2]
      current += 1
    elif (current_quad.op == 'print'):
      if (current_quad.arg1 == '"\\n"'):
        print('\n', end = "")
      else:
        print(cur_fun.memov[current_quad.arg1], end="")
      current += 1
    else:
      current += 1

else:
  print("Errors found within the code, exiting...")