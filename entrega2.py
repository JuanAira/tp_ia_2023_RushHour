from itertools import combinations
from simpleai.search import CspProblem, backtrack

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


def armar_tablero(filas, columnas, pisos, salida, piezas, pieza_sacar):
    variables = []
    dominio = {}
    restricciones = []

    # Definir los rangos para pisos, filas y columnas
    pisos_range = range(pisos)
    filas_range = range(filas)
    columnas_range = range(columnas)

    def posibles_coordenadas_por_forma(forma):
        posibles_coordenadas = []

        for piso in pisos_range:
            for fila in filas_range:
                for columna in columnas_range:

                    if forma == ".":
                        posibles_coordenadas.append(list((
                            (piso, fila, columna),
                        )))

                    elif forma == "L":
                        if columna + 1 < columnas and fila + 1 < filas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila + 1, columna),
                                (piso, fila + 1, columna + 1),
                            )))

                    elif forma == "T":
                        if columna + 2 < columnas and fila + 1 < filas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila, columna + 1),
                                (piso, fila, columna + 2),
                                (piso, fila + 1, columna + 1),
                            )))

                    elif forma == "O":
                        if columna + 1 < columnas and fila + 1 < filas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila, columna + 1),
                                (piso, fila + 1, columna),
                                (piso, fila + 1, columna + 1),
                            )))

                    elif forma == "I":
                        if fila + 3 < columnas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila + 1, columna),
                                (piso, fila + 2, columna),
                                (piso, fila + 3, columna),
                            )))

                    elif forma == "-":
                        if columna + 2 < columnas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila, columna + 1),
                                (piso, fila, columna + 2),
                            )))

                    elif forma == "Z":
                        if columna + 2 < columnas and fila + 1 < filas:
                            posibles_coordenadas.append(list((
                                (piso, fila, columna),
                                (piso, fila, columna + 1),
                                (piso, fila + 1, columna + 1),
                                (piso, fila + 1, columna + 2),
                            )))

        return posibles_coordenadas

    # Asignación de variables y dominio: cada pieza tiene un dominio de posibles coordenadas
    for pieza, forma in piezas:
        variables.append(pieza)
        dominio[pieza] = posibles_coordenadas_por_forma(forma)

    # Función que verifica si una pieza está en el mismo piso que la salida
    def no_en_mismo_piso(variables, valores):
        variable_a_sacar = variables[0]
        pieza_cualquiera = valores[0]
        piso_salida, _, _ = salida

        if variable_a_sacar == pieza_sacar:
            for pieza in pieza_cualquiera:
                piso_p, _, _ = pieza
                if piso_p == piso_salida:
                    return False

        return True

    for pieza in combinations(variables, 1):
        restricciones.append(
            ((pieza), no_en_mismo_piso)
        )

    # Función que verifica si una pieza está en el mismo casillero que la salida
    def no_en_mismo_casillero(variables, valores):
        partes_pieza_cualquiera = valores[0]
        _, fila_salida, columna_salida = salida

        for parte in partes_pieza_cualquiera:
            _, fila_parte, columna_parte = parte

            if fila_parte == fila_salida and columna_parte == columna_salida:
                return False

        return True

    for pieza in combinations(variables, 1):
        restricciones.append(
            ((pieza), no_en_mismo_casillero)
        )

    # Función que verifica que todas las piezas estén en pisos distintos
    def todos_pisos_con_piezas(variables, valores):
        pisos_asignados = []

        for partes_pieza in valores:
            primer_parte = partes_pieza[0]
            piso_primer_parte, _, _ = primer_parte

            pisos_asignados.append(piso_primer_parte)

        pisos_asignados = list(set(pisos_asignados))

        return len(pisos_asignados) == pisos

    restricciones.append((tuple(variables), todos_pisos_con_piezas))

    # Función que verifica que las piezas no se superpongan
    def no_se_superponen(variables, valores):
        coordenadas_piezas = list(valores)
        valores_vistos = set()

        for sublista in coordenadas_piezas:
            for valor in sublista:
                if valor in valores_vistos:
                    return False
                valores_vistos.add(valor)

        return True

    restricciones.append((tuple(variables), no_se_superponen))

    # Función que verifica que ningún piso tiene que tener más del doble de piezas que ningún otro piso
    def no_doble_piezas_que_otro_piso(variables, valores):
        coordenadas_piezas = list(valores)
        cantidad_piezas_en_pisos = [0] * pisos

        for posiciones_piezas in coordenadas_piezas:
            piso_pieza, _, _ = posiciones_piezas[0]

            cantidad_piezas_en_pisos[piso_pieza] += 1

        min_piezas = min(cantidad_piezas_en_pisos)

        for cantidad_piezas in cantidad_piezas_en_pisos:
            if cantidad_piezas > min_piezas * 2:
                return False

        return True

    restricciones.append((tuple(variables), no_doble_piezas_que_otro_piso))

    # La cantidad de casilleros que ocupan las piezas de un piso, no puede ser mayor a dos tercios
    def no_casilleros_ocupando_dos_tercios_del_piso(variables, valores):
        coordenadas_piezas = list(valores)
        cantidad_piezas_en_pisos = [0] * pisos

        for posiciones_piezas in coordenadas_piezas:
            piso_pieza, _, _ = posiciones_piezas[0]

            cantidad_piezas_en_pisos[piso_pieza] += len(posiciones_piezas)

        total_casilleros = filas * columnas
        for cantidad_piezas in cantidad_piezas_en_pisos:
            if cantidad_piezas > total_casilleros * 2 / 3:
                return False

        return True

    restricciones.append(
        (tuple(variables),
         no_casilleros_ocupando_dos_tercios_del_piso))

    # Crea el problema CSP
    problem = CspProblem(variables, dominio, restricciones)

    # Resuelve el problema utilizando el algoritmo de backtrack
    result = backtrack(problem)

    if result is not None:
        print("Solución encontrada:")
        for variable in result:
            print(variable, ":", result[variable])
    else:
        print("No se encontró solución que cumpla con las restricciones.")


if __name__ == "__main__":
    armar_tablero()

""" 
# Pruebas de la función armar_tablero

armar_tablero(
    filas=5,
    columnas=5,
    pisos=3,
    salida=(0, 0, 0),
    piezas=[
        ("pieza_verde", "L"),
        ("pieza_roja", "O"),
        ("pieza_azul", "T"),
        ("pieza_morada", "Z"),
        ("pieza_amarilla", "."),
        ("pieza_naranja", "I"),
    ],
    pieza_sacar="pieza_roja",
)

"""
