"""Botón de menú con hover y destello (boton.py)."""

from pygame import *

from config import RUTA_AUDIO_HOVER_BOTON, RUTA_AUDIO_PRESIONAR_BOTON

mixer.init()
sonido_presionar_boton = mixer.Sound(RUTA_AUDIO_PRESIONAR_BOTON)
sonido_hover_boton = mixer.Sound(RUTA_AUDIO_HOVER_BOTON)

class BotonTexto:
    def __init__(
        self,
        texto,
        posicion_centro,
        fuente,
        color_reposo=(180, 190, 205),
        color_hover=(255, 235, 90),
        color_destello=(255, 255, 255),
        color_sombra=(10, 12, 18),
        accion=None,
    ):
        self.texto = texto
        self.fuente = fuente
        self.posicion_centro = posicion_centro
        self.color_reposo = color_reposo
        self.color_hover = color_hover
        self.color_destello = color_destello
        self.color_sombra = color_sombra
        self.accion = accion

        superficie_base = self.fuente.render(self.texto, True, self.color_reposo)
        self.rect = superficie_base.get_rect(center=self.posicion_centro).inflate(40, 16)

        self.esta_encima = False
        self.estaba_encima = False  # Rastrea el estado del fotograma anterior
        self.en_animacion = False
        self.visible = True
        self.fase_destello = False

        self.tiempo_inicio = 0
        self.duracion_animacion_ms = 400
        self.intervalo_parpadeo_ms = 60

    def manejar_evento(self, evento):
        if self.en_animacion:
            return

        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                sonido_presionar_boton.play()
                self.en_animacion = True
                self.tiempo_inicio = time.get_ticks()

    def actualizar(self):
        self.esta_encima = self.rect.collidepoint(mouse.get_pos())

        # Dispara el sonido solo en el instante en que entra el cursor
        if self.esta_encima and not self.estaba_encima and not self.en_animacion:
            sonido_hover_boton.play()

        # Guarda el estado actual para la comparación del próximo fotograma
        self.estaba_encima = self.esta_encima

        if self.en_animacion:
            tiempo_transcurrido = time.get_ticks() - self.tiempo_inicio

            ciclo = (tiempo_transcurrido // self.intervalo_parpadeo_ms) % 2
            self.visible = ciclo == 0
            self.fase_destello = (tiempo_transcurrido // (self.intervalo_parpadeo_ms // 2)) % 2 == 1

            if tiempo_transcurrido >= self.duracion_animacion_ms:
                self.en_animacion = False
                self.visible = True
                if self.accion:
                    self.accion()

    def dibujar(self, superficie_destino):
        if not self.visible:
            return

        texto_a_mostrar = f"> {self.texto} <" if (self.esta_encima or self.en_animacion) else self.texto

        if self.en_animacion and self.fase_destello:
            color_actual = self.color_destello
        elif self.esta_encima:
            color_actual = self.color_hover
        else:
            color_actual = self.color_reposo

        superficie_sombra = self.fuente.render(texto_a_mostrar, True, self.color_sombra)
        superficie_destino.blit(
            superficie_sombra,
            superficie_sombra.get_rect(center=(self.posicion_centro[0] + 3, self.posicion_centro[1] + 3)),
        )

        superficie_texto = self.fuente.render(texto_a_mostrar, True, color_actual)
        superficie_destino.blit(superficie_texto, superficie_texto.get_rect(center=self.posicion_centro))