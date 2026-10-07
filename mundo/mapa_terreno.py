"""Rejilla de terreno: carga desde JSON, dibujo y resolucion de movimiento.

El terreno se guarda como clave de texto por celda, y las superposiciones de la
busqueda en una matriz aparte. Asi el camino solucionado puede discurrir por
pavimento o por tierra sin que ambas cosas se pisen.
"""

import json
import os

from pygame import *

from config import (
    MARCA_CAMINO,
    MARCA_NINGUNA,
    MARCA_VISITADA,
    TAM_CELDA,
)
from paleta import (
    CIAN_BRILLANTE,
    CIAN_RESPLANDOR,
    COLOR_FONDO_MAPA,
    COLOR_INICIO,
    COLOR_LINEA,
    COLOR_MARCA_CAMINO,
    COLOR_MARCA_VISITADA,
    COLOR_META,
)
from .terreno import catalogo_por_defecto, cargar_catalogo

# Alfa con el que se pinta cada superposicion sobre el terreno
ALFA_MARCA_CAMINO = 205
ALFA_MARCA_VISITADA = 115
ALFA_REALCE = 55

NOMBRE_CAPAS_POR_DEFECTO = ("terreno", "terrenos", "suelo")


class MapaTerreno:
    """Rejilla de celdas de terreno con consulta de costo y colision."""

    def __init__(
        self,
        columnas,
        filas,
        tamano_celda=TAM_CELDA,
        origen_x=0,
        origen_y=0,
        terreno_defecto="t",
    ):
        if columnas < 1 or filas < 1:
            raise ValueError("el mapa necesita al menos una celda")

        self.columnas = columnas
        self.filas = filas
        self.tamano_celda = tamano_celda
        self.origen_x = origen_x
        self.origen_y = origen_y
        self.ancho_util = columnas * tamano_celda
        self.alto_util = filas * tamano_celda

        self.nombre = "mapa"
        self.catalogo = catalogo_por_defecto()
        self.terreno_defecto = terreno_defecto

        self.celdas = [[terreno_defecto] * columnas for _ in range(filas)]
        self.marcas = [[MARCA_NINGUNA] * columnas for _ in range(filas)]
        self.inicio = None
        self.meta = None

        self.mostrar_rejilla = True
        self.hover = None

        self._imagenes = {}
        self._imagenes_marca = {}
        self.capa_terreno = Surface((self.ancho_util, self.alto_util))
        self.capa_rejilla = Surface((self.ancho_util, self.alto_util), SRCALPHA)
        self.preparar_capa()

    # ------------------------------------------------------------- geometria

    def area(self):
        return Rect(self.origen_x, self.origen_y, self.ancho_util, self.alto_util)

    def rect_celda(self, fila, col):
        return Rect(
            self.origen_x + col * self.tamano_celda,
            self.origen_y + fila * self.tamano_celda,
            self.tamano_celda,
            self.tamano_celda,
        )

    def celda_por_pos(self, posicion):
        if posicion[0] < self.origen_x or posicion[1] < self.origen_y:
            return None
        col = (posicion[0] - self.origen_x) // self.tamano_celda
        fila = (posicion[1] - self.origen_y) // self.tamano_celda
        if 0 <= col < self.columnas and 0 <= fila < self.filas:
            return (fila, col)
        return None

    def centro_celda(self, fila, col):
        rect = self.rect_celda(fila, col)
        return rect.center

    def _dentro(self, fila, col):
        return 0 <= fila < self.filas and 0 <= col < self.columnas

    # ------------------------------------------------------- consultas terreno

    def terreno_en(self, fila, col):
        if not self._dentro(fila, col):
            return None
        return self.catalogo.get(self.celdas[fila][col])

    def terreno_bajo(self, posicion):
        celda = self.celda_por_pos(posicion)
        if celda is None:
            return None
        return self.terreno_en(celda[0], celda[1])

    def transitable(self, fila, col):
        tipo = self.terreno_en(fila, col)
        return bool(tipo is not None and tipo.transitable)

    def costo_en(self, fila, col):
        """Costo de recorrer la celda; 0.0 si es obstaculo, para no proteger el None."""
        tipo = self.terreno_en(fila, col)
        if tipo is None or not tipo.transitable or tipo.costo is None:
            return 0.0
        return float(tipo.costo)

    def costo_bajo(self, posicion):
        """Costo bajo un punto, o None si no hay celda transitable ahi."""
        tipo = self.terreno_bajo(posicion)
        if tipo is None or not tipo.transitable or tipo.costo is None:
            return None
        return float(tipo.costo)

    def terreno_mas_barato(self):
        """Tipo transitable de menor costo; el mas rapido para mover entidades."""
        transitable = [t for t in self.catalogo.values() if t.transitable and t.costo]
        if not transitable:
            return None
        return min(transitable, key=lambda t: t.costo)

    def clave_obstaculo(self):
        """Clave del tipo intransitable, o None si el catalogo no tiene ninguno."""
        for clave, tipo in self.catalogo.items():
            if not tipo.transitable:
                return clave
        return None

    def terreno_heredado(self, clave_por_defecto=None):
        """Tipo que se restaura al borrar: el defecto, o el que indique la vista."""
        if clave_por_defecto is not None and clave_por_defecto in self.catalogo:
            return clave_por_defecto
        if self.terreno_defecto in self.catalogo:
            return self.terreno_defecto
        return next(iter(self.catalogo))

    # -------------------------------------------------------------- colisiones

    def superficie_libre(self, rect):
        """True si el rect cabe entero en el mapa y no toca ningun obstaculo."""
        if not self.area().colliderect(rect):
            return False

        celda_a = self.celda_por_pos(rect.topleft)
        celda_b = self.celda_por_pos((rect.right - 1, rect.bottom - 1))
        if celda_a is None or celda_b is None:
            return False

        fila_min = min(celda_a[0], celda_b[0])
        fila_max = max(celda_a[0], celda_b[0])
        col_min = min(celda_a[1], celda_b[1])
        col_max = max(celda_a[1], celda_b[1])

        for fila in range(fila_min, fila_max + 1):
            for col in range(col_min, col_max + 1):
                if not self.transitable(fila, col):
                    return False
        return True

    def desplazar(self, rect, desplazamiento_x, desplazamiento_y):
        """Cuanto de un desplazamiento se admite, resolviendo eje a eje.

        Primero se prueba el movimiento entero. Si choca, se prueban por separado
        los ejes X e Y y se suma lo que quede libre, de modo que el jugador
        siempre avanza por el eje que encuentra despejado.
        """
        if desplazamiento_x == 0 and desplazamiento_y == 0:
            return (0, 0)

        if self.superficie_libre(rect.move(desplazamiento_x, desplazamiento_y)):
            return (desplazamiento_x, desplazamiento_y)

        admite_x = (
            desplazamiento_x != 0
            and self.superficie_libre(rect.move(desplazamiento_x, 0))
        )
        admite_y = (
            desplazamiento_y != 0
            and self.superficie_libre(rect.move(0, desplazamiento_y))
        )

        if admite_x and admite_y:
            return (desplazamiento_x, desplazamiento_y)
        if admite_x:
            return (desplazamiento_x, 0)
        if admite_y:
            return (0, desplazamiento_y)
        return (0, 0)

    def punto_libre_cerca(self, centro, tamano):
        """Centro valido mas proximo a `centro` donde quepa un rect de `tamano`.

        Se usa cuando el jugador recibe un destino que cae sobre un obstaculo: en
        vez de quedarse empujando el muro, se recalcula un destino alcanzable.
        """
        objetivo = Rect(0, 0, tamano[0], tamano[1])
        objetivo.center = centro

        if self.superficie_libre(objetivo):
            return (centro[0], centro[1])

        paso = self.tamano_celda
        for radio in range(1, max(self.columnas, self.filas) + 1):
            for delta_fila in range(-radio, radio + 1):
                for delta_col in range(-radio, radio + 1):
                    if max(abs(delta_fila), abs(delta_col)) != radio:
                        continue
                    candidato = objetivo.move(delta_col * paso, delta_fila * paso)
                    if self.superficie_libre(candidato):
                        return candidato.center
        return None

    # ------------------------------------------------------------ carga JSON

    @classmethod
    def cargar_json(
        cls,
        ruta,
        columnas=None,
        filas=None,
        tamano_celda=None,
        origen_x=0,
        origen_y=0,
    ):
        """Lee un mapa de disco. Los parametros de la vista mandan sobre el JSON."""
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"no encuentro el mapa: {ruta}")

        with open(ruta, encoding="utf-8") as archivo:
            try:
                datos = json.load(archivo)
            except json.JSONDecodeError as error:
                raise ValueError(f"el JSON de {ruta} esta mal formado: {error}") from error

        if not isinstance(datos, dict):
            raise ValueError(f"el mapa de {ruta} debe ser un objeto con claves, no {type(datos).__name__}")

        carpeta = os.path.dirname(os.path.abspath(ruta))
        catalogo = cargar_catalogo(datos.get("terrenos"), carpeta)
        filas_datos = _buscar_capa_terreno(datos, ruta)

        if filas is None:
            filas = len(filas_datos)
        if columnas is None:
            columnas = max(len(f) for f in filas_datos)
        if tamano_celda is None:
            tamano_celda = int(datos.get("tamano_celda", TAM_CELDA))

        # Recortar en silencio dejaria un mapa con una forma distinta de la que
        # quiere la vista, asi que un mapa que no cabe es un error, no un recorte.
        if len(filas_datos) > filas or max(len(f) for f in filas_datos) > columnas:
            raise ValueError(
                f"el mapa de {ruta} es de {max(len(f) for f in filas_datos)} x"
                f" {len(filas_datos)} celdas y no cabe en {columnas} x {filas};"
                " la vista no recorta, ajusta 'tamano_celda' o el mapa"
            )

        mapa = cls(columnas, filas, tamano_celda, origen_x, origen_y)
        mapa.nombre = datos.get("nombre", os.path.splitext(os.path.basename(ruta))[0])
        mapa.catalogo = catalogo
        mapa.terreno_defecto = _elegir_terreno_defecto(catalogo)

        for numero_fila, fila in enumerate(filas_datos):
            for numero_col, caracter in enumerate(fila):
                if caracter not in catalogo:
                    raise ValueError(
                        f"el mapa {ruta} usa el caracter {caracter!r} en la fila {numero_fila},"
                        f" columna {numero_col}, que no es ningun terreno del catalogo",
                    )
                mapa.celdas[numero_fila][numero_col] = caracter

        if datos.get("inicio") is None:
            raise ValueError(
                f"el mapa de {ruta} necesita 'inicio' con {{\"fila\": n, \"col\": n}}"
                " para saber donde aparece el jugador"
            )
        mapa.colocar_desde_json(datos.get("inicio"), "inicio")
        mapa.colocar_desde_json(datos.get("meta"), "meta")
        mapa.preparar_capa()
        return mapa

    def colocar_desde_json(self, coordenada, que):
        """Fija `inicio` o `meta` desde el JSON, con errores claros."""
        if coordenada is None:
            return
        if not isinstance(coordenada, dict):
            raise ValueError(f"'{que}' debe ser un objeto con 'fila' y 'col', no {type(coordenada).__name__}")

        fila = coordenada.get("fila")
        col = coordenada.get("col")
        if not isinstance(fila, int) or not isinstance(col, int):
            raise ValueError(f"'{que}' necesita 'fila' y 'col' como numeros enteros, recibido: {coordenada!r}")
        if not self._dentro(fila, col):
            raise ValueError(
                f"'{que}' apunta a la celda ({fila}, {col}), fuera del mapa de"
                f" {self.filas} x {self.columnas}",
            )
        if not self.transitable(fila, col):
            raise ValueError(f"'{que}' apunta a la celda ({fila}, {col}), que es un obstaculo")

        setattr(self, que, (fila, col))

    # --------------------------------------------------------------- edicion

    def colocar_terreno(self, fila, col, clave):
        """Pinta un terreno. Claves desconocidas se ignoran."""
        if not self._dentro(fila, col) or clave not in self.catalogo:
            return False
        self.celdas[fila][col] = clave
        return True

    def limpiar_celda(self, fila, col):
        return self.colocar_terreno(fila, col, self.terreno_defecto)

    def colocar_inicio(self, fila, col):
        if not self._dentro(fila, col) or not self.transitable(fila, col):
            return False
        self._liberar_celda_anterior("inicio")
        self.inicio = (fila, col)
        return True

    def colocar_meta(self, fila, col):
        if not self._dentro(fila, col) or not self.transitable(fila, col):
            return False
        self._liberar_celda_anterior("meta")
        self.meta = (fila, col)
        return True

    def _liberar_celda_anterior(self, que):
        """Inicio y meta son unicos: al mover uno, su celda vuelve a terreno normal.

        Antes el sitio vacio era 'celda libre'; con los terrenos no hay un estado
        vacio, asi que la celda recupera el terreno por defecto del mapa.
        """
        anterior = getattr(self, que)
        if anterior is not None and self._dentro(*anterior):
            self.celdas[anterior[0]][anterior[1]] = self.terreno_defecto
        return anterior

    def limpiar(self):
        self.celdas = [[self.terreno_defecto] * self.columnas for _ in range(self.filas)]
        self.marcas = [[MARCA_NINGUNA] * self.columnas for _ in range(self.filas)]
        self.inicio = None
        self.meta = None
        self.hover = None
        self.preparar_capa()

    # ------------------------------------------------------------------ marcas

    # Esta capa no la coloca nadie todavia: es el enganche de la busqueda.
    # Un algoritmo marca mientras expande, dibuja el resultado y al terminar
    # llama a limpiar_marcas() antes de empezar otra vez.

    def marca_en(self, fila, col):
        """Superposicion de una celda; MARCA_NINGUNA si no hay celda ahi."""
        if not self._dentro(fila, col):
            return MARCA_NINGUNA
        return self.marcas[fila][col]

    def marcar(self, fila, col, marca=MARCA_VISITADA):
        """Pone una superposicion. Devuelve False si la celda no existe."""
        if not self._dentro(fila, col):
            return False
        self.marcas[fila][col] = marca
        return True

    def limpiar_marcas(self):
        self.marcas = [[MARCA_NINGUNA] * self.columnas for _ in range(self.filas)]

    def celdas_marcadas(self, marca):
        """Coordenadas con esa superposicion, para que el algoritmo las recorra."""
        return [
            (fila, col)
            for fila in range(self.filas)
            for col in range(self.columnas)
            if self.marcas[fila][col] == marca
        ]

    # ---------------------------------------------------------------- render

    def _imagen_terreno(self, tipo):
        """Textura escalada o color plano, cacheado por clave."""
        if tipo.clave in self._imagenes:
            return self._imagenes[tipo.clave]

        if tipo.textura:
            imagen = image.load(tipo.textura).convert_alpha()
            imagen = transform.scale(imagen, (self.tamano_celda, self.tamano_celda))
        else:
            imagen = Surface((self.tamano_celda, self.tamano_celda))
            imagen.fill(tipo.color)

        self._imagenes[tipo.clave] = imagen
        return imagen

    def _imagen_marca(self, marca):
        if marca in self._imagenes_marca:
            return self._imagenes_marca[marca]

        if marca == MARCA_CAMINO:
            color, alfa = COLOR_MARCA_CAMINO, ALFA_MARCA_CAMINO
        else:
            color, alfa = COLOR_MARCA_VISITADA, ALFA_MARCA_VISITADA

        capa = Surface((self.tamano_celda, self.tamano_celda), SRCALPHA)
        capa.fill(color + (alfa,))
        self._imagenes_marca[marca] = capa
        return capa

    def preparar_capa(self):
        """Pre-renderiza el terreno y la rejilla, para poder blitear de una vez."""
        self._imagenes = {}
        self.capa_terreno = Surface((self.ancho_util, self.alto_util))
        self.capa_terreno.fill(COLOR_FONDO_MAPA)

        for fila in range(self.filas):
            for col in range(self.columnas):
                self.capa_terreno.blit(
                    self._imagen_terreno(self.terreno_en(fila, col)),
                    (col * self.tamano_celda, fila * self.tamano_celda),
                )

        self.capa_rejilla = Surface((self.ancho_util, self.alto_util), SRCALPHA)
        for col in range(self.columnas + 1):
            x = col * self.tamano_celda
            draw.line(self.capa_rejilla, COLOR_LINEA, (x, 0), (x, self.alto_util))
        for fila in range(self.filas + 1):
            y = fila * self.tamano_celda
            draw.line(self.capa_rejilla, COLOR_LINEA, (0, y), (self.ancho_util, y))

    def dibujar_terreno(self, superficie):
        superficie.blit(self.capa_terreno, (self.origen_x, self.origen_y))

    def dibujar_rejilla(self, superficie):
        if self.mostrar_rejilla:
            superficie.blit(self.capa_rejilla, (self.origen_x, self.origen_y))

    def dibujar_marcas(self, superficie):
        for fila in range(self.filas):
            for col in range(self.columnas):
                marca = self.marcas[fila][col]
                if marca == MARCA_NINGUNA:
                    continue
                superficie.blit(
                    self._imagen_marca(marca),
                    (self.origen_x + col * self.tamano_celda,
                     self.origen_y + fila * self.tamano_celda),
                )

    def dibujar_hover(self, superficie):
        if self.hover is None:
            return
        fila, col = self.hover
        rect_hover = self.rect_celda(fila, col)

        if self.transitable(fila, col):
            realce = Surface((self.tamano_celda, self.tamano_celda), SRCALPHA)
            realce.fill(CIAN_RESPLANDOR + (ALFA_REALCE,))
            superficie.blit(realce, rect_hover.topleft)

        draw.rect(superficie, CIAN_BRILLANTE, rect_hover, 1)

    def dibujar_inicio_meta(self, superficie):
        """Anillos de inicio y meta, por encima del terreno pero bajo la rejilla."""
        for coordenada, color, radio in (
            (self.inicio, COLOR_INICIO, 0.38),
            (self.meta, COLOR_META, 0.30),
        ):
            if coordenada is None:
                continue
            rect = self.rect_celda(*coordenada)
            centro = rect.center
            diametro = int(self.tamano_celda * radio)
            draw.circle(superficie, color, centro, diametro, 2)
            # una cruz en el centro, para que se distinga de un obstaculo circular
            cruz = max(3, self.tamano_celda // 10)
            draw.line(superficie, color,
                      (centro[0] - cruz, centro[1]), (centro[0] + cruz, centro[1]), 2)
            draw.line(superficie, color,
                      (centro[0], centro[1] - cruz), (centro[0], centro[1] + cruz), 2)

    def dibujar(self, superficie):
        """El terreno completo, en el orden en que debe apilarse."""
        self.dibujar_terreno(superficie)
        self.dibujar_marcas(superficie)
        self.dibujar_inicio_meta(superficie)
        self.dibujar_rejilla(superficie)


def _buscar_capa_terreno(datos, ruta):
    capas = datos.get("capas")
    if capas is None:
        raise ValueError(f"el mapa de {ruta} no tiene 'capas'")
    if not isinstance(capas, list) or not capas:
        raise ValueError(f"'capas' de {ruta} debe ser una lista no vacia")

    for capa in capas:
        if isinstance(capa, dict) and str(capa.get("nombre", "")).lower() in NOMBRE_CAPAS_POR_DEFECTO:
            filas = capa.get("datos")
            break
    else:
        filas = None

    if filas is None:
        raise ValueError(
            f"el mapa de {ruta} no tiene capa de terreno;"
            f" se esperaba una llamada {NOMBRE_CAPAS_POR_DEFECTO[0]!r}",
        )
    if not isinstance(filas, list) or not filas:
        raise ValueError(f"la capa de terreno de {ruta} necesita 'datos' con al menos una fila")
    if not all(isinstance(f, str) for f in filas):
        raise ValueError(f"las filas de 'datos' de {ruta} deben ser cadenas de texto")

    anchos = {len(f) for f in filas}
    if len(anchos) != 1:
        raise ValueError(
            f"las filas de 'datos' de {ruta} miden distinto: {sorted(anchos)}",
        )
    return filas


def _elegir_terreno_defecto(catalogo):
    """Clave con la que se rellena lo que el JSON no define."""
    for clave in ("t", "pavimento", "suelo"):
        if clave in catalogo and catalogo[clave].transitable:
            return clave
    for clave, tipo in catalogo.items():
        if tipo.transitable:
            return clave
    raise ValueError("el catalogo de terrenos no tiene ningun tipo transitable que pueda servir de relleno")
