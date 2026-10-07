"""Simulador de rutas y movimiento.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .arranque import comprobar_iniciado, fuente, iniciar
from .motor import Juego

__all__ = ["Juego", "comprobar_iniciado", "fuente", "iniciar"]
