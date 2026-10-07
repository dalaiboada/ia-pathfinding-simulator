"""Las cuatro vistas navegables del simulador."""

from .base import Vista
from .exploracion import VistaExploracion
from .menu import VistaMenu
from .persecucion import VistaPersecucion
from .rutas import VistaControladorRutas

__all__ = [
    "Vista",
    "VistaControladorRutas",
    "VistaExploracion",
    "VistaMenu",
    "VistaPersecucion",
]
