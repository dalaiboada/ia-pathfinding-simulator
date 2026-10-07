"""Tipos de terreno orientados a objetos.

Cada tipo encapsula sus datos fisicos: si se puede pasar, cuanto cuesta
recorrerlo, que intervalo tienen sus pisadas y que sonido suenan. La velocidad
no se guarda aparte: se deriva del costo (`factor_vel`), de modo que el costo que
alimenta a BFS/Dijkstra/A* es la unica fuente de verdad.

Modulo de datos puros, sin pygame, como config.py y paleta.py. El recorte del
tileset y la carga de sonidos los resuelve catalogo.py, que si importa pygame y
deja el sonido ya cargado en `Terreno.sonido`.
"""

from config import (
    COSTO_REFERENCIA,
    RUTA_AUDIO_PISADAS_HIERBA,
    RUTA_AUDIO_PISADAS_PAVIMENTO,
)


class Terreno:
    """Un tipo de celda del mapa.

    `costo` es None exactamente cuando el terreno es intransitable: un obstaculo
    no tiene precio porque no se puede recorrer. Los transitables lo tienen
    siempre positivo. `ruta_sonido` es la ruta del audio de pisadas; `sonido` es
    el objeto Sound ya cargado (o None si el audio no esta disponible).
    """

    def __init__(
        self,
        clave,
        nombre,
        transitable,
        costo,
        color,
        intervalo_pasos_ms=None,
        ruta_sonido=None,
    ):
        self.clave = clave
        self.nombre = nombre
        self.transitable = transitable
        self.costo = costo
        self.color = color
        self.intervalo_pasos_ms = intervalo_pasos_ms
        self.ruta_sonido = ruta_sonido
        self.sonido = None

    @property
    def factor_vel(self):
        """Factor de velocidad derivado del costo (1.0 en el terreno mas barato)."""
        if not self.transitable or not self.costo:
            return None
        return COSTO_REFERENCIA / self.costo

    def superficie(self, pygame_mod):
        """Superficie plana de respaldo, cuando no hay tile en el tileset."""
        capa = pygame_mod.Surface((32, 32))
        capa.fill(self.color)
        return capa

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.clave!r}, {self.nombre!r},"
            f" transitable={self.transitable}, costo={self.costo})"
        )


class TerrenoHierba(Terreno):
    """Hierba: pesada y con pisadas mas espaciadas."""

    def __init__(self, **alters):
        base = dict(
            clave="hierba",
            nombre="Hierba",
            transitable=True,
            costo=2.0,
            color=(124, 183, 66),
            intervalo_pasos_ms=500,
            ruta_sonido=RUTA_AUDIO_PISADAS_HIERBA,
        )
        base.update(alters)
        super().__init__(**base)


class TerrenoPavimento(Terreno):
    """Pavimento: terreno rapido y sonido seco de pisadas."""

    def __init__(self, **alters):
        base = dict(
            clave="pavimento",
            nombre="Pavimento",
            transitable=True,
            costo=1.0,
            color=(125, 135, 130),
            intervalo_pasos_ms=350,
            ruta_sonido=RUTA_AUDIO_PISADAS_PAVIMENTO,
        )
        base.update(alters)
        super().__init__(**base)


class TerrenoMuro(Terreno):
    """Obstaculo: no se puede recorrer, sin costo ni pisadas."""

    def __init__(self, **alters):
        base = dict(
            clave="muro",
            nombre="Muro",
            transitable=False,
            costo=None,
            color=(58, 34, 44),
            intervalo_pasos_ms=None,
            ruta_sonido=None,
        )
        base.update(alters)
        super().__init__(**base)


TIPOS_TERRENO = {
    "hierba": TerrenoHierba,
    "pavimento": TerrenoPavimento,
    "muro": TerrenoMuro,
}


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


def terreno_desde_json(datos):
    """Construye un terreno a partir de su bloque en el JSON del mapa.

    La clave elige la clase; los demas campos son opcionales y sobreescriben los
    valores por defecto de esa clase (por ejemplo, un costo distinto al original).
    """
    if not isinstance(datos, dict):
        raise ValueError(f"cada terreno debe ser un objeto, no {type(datos).__name__}")

    clave = datos.get("clave", datos.get("codigo"))
    if not isinstance(clave, str) or clave not in TIPOS_TERRENO:
        raise ValueError(
            f"la clave de terreno {clave!r} no es ninguna conocida: {sorted(TIPOS_TERRENO)}"
        )

    alters = {}
    if "nombre" in datos:
        alters["nombre"] = datos["nombre"]
    if "color" in datos:
        alters["color"] = _leer_color(datos["color"], clave)
    if "costo" in datos:
        alters["costo"] = datos["costo"]
    if "intervalo_pasos_ms" in datos:
        alters["intervalo_pasos_ms"] = datos["intervalo_pasos_ms"]
    if "sonido" in datos:
        alters["ruta_sonido"] = datos["sonido"]

    terreno = TIPOS_TERRENO[clave](**alters)
    _validar(terreno)
    return terreno


def _validar(terreno):
    if terreno.transitable:
        if terreno.costo is None or terreno.costo <= 0:
            raise ValueError(
                f"el terreno transitable {terreno.nombre!r} necesita un 'costo' mayor que cero"
            )
    elif terreno.costo is not None:
        raise ValueError(
            f"el terreno intransitable {terreno.nombre!r} declara un 'costo':"
            " dejalo en null, porque no se puede recorrer"
        )


def catalogo_por_defecto():
    """Los tres tipos del juego. El JSON puede ajustar costo y sonidos."""
    return {
        "hierba": TerrenoHierba(),
        "pavimento": TerrenoPavimento(),
        "muro": TerrenoMuro(),
    }


def cargar_catalogo(entradas):
    """Convierte la lista `terrenos` del JSON en un dict clave -> Terreno.

    Sin entradas devuelve el catalogo por defecto. Comprueba que no haya claves
    repetidas.
    """
    if not entradas:
        return catalogo_por_defecto()

    if not isinstance(entradas, list):
        raise ValueError("'terrenos' debe ser una lista de terrenos")

    catalogo = {}
    for datos in entradas:
        terreno = terreno_desde_json(datos)
        if terreno.clave in catalogo:
            raise ValueError(f"el terreno {terreno.clave!r} esta definido dos veces")
        catalogo[terreno.clave] = terreno

    if not catalogo:
        raise ValueError("'terrenos' esta vacio: el mapa no tendria celdas")

    return catalogo
