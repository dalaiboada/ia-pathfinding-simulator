"""Paleta cyberpunk
"""

def mezclar(color, fondo, alfa):
    """Pre-mecla un color con alfa sobre un fondo opaco (equivale a BLEND_RGBA)."""
    
    return (
        int(color[0] * alfa + fondo[0] * (1 - alfa)),
        int(color[1] * alfa + fondo[1] * (1 - alfa)),
        int(color[2] * alfa + fondo[2] * (1 - alfa)),
    )


# Fondos
COLOR_FONDO = (8, 12, 22)
COLOR_REJILLA = (14, 25, 45)
COLOR_FONDO_PANEL = (10, 18, 32)
COLOR_FONDO_TARJETA = (15, 28, 48)
COLOR_FONDO_MAPA = (10, 18, 34)
COLOR_FONDO_EXPLORACION = (16, 20, 28)
COLOR_BORDE = (46, 52, 66)
COLOR_PROYECTIL = (80, 220, 255)

# Acentos y texto
CIAN_BRILLANTE = (0, 240, 255)
CIAN_RESPLANDOR = (0, 160, 220)
CIAN_OSCURO = (0, 70, 110)
TEXTO_BLANCO = (230, 245, 255)
TEXTO_SECUNDARIO = (90, 140, 180)

# Colores de las superposiciones de la busqueda (se dibujan con alfa)
COLOR_MARCA_CAMINO = (241, 196, 15)
COLOR_MARCA_VISITADA = (52, 152, 219)

# Inicio y meta se distinguen tanto del cian de la interfaz como del oro del camino
COLOR_INICIO = (0, 240, 255)
COLOR_META = (255, 62, 154)

# Lineas de la rejilla
COLOR_LINEA = mezclar((255, 255, 255), COLOR_FONDO_MAPA, 45 / 255)
