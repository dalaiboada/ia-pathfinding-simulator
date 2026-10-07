"""Catalogo central: tileset, sonidos e instancias de terrenos y objetos.

Carga una sola vez la hoja de tiles y los audios, y traduce los IDs numericos de
las matrices del mapa a su representacion visual y a su clase fisica. Es el
equivalente a la clase Catalogo del ejemplo de logica_de_mapa, integrado en el
juego real.
"""

from pygame import Surface, image, transform

from config import (
    OBJETO_NINGUNO,
    RUTA_TILESET,
    VOLUMEN_PISADAS,
)
from .objetos import objeto_desde_json
from .terreno import cargar_catalogo, catalogo_por_defecto

# IDs por defecto: reproducen el mapeo del ejemplo (bases, bordes y esquinas de
# pavimento) usando las coordenadas documentadas del tileset.
TILES_POR_DEFECTO = [
    {"id": 0, "terreno": "hierba", "col": 0, "fila": 0},
    {"id": 1, "terreno": "pavimento", "col": 6, "fila": 3},
    {"id": 2, "terreno": "pavimento", "col": 6, "fila": 4},
    {"id": 3, "terreno": "pavimento", "col": 6, "fila": 4, "giro": 180},
    {"id": 4, "terreno": "pavimento", "col": 6, "fila": 4, "giro": -90},
    {"id": 5, "terreno": "pavimento", "col": 6, "fila": 4, "giro": 90},
    {"id": 6, "terreno": "pavimento", "col": 4, "fila": 4},
    {"id": 7, "terreno": "pavimento", "col": 5, "fila": 4},
    {"id": 8, "terreno": "pavimento", "col": 4, "fila": 5},
    {"id": 9, "terreno": "pavimento", "col": 5, "fila": 5},
    {"id": 100, "terreno": "muro"},
]
OBJETOS_POR_DEFECTO = [
    {"id": 101, "tipo": "cofre"},
]

# Etiquetas legibles de las esquinas/bordes, para la paleta del editor.
VARIANTES_PAVIMENTO = {
    1: "Centro",
    2: "Borde ↑",
    3: "Borde ↓",
    4: "Borde →",
    5: "Borde ←",
    6: "Esquina ↖",
    7: "Esquina ↗",
    8: "Esquina ↙",
    9: "Esquina ↘",
}


def _cargar_sonido(ruta, volumen):
    """Carga un audio sin romper el juego si no hay mixer o falta el archivo."""
    if not ruta:
        return None
    try:
        from pygame import mixer
        sonido = mixer.Sound(ruta)
        sonido.set_volume(volumen)
        return sonido
    except Exception:
        return None


class Catalogo:
    """Instancias de terrenos y objetos, indexadas por clave y por ID."""

    def __init__(self, terrenos, tiles, objetos, ruta_tileset=RUTA_TILESET, tamano_celda=32, carpeta_base=None):
        self.tamano_celda = tamano_celda
        self.ruta_tileset = ruta_tileset
        self.tileset = self._cargar_tileset()
        self.carpeta_base = carpeta_base

        self.terrenos = terrenos
        for terreno in self.terrenos.values():
            terreno.sonido = _cargar_sonido(terreno.ruta_sonido, VOLUMEN_PISADAS)

        self.tiles = {}
        self.terreno_por_id = {}
        self.id_base_por_terreno = {}
        for definicion in tiles:
            id_tile = int(definicion["id"])
            clave = definicion["terreno"]
            if clave not in self.terrenos:
                raise ValueError(f"el tile {id_tile} usa el terreno {clave!r}, que no esta definido")
            if id_tile in self.tiles:
                raise ValueError(f"el id de tile {id_tile} esta definido dos veces")
            self.terreno_por_id[id_tile] = self.terrenos[clave]
            self.tiles[id_tile] = self._cortar_tile(definicion)
            self.id_base_por_terreno.setdefault(clave, id_tile)

        self.objetos = {}
        for definicion in objetos:
            id_objeto = int(definicion["id"])
            if id_objeto == OBJETO_NINGUNO:
                raise ValueError(f"el id {OBJETO_NINGUNO} esta reservado para 'sin objeto'")
            if id_objeto in self.objetos:
                raise ValueError(f"el id de objeto {id_objeto} esta definido dos veces")
            definicion = dict(definicion)
            definicion.setdefault("tile", None)
            self.objetos[id_objeto] = objeto_desde_json(definicion, tamano_celda, ruta_tileset, carpeta_base)

        self.id_defecto = self.id_base_por_terreno.get("hierba")
        if self.id_defecto is None:
            self.id_defecto = next(iter(self.tiles)) if self.tiles else OBJETO_NINGUNO

    # ------------------------------------------------------------- construccion

    @classmethod
    def por_defecto(cls, tamano_celda=32, carpeta_base=None):
        return cls(
            terrenos=catalogo_por_defecto(),
            tiles=TILES_POR_DEFECTO,
            objetos=OBJETOS_POR_DEFECTO,
            tamano_celda=tamano_celda,
            carpeta_base=carpeta_base,
        )

    @classmethod
    def desde_json(cls, datos, carpeta_base, tamano_celda=32):
        import os

        ruta_tileset = datos.get("tileset")
        if ruta_tileset:
            ruta_tileset = os.path.join(carpeta_base, ruta_tileset.replace("\\", "/"))
        else:
            ruta_tileset = RUTA_TILESET

        terrenos = cargar_catalogo(datos.get("terrenos"))
        for terreno in terrenos.values():
            if terreno.ruta_sonido and not os.path.isabs(terreno.ruta_sonido):
                terreno.ruta_sonido = os.path.join(
                    carpeta_base, terreno.ruta_sonido.replace("\\", "/")
                )

        return cls(
            terrenos=terrenos,
            tiles=datos.get("tiles") or TILES_POR_DEFECTO,
            objetos=datos.get("objetos") or [],
            ruta_tileset=ruta_tileset,
            tamano_celda=tamano_celda,
            carpeta_base=carpeta_base,
        )

    def _cargar_tileset(self):
        try:
            return image.load(self.ruta_tileset).convert_alpha()
        except Exception:
            return None

    def _cortar_tile(self, definicion):
        if "col" not in definicion or "fila" not in definicion:
            return None
        if self.tileset is None:
            return None

        paso = self.tamano_celda
        col = int(definicion["col"])
        fila = int(definicion["fila"])
        try:
            recorte = self.tileset.subsurface((col * paso, fila * paso, paso, paso)).copy()
        except ValueError:
            return None

        giro = int(definicion.get("giro", 0))
        if giro:
            recorte = transform.rotate(recorte, giro)
        return recorte

    # ------------------------------------------------------------------ consulta

    def tile(self, id_tile):
        """Superficie de un tile, o None para que el mapa use el color del terreno."""
        return self.tiles.get(id_tile)

    def terreno(self, id_tile):
        return self.terreno_por_id.get(id_tile)

    def objeto(self, id_objeto):
        return self.objetos.get(id_objeto)

    def id_base_de(self, clave):
        """ID de tile que representa el centro/base de un terreno."""
        return self.id_base_por_terreno.get(clave)

    def etiqueta_tile(self, id_tile):
        if id_tile in VARIANTES_PAVIMENTO:
            return VARIANTES_PAVIMENTO[id_tile]
        terreno = self.terreno(id_tile)
        return terreno.nombre if terreno else str(id_tile)

    def clave_muro(self):
        for clave, terreno in self.terrenos.items():
            if not terreno.transitable:
                return clave
        return None

    def clave_mas_rapida(self):
        transitables = [t for t in self.terrenos.values() if t.transitable and t.costo]
        if not transitables:
            return None
        return min(transitables, key=lambda t: t.costo).clave

    def color_tile(self, id_tile):
        """Superficie plana de un tile, usando el color de su terreno."""
        terreno = self.terreno(id_tile)
        capa = Surface((self.tamano_celda, self.tamano_celda))
        capa.fill(terreno.color if terreno else (0, 0, 0))
        return capa
