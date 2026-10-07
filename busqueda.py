"""Algoritmos de busqueda de caminos: logica pura, sin pygame.

El modulo no sabe de mapas ni de sprites: solo de una "rejilla" que exponga

    rejilla.filas, rejilla.columnas
    rejilla.bloqueada(fila, col) -> bool
    rejilla.costo_en(fila, col) -> float   (coste de ENTRAR en la celda)

El movimiento es cardinal (4 vecinos), igual que el del jugador. Cada funcion
devuelve un ResultadoBusqueda con el camino (incluyendo inicio y meta), el orden
en que se expandieron las celdas, el coste total y el algoritmo usado.
"""

from collections import deque
from itertools import count

import heapq

# Arriba, abajo, izquierda, derecha
DIRECCIONES = ((-1, 0), (1, 0), (0, -1), (0, 1))

# Algoritmos que ofrece el juego (el "ninguno" no es una busqueda, es linea recta)
ALGORITMOS = ("astar", "bfs", "dfs", "greedy")

NOMBRES_ALGORITMO = {
    "astar": "A*",
    "bfs": "BFS",
    "dfs": "DFS",
    "greedy": "GREEDY",
}

# Coste minimo posible de una celda transitable; sirve de heuristica admisible
COSTO_MINIMO = 1.0


class ResultadoBusqueda:
    """Camino encontrado, celdas expandidas y coste, con el algoritmo usado."""

    __slots__ = ("camino", "visitados", "costo", "algoritmo")

    def __init__(self, camino, visitados, costo, algoritmo):
        self.camino = camino
        self.visitados = visitados
        self.costo = costo
        self.algoritmo = algoritmo

    @property
    def encontrado(self):
        return bool(self.camino)

    def __repr__(self):
        return (
            f"ResultadoBusqueda({self.algoritmo!r}, camino={len(self.camino)}, "
            f"visitados={len(self.visitados)}, costo={self.costo:.2f})"
        )


def _valida(rejilla, fila, col):
    return (
        0 <= fila < rejilla.filas
        and 0 <= col < rejilla.columnas
        and not rejilla.bloqueada(fila, col)
    )


def _vecinos(rejilla, fila, col):
    for delta_fila, delta_col in DIRECCIONES:
        nueva_fila = fila + delta_fila
        nueva_col = col + delta_col
        if _valida(rejilla, nueva_fila, nueva_col):
            yield nueva_fila, nueva_col


def _reconstruir(padres, inicio, meta):
    """Camino desde `inicio` hasta `meta` siguiendo los padres, o []."""
    if meta not in padres:
        return []
    camino = [meta]
    actual = meta
    while actual != inicio:
        actual = padres.get(actual)
        if actual is None:
            return []
        camino.append(actual)
    camino.reverse()
    return camino


def _coste(rejilla, camino):
    return float(sum(rejilla.costo_en(fila, col) for fila, col in camino[1:]))


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _resultado(rejilla, padres, inicio, meta, visitados, algoritmo):
    camino = _reconstruir(padres, inicio, meta)
    return ResultadoBusqueda(camino, visitados, _coste(rejilla, camino), algoritmo)


def _vacio(algoritmo):
    return ResultadoBusqueda([], [], 0.0, algoritmo)


# --------------------------------------------------------------------- BFS

def buscar_bfs(rejilla, inicio, meta):
    """Anchura primero: minimiza el numero de pasos, ignora el coste."""
    if not _valida(rejilla, *inicio) or not _valida(rejilla, *meta):
        return _vacio("bfs")

    padres = {inicio: None}
    visitados = []
    frontera = deque([inicio])

    while frontera:
        actual = frontera.popleft()
        visitados.append(actual)
        if actual == meta:
            break
        for vecino in _vecinos(rejilla, *actual):
            if vecino not in padres:
                padres[vecino] = actual
                frontera.append(vecino)

    return _resultado(rejilla, padres, inicio, meta, visitados, "bfs")


# --------------------------------------------------------------------- DFS

def buscar_dfs(rejilla, inicio, meta):
    """Profundidad primero: rapido, pero da caminos largos y sinuosos."""
    if not _valida(rejilla, *inicio) or not _valida(rejilla, *meta):
        return _vacio("dfs")

    padres = {inicio: None}
    visitados = []
    expandidos = set()
    frontera = [inicio]

    while frontera:
        actual = frontera.pop()
        if actual in expandidos:
            continue
        expandidos.add(actual)
        visitados.append(actual)
        if actual == meta:
            break
        for vecino in _vecinos(rejilla, *actual):
            if vecino not in padres:
                padres[vecino] = actual
                frontera.append(vecino)

    return _resultado(rejilla, padres, inicio, meta, visitados, "dfs")


# ----------------------------------------------------------------- Dijkstra

def buscar_dijkstra(rejilla, inicio, meta):
    """Coste uniforme: camino de coste minimo aunque el terreno pese distinto."""
    if not _valida(rejilla, *inicio) or not _valida(rejilla, *meta):
        return _vacio("dijkstra")

    desempate = count()
    padres = {inicio: None}
    costos = {inicio: 0.0}
    visitados = []
    expandidos = set()
    frontera = [(0.0, next(desempate), inicio)]

    while frontera:
        costo, _, actual = heapq.heappop(frontera)
        if actual in expandidos:
            continue
        expandidos.add(actual)
        visitados.append(actual)
        if actual == meta:
            break
        for vecino in _vecinos(rejilla, *actual):
            nuevo = costo + rejilla.costo_en(*vecino)
            if vecino not in costos or nuevo < costos[vecino]:
                costos[vecino] = nuevo
                padres[vecino] = actual
                heapq.heappush(frontera, (nuevo, next(desempate), vecino))

    return _resultado(rejilla, padres, inicio, meta, visitados, "dijkstra")


# --------------------------------------------------------------------- A*

def buscar_astar(rejilla, inicio, meta):
    """A*: coste real acumulado + heuristica de Manhattan."""
    if not _valida(rejilla, *inicio) or not _valida(rejilla, *meta):
        return _vacio("astar")

    desempate = count()
    padres = {inicio: None}
    costos = {inicio: 0.0}
    visitados = []
    expandidos = set()
    frontera = [
        (_manhattan(inicio, meta) * COSTO_MINIMO, 0.0, next(desempate), inicio)
    ]

    while frontera:
        _, costo, _, actual = heapq.heappop(frontera)
        if actual in expandidos:
            continue
        expandidos.add(actual)
        visitados.append(actual)
        if actual == meta:
            break
        for vecino in _vecinos(rejilla, *actual):
            nuevo = costo + rejilla.costo_en(*vecino)
            if vecino not in costos or nuevo < costos[vecino]:
                costos[vecino] = nuevo
                padres[vecino] = actual
                prioridad = nuevo + _manhattan(vecino, meta) * COSTO_MINIMO
                heapq.heappush(frontera, (prioridad, nuevo, next(desempate), vecino))

    return _resultado(rejilla, padres, inicio, meta, visitados, "astar")


# ----------------------------------------------------------------- Greedy

def buscar_greedy(rejilla, inicio, meta):
    """Voraz: solo mira la heuristica; rapido pero no garantiza el optimo."""
    if not _valida(rejilla, *inicio) or not _valida(rejilla, *meta):
        return _vacio("greedy")

    desempate = count()
    padres = {inicio: None}
    visitados = []
    expandidos = set()
    frontera = [(_manhattan(inicio, meta), next(desempate), inicio)]

    while frontera:
        _, _, actual = heapq.heappop(frontera)
        if actual in expandidos:
            continue
        expandidos.add(actual)
        visitados.append(actual)
        if actual == meta:
            break
        for vecino in _vecinos(rejilla, *actual):
            if vecino not in padres:
                padres[vecino] = actual
                heapq.heappush(frontera, (_manhattan(vecino, meta), next(desempate), vecino))

    return _resultado(rejilla, padres, inicio, meta, visitados, "greedy")


_BUSCADORES = {
    "astar": buscar_astar,
    "bfs": buscar_bfs,
    "dfs": buscar_dfs,
    "greedy": buscar_greedy,
    "dijkstra": buscar_dijkstra,
}


def buscar(algoritmo, rejilla, inicio, meta):
    """Despacha al algoritmo pedido. 'ninguno' no es una busqueda."""
    buscador = _BUSCADORES.get(algoritmo)
    if buscador is None:
        raise ValueError(
            f"algoritmo desconocido: {algoritmo!r}; disponibles: {sorted(_BUSCADORES)}"
        )
    return buscador(rejilla, inicio, meta)
