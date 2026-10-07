"""Entidades que viven en el mapa: el jugador y sus proyectiles."""

from .jugador import Jugador, obtener_sub_cuadros
from .proyectil import Proyectil

__all__ = ["Jugador", "Proyectil", "obtener_sub_cuadros"]
