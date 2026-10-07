"""Mapa de la vista de rutas: el mismo mapa de 3 capas, editado a mano.

Sobre MapaTerreno solo anade la politica de edicion de esta vista y el auto-borde
del pavimento. Los puntos de enganche de la busqueda son `marcas`, `inicio` y
`meta`.
"""

from pygame import *

from config import TAM_CELDA
from .mapa_terreno import MapaTerreno

# IDs de las variantes de pavimento del catalogo por defecto (ver catalogo.py)
CENTRO_PAVIMENTO = 1
BORDE_ARRIBA = 2
BORDE_ABAJO = 3
BORDE_DERECHA = 4
BORDE_IZQUIERDA = 5
ESQUINA_SUP_IZQ = 6
ESQUINA_SUP_DER = 7
ESQUINA_INF_IZQ = 8
ESQUINA_INF_DER = 9


class MapaRutas(MapaTerreno):
    """Rejilla del controlador de rutas, lista para que la busqueda la recorra."""

    def __init__(
        self,
        columnas,
        filas,
        tamano_celda=TAM_CELDA,
        origen_x=0,
        origen_y=0,
        catalogo=None,
    ):
        super().__init__(columnas, filas, tamano_celda, origen_x, origen_y, catalogo)
        self.nombre = "rutas"

    def manejar_tecla(self, evento):
        """Teclas propias de esta vista; la pintura la hace la vista."""
        if evento.type != KEYDOWN:
            return False
        if evento.key == K_TAB:
            self.mostrar_rejilla = not self.mostrar_rejilla
            return True
        if evento.key == K_r:
            self.limpiar()
            return True
        if evento.key == K_b:
            self.autotile_pavimento()
            return True
        return False

    def _es_pavimento(self, fila, col):
        if not self._dentro(fila, col):
            return False
        terreno = self.terreno_en(fila, col)
        return terreno is not None and terreno.clave == "pavimento"

    def autotile_pavimento(self):
        """Recalcula borde y esquina de cada celda de pavimento segun sus vecinos."""
        for fila in range(self.filas):
            for col in range(self.columnas):
                if not self._es_pavimento(fila, col):
                    continue
                sin_arriba = not self._es_pavimento(fila - 1, col)
                sin_abajo = not self._es_pavimento(fila + 1, col)
                sin_izquierda = not self._es_pavimento(fila, col - 1)
                sin_derecha = not self._es_pavimento(fila, col + 1)

                lados = frozenset(
                    lado
                    for lado, abierto in (
                        ("arriba", sin_arriba),
                        ("abajo", sin_abajo),
                        ("izquierda", sin_izquierda),
                        ("derecha", sin_derecha),
                    )
                    if abierto
                )

                if lados == {"arriba", "izquierda"}:
                    id_tile = ESQUINA_SUP_IZQ
                elif lados == {"arriba", "derecha"}:
                    id_tile = ESQUINA_SUP_DER
                elif lados == {"abajo", "izquierda"}:
                    id_tile = ESQUINA_INF_IZQ
                elif lados == {"abajo", "derecha"}:
                    id_tile = ESQUINA_INF_DER
                elif lados == {"arriba"}:
                    id_tile = BORDE_ARRIBA
                elif lados == {"abajo"}:
                    id_tile = BORDE_ABAJO
                elif lados == {"derecha"}:
                    id_tile = BORDE_DERECHA
                elif lados == {"izquierda"}:
                    id_tile = BORDE_IZQUIERDA
                else:
                    id_tile = CENTRO_PAVIMENTO

                self.suelo[fila][col] = id_tile

        self.preparar_capa()
