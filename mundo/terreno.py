"""Tipos de terreno: color, textura, si se puede pasar y cuanto cuesta pasar.

Modulo de datos puros, sin pygame, como config.py y paleta.py. El recorte y el
escalado de la textura los resuelve mapa_terreno.py, que si importa pygame.
"""

import os


class TipoTerreno:
    """Un tipo de celda del mapa.

    `costo` es None exactamente cuando el terreno es intransitable: un obstaculo
    no tiene precio porque no se puede recorrer. Los transitable lo tienen siempre
    positivo.
    """

    def __init__(self, clave, nombre, transitable, costo, color, textura=None):
        self.clave = clave
        self.nombre = nombre
        self.transitable = transitable
        self.costo = costo
        self.color = color
        self.textura = textura

    @classmethod
    def desde_json(cls, datos, carpeta_base):
        """Construye un tipo a partir de su bloque en el JSON del mapa."""
        if not isinstance(datos, dict):
            raise ValueError(f"cada terreno debe ser un objeto, no {type(datos).__name__}")

        clave = datos.get("codigo")
        if not isinstance(clave, str) or len(clave) != 1:
            raise ValueError(f"el terreno necesita un 'codigo' de un solo caracter, recibido: {clave!r}")

        nombre = datos.get("nombre", clave)
        if not isinstance(nombre, str) or not nombre:
            raise ValueError(f"el terreno {clave!r} necesita un 'nombre' de texto")

        transitable = bool(datos.get("transitable", True))
        if transitable:
            costo = datos.get("costo", 1.0)
            if costo is None or costo <= 0:
                raise ValueError(f"el terreno transitable {nombre!r} necesita un 'costo' mayor que cero")
        else:
            if datos.get("costo") is not None:
                raise ValueError(
                    f"el terreno intransitable {nombre!r} declara un 'costo':"
                    " dejalo en null, porque no se puede recorrer"
                )
            costo = None

        color = _leer_color(datos.get("color"), clave)

        textura = datos.get("textura")
        if textura is not None:
            if not isinstance(textura, str) or not textura:
                raise ValueError(f"la 'textura' del terreno {nombre!r} debe ser una ruta de texto o null")
            textura = os.path.join(carpeta_base, textura.replace("\\", "/"))

        return cls(clave, nombre, transitable, costo, color, textura)

    def __repr__(self):
        return f"TipoTerreno({self.clave!r}, {self.nombre!r}, transitable={self.transitable}, costo={self.costo})"


def _leer_color(color, clave):
    if color is None:
        raise ValueError(f"el terreno {clave!r} necesita un 'color' de tres componentes")
    if not isinstance(color, (list, tuple)) or len(color) != 3:
        raise ValueError(f"el 'color' del terreno {clave!r} debe ser una lista de tres numeros")
    try:
        componentes = [int(c) for c in color]
    except (TypeError, ValueError):
        raise ValueError(f"el 'color' del terreno {clave!r} tiene componentes no numericos: {color!r}") from None
    for componente in componentes:
        if not 0 <= componente <= 255:
            raise ValueError(f"el 'color' del terreno {clave!r} tiene un componente fuera de 0..255: {color!r}")
    return tuple(componentes)


def catalogo_por_defecto():
    """Los tres tipos del enunciado. Los costos son editables desde el JSON."""
    return {
        "p": TipoTerreno("p", "Pavimento", True, 1.0, (148, 150, 158)),
        "t": TipoTerreno("t", "Tierra", True, 2.0, (122, 92, 63)),
        "#": TipoTerreno("#", "Obstáculo", False, None, (58, 34, 44)),
    }


def cargar_catalogo(entradas, carpeta_base):
    """Convierte la lista `terrenos` del JSON en un dict clave -> TipoTerreno.

    Sin entradas devuelve el catalogo por defecto. Comprueba que no haya claves
    repetidas y que toda textura declarada exista en disco.
    """
    if not entradas:
        return catalogo_por_defecto()

    if not isinstance(entradas, list):
        raise ValueError("'terrenos' debe ser una lista de terrenos")

    catalogo = {}
    for datos in entradas:
        tipo = TipoTerreno.desde_json(datos, carpeta_base)
        if tipo.clave in catalogo:
            raise ValueError(f"el terreno {tipo.clave!r} esta definido dos veces")
        if tipo.textura and not os.path.isfile(tipo.textura):
            raise FileNotFoundError(
                f"el terreno {tipo.nombre!r} declara la textura {tipo.textura!r}, que no existe",
            )
        catalogo[tipo.clave] = tipo

    if not catalogo:
        raise ValueError("'terrenos' esta vacio: el mapa no tendria celdas")

    return catalogo
