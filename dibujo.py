"""Helpers de dibujo compartidos."""

from pygame import *

from arranque import fuente
from config import ANCHO_VENTANA
from paleta import (
    CIAN_BRILLANTE,
    CIAN_OSCURO,
    COLOR_FONDO_PANEL,
    COLOR_FONDO_TARJETA,
    COLOR_REJILLA,
    TEXTO_BLANCO,
    TEXTO_SECUNDARIO,
)

def crear_velo(ancho, alto, color, alfa_maximo=200):
    """Degradado vertical que oscurece el fondo del menu."""
    
    velo = Surface((ancho, alto), SRCALPHA)
    
    for y in range(alto):
        factor = 1.0 - (y / max(alto - 1, 1)) * 0.6
        velo.fill(color + (int(alfa_maximo * factor),), (0, y, ancho, 1))
    
    return velo


def dibujar_rejilla_fondo(superficie, area, color=COLOR_REJILLA, tamano_celda=32):
    """Cuadricula tenue de fondo (estadisticas.py)."""
   
    for x in range(area.left, area.right, tamano_celda):
        draw.line(superficie, color, (x, area.top), (x, area.bottom), 1)
        
    for y in range(area.top, area.bottom, tamano_celda):
        draw.line(superficie, color, (area.left, y), (area.right, y), 1)


def dibujar_tarjeta_cyber(superficie, x, y, ancho, alto, titulo, valor, unidad=""):
    """Tarjeta con detalles de neon"""
    
    rect_tarjeta = Rect(x, y, ancho, alto)

    draw.rect(superficie, COLOR_FONDO_TARJETA, rect_tarjeta, border_radius=6)
    draw.rect(superficie, CIAN_OSCURO, rect_tarjeta, 1, border_radius=6)
    draw.line(superficie, CIAN_BRILLANTE, (x, y), (x + 25, y), 2)
    draw.line(superficie, CIAN_BRILLANTE, (x, y), (x, y + 25), 2)

    superficie.blit(
        fuente("cyber_etiqueta").render(titulo.upper(), True, TEXTO_SECUNDARIO),
        (x + 15, y + 10),
    )
    superficie.blit(
        fuente("cyber_valor").render(f"{valor} {unidad}".strip(), True, CIAN_BRILLANTE),
        (x + 15, y + 32),
    )


def dibujar_texto_centrado(superficie, texto, fuente_obj, color, centro):
    """Dibuja texto centrado en la posición indicada"""
    
    sup_texto = fuente_obj.render(texto, True, color)
    superficie.blit(sup_texto, sup_texto.get_rect(center=centro))


def dibujar_banda_hud(superficie, alto_hud, titulo, lineas_pista, ancho_hud=None):
    """Franja superior común: título a la izquierda y pistas debajo"""
    
    ancho = ancho_hud if ancho_hud is not None else ANCHO_VENTANA
    area = Rect(0, 0, ancho, alto_hud)

    draw.rect(superficie, COLOR_FONDO_PANEL, area)
    draw.line(superficie, CIAN_BRILLANTE, (0, area.bottom), (ancho, area.bottom), 1)
    draw.line(superficie, CIAN_OSCURO, (0, 0), (ancho, 0), 1)

    superficie.blit(fuente("hud").render(titulo, True, CIAN_BRILLANTE), (20, 18))

    y_actual = 54
    for linea in lineas_pista:
        superficie.blit(fuente("instrucciones").render(linea, True, TEXTO_SECUNDARIO), (20, y_actual))
        y_actual += 26
