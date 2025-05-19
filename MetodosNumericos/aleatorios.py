import random

def generar_valor_discreto():
    # Tabla de probabilidades
    valores = [1, 2, 3, 4]
    probabilidades = [0.3, 0.2, 0.1, 0.4]

    # Cálculo de la función de distribución acumulada (CDF)
    cdf = []
    acumulado = 0
    for p in probabilidades:
        acumulado += p
        cdf.append(acumulado)

    # Generar número aleatorio U entre 0 y 1
    u = random.random()

    # Encontrar el valor correspondiente
    for i in range(len(cdf)):
        if u < cdf[i]:
            return valores[i]

#generar 100 valores
for _ in range(100):
    print(generar_valor_discreto(),", ", end="")