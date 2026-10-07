"""Selector segmentado cyberpunk: elige una opcion entre varias."""

from pygame import *

from arranque import fuente
from paleta import (
    CIAN_BRILLANTE,
    CIAN_OSCURO,
    CIAN_RESPLANDOR,
    COLOR_FONDO_TARJETA,
    TEXTO_BLANCO,
    TEXTO_SECUNDARIO,
)


class SelectorCyber:
    """Fila (o columna) de botones; solo uno queda seleccionado.

    `opciones` es una lista de pares `(clave, etiqueta)`. La vista pregunta por
    `selector.clave` y recibe la clave de la opcion activa.
    """

    def __init__(self, x, y, ancho, alto, opciones, seleccion=0, vertical=False):
        if not opciones:
            raise ValueError("un selector necesita al menos una opcion")

        self.rect = Rect(x, y, ancho, alto)
        self.opciones = [(clave, etiqueta) for clave, etiqueta in opciones]
        self.seleccion = max(0, min(seleccion, len(self.opciones) - 1))
        self.vertical = vertical
        self.indice_hover = None
        self._repartir()

    def _repartir(self):
        total = len(self.opciones)
        self.rects = []
        if self.vertical:
            alto = self.rect.height // total
            for indice in range(total):
                self.rects.append(
                    Rect(self.rect.x, self.rect.y + indice * alto, self.rect.width, alto)
                )
        else:
            ancho = self.rect.width // total
            for indice in range(total):
                self.rects.append(
                    Rect(self.rect.x + indice * ancho, self.rect.y, ancho, self.rect.height)
                )

    @property
    def clave(self):
        return self.opciones[self.seleccion][0]

    @property
    def etiqueta(self):
        return self.opciones[self.seleccion][1]

    def manejar_evento(self, evento):
        """Devuelve True si el clic cayo dentro del selector."""
        if evento.type != MOUSEBUTTONDOWN or evento.button != 1:
            return False
        for indice, rect in enumerate(self.rects):
            if rect.collidepoint(evento.pos):
                self.seleccion = indice
                return True
        return False

    def actualizar(self):
        posicion = mouse.get_pos()
        self.indice_hover = None
        for indice, rect in enumerate(self.rects):
            if rect.collidepoint(posicion):
                self.indice_hover = indice
                break

    def dibujar(self, superficie):
        for indice, (_, etiqueta) in enumerate(self.opciones):
            rect = self.rects[indice]
            elegido = indice == self.seleccion
            resaltado = indice == self.indice_hover and not elegido

            draw.rect(superficie, CIAN_OSCURO if elegido else COLOR_FONDO_TARJETA,
                      rect, border_radius=4)
            if elegido:
                color_borde = CIAN_BRILLANTE
            elif resaltado:
                color_borde = CIAN_RESPLANDOR
            else:
                color_borde = CIAN_OSCURO
            draw.rect(superficie, color_borde, rect, 2 if elegido else 1, border_radius=4)

            if elegido:
                color_texto = TEXTO_BLANCO
            elif resaltado:
                color_texto = CIAN_BRILLANTE
            else:
                color_texto = TEXTO_SECUNDARIO

            texto = fuente("cyber_etiqueta").render(etiqueta, True, color_texto)
            superficie.blit(texto, texto.get_rect(center=rect.center))

    def dibujar_etiqueta(self, superficie, texto):
        """Etiqueta opcional encima del selector (misma banda visual)."""
        superficie.blit(
            fuente("cyber_etiqueta").render(texto, True, TEXTO_SECUNDARIO),
            (self.rect.x, self.rect.y - 15),
        )
