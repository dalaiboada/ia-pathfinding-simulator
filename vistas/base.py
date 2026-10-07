"""Base común de las vistas: entrar -> manejar_evento -> actualizar -> dibujar."""


class Vista:
    nombre = "vista"
    permite_escape = True

    def __init__(self, juego):
        self.juego = juego
        self.pantalla = juego.pantalla

    def entrar(self):
        pass

    def salir(self):
        pass

    def manejar_evento(self, evento):
        pass

    def actualizar(self):
        pass

    def dibujar(self):
        pass
