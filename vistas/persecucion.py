"""Persecución: escenario con las 3 capas, pendiente del sistema de IA enemiga."""

from pygame import *

from arranque import fuente
from config import (
    ALTO_HUD,
    ALTO_VENTANA,
    ANCHO_VENTANA,
    RUTA_MAPA_EXPLORACION,
    TAM_CELDA,
)
from dibujo import dibujar_banda_hud, dibujar_texto_centrado
from mundo.mapa_terreno import MapaTerreno
from paleta import COLOR_BORDE, COLOR_FONDO, TEXTO_BLANCO, TEXTO_SECUNDARIO
from .base import Vista


class VistaPersecucion(Vista):
    nombre = "persecucion"

    def __init__(self, juego):
        super().__init__(juego)
        self.area = Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)
        self.mapa = self.cargar_mapa()
        self.mapa.mostrar_rejilla = False
        self.area_juego = self.mapa.area()

    # ------------------------------------------------------------------ mapa

    def cargar_mapa(self):
        columnas = ANCHO_VENTANA // TAM_CELDA
        filas = (ALTO_VENTANA - ALTO_HUD) // TAM_CELDA
        origen_x = (ANCHO_VENTANA - columnas * TAM_CELDA) // 2

        try:
            return MapaTerreno.cargar_json(
                RUTA_MAPA_EXPLORACION,
                columnas=columnas,
                filas=filas,
                tamano_celda=TAM_CELDA,
                origen_x=origen_x,
                origen_y=ALTO_HUD,
            )
        except (OSError, ValueError) as error:
            print(f"[persecucion] no pude leer {RUTA_MAPA_EXPLORACION}: {error}")
            print("[persecucion] uso un escenario de respaldo generado por codigo")
            return self.mapa_de_respaldo(columnas, filas, origen_x)

    def mapa_de_respaldo(self, columnas, filas, origen_x):
        """Escenario minimo con un par de objetos, para no quedarnos sin capas."""
        mapa = MapaTerreno(columnas, filas, TAM_CELDA, origen_x, ALTO_HUD)
        ids_objeto = list(mapa.catalogo.objetos)
        if ids_objeto:
            id_objeto = ids_objeto[0]
            for fila, col in ((filas // 2, columnas // 3), (filas // 3, 2 * columnas // 3)):
                mapa.colocar_objeto(fila, col, id_objeto)
        mapa.preparar_capa()
        return mapa

    # ----------------------------------------------------------------- ciclo

    def manejar_evento(self, evento):
        if evento.type == KEYDOWN and evento.key == K_F5:
            self.mapa = self.cargar_mapa()
            self.mapa.mostrar_rejilla = False
            self.area_juego = self.mapa.area()

    def actualizar(self):
        self.mapa.hover = self.mapa.celda_por_pos(mouse.get_pos())

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        self.mapa.dibujar(self.pantalla)
        self.mapa.dibujar_hover(self.pantalla)
        draw.rect(self.pantalla, COLOR_BORDE, self.area, 1)

        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "PERSECUCION",
            ["MAPA DE 3 CAPAS LISTO (SUELO / OBJETOS / ENTIDADES)   ·   [F5] RECARGAR   ·   [ESC] VOLVER AL MENU"],
        )

        dibujar_texto_centrado(
            self.pantalla, "MODULO DE PERSECUCION DE ENEMIGOS",
            fuente("hud"), TEXTO_BLANCO, (ANCHO_VENTANA // 2, self.area.centery - 20),
        )
        dibujar_texto_centrado(
            self.pantalla, "Aqui ira el calculo de la ruta enemiga (A* / BFS) y su persecucion.",
            fuente("instrucciones"), TEXTO_SECUNDARIO, (ANCHO_VENTANA // 2, self.area.centery + 20),
        )
