from simpleai.search import (
    SearchProblem,
    astar,
)
from simpleai.search.viewers import (WebViewer, BaseViewer)

MOVIMIENTOS = ["arriba", "abajo", "izquierda", "derecha", "trepar", "caer"]

def convert_state_to_tuple(estado):
    estado = [tuple(tuple(row) for row in piso) for piso in estado]
    return tuple(estado)

def convert_state_to_list(estado):
    estado = [list(list(fila) for fila in piso) for piso in estado]
    return list(estado)

def encontrar_pieza(estado, id_pieza):
    coordenadas = {}
    for piso, filas in enumerate(estado):
        for fila, columnas in enumerate(filas):
            for columna, pieza in enumerate(columnas):
                if pieza is not None and pieza == id_pieza:
                    pieza_info = coordenadas.get(
                        pieza, {'piso': piso, 'partes': []})
                    pieza_info['partes'].append((fila, columna))
                    coordenadas[pieza] = pieza_info
    return coordenadas

class ProblemaRushHour(SearchProblem):
    def __init__(
        self,
        INITIAL,
        piezas,
        salida,
        pieza_sacar,
        max_filas,
        max_columnas,
    ):
        self.piezas = piezas
        self.salida = salida
        self.pieza_sacar = pieza_sacar
        self.max_filas = max_filas
        self.max_columnas = max_columnas
        super().__init__(INITIAL)

    def is_goal(self, state):
        tableros = convert_state_to_list(state)

        piso_salida, fila_salida, columna_salida = self.salida
        
        # Obtenemos el tablero del piso actual.
        tablero_salida = tableros[piso_salida]

        # Si la pieza objetivo está en la salida, entonces termina el juego.
        return tablero_salida[fila_salida][columna_salida] == self.pieza_sacar

    def actions(self, state):
        acciones_disponibles = []

        for pieza in self.piezas:
            for movimiento in MOVIMIENTOS:
                if self.movimiento_valido(
                    state, 
                    pieza, 
                    movimiento, 
                    self.max_filas, 
                    self.max_columnas,
                    ):
                    acciones_disponibles.append((pieza['id'], movimiento))

        return acciones_disponibles

    def cost(self, state1, action, state2):
        # Costo uniforme para todas las acciones
        return 1

    def result(self, state, accion):
        tableros = convert_state_to_list(state)
        pieza_id, direccion = accion

        pieza_encontrada = encontrar_pieza(tableros, pieza_id)

        self.mover_pieza(
            tableros, 
            pieza_id, 
            pieza_encontrada, 
            direccion,
        )

        return convert_state_to_tuple(tableros)

    def movimiento_valido(
        self, 
        estado, 
        pieza, 
        movimiento, 
        max_filas, 
        max_column,
    ):
        tableros = estado

        pieza_encontrada = encontrar_pieza(tableros, pieza['id'])
        info_pieza = pieza_encontrada[pieza['id']]

        # Obtenemos la posición actual de la pieza y sus partes
        piso_actual = info_pieza['piso']
        partes = info_pieza['partes']

        # Verificamos si el movimiento es válido según las reglas del juego.
        if movimiento == "arriba":
            for fila, columna in partes:
                if fila == 0:
                    return False

                # Obtengo el valor del casillero: ya sea None o una pieza
                valor_obtenido = tableros[piso_actual][fila - 1][columna] 
                if valor_obtenido != pieza['id'] and valor_obtenido is not None:
                    return False
            return True

        elif movimiento == "abajo":
            for fila, columna in partes:

                # Si llegamos a la maxima fila no podemos bajar mas
                # porque nos salimos del tablero
                if fila == max_filas - 1:
                    return False

                # Obtengo el valor del casillero: ya sea None o una pieza
                valor_obtenido = tableros[piso_actual][fila + 1][columna] 
                if valor_obtenido != pieza['id'] and valor_obtenido is not None:
                    return False
            return True

        elif movimiento == "izquierda":
            for fila, columna in partes:
                # Si la columna es 0 no podemos ir mas a la izquierda
                if columna == 0:
                    return False

                # Obtengo el valor del casillero: ya sea None o una pieza
                valor_obtenido = tableros[piso_actual][fila][columna - 1]
                if valor_obtenido != pieza['id'] and valor_obtenido is not None:
                    return False
            return True

        elif movimiento == "derecha":
            for parte in partes:
                fila, columna = parte

                # Si llegamos al maximo de columna no podemos ir mas para la derecha
                if columna == max_column - 1:
                    return False

                # Obtengo el valor del casillero: ya sea None o una pieza
                valor_obtenido = tableros[piso_actual][fila][columna + 1]
                if valor_obtenido != pieza['id'] and valor_obtenido is not None:
                    return False
            return True

        elif movimiento == "trepar":
            # No se puede trepar desde el piso más alto.
            if piso_actual == len(tableros) - 1:
                return False  

            for parte in partes:
                fila, columna = parte

                # No se puede trepar si hay obstáculos en el piso superior.
                if tableros[piso_actual + 1][fila][columna] is not None:
                    return False
            return True

        elif movimiento == "caer":
            # No se puede caer desde el piso más bajo.
            if piso_actual == 0:
                return False  

            for parte in partes:
                fila, columna = parte

                # No se puede caer si hay obstáculos en el piso inferior.
                if tableros[piso_actual - 1][fila][columna] is not None:
                    return False
            return True

    def mover_pieza(
            self, 
            estado, 
            pieza, 
            pieza_encontrada, 
            direccion,
        ):

        piso = pieza_encontrada[pieza]['piso']
        partes = pieza_encontrada[pieza]['partes']

        # Actualizo el valor de la pieza con None en el tablero
        for fila, columna in partes:
            estado[piso][fila][columna] = None

        if direccion == 'arriba':
            partes = [(parte[0] - 1, parte[1]) for parte in partes]

        elif direccion == 'abajo':
            partes = [(parte[0] + 1, parte[1]) for parte in partes]

        elif direccion == 'izquierda':
            partes = [(parte[0], parte[1] - 1) for parte in partes]

        elif direccion == 'derecha':
            partes = [(parte[0], parte[1] + 1) for parte in partes]

        elif direccion == 'trepar':
            partes = [(parte[0], parte[1]) for parte in partes]
            piso += 1

        elif direccion == 'caer':
            partes = [(parte[0], parte[1]) for parte in partes]
            piso -= 1

        # Coloco el id de la pieza en la nueva posicion
        for fila, columna in partes:
            estado[piso][fila][columna] = pieza

    def heuristic(self, estado):
        tableros = convert_state_to_list(estado)

        pieza_encontrada = encontrar_pieza(tableros, self.pieza_sacar)
        piso = pieza_encontrada[self.pieza_sacar]['piso']
        partes = pieza_encontrada[self.pieza_sacar]['partes']

        # Posición de la salida
        piso_salida, fila_salida, columna_salida = self.salida

        dist_horizontal = []

        for fila, columna in partes:
            dist_horizontal.append(abs(fila - fila_salida) + abs(columna - columna_salida))

        dist_vertical = abs(piso - piso_salida)

        # Minima distancia horizontal + delta vertical
        return min(dist_horizontal) + dist_vertical

def initial_state(filas, columnas, pisos, piezas):
    # Crea una matriz con el tamaño de filas, columnas y pisos y llena cada celda con None
    tableros = [[[None for _ in range(columnas)]
                 for _ in range(filas)] for _ in range(pisos)]

    # Llena la matriz con los colores de las piezas en sus posiciones correspondientes
    for pieza in piezas:
        piso = pieza['piso']
        for fila, columna in pieza['partes']:
            # Asigna el color de la pieza a la celda en el piso correspondiente
            tableros[piso][fila][columna] = pieza['id']

    return convert_state_to_tuple(tableros)


def jugar(filas, columnas, pisos, salida, piezas, pieza_sacar):
    INITIAL = initial_state(filas, columnas, pisos, piezas)

    # Instanciar la clase ProblemaRushHour
    my_problem = ProblemaRushHour(
        INITIAL,
        piezas,
        salida,
        pieza_sacar,
        max_filas=filas,
        max_columnas=columnas,
    )

    # Llamar a Astar
    result = astar(my_problem)

    if result is None:
        print("No solution")
        return []
    else:
        # Imprimir la solución
        result_list = []
        for action, state in result.path():
            if action is not None:
                result_list.append(action)
        print(result_list)
        return result_list

if __name__ == "__main__":
    jugar()


""" 
# Formato ultimo test

jugar(
    filas=3,
    columnas=4,
    pisos=3,
    piezas=[
        {"id": "A", "piso": 2, "partes": [(1, 0), (2, 0), (2, 1)]},
        {"id": "E", "piso": 2, "partes": [(0, 3), (1, 2), (1, 3), (2, 2)]},
        {"id": "C", "piso": 1, "partes": [(0, 1), (1, 1), (2, 1)]},
        {"id": "D", "piso": 1, "partes": [(2, 2), (2, 3)]},
        {"id": "B", "piso": 0, "partes": [(0, 0), (0, 1), (1, 0), (1, 1)]},
        {"id": "F", "piso": 0, "partes": [(0, 2), (0, 3)]},
    ],
    salida=(0, 0, 0),  # piso 0, fila 3, columna 1
    pieza_sacar="A"
) 
 """
