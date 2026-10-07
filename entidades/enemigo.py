"""Enemigo representativo: un cuadrado que persigue al jugador.

Aun no hay hoja de sprites de Ultron en juego, asi que el enemigo es un cuadrado
Sabe dos formas de perseguir:

  - con un algoritmo de busqueda del modulo `busqueda` (A*, BFS, DFS, Greedy);
  - en linea recta hacia el jugador, cuando se elige la opcion "ninguno".

No se mueve hasta que el jugador entra en su campo de vision; a partir de ahi
queda alerta para siempre.
"""

from pygame import *

import busqueda
from config import (
    CAMPO_VISION_ENEMIGO,
    LADO_ENEMIGO,
    RECALCULO_RUTA_ENEMIGA,
    TAM_CELDA,
    VELOCIDAD_ENEMIGO,
)
from paleta import COLOR_ENEMIGO, COLOR_ENEMIGO_BORDE

TOLERANCIA_CELDA = 2


def _linea_libre(mapa, origen, destino):
    """Bresenham entre dos celdas: True si ninguna intermedia esta bloqueada."""
    fila0, col0 = origen
    fila1, col1 = destino
    delta_fila = abs(fila1 - fila0)
    delta_col = abs(col1 - col0)
    paso_fila = 1 if fila1 > fila0 else -1
    paso_col = 1 if col1 > col0 else -1
    error = delta_col - delta_fila

    fila, col = fila0, col0
    while True:
        if (fila, col) != origen and (fila, col) != destino and mapa.bloqueada(fila, col):
            return False
        if fila == fila1 and col == col1:
            return True

        error2 = 2 * error
        if error2 > -delta_fila:
            error -= delta_fila
            col += paso_col
        if error2 < delta_col:
            error += delta_col
            fila += paso_fila


class Enemigo(sprite.Sprite):
    def __init__(self, centro, mapa, rejilla=None, lado=LADO_ENEMIGO):
        sprite.Sprite.__init__(self)
        self.lado = int(lado)
        self.image = self._crear_imagen(self.lado)
        self.rect = self.image.get_rect(center=(int(centro[0]), int(centro[1])))
        self.mapa = mapa
        self.rejilla = rejilla if rejilla is not None else mapa
        self.velocidad = VELOCIDAD_ENEMIGO * (lado / float(TAM_CELDA))

        self.alerta = False
        self.ruta = []
        self.celda_objetivo = None
        self.espera = 0

        # Posicion en coma flotante: el Rect solo guarda enteros.
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    @staticmethod
    def _crear_imagen(lado):
        imagen = Surface((lado, lado), SRCALPHA)
        imagen.fill(COLOR_ENEMIGO)
        draw.rect(imagen, COLOR_ENEMIGO_BORDE, imagen.get_rect(), 2, border_radius=3)
        return imagen

    # ---------------------------------------------------------------- vision

    def _celda(self, posicion):
        if self.mapa is None:
            return None
        return self.mapa.celda_por_pos(posicion)

    def ve_al_jugador(self, jugador):
        if self.mapa is None:
            return False
        celda_enemigo = self._celda(self.rect.center)
        celda_jugador = self._celda(jugador.rect.center)
        if celda_enemigo is None or celda_jugador is None:
            return False

        distancia = max(
            abs(celda_enemigo[0] - celda_jugador[0]),
            abs(celda_enemigo[1] - celda_jugador[1]),
        )
        if distancia > CAMPO_VISION_ENEMIGO:
            return False
        return _linea_libre(self.mapa, celda_enemigo, celda_jugador)

    # --------------------------------------------------------------- movimiento

    def _mover(self, delta_x, delta_y):
        """Desplaza acumulando en floats para no perder pasos menores de 1 px."""
        self.pos_x += delta_x
        self.pos_y += delta_y
        destino_x = int(round(self.pos_x))
        destino_y = int(round(self.pos_y))
        admitido_x, admitido_y = self.mapa.desplazar(
            self.rect, destino_x - self.rect.x, destino_y - self.rect.y,
        )
        self.rect.x += admitido_x
        self.rect.y += admitido_y
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def _perseguir_recto(self, jugador):
        diferencia_x = jugador.rect.centerx - self.rect.centerx
        diferencia_y = jugador.rect.centery - self.rect.centery
        if diferencia_x == 0 and diferencia_y == 0:
            return
        longitud = (diferencia_x ** 2 + diferencia_y ** 2) ** 0.5
        self._mover(
            diferencia_x / longitud * self.velocidad,
            diferencia_y / longitud * self.velocidad,
        )

    def _perseguir_con_busqueda(self, jugador, algoritmo):
        celda_enemigo = self._celda(self.rect.center)
        celda_jugador = self._celda(jugador.rect.center)
        if celda_enemigo is None or celda_jugador is None:
            return

        self.espera -= 1
        necesita_ruta = (
            self.espera <= 0
            or not self.ruta
            or self.celda_objetivo != celda_jugador
        )
        if necesita_ruta:
            resultado = busqueda.buscar(algoritmo, self.rejilla, celda_enemigo, celda_jugador)
            self.ruta = list(resultado.camino[1:]) if resultado.camino else []
            self.celda_objetivo = celda_jugador
            self.espera = RECALCULO_RUTA_ENEMIGA

        while self.ruta:
            destino = self.mapa.centro_celda(*self.ruta[0])
            if (abs(destino[0] - self.rect.centerx) <= TOLERANCIA_CELDA
                    and abs(destino[1] - self.rect.centery) <= TOLERANCIA_CELDA):
                self.ruta.pop(0)
            else:
                break

        if not self.ruta:
            return

        destino = self.mapa.centro_celda(*self.ruta[0])
        diferencia_x = destino[0] - self.rect.centerx
        diferencia_y = destino[1] - self.rect.centery

        if abs(diferencia_x) >= abs(diferencia_y):
            paso = max(-self.velocidad, min(self.velocidad, diferencia_x))
            self._mover(paso, 0)
        else:
            paso = max(-self.velocidad, min(self.velocidad, diferencia_y))
            self._mover(0, paso)

    # ------------------------------------------------------------------- ciclo

    def update(self, jugador, algoritmo):
        if self.mapa is None:
            return
        if not self.alerta and self.ve_al_jugador(jugador):
            self.alerta = True
        if not self.alerta:
            return

        if algoritmo == "ninguno":
            self._perseguir_recto(jugador)
        else:
            self._perseguir_con_busqueda(jugador, algoritmo)

    def dibujar(self, superficie):
        superficie.blit(self.image, self.rect)
