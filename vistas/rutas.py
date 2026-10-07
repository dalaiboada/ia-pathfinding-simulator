"""Controlador de rutas: rejilla de terreno editable a la izquierda, telemetría a la derecha."""

from pygame import *

from arranque import fuente
from busqueda import ALGORITMOS, NOMBRES_ALGORITMO
from config import (
    ALTO_HUD,
    ALTO_VENTANA,
    ANCHO_MAPA,
    ANCHO_PANEL,
    ANCHO_VENTANA,
    RUTA_JUGADOR,
    STEP_ANGULOS,
    TAM_CELDA,
    VELOCIDAD_ANIMACION_MAX,
    VELOCIDAD_ANIMACION_MIN,
)
from dibujo import dibujar_banda_hud, dibujar_tarjeta_cyber
from entidades.jugador import Jugador
from interfaz.deslizador import DeslizadorCyber
from interfaz.selector import SelectorCyber
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
Y_SELECTOR = 92
ALTO_SELECTOR = 30
Y_PALETA = 138
ALTO_PALETA = 34
Y_TARJETAS = 184
PASO_TARJETA = 56
ALTO_TARJETA = 48
Y_DIVISOR = 522
Y_ETIQUETA_VELOCIDAD = Y_DIVISOR + 14
Y_DESLIZADOR = 566


class VistaControladorRutas(Vista):
    nombre = "rutas"

    def __init__(self, juego):
        super().__init__(juego)

        self.mapa = MapaRutas(ANCHO_MAPA, ALTO_VENTANA, ALTO_HUD, TAM_CELDA)
        self.area_mapa = self.mapa.area()
        self.area_panel = Rect(ANCHO_MAPA, 0, ANCHO_PANEL, ALTO_VENTANA)

        self.seleccion = self._seleccion_inicial()
        self.paleta = self.preparar_paleta()

        # Punto de partida y meta de ejemplo, y el personaje que recorre la ruta.
        self.mapa.colocar_inicio(self.mapa.filas // 2, 1)
        self.mapa.colocar_meta(self.mapa.filas // 2, self.mapa.columnas - 2)
        self.jugador = Jugador(
            RUTA_JUGADOR,
            *self.mapa.centro_celda(*self.mapa.inicio),
            self.mapa.area(),
            mapa=self.mapa,
        )

        self.selector = self._crear_selector(juego.algoritmo_busqueda)

        # Telemetria del ultimo recorrido
        self.nodos_explorados = 0
        self.costo_ruta = 0.0
        self.longitud_ruta = 0
        self.algoritmo_ejecutado = "-"

        self.deslizador_velocidad = DeslizadorCyber(
            x=ANCHO_MAPA + 30,
            y=Y_DESLIZADOR,
            ancho=ANCHO_PANEL - 60,
            valor_min=VELOCIDAD_ANIMACION_MIN,
            valor_max=VELOCIDAD_ANIMACION_MAX,
            valor_inicial=juego.velocidad_animacion,
        )

    def _crear_selector(self, algoritmo_actual):
        opciones = [(clave, NOMBRES_ALGORITMO.get(clave, clave)) for clave in ALGORITMOS]
        claves = [clave for clave, _ in opciones]
        indice = claves.index(algoritmo_actual) if algoritmo_actual in claves else 0
        return SelectorCyber(
            X_PANEL, Y_SELECTOR, ANCHO_TARJETA, ALTO_SELECTOR, opciones, seleccion=indice,
        )

    # ---------------------------------------------------------------- paleta

    def _seleccion_inicial(self):
        clave = "hierba" if "hierba" in self.mapa.catalogo.terrenos else next(
            iter(self.mapa.catalogo.terrenos)
        )
        return ("terreno", clave)

    def preparar_paleta(self):
        """Un boton por tipo de terreno y por objeto, para elegir con que se pinta."""
        entradas = []

        for terreno in self.mapa.catalogo.terrenos.values():
            id_base = self.mapa.catalogo.id_base_de(terreno.clave)
            entradas.append({
                "clase": "terreno",
                "clave": terreno.clave,
                "nombre": terreno.nombre,
                "imagen": self.mapa.catalogo.tile(id_base),
                "color": terreno.color,
            })

        for id_objeto, objeto in self.mapa.catalogo.objetos.items():
            entradas.append({
                "clase": "objeto",
                "clave": id_objeto,
                "nombre": objeto.nombre,
                "imagen": objeto.imagen,
                "color": None,
            })

        hueco = 6
        ancho = (ANCHO_TARJETA - hueco * (len(entradas) - 1)) // len(entradas)
        for indice, entrada in enumerate(entradas):
            entrada["rect"] = Rect(X_PANEL + indice * (ancho + hueco), Y_PALETA, ancho, ALTO_PALETA)
        return entradas

    def paleta_en_pos(self, posicion):
        for entrada in self.paleta:
            if entrada["rect"].collidepoint(posicion):
                return entrada
        return None

    def aplicar_seleccion(self, fila, col):
        clase, valor = self.seleccion
        if clase == "terreno":
            self.mapa.colocar_terreno_clave(fila, col, valor)
        else:
            self.mapa.colocar_objeto(fila, col, valor)

    # -------------------------------------------------------------- busqueda

    def ejecutar_busqueda(self):
        """Busca desde inicio hasta meta con el algoritmo elegido y anima la ruta."""
        inicio = self.mapa.inicio
        meta = self.mapa.meta
        if inicio is None or meta is None:
            return

        rejilla = self.mapa.rejilla_para(self.jugador.rect.size)
        resultado = self.mapa.buscar_camino(
            inicio, meta, self.juego.algoritmo_busqueda, rejilla,
        )

        self.nodos_explorados = len(resultado.visitados)
        self.costo_ruta = resultado.costo
        self.longitud_ruta = len(resultado.camino)
        self.algoritmo_ejecutado = NOMBRES_ALGORITMO.get(self.juego.algoritmo_busqueda, "-")

        self.jugador.rect.center = self.mapa.centro_celda(*inicio)
        if resultado.camino:
            self.jugador.fijar_ruta(
                [self.mapa.centro_celda(*celda) for celda in resultado.camino[1:]]
            )
        else:
            self.jugador.cancelar_ruta()

    def limpiar_busqueda(self):
        """Descarta marcas, ruta y telemetria tras editar el mapa."""
        self.mapa.limpiar_marcas()
        self.jugador.cancelar_ruta()
        self.nodos_explorados = 0
        self.costo_ruta = 0.0
        self.longitud_ruta = 0
        self.algoritmo_ejecutado = "-"

    # ----------------------------------------------------------------- ciclo

    def entrar(self):
        self.jugador.cancelar_ruta()

    def manejar_evento(self, evento):
        if self.mapa.manejar_tecla(evento):
            # TAB, R y B cambian el mapa: la busqueda anterior ya no vale.
            self.limpiar_busqueda()
            return

        if evento.type == KEYDOWN and evento.key == K_SPACE:
            self.ejecutar_busqueda()
            return

        if evento.type == KEYDOWN:
            # Se usa la posicion actual del raton y no `hover`, para que la tecla
            # tambien funcione antes de que el puntero se haya movido un solo pixel.
            celda = self.mapa.celda_por_pos(mouse.get_pos())
            if celda is not None and self.mapa.hover is None:
                self.mapa.hover = celda
            if celda is not None:
                fila, col = celda
                if evento.key == K_1 and self.mapa.colocar_inicio(fila, col):
                    self.jugador.rect.center = self.mapa.centro_celda(fila, col)
                    self.limpiar_busqueda()
                    return
                if evento.key == K_2 and self.mapa.colocar_meta(fila, col):
                    self.limpiar_busqueda()
                    return

        if evento.type != MOUSEBUTTONDOWN:
            return

        if self.selector.manejar_evento(evento):
            self.juego.algoritmo_busqueda = self.selector.clave
            return

        entrada = self.paleta_en_pos(evento.pos)
        if entrada is not None:
            self.seleccion = (entrada["clase"], entrada["clave"])
            return

        celda = self.mapa.celda_por_pos(evento.pos)
        if celda is None:
            return

        fila, col = celda
        if evento.button == 1:
            self.aplicar_seleccion(fila, col)
        elif evento.button == 3:
            # Primero retira el objeto; si no hay, restaura el suelo.
            if not self.mapa.quitar_objeto(fila, col):
                self.mapa.limpiar_celda(fila, col)
        else:
            return

        self.mapa.preparar_capa()
        self.limpiar_busqueda()

    def actualizar(self):
        self.mapa.hover = self.mapa.celda_por_pos(mouse.get_pos())
        self.selector.actualizar()
        self.deslizador_velocidad.actualizar(self.juego.eventos)
        if self.deslizador_velocidad.valor != self.juego.velocidad_animacion:
            self.juego.velocidad_animacion = self.deslizador_velocidad.valor
            # Se aplica ya, sin esperar a entrar en exploracion, para que el
            # efecto se vea al ir y volver entre vistas.
            Jugador.fijar_multiplicador(self.juego.velocidad_animacion)

        self.jugador.update()

    # ---------------------------------------------------------------- dibujo

    def dibujar(self):
        self.pantalla.fill(COLOR_FONDO)

        dibujar_banda_hud(
            self.pantalla, ALTO_HUD, "CONTROLADOR DE RUTAS",
            ["[CLIC IZQ] PINTAR   ·   [CLIC DER] BORRAR   ·   [B] AUTO-BORDE   ·   [1] INICIO   ·   [2] META   ·   [ESPACIO] EJECUTAR",
             "[TAB] REJILLA   ·   [R] LIMPIAR MAPA   ·   [ESC] VOLVER AL MENÚ"],
            ancho_hud=ANCHO_MAPA,
        )

        self.pantalla.fill(COLOR_FONDO, self.area_mapa)
        self.mapa.dibujar(self.pantalla)
        self.mapa.dibujar_hover(self.pantalla)
        self.jugador.dibujar(self.pantalla)
        draw.rect(self.pantalla, COLOR_BORDE, self.area_mapa, 1)

        self.dibujar_panel()

    def dibujar_panel(self):
        panel = self.pantalla

        draw.rect(panel, COLOR_FONDO, self.area_panel)
        draw.line(panel, CIAN_BRILLANTE, (ANCHO_MAPA, 0), (ANCHO_MAPA, ALTO_VENTANA), 2)
        draw.line(panel, CIAN_OSCURO, (ANCHO_MAPA - 2, 0), (ANCHO_MAPA - 2, ALTO_VENTANA), 1)

        panel.blit(fuente("cyber_titulo").render("MÉTRICAS", True, CIAN_BRILLANTE), (X_PANEL, 18))
        panel.blit(
            fuente("cyber_diminuta").render("ESTADO: SIMULADOR EN LÍNEA", True, TEXTO_SECUNDARIO),
            (X_PANEL, 44),
        )
        draw.line(panel, CIAN_OSCURO, (X_PANEL, 68), (ANCHO_VENTANA - 25, 68), 1)

        self.selector.dibujar_etiqueta(panel, "ALGORITMO DEL PERSONAJE")
        self.selector.dibujar(panel)

        self.dibujar_paleta()
        self.dibujar_tarjetas()
        self.dibujar_deslizador()

    def dibujar_paleta(self):
        panel = self.pantalla

        for entrada in self.paleta:
            celda = entrada["rect"]
            seleccionada = (entrada["clase"], entrada["clave"]) == self.seleccion
            muestra = Rect(celda.x + 3, celda.y + 3, celda.width - 6, celda.height - 16)

            if entrada["imagen"] is not None:
                panel.blit(transform.scale(entrada["imagen"], muestra.size), muestra.topleft)
            else:
                draw.rect(panel, entrada["color"] or COLOR_FONDO, muestra)

            draw.rect(
                panel,
                CIAN_BRILLANTE if seleccionada else CIAN_OSCURO,
                celda,
                2 if seleccionada else 1,
            )

            etiqueta = fuente("cyber_diminuta").render(entrada["nombre"], True, TEXTO_SECUNDARIO)
            panel.blit(etiqueta, etiqueta.get_rect(center=(celda.centerx, celda.bottom - 7)))

    def dibujar_tarjetas(self):
        panel = self.pantalla

        hover = self.mapa.hover
        terreno = self.mapa.terreno_en(*hover) if hover else None
        objeto = self.mapa.objeto_en(*hover) if hover else None

        if terreno is None:
            valor_terreno, unidad_terreno = "-", ""
        elif terreno.transitable:
            valor_terreno, unidad_terreno = terreno.nombre, f"COSTO {terreno.costo:g}"
        else:
            valor_terreno, unidad_terreno = terreno.nombre, "BLOQUEA"

        if objeto is not None:
            unidad_terreno = f"OBJETO: {objeto.nombre.upper()}"

        inicio = self.mapa.inicio
        meta = self.mapa.meta

        tarjetas = [
            ("Posición", f"({hover[0]}, {hover[1]})" if hover else "(-, -)", ""),
            ("Inicio", f"({inicio[0]}, {inicio[1]})" if inicio else "(-, -)", ""),
            ("Meta", f"({meta[0]}, {meta[1]})" if meta else "(-, -)", ""),
            ("Terreno", valor_terreno, unidad_terreno),
            ("Nodos Explorados", str(self.nodos_explorados), "NODOS"),
            (f"Costo Ruta {self.algoritmo_ejecutado}", f"{self.costo_ruta:.2f}", "PTS"),
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
