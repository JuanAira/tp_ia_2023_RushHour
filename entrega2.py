from itertools import combinations

from simpleai.search import (
    CspProblem,
    backtrack,
    min_conflicts,
   
)
from simpleai.search.csp import _find_conflicts

def armar_tablero(filas, columnas, pisos, salida, piezas, pieza_sacar):
    
    # Lista de piezas
    """ 
    piezas =[
    ("pieza_verde", "L"),
    ("pieza_roja", "O"),
    ("pieza_azul", "T"),
    ("pieza_amarilla", "T"),
    ] """
    
    variables= (piezas,pieza_sacar)
                    
    # Crear un diccionario para almacenar los dominios de las piezas
    dominios_piezas = {}

    # Definir los rangos para pisos, filas y columnas
    pisos_range = range(pisos)  # 0 a 3
    filas_range = range(filas)  # 0 a 5
    columnas_range = range(columnas)  # 0 a 5

    # Llenar el dominio para cada pieza
    for pieza, forma in piezas:
        dominio_pieza = [(piso, fila, columna) for piso in pisos_range for fila in filas_range for columna in columnas_range]
        dominios_piezas[pieza] = dominio_pieza

    # Imprimir los dominios en el formato deseado
    for pieza, dominio in dominios_piezas.items():
        print(f"Dominio de {pieza}: {dominio}")
    
    restricciones = []
    
    

if __name__ == "__main__":
    armar_tablero()

""" 
# Formato llamada tablero

posiciones_piezas = armar_tablero(
    filas=5,
    columnas=5,
    pisos=3,
    salida=(0, 3, 1),  # piso 0, fila 3, columna 1 
    piezas=[
        # una lista de piezas presentes en el tablero, cada una con un id 
        # y una forma (expresada como un caracter, debajo se explican las formas
        # disponibles)
        ("pieza_verde", "L"),
        ("pieza_roja", "O"),
        ("pieza_azul", "T"),
        ("pieza_amarilla", "T"),
        ... 
    ],
    pieza_sacar="pieza_roja",
)
 """
