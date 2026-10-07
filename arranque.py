"""Arranque de pygame: unico punto del proyecto que abre la ventana."""

from pygame import *

from config import ALTO_VENTANA, ANCHO_VENTANA, RUTA_FONTE, TITULO_JUEGO

# Estado global del juego
pantalla = None
reloj = None
fuentes = {}

# Fuentes pixeladas (game.ttf)
FUENTES_PIXEL = {
    "titulo_menu": 58,
    "subtitulo_menu": 22,
    "boton": 30,
    "hud": 22
}

# Fuentes del sistema (para los numeros del panel)
FUENTES_SISTEMA = {
    "cyber_titulo": ("Consolas", 20, True),
    "cyber_etiqueta": ("Consolas", 13, True),
    "cyber_valor": ("Consolas", 18, True),
    "instrucciones": ("Consolas", 18, False),
    "cyber_diminuta": ("Consolas", 11, False),
}


def iniciar():
    """Inicializa pygame, abre la ventana y carga las fuentes."""
    
    global pantalla, reloj

    if pantalla is not None:
        return

    init()
    
    font.init()
    
    pantalla = display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    display.set_caption(TITULO_JUEGO)
    reloj = time.Clock()
    
    # Iniciar fuentes
    for clave, tamano in FUENTES_PIXEL.items():
        fuentes[clave] = font.Font(RUTA_FONTE, tamano)
        
    for clave, (familia, tamano, negrita) in FUENTES_SISTEMA.items():
        fuentes[clave] = font.SysFont(familia, tamano, bold=negrita)


def comprobar_iniciado():
    """Falla con un mensaje claro si se usa el juego antes de iniciar()."""
    if pantalla is None:
        raise RuntimeError("llama a simulador.iniciar() antes de usar el juego")


def fuente(clave):
    """Devuelve una fuente por clave"""
    comprobar_iniciado()
    
    if clave not in fuentes:
        raise KeyError(f"fuente desconocida: {clave!r}. Disponibles: {sorted(fuentes)}")
    
    return fuentes[clave]
