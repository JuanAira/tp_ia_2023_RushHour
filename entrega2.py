from itertools import combinations
from random import shuffle
from simpleai.search import (
    CspProblem,
    backtrack,
    min_conflicts,
    MOST_CONSTRAINED_VARIABLE,
    LEAST_CONSTRAINING_VALUE,
)

""" 
Las piezas claramente no deben estar superpuestas entre si. ✅

No debe haber ninguna pieza en el casillero de salida. ✅

La pieza a sacar no tiene que estar en el mismo piso que el casillero de salida. ✅

Todos los pisos tienen que tener piezas. ✅

Ningún piso tiene que tener más del doble de piezas que ningún otro piso (por ejemplo, si un piso tiene 2 piezas, 
otro piso puede tener 4 piezas, pero ya no puede tener 8 piezas). ✅

La cantidad de casilleros que ocupan las piezas de un piso, no puede ser mayor a dos tercios 
de los casilleros de ese piso (por ejemplo, en un piso de 3x4, es decir, 12 casilleros, la suma de los casilleros 
ocupados con piezas en ese piso puede ser de hasta 8 casilleros, pero ya no 9 casilleros). ✅
"""

CANTIDAD_CASILLEROS_POR_PIEZA = {
  "L": 4,
  "T": 4,
  "O": 4,
  "Z": 4,
  "-": 3,
  "I": 3,
  ".": 1
}


# Función que devuelve las posibles coordenadas de una pieza
def posibles_coordenadas_por_forma(forma, pisos_range, filas_range, columnas_range, filas, columnas):
    posibles_coordenadas = []

    forma_condiciones = {
        ".": lambda fila, columna: True,
        "L": lambda fila, columna: columna + 1 < columnas and fila + 1 < filas,
        "T": lambda fila, columna: columna + 2 < columnas and fila + 1 < filas,
        "O": lambda fila, columna: columna + 1 < columnas and fila + 1 < filas,
        "I": lambda fila, columna: fila + 2 < filas,
        "-": lambda fila, columna: columna + 2 < columnas,
        "Z": lambda fila, columna: columna + 2 < columnas and fila + 1 < filas,
    }

    for piso in pisos_range:
        for fila in filas_range:
            for columna in columnas_range:
                if forma_condiciones.get(forma, lambda x, y: False)(fila, columna):
                    posibles_coordenadas.append((piso, fila, columna))

    return posibles_coordenadas



# Función que genera las coordenadas de una pieza
def generar_pieza(forma, coordenada_inicio):
    coordenadas = [coordenada_inicio]
    piso, fila, columna = coordenada_inicio

    if forma == "L":
        coordenadas.extend([(piso, fila + 1, columna), (piso, fila + 1, columna + 1)])
    elif forma == "T":
        coordenadas.extend([(piso, fila, columna + 1), (piso, fila, columna + 2), (piso, fila + 1, columna + 1)])
    elif forma == "O":
        coordenadas.extend([(piso, fila, columna + 1), (piso, fila + 1, columna), (piso, fila + 1, columna + 1)])
    elif forma == "I":
        coordenadas.extend([(piso, fila + 1, columna), (piso, fila + 2, columna)])
    elif forma == "-":
        coordenadas.extend([(piso, fila, columna + 1), (piso, fila, columna + 2)])
    elif forma == "Z":
        coordenadas.extend([(piso, fila, columna + 1), (piso, fila + 1, columna + 1), (piso, fila + 1, columna + 2)])

    return coordenadas



def calcular_tamaño_pieza(pieza):
    return CANTIDAD_CASILLEROS_POR_PIEZA.get(pieza, 0)



def armar_tablero(filas, columnas, pisos, salida, piezas, pieza_sacar):
    variables = []
    dominio = {}
    restricciones = []

    # Definir los rangos para pisos, filas y columnas
    pisos_range = range(pisos)
    filas_range = range(filas)
    columnas_range = range(columnas)


    # Asignación de variables 
    variables = [pieza for pieza, forma in piezas]


    # Asignación de dominio
    dominio = {pieza: posibles_coordenadas_por_forma(forma, pisos_range, filas_range, columnas_range, filas, columnas) for pieza, forma in piezas}

    # Random dominio
    for dom in dominio.values():
        shuffle(dom)


    # Función que verifica si una pieza está en el mismo piso que la salida
    def pieza_a_sacar_no_en_mismo_piso_que_salida(variables, valores):
        piso_salida, _, _ = salida
        piso_pieza_sacar, _, _ = list(valores).pop()

        return piso_salida != piso_pieza_sacar

    restricciones.append(([pieza_sacar], pieza_a_sacar_no_en_mismo_piso_que_salida))




    # Función que verifica si una pieza está en el mismo casillero que la salida
    def no_en_mismo_casillero_salida(variables, valores):
        _, fila_salida, columna_salida = salida

        return all((fila_pieza != fila_salida) or (columna_pieza != columna_salida) for _, fila_pieza, columna_pieza in valores)

    restricciones.append((variables, no_en_mismo_casillero_salida))




    # Función que verifica que todas las piezas estén en pisos distintos
    def todos_pisos_con_piezas(variables, valores):
        pisos_asignados = {piso for piso, _, _ in valores}

        return len(pisos_asignados) == pisos

    restricciones.append((variables, todos_pisos_con_piezas))




    # Función que verifica que las piezas no se superpongan
    def no_se_superponen(variables, valores):
        variable_1, variable_2 = variables

        pieza1, pieza2 = valores
        piso_pieza1, _, _ = pieza1
        piso_pieza2, _, _ = pieza2

        coordenadas_todas_las_piezas = []

        if piso_pieza1 != piso_pieza2:
            return True
        else:
            for pieza, forma in piezas:
                if pieza == variable_1 :
                    coordenadas_todas_las_piezas.extend(generar_pieza(forma, pieza1))
                
                if pieza == variable_2 :
                    coordenadas_todas_las_piezas.extend(generar_pieza(forma, pieza2))

            return len(coordenadas_todas_las_piezas) == len(set(coordenadas_todas_las_piezas))

    for pieza1, pieza2 in combinations(variables, 2):
        restricciones.append(((pieza1,pieza2), no_se_superponen))



    # Función que verifica que ningún piso tiene que tener más del doble de piezas que ningún otro piso
    def no_doble_piezas_que_otro_piso(variables, valores):
        pisos_piezas = [piso for piso, _, _ in valores]
        cantidad_piezas_en_pisos = [0] * pisos

        for piso_pieza in pisos_piezas:
            cantidad_piezas_en_pisos[piso_pieza] += 1

        min_piezas = min(cantidad_piezas_en_pisos)
        if any(cantidad_piezas > min_piezas * 2 for cantidad_piezas in cantidad_piezas_en_pisos):
            return False

        return True

    restricciones.append((variables, no_doble_piezas_que_otro_piso))




    # La cantidad de casilleros que ocupan las piezas de un piso, no puede ser mayor a dos tercios
    def no_casilleros_ocupando_dos_tercios_del_piso(variables, valores):
        valores_en_lista = list(valores)
        
        cantidad_piezas_en_pisos = [0] * pisos

        for key, pieza_cualquiera in enumerate(variables):
            piso_pieza, _ , _ = valores_en_lista[key]

            for pieza, forma in piezas:
                if pieza == pieza_cualquiera:
                    cantidad_piezas_en_pisos[piso_pieza] += calcular_tamaño_pieza(forma)

        total_casilleros = filas * columnas
        return all(cantidad_piezas <= total_casilleros * 2 / 3 for cantidad_piezas in cantidad_piezas_en_pisos)


    restricciones.append((variables, no_casilleros_ocupando_dos_tercios_del_piso))




    # Crea el problema CSP
    problem = CspProblem(variables, dominio, restricciones)

    # Resuelve el problema utilizando el algoritmo de backtrack
    # result = backtrack(problem, variable_heuristic=MOST_CONSTRAINED_VARIABLE, value_heuristic=LEAST_CONSTRAINING_VALUE)

    result = min_conflicts(problem)

    if result is not None:
        print("Solución encontrada:")
        print(result)

        return result
    else:
        print("No se encontró solución que cumpla con las restricciones.")

        return None



if __name__ == "__main__":
    armar_tablero() 
