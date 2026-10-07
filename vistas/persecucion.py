"""Persecución: el jugador escapa y 5 enemigos lo persiguen al verlo."""

from pygame import *

from arranque import fuente
from busqueda import ALGORITMOS, NOMBRES_ALGORITMO
from config import (
    ALTO_HUD,
    ALTO_VENTANA,
    ANCHO_VENTANA,
    CAMPO_VISION_ENEMIGO,
    LADO_ENEMIGO,
    NUMERO_ENEMIGOS,
    RUTA_JUGADOR,
    RUTA_MAPA_PERSECUCION,
    TAM_CELDA,
)
from dibujo import dibujar_banda_hud
from entidades.enemigo import Enemigo
from entidades.jugador import Jugador
from interfaz.selector import SelectorCyber
from mundo.mapa_terreno import MapaTerreno
from paleta import (
    CIAN_BRILLANTE,
    COLOR_BORDE,
    COLOR_CAMPO_VISION,
    COLOR_FONDO,
)
from .base import Vista

# Selector de IA enemiga, pegado a la parte baja del mapa
X_SELECTOR = 190
ANCHO_SELECTOR = 560
ALTO_SELECTOR = 34
Y_SELECTOR = ALTO_VENTANA - ALTO_SELECTOR - 12


class VistaPersecucion(Vista):
    nombre = "persecucion"

    def __init__(self, juego):
        super().__init__(juego)
        self.area = Rect(0, ALTO_HUD, ANCHO_VENTANA, ALTO_VENTANA - ALTO_HUD)
        self.mapa = self.cargar_mapa()
        self.area_juego = self.mapa.area()

        self.selector = self._crear_selector(juego.algoritmo_enemigo)
        self._campo_vision = self._crear_campo_vision()

        self.jugador = self._crear_jugador()
        self.enemigos = self._crear_enemigos()

    # ------------------------------------------------------------------ mapa

    def cargar_mapa(self):
        columnas = ANCHO_VENTANA // TAM_CELDA
        filas = (ALTO_VENTANA - ALTO_HUD) // TAM_CELDA
        origen_x = (ANCHO_VENTANA - columnas * TAM_CELDA) // 2

        try:
            return MapaTerreno.cargar_json(
                RUTA_MAPA_PERSECUCION,
                columnas=columnas,
                filas=filas,
                tamano_celda=TAM_CELDA,
                origen_x=origen_x,
                origen_y=ALTO_HUD,
            )
        except (OSError, ValueError) as error:
            print(f"[persecucion] no pude leer {RUTA_MAPA_PERSECUCION}: {error}")
            print("[persecucion] uso un escenario de respaldo generado por codigo")
            return self.mapa_de_respaldo(columnas, filas, origen_x)

    def mapa_de_respaldo(self, columnas, filas, origen_x):
        """Escenario minimo con un par de objetos, para no quedarnos sin capas."""
        mapa = MapaTerreno(columnas, filas, TAM_CELDA, origen_x, ALTO_HUD)
        ids_objeto = list(mapa.catalogo.objetos)
        if ids_objeto:
            id_objeto = ids_objeto[0]
            for fila, col in ((filas // 2, columnas // 3), (filas // 3, 2 * columnas // 3)):
                mapa.colocar_objeto(fila, col, id_objeto)
        mapa.colocar_inicio(filas - 2, columnas // 2)
        mapa.preparar_capa()
        return mapa

    # ------------------------------------------------------------- entidades

    def _crear_jugador(self):
        if self.mapa.inicio is not None:
            centro = self.mapa.centro_celda(*self.mapa.inicio)
        else:
            centro = self.mapa.area().center
        return Jugador(
            RUTA_JUGADOR,
            *centro,
            self.area_juego,
            mapa=self.mapa,
        )

    def _crear_enemigos(self):
        enemigos = sprite.Group()
        columnas = self.mapa.columnas
        for indice in range(NUMERO_ENEMIGOS):
            col = int((indice + 1) * columnas / (NUMERO_ENEMIGOS + 1))
            col = max(1, min(columnas - 2, col))
            centro = self.mapa.centro_celda(1, col)
            seguro = self.mapa.punto_libre_cerca(centro, (LADO_ENEMIGO, LADO_ENEMIGO))
            if seguro is None:
                continue
            enemigos.add(Enemigo(seguro, self.mapa, self.mapa))
        return enemigos

    def _crear_selector(self, algoritmo_actual):
        opciones = [("ninguno", "NINGUNO")]
        opciones += [(clave, NOMBRES_ALGORITMO.get(clave, clave)) for clave in ALGORITMOS]
        claves = [clave for clave, _ in opciones]
        indice = claves.index(algoritmo_actual) if algoritmo_actual in claves else 0
        return SelectorCyber(
            X_SELECTOR, Y_SELECTOR, ANCHO_SELECTOR, ALTO_SELECTOR, opciones, seleccion=indice,
        )

    def _crear_campo_vision(self):
        radio = CAMPO_VISION_ENEMIGO * TAM_CELDA
        superficie = Surface((radio * 2, radio * 2), SRCALPHA)
        draw.circle(superficie, COLOR_CAMPO_VISION + (26,), (radio, radio), radio)
        draw.circle(superficie, COLOR_CAMPO_VISION + (60,), (radio, radio), radio, 1)
        return superficie

    # ----------------------------------------------------------------- ciclo

    def entrar(self):
        self.jugador = self._crear_jugador()
        self.enemigos = self._crear_enemigos()

    def ir_hacia(self, posicion):
        mapa = self.mapa
        rejilla = mapa.rejilla_para(self.jugador.rect.size)

        celda = mapa.celda_por_pos(posicion)
        if celda is None:
            return
        if rejilla.bloqueada(*celda):
            seguro = mapa.punto_libre_cerca(posicion, self.jugador.rect.size)
            if seguro is None:
                return
            celda = mapa.celda_por_pos(seguro) or celda

        origen = mapa.celda_por_pos(self.jugador.rect.center)
        if origen is None:
            return

        resultado = mapa.buscar_camino(
            origen, celda, self.juego.algoritmo_busqueda, rejilla,
        )
        if not resultado.camino:
            self.jugador.cancelar_ruta()
            return

        self.jugador.fijar_ruta([mapa.centro_celda(*c) for c in resultado.camino[1:]])
        self.jugador.objetivo = mapa.centro_celda(*celda)

    def manejar_evento(self, evento):
        if evento.type == KEYDOWN and evento.key == K_TAB:
            self.mapa.mostrar_rejilla = not self.mapa.mostrar_rejilla
            return

        if evento.type == KEYDOWN and evento.key == K_F5:
            mostrar_rejilla = self.mapa.mostrar_rejilla
            self.mapa = self.cargar_mapa()
            self.mapa.mostrar_rejilla = mostrar_rejilla
            self.area_juego = self.mapa.area()
            self.jugador = self._crear_jugador()
            self.enemigos = self._crear_enemigos()
            return

        if self.selector.manejar_evento(evento):
            self.juego.algoritmo_enemigo = self.selector.clave
            return

        if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
            self.ir_hacia(evento.pos)

    def actualizar(self):
        self.mapa.hover = self.mapa.celda_por_pos(mouse.get_pos())
        self.selector.actualizar()
        self.jugador.update()
        self.enemigos.update(self.jugador, self.juego.algoritmo_enemigo)

    # ---------------------------------------------------------------- dibujo

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)
        self.mapa.dibujar(self.pantalla)
        self.mapa.dibujar_hover(self.pantalla)

        for enemigo in self.enemigos:
            self.pantalla.blit(self._campo_vision, self._campo_vision.get_rect(center=enemigo.rect.center))

        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla)
        self.jugador.dibujar(self.pantalla)

        draw.rect(self.pantalla, COLOR_BORDE, self.area, 1)

        algoritmo = self.selector.etiqueta
        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "PERSECUCION",
            ["[CLIC IZQ] RUTA DEL JUGADOR   ·   LOS ENEMIGOS PERSIGUEN AL VERTE   ·   [TAB] REJILLA   ·   [F5] RECARGAR",
             f"IA ENEMIGA: {algoritmo}   ·   ELIGELA ABAJO   ·   [ESC] VOLVER AL MENU"],
        )

        self.pantalla.blit(
            fuente("cyber_etiqueta").render("IA ENEMIGA", True, CIAN_BRILLANTE),
            (20, Y_SELECTOR + 9),
        )
        self.selector.dibujar(self.pantalla)
