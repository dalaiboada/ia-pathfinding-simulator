"""Enemigo perseguidor
"""

from pygame import *

import busqueda
from config import (
    CAMPO_VISION_ENEMIGO,
    CUADRO_ENEMIGO,
    ESCALA_ENEMIGO,
    LADO_ENEMIGO,
    RECALCULO_RUTA_ENEMIGA,
    RUTA_ENEMIGO,
    TAM_CELDA,
    VELOCIDAD_ANIMACION_ENEMIGO,
    VELOCIDAD_ENEMIGO,
)
from paleta import COLOR_ENEMIGO, COLOR_ENEMIGO_BORDE

TOLERANCIA_CELDA = 2

# Fila de la hoja por direccion y numero de cuadros por animacion
FILA_POR_DIRECCION = {"down": 0, "left": 1, "right": 2, "up": 3}
NUMERO_CUADROS = 3
CUADRO_REPOSO = 1

_ANIMACIONES = None


def cargar_animaciones():
    """Recorta la hoja en 4 direcciones x 3 cuadros y la cachea a nivel de modulo."""
    global _ANIMACIONES
    if _ANIMACIONES is not None:
        return _ANIMACIONES

    try:
        hoja = image.load(RUTA_ENEMIGO).convert_alpha()
    except error:
        _ANIMACIONES = None
        return _ANIMACIONES

    lado = int(CUADRO_ENEMIGO * ESCALA_ENEMIGO)
    animaciones = {}
    for direccion, fila in FILA_POR_DIRECCION.items():
        cuadros = []
        for col in range(NUMERO_CUADROS):
            rect = Rect(col * CUADRO_ENEMIGO, fila * CUADRO_ENEMIGO, CUADRO_ENEMIGO, CUADRO_ENEMIGO)
            cuadro = transform.scale(hoja.subsurface(rect).copy(), (lado, lado))
            cuadros.append(cuadro)
        animaciones[direccion] = cuadros

    _ANIMACIONES = animaciones
    return _ANIMACIONES


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
        self.animaciones = cargar_animaciones()
        if self.animaciones:
            self.image = self.animaciones["down"][CUADRO_REPOSO]
        else:
            self.image = self._crear_imagen(lado)

        self.rect = self.image.get_rect(center=(int(centro[0]), int(centro[1])))
        self.mapa = mapa
        self.rejilla = rejilla if rejilla is not None else mapa
        self.velocidad = VELOCIDAD_ENEMIGO * (self.rect.width / float(TAM_CELDA))

        self.direccion = "down"
        self.cuadro = CUADRO_REPOSO
        self.contador_anim = float(CUADRO_REPOSO)

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

    # --------------------------------------------------------------- animacion

    def _orientar(self, delta_x, delta_y):
        if delta_x < 0:
            self.direccion = "left"
        elif delta_x > 0:
            self.direccion = "right"
        elif delta_y < 0:
            self.direccion = "up"
        elif delta_y > 0:
            self.direccion = "down"

    def _animar(self, moviendose):
        if not self.animaciones:
            return
        if moviendose:
            self.contador_anim += VELOCIDAD_ANIMACION_ENEMIGO
            self.cuadro = int(self.contador_anim) % NUMERO_CUADROS
        else:
            self.contador_anim = float(CUADRO_REPOSO)
            self.cuadro = CUADRO_REPOSO
        self.image = self.animaciones[self.direccion][self.cuadro]

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
        """Desplaza acumulando en floats. Devuelve True si el rect cambio de pixel."""
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
        return admitido_x != 0 or admitido_y != 0

    def _perseguir_recto(self, jugador):
        diferencia_x = jugador.rect.centerx - self.rect.centerx
        diferencia_y = jugador.rect.centery - self.rect.centery
        if diferencia_x == 0 and diferencia_y == 0:
            return False
        longitud = (diferencia_x ** 2 + diferencia_y ** 2) ** 0.5
        return self._mover(
            diferencia_x / longitud * self.velocidad,
            diferencia_y / longitud * self.velocidad,
        )

    def _perseguir_con_busqueda(self, jugador, algoritmo):
        celda_enemigo = self._celda(self.rect.center)
        celda_jugador = self._celda(jugador.rect.center)
        if celda_enemigo is None or celda_jugador is None:
            return False

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
            return False

        destino = self.mapa.centro_celda(*self.ruta[0])
        diferencia_x = destino[0] - self.rect.centerx
        diferencia_y = destino[1] - self.rect.centery

        if abs(diferencia_x) >= abs(diferencia_y):
            paso = max(-self.velocidad, min(self.velocidad, diferencia_x))
            self._orientar(1 if paso > 0 else -1 if paso < 0 else 0, 0)
            return self._mover(paso, 0)

        paso = max(-self.velocidad, min(self.velocidad, diferencia_y))
        self._orientar(0, 1 if paso > 0 else -1 if paso < 0 else 0)
        return self._mover(0, paso)

    # ------------------------------------------------------------------- ciclo

    def update(self, jugador, algoritmo):
        if self.mapa is None:
            self._animar(False)
            return
        if not self.alerta and self.ve_al_jugador(jugador):
            self.alerta = True
        if not self.alerta:
            self._animar(False)
            return

        if algoritmo == "ninguno":
            self._orientar(
                jugador.rect.centerx - self.rect.centerx,
                jugador.rect.centery - self.rect.centery,
            )
            moviendose = self._perseguir_recto(jugador)
        else:
            moviendose = self._perseguir_con_busqueda(jugador, algoritmo)

        self._animar(moviendose)

    def dibujar(self, superficie):
        superficie.blit(self.image, self.rect)
