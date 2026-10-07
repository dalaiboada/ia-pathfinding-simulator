"""Musica de fondo por vista: un tema en el menu y otro en las vistas de mapa.

El reproductor recuerda el tema vigente para no reiniciar una pista que ya suena,
y no rompe si el mixer no esta disponible ni si falta el archivo.
"""

from pygame import mixer

from config import (
    RUTA_TEMA_MENU,
    RUTA_TEMA_VISTAS,
    VOLUMEN_TEMA_MENU,
    VOLUMEN_TEMA_VISTAS,
)

# Ruta del tema que esta sonando ahora mismo, o None si no hay ninguno
_TEMA_ACTUAL = None


def _reproducir(ruta, volumen):
    global _TEMA_ACTUAL
    if not mixer.get_init() or not ruta:
        return
    if _TEMA_ACTUAL == ruta:
        return

    try:
        mixer.music.stop()
        mixer.music.load(ruta)
        mixer.music.set_volume(volumen)
        mixer.music.play(-1)
        _TEMA_ACTUAL = ruta
    except Exception:
        # Sin mixer, archivo faltante o formato no soportado: silencio
        _TEMA_ACTUAL = None


def iniciar_tema(nombre_vista):
    """Pone el tema de la vista (el menu tiene el suyo, el resto uno comun)."""
    if nombre_vista == "menu":
        _reproducir(RUTA_TEMA_MENU, VOLUMEN_TEMA_MENU)
    else:
        _reproducir(RUTA_TEMA_VISTAS, VOLUMEN_TEMA_VISTAS)


def detener():
    global _TEMA_ACTUAL
    if mixer.get_init():
        try:
            mixer.music.stop()
        except Exception:
            pass
    _TEMA_ACTUAL = None