"""Mapa de la vista de rutas: el mismo terreno, editado a mano.

Sobre MapaTerreno solo anade la politica de edicion de esta vista. El punto de
enganche de la busqueda son `marcas`, `inicio` y `meta`.
"""

from pygame import *

from .mapa_terreno import MapaTerreno


class MapaRutas(MapaTerreno):
    """Rejilla del controlador de rutas, lista para que la busquenia la recorra."""

    def __init__(self, ancho, alto, origen_y, tamano_celda):
        super().__init__(
            columnas=ancho // tamano_celda,
            filas=(alto - origen_y) // tamano_celda,
            tamano_celda=tamano_celda,
            origen_x=0,
            origen_y=origen_y,
        )
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
        return False
