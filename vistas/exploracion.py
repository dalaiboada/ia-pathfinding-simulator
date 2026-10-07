"""Exploración: mapa de terreno desde JSON, jugador con colisión y costo."""

from pygame import *

from config import (
    ALTO_HUD,
    ALTO_VENTANA,
    ANCHO_VENTANA,
    RUTA_JUGADOR,
    RUTA_MAPA_EXPLORACION,
    TAM_CELDA,
)
from dibujo import dibujar_banda_hud
from entidades.jugador import Jugador
from mundo.mapa_terreno import MapaTerreno
from paleta import (
    CIAN_BRILLANTE,
    COLOR_BORDE,
    COLOR_FONDO_EXPLORACION,
)
from .base import Vista


class VistaExploracion(Vista):
    nombre = "exploracion"

    def __init__(self, juego):
        super().__init__(juego)

        self.area = Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)
        self.mapa = self.cargar_mapa()
        self.area_juego = self.mapa.area()

        self.proyectiles = sprite.Group()
        self.jugador = Jugador(
            RUTA_JUGADOR,
            *self.posicion_inicial(),
            self.area_juego,
            self.proyectiles,
            mapa=self.mapa,
        )
        self.velas = self.preparar_velas()

    # ------------------------------------------------------------------ mapa

    def cargar_mapa(self):
        """Lee el JSON de disco, ajustado al area visible.

        Si el JSON falla se avisa por consola y se dibuja un patio generado por
        codigo, para que el juego siga siendo jugable.
        """
        columnas = ANCHO_VENTANA // TAM_CELDA
        filas = (ALTO_VENTANA - ALTO_HUD) // TAM_CELDA
        origen_x = (ANCHO_VENTANA - columnas * TAM_CELDA) // 2

        try:
            mapa = MapaTerreno.cargar_json(
                RUTA_MAPA_EXPLORACION,
                columnas=columnas,
                filas=filas,
                tamano_celda=TAM_CELDA,
                origen_x=origen_x,
                origen_y=ALTO_HUD,
            )
        except (OSError, ValueError) as error:
            print(f"[exploracion] no pude leer {RUTA_MAPA_EXPLORACION}: {error}")
            print("[exploracion] uso un mapa de respaldo generado por codigo")
            mapa = self.mapa_de_respaldo(columnas, filas, origen_x)

        return mapa

    def mapa_de_respaldo(self, columnas, filas, origen_x):
        """Patio minimo: perimetro bloqueado, avenida en cruz y nada mas."""
        mapa = MapaTerreno(columnas, filas, TAM_CELDA, origen_x, ALTO_HUD)
        clave_muro = mapa.clave_obstaculo() or mapa.terreno_defecto
        clave_rapida = mapa.terreno_mas_barato().clave

        for col in range(columnas):
            mapa.colocar_terreno(0, col, clave_muro)
            mapa.colocar_terreno(filas - 1, col, clave_muro)
        for fila in range(1, filas - 1):
            mapa.colocar_terreno(fila, 0, clave_muro)
            mapa.colocar_terreno(fila, columnas - 1, clave_muro)

        avenida_fila = filas // 2
        for col in range(1, columnas - 1):
            mapa.colocar_terreno(avenida_fila, col, clave_rapida)
        avenida_col = columnas // 2
        for fila in range(1, filas - 1):
            mapa.colocar_terreno(fila, avenida_col, clave_rapida)

        mapa.colocar_inicio(filas // 2, avenida_col)
        mapa.preparar_capa()
        return mapa

    def posicion_inicial(self):
        if self.mapa.inicio is not None:
            return self.mapa.centro_celda(*self.mapa.inicio)
        return (self.mapa.area().centerx, self.mapa.area().centery)

    def recargar_mapa(self):
        """Vuelve a leer el JSON del disco y recoloca al jugador en un sitio libre."""
        self.mapa = self.cargar_mapa()
        self.area_juego = self.mapa.area()
        self.jugador.mapa = self.mapa
        self.jugador.area_movimiento = self.area_juego
        self.jugador.objetivo = None

        destino = self.mapa.punto_libre_cerca(self.jugador.rect.center, self.jugador.rect.size)
        if destino is None:
            destino = self.posicion_inicial()
        self.jugador.rect.center = destino

    # ----------------------------------------------------------------- ciclo

    def preparar_velas(self):
        velas = []
        for indice in range(14):
            radio = 6 + indice * 2
            alfa = 170 - indice * 11
            if alfa <= 0:
                break
            circulo = Surface((radio * 2, radio * 2), SRCALPHA)
            draw.circle(circulo, CIAN_BRILLANTE + (alfa,), (radio, radio), radio, 1)
            velas.append(circulo)
        return velas

    def entrar(self):
        self.jugador.objetivo = None
        self.jugador.cambiar_estado("reposo")

    def manejar_evento(self, evento):
        if evento.type == KEYDOWN and evento.key == K_F5:
            self.recargar_mapa()
            return

        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            self.jugador.fijar_objetivo(evento.pos)

        self.jugador.procesar_eventos([evento])

    def actualizar(self):
        self.mapa.hover = self.mapa.celda_por_pos(mouse.get_pos())
        # El deslizador se ajusta en la vista de rutas, asi que se aplica aqui:
        # exploracion es la unica vista con un jugador que saltar.
        Jugador.fijar_multiplicador(self.juego.velocidad_animacion)
        self.jugador.update()
        self.proyectiles.update()

    # ---------------------------------------------------------------- dibujo

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO_EXPLORACION)
        self.mapa.dibujar(self.pantalla)
        self.mapa.dibujar_hover(self.pantalla)
        draw.rect(self.pantalla, COLOR_BORDE, self.area, 1)

        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "EXPLORACION",
            ["[CLIC IZQ] CAMINAR HACIA EL CURSOR   ·   [WASD] MOVIMIENTO ALTERNATIVO   ·   [J] DISPARAR",
             "[K] GOLPEAR   ·   [C] AGACHARSE   ·   [F5] RECARGAR MAPA   ·   [ESC] VOLVER AL MENÚ"],
        )

        if self.jugador.objetivo is not None:
            for vela in self.velas:
                self.pantalla.blit(vela, vela.get_rect(center=self.jugador.objetivo))

        self.proyectiles.draw(self.pantalla)
        self.jugador.dibujar(self.pantalla)
