"""Cursor personalizado con rastros que se desvanecen (cursor.py)."""

from pygame import *


class CustomMouse:
    def __init__(self, ruta_cursor, ruta_rastro, velocidad_desvanecido=7):
        mouse.set_visible(False)

        self.img_cursor = image.load(ruta_cursor).convert_alpha()
        self.img_rastro = image.load(ruta_rastro).convert_alpha()

        self.velocidad_desvanecido = velocidad_desvanecido
        self.rastros = []

    def procesar_evento(self, evento):
        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            self.rastros.append({"pos": evento.pos, "alfa": 255})

    def update(self):
        for rastro in self.rastros[:]:
            rastro["alfa"] -= self.velocidad_desvanecido
            if rastro["alfa"] <= 0:
                self.rastros.remove(rastro)

    def render(self, superficie):
        for rastro in self.rastros:
            img_temporal = self.img_rastro.copy()
            img_temporal.set_alpha(int(rastro["alfa"]))
            superficie.blit(img_temporal, img_temporal.get_rect(center=rastro["pos"]))

        superficie.blit(self.img_cursor, mouse.get_pos())
