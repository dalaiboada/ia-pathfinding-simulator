"""Objetos colocables sobre el suelo: capa intermedia del mapa.

Cada objeto encapsula si bloquea el paso (`es_solido`), su imagen y, si procede,
una interaccion. El catalogo les asigna la imagen del tileset cuando el mapa la
define; si no, cada clase trae un dibujo procedural de respaldo.
"""

from pygame import draw, Surface, SRCALPHA


class ObjetoMapa:
    """Clase base de cualquier objeto estatico colocado en la rejilla."""

    def __init__(self, nombre, es_solido=True, imagen=None):
        self.nombre = nombre
        self.es_solido = es_solido
        self.imagen = imagen

    def interactuar(self):
        """Gancho para cuando el jugador interactua con el objeto."""
        pass

    def __repr__(self):
        return f"{type(self).__name__}({self.nombre!r}, es_solido={self.es_solido})"


class ObjetoCofre(ObjetoMapa):
    """Cofre interactivo y solido."""

    def __init__(self, imagen=None):
        super().__init__("Cofre", es_solido=True, imagen=imagen)

    def dibujo_respaldo(self, tamano_celda):
        """Cofre procedural, por si el tileset no trae su tile."""
        imagen = Surface((tamano_celda, tamano_celda), SRCALPHA)
        lado = max(6, tamano_celda // 3)
        draw.rect(imagen, (139, 69, 19), (2, lado, tamano_celda - 4, tamano_celda - lado - 2), border_radius=3)
        draw.rect(imagen, (255, 215, 0), (tamano_celda // 2 - 3, lado + 2, 6, 6))
        return imagen

    def interactuar(self):
        print("¡Has abierto el cofre!")


TIPOS_OBJETO = {
    "cofre": ObjetoCofre,
}


def objeto_desde_json(datos, tamano_celda, ruta_tileset=None):
    """Construye un objeto a partir de su bloque en el JSON del mapa."""
    if not isinstance(datos, dict):
        raise ValueError(f"cada objeto debe ser un objeto, no {type(datos).__name__}")

    tipo = datos.get("tipo")
    if tipo not in TIPOS_OBJETO:
        raise ValueError(f"el tipo de objeto {tipo!r} no es conocido: {sorted(TIPOS_OBJETO)}")

    imagen = None
    tile = datos.get("tile")
    if tile is not None:
        imagen = _recortar_tile(ruta_tileset, tile, tamano_celda)

    objeto = TIPOS_OBJETO[tipo](imagen=imagen)
    if "solido" in datos:
        objeto.es_solido = bool(datos["solido"])

    if objeto.imagen is None:
        objeto.imagen = objeto.dibujo_respaldo(tamano_celda) if hasattr(objeto, "dibujo_respaldo") else _vacio(tamano_celda)
    return objeto


def _recortar_tile(ruta_tileset, tile, tamano_celda):
    if ruta_tileset is None:
        return None
    if not isinstance(tile, (list, tuple)) or len(tile) != 2:
        raise ValueError(f"'tile' del objeto debe ser [columna, fila], recibido: {tile!r}")
    try:
        from pygame import image as _image
        hoja = _image.load(ruta_tileset).convert_alpha()
    except Exception:
        return None
    col, fila = int(tile[0]), int(tile[1])
    rect = (col * tamano_celda, fila * tamano_celda, tamano_celda, tamano_celda)
    try:
        return hoja.subsurface(rect).copy()
    except ValueError:
        return None


def _vacio(tamano_celda):
    return Surface((tamano_celda, tamano_celda), SRCALPHA)
