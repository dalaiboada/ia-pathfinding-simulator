"""El mundo del simulador: el terreno y la rejilla de rutas."""

from .mapa import MapaRutas
from .mapa_terreno import MapaTerreno
from .terreno import TipoTerreno, catalogo_por_defecto, cargar_catalogo

__all__ = [
    "MapaRutas",
    "MapaTerreno",
    "TipoTerreno",
    "catalogo_por_defecto",
    "cargar_catalogo",
]
