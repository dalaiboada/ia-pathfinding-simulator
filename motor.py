"""Motor del juego: bucle principal y cambio entre vistas."""

from pygame import *

import arranque
from config import FPS, RUTA_CURSOR, RUTA_RASTRO, VELOCIDAD_ANIMACION_INICIAL
from interfaz.cursor import CustomMouse
from vistas import VistaControladorRutas, VistaExploracion, VistaMenu, VistaPersecucion


class Juego:
    def __init__(self):
        arranque.comprobar_iniciado()
        self.pantalla = arranque.pantalla
        self.reloj = arranque.reloj
        self.cursor = CustomMouse(RUTA_CURSOR, RUTA_RASTRO)
        
        self.velocidad_animacion = VELOCIDAD_ANIMACION_INICIAL
        self.eventos = []

        self.vistas = {
            "menu": VistaMenu(self),
            "exploracion": VistaExploracion(self),
            "rutas": VistaControladorRutas(self),
            "persecucion": VistaPersecucion(self),
        }

        self.vista = None
        self.ir_a("menu")

    def ir_a(self, nombre):
        if self.vista is not None:
            self.vista.salir()
            
        self.vista = self.vistas[nombre]
        self.vista.entrar()

    def ejecutar(self):
        ejecutando = True

        while ejecutando:
            self.eventos = event.get()

            for evento in self.eventos:
                if evento.type == QUIT:
                    ejecutando = False
                    continue

                if evento.type == KEYDOWN and evento.key == K_ESCAPE and self.vista.permite_escape:
                    self.ir_a("menu")
                    continue

                self.cursor.procesar_evento(evento)
                self.vista.manejar_evento(evento)

            self.cursor.update()
            self.vista.actualizar()
            self.vista.dibujar()
            self.cursor.render(self.pantalla)

            display.flip()
            self.reloj.tick(FPS)

        quit()
