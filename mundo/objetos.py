"""Objetos colocables sobre el suelo: capa intermedia del mapa.

Cada objeto encapsula si bloquea el paso (`es_solido`), su imagen y, si procede,
una interaccion. El catalogo les asigna la imagen del tileset cuando el mapa la
define; si no, cada clase trae un dibujo procedural de respaldo.
"""

import os
from pygame import draw, Surface, SRCALPHA, image as pygame_image


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

    def __init__(self, imagen=None, es_solido=True):
        super().__init__("Cofre", es_solido=es_solido, imagen=imagen)

    def dibujo_respaldo(self, tamano_celda):
        """Cofre procedural, por si el tileset no trae su tile."""
        imagen = Surface((tamano_celda, tamano_celda), SRCALPHA)
        lado = max(6, tamano_celda // 3)
        draw.rect(imagen, (139, 69, 19), (2, lado, tamano_celda - 4, tamano_celda - lado - 2), border_radius=3)
        draw.rect(imagen, (255, 215, 0), (tamano_celda // 2 - 3, lado + 2, 6, 6))
        return imagen

    def interactuar(self):
        print("¡Has abierto el cofre!")


class ObjetoAnimado(ObjetoMapa):
    """Objeto estático con animación basada en spritesheet."""

    def __init__(self, ruta_spritesheet, columnas=6, filas=3, velocidad=0.15, es_solido=True, imagen=None):
        super().__init__("ObjetoAnimado", es_solido=es_solido, imagen=imagen)
        self.ruta_spritesheet = ruta_spritesheet
        self.columnas = columnas
        self.filas = filas
        self.velocidad = velocidad
        self.cuadros = []
        self.indice_frame = 0.0
        self.total_frames = columnas * filas
        self._cargar_spritesheet()

    def _cargar_spritesheet(self):
        """Carga y recorta el spritesheet en cuadros individuales."""
        try:
            spritesheet = pygame_image.load(self.ruta_spritesheet).convert_alpha()
            ancho_sheet, alto_sheet = spritesheet.get_size()
            ancho_frame = ancho_sheet // self.columnas
            alto_frame = alto_sheet // self.filas

            for fila in range(self.filas):
                for col in range(self.columnas):
                    rect_recorte = (
                        col * ancho_frame,
                        fila * alto_frame,
                        ancho_frame,
                        alto_frame
                    )
                    frame = spritesheet.subsurface(rect_recorte).copy()
                    self.cuadros.append(frame)
        except Exception:
            self.cuadros = []

    def actualizar(self):
        """Actualiza el frame de animación."""
        if not self.cuadros:
            return
        self.indice_frame += self.velocidad
        if self.indice_frame >= self.total_frames:
            self.indice_frame = 0.0
        self.imagen = self.cuadros[int(self.indice_frame)]

    def dibujo_respaldo(self, tamano_celda):
        """Dibujo procedural por si falla la carga del spritesheet."""
        imagen = Surface((tamano_celda, tamano_celda), SRCALPHA)
        draw.rect(imagen, (34, 139, 34), (2, 2, tamano_celda - 4, tamano_celda - 4), border_radius=4)
        return imagen


class ObjetoArbol(ObjetoAnimado):
    """Árbol animado (sólido) para el mapa."""

    def __init__(self, ruta_spritesheet=None, es_solido=True, imagen=None):
        super().__init__(
            ruta_spritesheet=ruta_spritesheet,
            columnas=6,
            filas=3,
            velocidad=0.15,
            es_solido=es_solido,
            imagen=imagen
        )
        self.nombre = "Árbol animado"


TIPOS_OBJETO = {
    "cofre": ObjetoCofre,
    "arbol_animado": ObjetoArbol,
}


def objeto_desde_json(datos, tamano_celda, ruta_tileset=None, carpeta_mapa=None):
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

    # Parámetros específicos para objetos animados
    kwargs = {"imagen": imagen}
    if "solido" in datos:
        kwargs["es_solido"] = bool(datos["solido"])

    # Para objetos animados, procesar la ruta del spritesheet
    if tipo == "arbol_animado":
        ruta_spritesheet = datos.get("spritesheet")
        if ruta_spritesheet and carpeta_mapa:
            # Si es una ruta relativa, resolverla contra la carpeta del mapa
            if not os.path.isabs(ruta_spritesheet):
                ruta_spritesheet = os.path.join(carpeta_mapa, ruta_spritesheet)
        kwargs["ruta_spritesheet"] = ruta_spritesheet

    objeto = TIPOS_OBJETO[tipo](**kwargs)

    if objeto.imagen is None and not hasattr(objeto, "cuadros"):
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
