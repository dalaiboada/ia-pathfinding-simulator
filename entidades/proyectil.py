"""Proyectil que se autodestruye al salir del área (sprites.py)."""

from pygame import *

from paleta import COLOR_PROYECTIL


class Proyectil(sprite.Sprite):
    def __init__(self, x, y, direccion, limite):
        sprite.Sprite.__init__(self)
        self.image = Surface((14, 6), SRCALPHA)
        self.image.fill(COLOR_PROYECTIL)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 12 if direccion == "derecha" else -12
        self.limite = limite

    def update(self):
        self.rect.x += self.velocidad
        if self.rect.right < self.limite.left or self.rect.left > self.limite.right:
            self.kill()
