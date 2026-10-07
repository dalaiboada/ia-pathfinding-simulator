"""Controlador de rutas: rejilla de terreno editable a la izquierda, telemetría a la derecha."""

from pygame import *

from arranque import fuente
from config import (
    ALTO_HUD,
    ALTO_VENTANA,
    ANCHO_MAPA,
    ANCHO_PANEL,
    ANCHO_VENTANA,
    STEP_ANGULOS,
    TAM_CELDA,
    VELOCIDAD_ANIMACION_MAX,
    VELOCIDAD_ANIMACION_MIN,
)
from dibujo import dibujar_banda_hud, dibujar_tarjeta_cyber
from entidades.jugador import Jugador
from interfaz.deslizador import DeslizadorCyber
from mundo.mapa import MapaRutas
from paleta import (
    CIAN_BRILLANTE,
    CIAN_OSCURO,
    COLOR_BORDE,
    COLOR_FONDO,
    TEXTO_BLANCO,
    TEXTO_SECUNDARIO,
)
from .base import Vista

# Reparto vertical del panel
X_PANEL = ANCHO_MAPA + 25
ANCHO_TARJETA = ANCHO_PANEL - 50
Y_PALETA = 86
ALTO_PALETA = 34
Y_TARJETAS = 130
PASO_TARJETA = 64
ALTO_TARJETA = 56
Y_DIVISOR = 520
Y_ETIQUETA_VELOCIDAD = Y_DIVISOR + 18
Y_DESLIZADOR = 570


class VistaControladorRutas(Vista):
    nombre = "rutas"

    def __init__(self, juego):
        super().__init__(juego)

        self.mapa = MapaRutas(ANCHO_MAPA, ALTO_VENTANA, ALTO_HUD, TAM_CELDA)
        self.area_mapa = self.mapa.area()
        self.area_panel = Rect(ANCHO_MAPA, 0, ANCHO_PANEL, ALTO_VENTANA)

        self.terreno_activo = self.mapa.clave_obstaculo() or self.mapa.terreno_defecto
        self.paleta = self.preparar_paleta()

        self.deslizador_velocidad = DeslizadorCyber(
            x=ANCHO_MAPA + 30,
            y=Y_DESLIZADOR,
            ancho=ANCHO_PANEL - 60,
            valor_min=VELOCIDAD_ANIMACION_MIN,
            valor_max=VELOCIDAD_ANIMACION_MAX,
            valor_inicial=juego.velocidad_animacion,
        )

    # ---------------------------------------------------------------- paleta

    def preparar_paleta(self):
        """Un boton por tipo de terreno, para elegir con que se pinta."""
        tipos = list(self.mapa.catalogo.values())
        hueco = 6
        ancho = (ANCHO_TARJETA - hueco * (len(tipos) - 1)) // len(tipos)

        paleta = []
        for indice, tipo in enumerate(tipos):
            celda = Rect(X_PANEL + indice * (ancho + hueco), Y_PALETA, ancho, ALTO_PALETA)
            paleta.append((tipo, celda))
        return paleta

    def terreno_de_la_paleta(self, posicion):
        for tipo, celda in self.paleta:
            if celda.collidepoint(posicion):
                return tipo
        return None

    # ----------------------------------------------------------------- ciclo

    def manejar_evento(self, evento):
        if self.mapa.manejar_tecla(evento):
            return

        if evento.type == KEYDOWN:
            # Se usa la posicion actual del raton y no `hover`, para que la tecla
            # tambien funcione antes de que el puntero se haya movido un solo pixel.
            celda = self.mapa.celda_por_pos(mouse.get_pos())
            if celda is not None and self.mapa.hover is None:
                self.mapa.hover = celda
            if celda is not None:
                fila, col = celda
                if evento.key == K_1:
                    self.mapa.colocar_inicio(fila, col)
                    return
                if evento.key == K_2:
                    self.mapa.colocar_meta(fila, col)
                    return

        if evento.type != MOUSEBUTTONDOWN:
            return

        tipo = self.terreno_de_la_paleta(evento.pos)
        if tipo is not None:
            self.terreno_activo = tipo.clave
            return

        celda = self.mapa.celda_por_pos(evento.pos)
        if celda is None:
            return

        fila, col = celda
        if evento.button == 1:
            self.mapa.colocar_terreno(fila, col, self.terreno_activo)
        elif evento.button == 3:
            self.mapa.limpiar_celda(fila, col)
        else:
            return

        self.mapa.preparar_capa()

    def actualizar(self):
        self.mapa.hover = self.mapa.celda_por_pos(mouse.get_pos())
        self.deslizador_velocidad.actualizar(self.juego.eventos)
        if self.deslizador_velocidad.valor != self.juego.velocidad_animacion:
            self.juego.velocidad_animacion = self.deslizador_velocidad.valor
            # Se aplica ya, sin esperar a entrar en exploracion, para que el
            # efecto se vea al ir y volver entre vistas.
            Jugador.fijar_multiplicador(self.juego.velocidad_animacion)

    # ---------------------------------------------------------------- dibujo

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)

        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "CONTROLADOR DE RUTAS",
            ["[CLIC IZQ] PINTAR TERRENO   ·   [CLIC DER] RESTAURAR   ·   [1] INICIO   ·   [2] META",
             "[TAB] MOSTRAR REJILLA   ·   [R] LIMPIAR MAPA   ·   [ESC] VOLVER AL MENÚ"],
            ancho_hud=ANCHO_MAPA,
        )

        self.pantalla.fill(COLOR_FONDO, self.area_mapa)
        self.mapa.dibujar(self.pantalla)
        self.mapa.dibujar_hover(self.pantalla)
        draw.rect(self.pantalla, COLOR_BORDE, self.area_mapa, 1)

        self.dibujar_panel()

    def dibujar_panel(self):
        panel = self.pantalla

        draw.rect(panel, COLOR_FONDO, self.area_panel)
        draw.line(panel, CIAN_BRILLANTE, (ANCHO_MAPA, 0), (ANCHO_MAPA, ALTO_VENTANA), 2)
        draw.line(panel, CIAN_OSCURO, (ANCHO_MAPA - 2, 0), (ANCHO_MAPA - 2, ALTO_VENTANA), 1)

        panel.blit(fuente("cyber_titulo").render("MÉTRICAS", True, CIAN_BRILLANTE), (X_PANEL, 25))
        panel.blit(
            fuente("cyber_diminuta").render("ESTADO: SIMULADOR EN LÍNEA", True, TEXTO_SECUNDARIO),
            (X_PANEL, 52),
        )
        draw.line(panel, CIAN_OSCURO, (X_PANEL, 75), (ANCHO_VENTANA - 25, 75), 1)

        self.dibujar_paleta()
        self.dibujar_tarjetas()
        self.dibujar_deslizador()

    def dibujar_paleta(self):
        panel = self.pantalla

        for tipo, celda in self.paleta:
            seleccionada = tipo.clave == self.terreno_activo
            muestra = Rect(celda.x + 3, celda.y + 3, celda.width - 6, celda.height - 16)

            draw.rect(panel, tipo.color, muestra)
            draw.rect(
                panel,
                CIAN_BRILLANTE if seleccionada else CIAN_OSCURO,
                celda,
                2 if seleccionada else 1,
            )

            etiqueta = fuente("cyber_diminuta").render(tipo.nombre, True, TEXTO_SECUNDARIO)
            panel.blit(etiqueta, etiqueta.get_rect(center=(celda.centerx, celda.bottom - 7)))

    def dibujar_tarjetas(self):
        panel = self.pantalla

        hover = self.mapa.hover
        terreno = self.mapa.terreno_en(*hover) if hover else None

        if terreno is None:
            valor_terreno, unidad_terreno = "-", ""
        elif terreno.transitable:
            valor_terreno, unidad_terreno = terreno.nombre, f"COSTO {terreno.costo:g}"
        else:
            valor_terreno, unidad_terreno = terreno.nombre, "BLOQUEA"

        inicio = self.mapa.inicio
        meta = self.mapa.meta

        tarjetas = [
            ("Posición", f"({hover[0]}, {hover[1]})" if hover else "(-, -)", ""),
            ("Inicio", f"({inicio[0]}, {inicio[1]})" if inicio else "(-, -)", ""),
            ("Meta", f"({meta[0]}, {meta[1]})" if meta else "(-, -)", ""),
            ("Terreno", valor_terreno, unidad_terreno),
            ("Nodos Explorados", "0", "NODOS"),
            ("Costo Ruta", "0.00", "PTS"),
        ]

        for indice, (titulo, valor, unidad) in enumerate(tarjetas):
            dibujar_tarjeta_cyber(
                panel,
                X_PANEL,
                Y_TARJETAS + indice * PASO_TARJETA,
                ANCHO_TARJETA,
                ALTO_TARJETA,
                titulo,
                valor,
                unidad,
            )

    def dibujar_deslizador(self):
        panel = self.pantalla

        draw.line(panel, CIAN_OSCURO, (X_PANEL, Y_DIVISOR), (ANCHO_VENTANA - 25, Y_DIVISOR), 1)
        panel.blit(
            fuente("cyber_etiqueta").render("VELOCIDAD DE ANIMACIÓN", True, TEXTO_SECUNDARIO),
            (X_PANEL, Y_ETIQUETA_VELOCIDAD),
        )

        valor_vel = fuente("cyber_valor").render(
            f"{self.deslizador_velocidad.valor}%", True, CIAN_BRILLANTE,
        )
        panel.blit(valor_vel, (ANCHO_VENTANA - 25 - valor_vel.get_width(), Y_ETIQUETA_VELOCIDAD - 3))
        self.deslizador_velocidad.dibujar(panel)

        paso = STEP_ANGULOS[0] * Jugador.multiplicador
        panel.blit(
            fuente("cyber_diminuta").render(
                f"paso {paso:.1f} px/fotograma en exploraci\u00f3n",
                True, TEXTO_SECUNDARIO,
            ),
            (X_PANEL, Y_DESLIZADOR + 18),
        )
