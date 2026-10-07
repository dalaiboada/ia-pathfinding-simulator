"""Persecución: marcador de posición, pendiente del sistema de IA enemiga."""

from pygame import *

from arranque import fuente
from config import ALTO_HUD, ALTO_VENTANA, ANCHO_VENTANA
from dibujo import dibujar_banda_hud, dibujar_rejilla_fondo, dibujar_texto_centrado
from paleta import COLOR_BORDE, COLOR_FONDO, TEXTO_BLANCO, TEXTO_SECUNDARIO
from .base import Vista


class VistaPersecucion(Vista):
    nombre = "persecucion"

    def __init__(self, juego):
        super().__init__(juego)
        self.area = Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        dibujar_rejilla_fondo(self.pantalla, self.area)
        draw.rect(self.pantalla, COLOR_BORDE, self.area, 1)

        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "PERSECUION",
            ["MODULO PENDIENTE DE IMPLEMENTACION   ·   [ESC] VOLVER AL MENu"],
        )

        dibujar_texto_centrado(
            self.pantalla, "MODULO DE PERSECUION DE ENEMIGOS",
            fuente("hud"), TEXTO_BLANCO, (ANCHO_VENTANA // 2, self.area.centery - 20),
        )
        dibujar_texto_centrado(
            self.pantalla, "Aqui ira el calculo de la ruta enemiga (A* / BFS) y su persecucion.",
            fuente("instrucciones"), TEXTO_SECUNDARIO, (ANCHO_VENTANA // 2, self.area.centery + 20),
        )
