from itertools import combinations
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

cantidad_casilleros_por_pieza = [
    (['L', 'T', 'O', 'Z'], 4),
    (['I', '-'], 3),
    (['.'], 1),
]

# Función que devuelve las posibles coordenadas de una pieza
def posibles_coordenadas_por_forma(forma, pisos_range, filas_range, columnas_range, filas, columnas):
    posibles_coordenadas = []

    for piso in pisos_range:
        for fila in filas_range:
            for columna in columnas_range:

                if forma == ".":
                    posibles_coordenadas.append((piso, fila, columna))

                elif forma == "L":
                    if columna + 1 < columnas and fila + 1 < filas:
                        posibles_coordenadas.append((piso, fila, columna))

                elif forma == "T":
                    if columna + 2 < columnas and fila + 1 < filas:
                        posibles_coordenadas.append((piso, fila, columna))

                elif forma == "O":
                    if columna + 1 < columnas and fila + 1 < filas:
                        posibles_coordenadas.append((piso, fila, columna))

                elif forma == "I":
                    if fila + 2 < columnas:
                        posibles_coordenadas.append((piso, fila, columna))

                elif forma == "-":
                    if columna + 2 < columnas:
                        posibles_coordenadas.append((piso, fila, columna))

                elif forma == "Z":
                    if columna + 2 < columnas and fila + 1 < filas:
                        posibles_coordenadas.append((piso, fila, columna))

    return posibles_coordenadas



# Función que genera las coordenadas de una pieza
def generar_pieza(forma, coordenada_inicio):
    coordenadas = []

    piso, fila, columna = coordenada_inicio

    coordenadas.append((piso, fila, columna))

    if forma == "L":
        coordenadas.append((piso, fila + 1, columna))
        coordenadas.append((piso, fila + 1, columna + 1))

    elif forma == "T":
        coordenadas.append((piso, fila, columna + 1))
        coordenadas.append((piso, fila, columna + 2))
        coordenadas.append((piso, fila + 1, columna + 1))

    elif forma == "O":
        coordenadas.append((piso, fila, columna + 1))
        coordenadas.append((piso, fila + 1, columna))
        coordenadas.append((piso, fila + 1, columna + 1))

    elif forma == "I":
        coordenadas.append((piso, fila + 1, columna))
        coordenadas.append((piso, fila + 2, columna))

    elif forma == "-":
        coordenadas.append((piso, fila, columna + 1))
        coordenadas.append((piso, fila, columna + 2))

    elif forma == "Z":
        coordenadas.append((piso, fila, columna + 1))
        coordenadas.append((piso, fila + 1, columna + 1))
        coordenadas.append((piso, fila + 1, columna + 2))

    return coordenadas


def calcular_tamaño_pieza(pieza):
    for piezas_agrupadas, cantidad in cantidad_casilleros_por_pieza:
        if pieza in piezas_agrupadas:
            return cantidad


def armar_tablero(filas, columnas, pisos, salida, piezas, pieza_sacar):
    variables = []
    dominio = {}
    restricciones = []

    # Definir los rangos para pisos, filas y columnas
    pisos_range = range(pisos)
    filas_range = range(filas)
    columnas_range = range(columnas)


    # Asignación de variables y dominio: cada pieza tiene un dominio de posibles coordenadas
    for pieza, forma in piezas:
        variables.append(pieza)
        dominio[pieza] = posibles_coordenadas_por_forma(forma, pisos_range, filas_range, columnas_range, filas, columnas)




    # Función que verifica si una pieza está en el mismo piso que la salida
    def pieza_a_sacar_no_en_mismo_piso_que_salida(variables, valores):
        piso_salida, _, _ = salida
        piso_pieza_sacar, _, _ = valores[0]

        return piso_salida != piso_pieza_sacar

    restricciones.append(([pieza_sacar], pieza_a_sacar_no_en_mismo_piso_que_salida))




    # Función que verifica si una pieza está en el mismo casillero que la salida
    def no_en_mismo_casillero_salida(variables, valores):
        _, fila_salida, columna_salida = salida

        for partes_pieza_cualquiera in valores:
            _, fila_parte, columna_parte = partes_pieza_cualquiera

            if fila_parte == fila_salida and columna_parte == columna_salida:
                return False

        return True

    restricciones.append((variables, no_en_mismo_casillero_salida))




    # Función que verifica que todas las piezas estén en pisos distintos
    def todos_pisos_con_piezas(variables, valores):
        pisos_asignados = []

        for partes_pieza in valores:
            primer_parte = partes_pieza
            piso_primer_parte, _, _ = primer_parte

            pisos_asignados.append(piso_primer_parte)

        pisos_asignados = list(set(pisos_asignados))

        return len(pisos_asignados) == pisos

    restricciones.append((variables, todos_pisos_con_piezas))




    # Función que verifica que las piezas no se superpongan
    def no_se_superponen(variables, valores):
        coordenadas_todas_las_piezas = []
        valores_list = list(valores)

        for key, varibale in enumerate(variables):
            for pieza_candidate, forma_candidate in piezas:
                if pieza_candidate == varibale:
                    coordenadas_todas_las_piezas.append(
                        list(map(tuple, generar_pieza(
                            forma_candidate, valores_list[key])))
                    )

        vistos = set()
        duplicados = set()

        for sublist in coordenadas_todas_las_piezas:
            for tupla in sublist:
                if tupla in vistos:
                    duplicados.add(tupla)
                else:
                    vistos.add(tupla)

        return len(duplicados) == 0

    restricciones.append((variables, no_se_superponen))
    
    


    # Función que verifica que ningún piso tiene que tener más del doble de piezas que ningún otro piso
    def no_doble_piezas_que_otro_piso(variables, valores):
        coordenadas_piezas = list(valores)
        cantidad_piezas_en_pisos = [0] * pisos

        for posiciones_piezas in coordenadas_piezas:
            piso_pieza, _, _ = posiciones_piezas

            cantidad_piezas_en_pisos[piso_pieza] += 1

        min_piezas = 0
        if cantidad_piezas_en_pisos:
            min_piezas = min(cantidad_piezas_en_pisos)

        for cantidad_piezas in cantidad_piezas_en_pisos:
            if cantidad_piezas > min_piezas * 2:
                return False

        return True

    restricciones.append((variables, no_doble_piezas_que_otro_piso))




    # La cantidad de casilleros que ocupan las piezas de un piso, no puede ser mayor a dos tercios
    def no_casilleros_ocupando_dos_tercios_del_piso(variables, valores):
        coordenadas_piezas = list(valores)
        cantidad_piezas_en_pisos = [0] * pisos

        for key, pieza_cualquiera in enumerate(variables):
            piso_pieza, _, _ = coordenadas_piezas[key]

            for pieza, forma in piezas:
                if pieza == pieza_cualquiera:
                    cantidad_piezas_en_pisos[piso_pieza] += calcular_tamaño_pieza(
                        forma)

        total_casilleros = filas * columnas
        for cantidad_piezas in cantidad_piezas_en_pisos:
            if cantidad_piezas > total_casilleros * 2 / 3:
                return False

        return True

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



"""

armar_tablero(
    filas=3,
    columnas=4,
    pisos=2,
    salida=(0, 0, 0),
    piezas=[
        ("p0", "T"),
        ("p1", "O"),
        ("p2", "Z"),
        ("p3", "."),
        ("p4", "-"),
    ],
    pieza_sacar="p0",
)


"""
