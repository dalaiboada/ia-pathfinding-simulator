"""Menú principal: fondo, velo y tres botones de navegación."""

from pygame import *

from arranque import fuente
from config import ALTO_VENTANA, ANCHO_VENTANA, RUTA_FONDO_MENU
from dibujo import crear_velo, dibujar_texto_centrado
from interfaz.boton import BotonTexto
from paleta import CIAN_BRILLANTE, CIAN_OSCURO, TEXTO_BLANCO
from .base import Vista


class VistaMenu(Vista):
    nombre = "menu"
    permite_escape = False

    def __init__(self, juego):
        super().__init__(juego)

        self.fondo = transform.scale(
            image.load(RUTA_FONDO_MENU).convert(), (ANCHO_VENTANA, ALTO_VENTANA),
        )
        self.velo = crear_velo(ANCHO_VENTANA, ALTO_VENTANA, (3, 6, 14))

        self.botones = []
        acciones = [
            ("Exploracion", lambda: juego.ir_a("exploracion")),
            ("Controlador de rutas", lambda: juego.ir_a("rutas")),
            ("Persecucion", lambda: juego.ir_a("persecucion")),
        ]

        for indice, (texto, accion) in enumerate(acciones):
            self.botones.append(
                BotonTexto(
                    texto=texto,
                    posicion_centro=(370, 500 + indice * 50),
                    fuente=fuente("boton"),
                    color_reposo=(185, 200, 220),
                    color_hover=CIAN_BRILLANTE,
                    color_destello=(255, 255, 255),
                    accion=accion,
                )
            )

    def manejar_evento(self, evento):
        for boton in self.botones:
            boton.manejar_evento(evento)

    def actualizar(self):
        for boton in self.botones:
            boton.actualizar()

    def dibujar(self):
        self.pantalla.blit(self.fondo, (0, 0))
        self.pantalla.blit(self.velo, (0, 0))

        for boton in self.botones:
            boton.dibujar(self.pantalla)
