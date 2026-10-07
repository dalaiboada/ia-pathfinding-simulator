"""Control deslizante cyberpunk (estadisticas.py)."""

from pygame import *

from paleta import CIAN_BRILLANTE, CIAN_OSCURO, CIAN_RESPLANDOR, TEXTO_BLANCO


class DeslizadorCyber:
    def __init__(self, x, y, ancho, valor_min, valor_max, valor_inicial):
        self.rectangulo = Rect(x, y, ancho, 10)
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.valor = valor_inicial
        self.radio_manija = 8
        self.arrastrando = False

    def obtener_posicion_x_manija(self):
        proporcion = (self.valor - self.valor_min) / (self.valor_max - self.valor_min)
        return int(self.rectangulo.x + proporcion * self.rectangulo.width)

    def actualizar(self, eventos):
        posicion_raton = mouse.get_pos()
        clic_sostenido = mouse.get_pressed()[0]

        rect_manija = Rect(
            self.obtener_posicion_x_manija() - 10,
            self.rectangulo.centery - 10,
            20,
            20,
        )

        for evento in eventos:
            if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                if rect_manija.collidepoint(posicion_raton) or self.rectangulo.collidepoint(posicion_raton):
                    self.arrastrando = True
            elif evento.type == MOUSEBUTTONUP and evento.button == 1:
                self.arrastrando = False

        if self.arrastrando and clic_sostenido:
            x_limitada = max(self.rectangulo.x, min(posicion_raton[0], self.rectangulo.right))
            proporcion = (x_limitada - self.rectangulo.x) / self.rectangulo.width
            self.valor = int(self.valor_min + proporcion * (self.valor_max - self.valor_min))

    def dibujar(self, superficie):
        draw.rect(superficie, CIAN_OSCURO, self.rectangulo, border_radius=4)

        x_actual = self.obtener_posicion_x_manija()
        draw.rect(
            superficie,
            CIAN_RESPLANDOR,
            Rect(self.rectangulo.x, self.rectangulo.y,
                 x_actual - self.rectangulo.x, self.rectangulo.height),
            border_radius=4,
        )
        draw.rect(superficie, CIAN_BRILLANTE, self.rectangulo, 1, border_radius=4)

        draw.circle(superficie, (0, 80, 140), (x_actual, self.rectangulo.centery), self.radio_manija + 3)
        draw.circle(superficie, CIAN_BRILLANTE, (x_actual, self.rectangulo.centery), self.radio_manija)
        draw.circle(superficie, TEXTO_BLANCO, (x_actual, self.rectangulo.centery), 3)
