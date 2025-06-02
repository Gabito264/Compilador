from main import program_is_ok
import re

if program_is_ok:

  print("Executing code... \n")

  input_program = "output.txt"

  with open(input_program) as f:
      input_program = f.read()

  regions = {
      "global_int": [1000],
      "global_float": [2000],
      "global_str": [3000],
      "global_void": [4000],
      "local_int": [7000],
      "local_float": [8000],
      "local_str": [9000],
      "temp_int": [12000],
      "temp_float": [13000],
      "temp_bool": [14000],
      "cte_int": [17000],
      "cte_float": [18000],
      "cte_str": [19000]
  }

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
      linea = re.findall(r'"[^"]*"|\S+', i)
      longitud = len(linea)

      if longitud == 0:
          seccion += 1
      elif seccion == 0 and longitud == 2:
          if linea[1] >= "17000" and linea[1] <= "18999":
              memov[linea[1]] = float(linea[0])
          elif linea[1] >= "19000":
              memov[linea[1]] = linea[0].strip('"')
      elif seccion == 2:
          quadTemp = Quad(linea[1:])
          lista_quads[int(linea[0])] = quadTemp

  for key in lista_quads:
      q = lista_quads[key]
      print(key, q.op, q.arg1, q.arg2, q.destino)

  n_quads = len(lista_quads)
  current = 1

  print('\n\nEmpieza analisis')

  call_stack = []
  pending_frame = None
  param_counter = 0

  while current <= n_quads:
      current_quad = lista_quads[current]

      if current_quad.op == 'gotomain':
          current = int(current_quad.destino)
      elif current_quad.op == 'gotof':
          if memov[current_quad.arg1]:
              current += 1
          else:
              current = int(current_quad.destino)
      elif current_quad.op == 'goto':
          current = int(current_quad.destino)
      elif current_quad.op == 'gotoV':
          if memov[current_quad.arg1]:
              current = int(current_quad.destino)
          else:
              current += 1
      elif current_quad.op == 'sub':
          pending_frame = {
              'mem': {},
              'return_ip': None
          }
          param_counter = 0
          current += 1
      elif current_quad.op == 'param':
          pending_frame['mem'][f'arg{param_counter}'] = memov[current_quad.arg1]
          param_counter += 1
          current += 1
      elif current_quad.op == 'gosub':
          pending_frame['return_ip'] = current + 1
          call_stack.append((pending_frame['mem'].copy(), pending_frame['return_ip']))
          pending_frame = None
          current = int(current_quad.destino)
      elif current_quad.op == 'endfun':
          frame, return_ip = call_stack.pop()
          current = return_ip
      elif current_quad.op == '=':
          memov[current_quad.destino] = memov[current_quad.arg1]
          current += 1
      elif current_quad.op == '+':
          memov[current_quad.destino] = memov[current_quad.arg1] + memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '-':
          memov[current_quad.destino] = memov[current_quad.arg1] - memov[current_quad.arg2]
          current += 1
      elif current_quad.op == 'uminus':
          memov[current_quad.destino] = -memov[current_quad.arg1]
          current += 1
      elif current_quad.op == '/':
          memov[current_quad.destino] = memov[current_quad.arg1] / memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '*':
          memov[current_quad.destino] = memov[current_quad.arg1] * memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '>=':
          memov[current_quad.destino] = memov[current_quad.arg1] >= memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '>':
          memov[current_quad.destino] = memov[current_quad.arg1] > memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '<=':
          memov[current_quad.destino] = memov[current_quad.arg1] <= memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '<':
          memov[current_quad.destino] = memov[current_quad.arg1] < memov[current_quad.arg2]
          current += 1
      elif current_quad.op == '!=':
          memov[current_quad.destino] = memov[current_quad.arg1] != memov[current_quad.arg2]
          current += 1
      elif current_quad.op == 'print':
          if current_quad.arg1 == '"\\n"':
              print('\n', end="")
          else:
              print(memov[current_quad.arg1], end="")
          current += 1
      else:
          current += 1

  print("\n\nMemoria final:")
  for i in memov:
      print(i, memov[i])

else:
    print("Errors found within the code, exiting...")
