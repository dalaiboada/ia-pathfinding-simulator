"""Rejilla de mapa: capas de suelo y objetos, colision y dibujo.

El mapa se organiza en tres capas, igual que en el ejemplo de logica_de_mapa:
  - `suelo`: matriz de IDs de tile (base, bordes y esquinas del tileset).
  - `objetos`: matriz de IDs de objeto estatico (cofres) o OBJETO_NINGUNO.
  - `entidades`: los sprites dinamicos, que dibuja cada vista por encima.

Las superposiciones de la busqueda van en una cuarta matriz aparte (`marcas`),
para que el camino solucionado no pise ni el suelo ni los objetos.
"""

import json
import os

from pygame import *

import busqueda
from config import (
    MARCA_CAMINO,
    MARCA_NINGUNA,
    MARCA_VISITADA,
    NOMBRE_CAPAS_OBJETOS,
    NOMBRE_CAPAS_SUELO,
    OBJETO_NINGUNO,
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
from .catalogo import Catalogo

# Alfa con el que se pinta cada superposicion sobre el terreno
ALFA_MARCA_CAMINO = 205
ALFA_MARCA_VISITADA = 115
ALFA_REALCE = 55

# Traduccion de un mapa de caracteres antiguo a claves de terreno
CLAVE_POR_CARACTER = {"p": "pavimento", "t": "hierba", "#": "muro"}


class MapaTerreno:
    """Rejilla con capas de suelo y objetos, consulta de costo y colision."""

    def __init__(
        self,
        columnas,
        filas,
        tamano_celda=TAM_CELDA,
        origen_x=0,
        origen_y=0,
        catalogo=None,
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
        self.catalogo = catalogo if catalogo is not None else Catalogo.por_defecto(tamano_celda)
        self.tile_defecto = self.catalogo.id_defecto

        self.suelo = [[self.tile_defecto] * columnas for _ in range(filas)]
        self.objetos = [[OBJETO_NINGUNO] * columnas for _ in range(filas)]
        self.marcas = [[MARCA_NINGUNA] * columnas for _ in range(filas)]
        self.inicio = None
        self.meta = None

        self.mostrar_rejilla = False
        self.hover = None

        self._imagenes = {}
        self._imagenes_marca = {}
        self.objetos_animados = []
        self.capa_suelo = Surface((self.ancho_util, self.alto_util))
        self.capa_objetos = Surface((self.ancho_util, self.alto_util), SRCALPHA)
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

    def id_suelo(self, fila, col):
        if not self._dentro(fila, col):
            return None
        return self.suelo[fila][col]

    def terreno_en(self, fila, col):
        if not self._dentro(fila, col):
            return None
        return self.catalogo.terreno(self.suelo[fila][col])

    def terreno_bajo(self, posicion):
        celda = self.celda_por_pos(posicion)
        if celda is None:
            return None
        return self.terreno_en(celda[0], celda[1])

    def transitable(self, fila, col):
        tipo = self.terreno_en(fila, col)
        return bool(tipo is not None and tipo.transitable)

    def objeto_id_en(self, fila, col):
        if not self._dentro(fila, col):
            return OBJETO_NINGUNO
        return self.objetos[fila][col]

    def objeto_en(self, fila, col):
        return self.catalogo.objeto(self.objeto_id_en(fila, col))

    def objeto_solido_en(self, fila, col):
        objeto = self.objeto_en(fila, col)
        return bool(objeto is not None and objeto.es_solido)

    def bloqueada(self, fila, col):
        """True si la celda no se puede pisar: suelo intransitable u objeto solido."""
        return not self.transitable(fila, col) or self.objeto_solido_en(fila, col)

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
        transitable = [t for t in self.catalogo.terrenos.values() if t.transitable and t.costo]
        if not transitable:
            return None
        return min(transitable, key=lambda t: t.costo)

    def clave_obstaculo(self):
        """Clave del tipo intransitable, o None si el catalogo no tiene ninguno."""
        return self.catalogo.clave_muro()

    # -------------------------------------------------------------- colisiones

    def superficie_libre(self, rect):
        """True si el rect cabe entero en el mapa y no toca suelo ni objeto solido."""
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
                if self.bloqueada(fila, col):
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

        if tamano_celda is None:
            tamano_celda = int(datos.get("tamano_celda", TAM_CELDA))

        carpeta = os.path.dirname(os.path.abspath(ruta))
        catalogo = Catalogo.desde_json(datos, carpeta, tamano_celda)
        filas_suelo = _buscar_capa(datos, ruta, NOMBRE_CAPAS_SUELO, obligatoria=True)
        filas_objetos = _buscar_capa(datos, ruta, NOMBRE_CAPAS_OBJETOS, obligatoria=False)

        if filas is None:
            filas = len(filas_suelo)
        if columnas is None:
            columnas = max(len(f) for f in filas_suelo)

        # Recortar en silencio dejaria un mapa con una forma distinta de la que
        # quiere la vista, asi que un mapa que no cabe es un error, no un recorte.
        if len(filas_suelo) > filas or max(len(f) for f in filas_suelo) > columnas:
            raise ValueError(
                f"el mapa de {ruta} es de {max(len(f) for f in filas_suelo)} x"
                f" {len(filas_suelo)} celdas y no cabe en {columnas} x {filas};"
                " la vista no recorta, ajusta 'tamano_celda' o el mapa"
            )

        mapa = cls(columnas, filas, tamano_celda, origen_x, origen_y, catalogo=catalogo)
        mapa.nombre = datos.get("nombre", os.path.splitext(os.path.basename(ruta))[0])

        for numero_fila, fila in enumerate(filas_suelo):
            for numero_col, valor in enumerate(_normalizar_suelo(fila, catalogo, ruta, numero_fila)):
                if valor not in catalogo.terreno_por_id:
                    raise ValueError(
                        f"el mapa {ruta} usa el tile {valor!r} en la fila {numero_fila},"
                        f" columna {numero_col}, que no esta en la lista de tiles"
                    )
                mapa.suelo[numero_fila][numero_col] = valor

        if filas_objetos is not None:
            for numero_fila, fila in enumerate(filas_objetos[:mapa.filas]):
                for numero_col, valor in enumerate(fila[:mapa.columnas]):
                    valor = int(valor or OBJETO_NINGUNO)
                    if valor == OBJETO_NINGUNO:
                        continue
                    if valor not in catalogo.objetos:
                        raise ValueError(
                            f"el mapa {ruta} usa el objeto {valor!r} en la fila"
                            f" {numero_fila}, columna {numero_col}, que no esta en la lista"
                        )
                    mapa.objetos[numero_fila][numero_col] = valor

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
        if self.bloqueada(fila, col):
            raise ValueError(f"'{que}' apunta a la celda ({fila}, {col}), que esta bloqueada")

        setattr(self, que, (fila, col))

    # --------------------------------------------------------------- edicion

    def colocar_terreno(self, fila, col, id_tile):
        """Pinta un tile de suelo. IDs desconocidos se ignoran."""
        if not self._dentro(fila, col):
            return False
        if id_tile not in self.catalogo.terreno_por_id:
            return False
        self.suelo[fila][col] = id_tile
        return True

    def colocar_terreno_clave(self, fila, col, clave):
        """Pinta el tile base de una clave de terreno."""
        id_tile = self.catalogo.id_base_de(clave)
        if id_tile is None:
            return False
        return self.colocar_terreno(fila, col, id_tile)

    def colocar_objeto(self, fila, col, id_objeto):
        if not self._dentro(fila, col) or not self.transitable(fila, col):
            return False
        if id_objeto not in self.catalogo.objetos:
            return False
        self.objetos[fila][col] = id_objeto
        return True

    def quitar_objeto(self, fila, col):
        if not self._dentro(fila, col) or self.objetos[fila][col] == OBJETO_NINGUNO:
            return False
        self.objetos[fila][col] = OBJETO_NINGUNO
        return True

    def limpiar_celda(self, fila, col):
        return self.colocar_terreno(fila, col, self.tile_defecto)

    def colocar_inicio(self, fila, col):
        if not self._dentro(fila, col) or self.bloqueada(fila, col):
            return False
        self._liberar_celda_anterior("inicio")
        self.inicio = (fila, col)
        return True

    def colocar_meta(self, fila, col):
        if not self._dentro(fila, col) or self.bloqueada(fila, col):
            return False
        self._liberar_celda_anterior("meta")
        self.meta = (fila, col)
        return True

    def _liberar_celda_anterior(self, que):
        """Inicio y meta son unicos: al mover uno, su celda recupera el suelo normal."""
        anterior = getattr(self, que)
        if anterior is not None and self._dentro(*anterior):
            self.suelo[anterior[0]][anterior[1]] = self.tile_defecto
        return anterior

    def limpiar(self):
        self.suelo = [[self.tile_defecto] * self.columnas for _ in range(self.filas)]
        self.objetos = [[OBJETO_NINGUNO] * self.columnas for _ in range(self.filas)]
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

    # -------------------------------------------------------------- busqueda

    def rejilla_para(self, tamano):
        """Rejilla de busqueda adaptada al tamano (en px) de una entidad.

        Una celda se considera bloqueada si el rect de la entidad centrado en
        ella no cabe sin tocar suelo intransitable ni objeto solido. Asi la ruta
        que devuelve el algoritmo es pisable por ese sprite y no solo por una
        celda abstracta.
        """
        return RejillaEntidad(self, tamano)

    def buscar_camino(self, inicio, meta, algoritmo, rejilla=None):
        """Ejecuta un algoritmo y pinta visitados y camino en la capa de marcas.

        Devuelve el ResultadoBusqueda. Si `rejilla` es None se usa el mapa tal
        cual (entidad de una celda); para sprites mayores pásale
        `rejilla_para(tamano)`.
        """
        if rejilla is None:
            rejilla = self
        resultado = busqueda.buscar(algoritmo, rejilla, inicio, meta)

        self.limpiar_marcas()
        for fila, col in resultado.visitados:
            self.marcar(fila, col, MARCA_VISITADA)
        for fila, col in resultado.camino:
            self.marcar(fila, col, MARCA_CAMINO)
        return resultado

    # ---------------------------------------------------------------- render

    def _imagen_tile(self, id_tile):
        """Textura del tileset o color plano, cacheada por ID."""
        if id_tile in self._imagenes:
            return self._imagenes[id_tile]

        imagen = self.catalogo.tile(id_tile)
        if imagen is None:
            imagen = self.catalogo.color_tile(id_tile)
        elif imagen.get_size() != (self.tamano_celda, self.tamano_celda):
            imagen = transform.scale(imagen, (self.tamano_celda, self.tamano_celda))

        self._imagenes[id_tile] = imagen
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
        """Pre-renderiza suelo y objetos, para poder blitear de una vez."""
        self._imagenes = {}
        self.objetos_animados = []
        self.capa_suelo = Surface((self.ancho_util, self.alto_util))
        self.capa_suelo.fill(COLOR_FONDO_MAPA)
        self.capa_objetos = Surface((self.ancho_util, self.alto_util), SRCALPHA)

        for fila in range(self.filas):
            for col in range(self.columnas):
                destino = (col * self.tamano_celda, fila * self.tamano_celda)
                self.capa_suelo.blit(self._imagen_tile(self.suelo[fila][col]), destino)
                objeto = self.objeto_en(fila, col)
                if objeto is not None:
                    if hasattr(objeto, "actualizar"):
                        self.objetos_animados.append((objeto, fila, col, destino))
                    if objeto.imagen is not None:
                        self.capa_objetos.blit(objeto.imagen, destino)

        self.capa_rejilla = Surface((self.ancho_util, self.alto_util), SRCALPHA)
        for col in range(self.columnas + 1):
            x = col * self.tamano_celda
            draw.line(self.capa_rejilla, COLOR_LINEA, (x, 0), (x, self.alto_util))
        for fila in range(self.filas + 1):
            y = fila * self.tamano_celda
            draw.line(self.capa_rejilla, COLOR_LINEA, (0, y), (self.ancho_util, y))

    def dibujar_suelo(self, superficie):
        superficie.blit(self.capa_suelo, (self.origen_x, self.origen_y))

    def actualizar_objetos_animados(self):
        """Actualiza la animación de los objetos animados y redibuja la capa de objetos."""
        if not self.objetos_animados:
            return

        self.capa_objetos.fill((0, 0, 0, 0))
        for fila in range(self.filas):
            for col in range(self.columnas):
                destino = (col * self.tamano_celda, fila * self.tamano_celda)
                objeto = self.objeto_en(fila, col)
                if objeto is not None:
                    if hasattr(objeto, "actualizar"):
                        objeto.actualizar()
                    if objeto.imagen is not None:
                        self.capa_objetos.blit(objeto.imagen, destino)

    def dibujar_objetos(self, superficie):
        superficie.blit(self.capa_objetos, (self.origen_x, self.origen_y))

    def dibujar_rejilla(self, superficie):
        if self.mostrar_rejilla:
            superficie.blit(self.capa_rejilla, (self.origen_x, self.origen_y))

    def dibujar_marcas(self, superficie):
        if not self.mostrar_rejilla:
            return
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

        if not self.bloqueada(fila, col):
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
        """Las capas de suelo y objetos, en el orden en que deben apilarse."""
        self.dibujar_suelo(superficie)
        self.dibujar_objetos(superficie)
        self.dibujar_marcas(superficie)
        self.dibujar_inicio_meta(superficie)
        self.dibujar_rejilla(superficie)


class RejillaEntidad:
    """Vista de un MapaTerreno para una entidad de cierto tamano en pixeles.

    Cumple la interfaz que espera `busqueda`: filas, columnas, bloqueada y
    costo_en. Cachea el resultado por celda, porque una misma consulta se repite
    mucho dentro de una busqueda.
    """

    def __init__(self, mapa, tamano):
        self.mapa = mapa
        self.filas = mapa.filas
        self.columnas = mapa.columnas
        self.tamano = (int(tamano[0]), int(tamano[1]))
        self._cache = {}

    def _rect(self, fila, col):
        rect = Rect(0, 0, self.tamano[0], self.tamano[1])
        rect.center = self.mapa.centro_celda(fila, col)
        return rect

    def bloqueada(self, fila, col):
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return True
        clave = (fila, col)
        if clave not in self._cache:
            self._cache[clave] = not self.mapa.superficie_libre(self._rect(fila, col))
        return self._cache[clave]

    def costo_en(self, fila, col):
        return self.mapa.costo_en(fila, col)

    def centro_celda(self, fila, col):
        return self.mapa.centro_celda(fila, col)


def _buscar_capa(datos, ruta, nombres, obligatoria):
    capas = datos.get("capas")
    if capas is None:
        if obligatoria:
            raise ValueError(f"el mapa de {ruta} no tiene 'capas'")
        return None
    if not isinstance(capas, list) or not capas:
        raise ValueError(f"'capas' de {ruta} debe ser una lista no vacia")

    for capa in capas:
        if isinstance(capa, dict) and str(capa.get("nombre", "")).lower() in nombres:
            filas = capa.get("datos")
            break
    else:
        if obligatoria:
            raise ValueError(
                f"el mapa de {ruta} no tiene capa de suelo;"
                f" se esperaba una llamada {nombres[0]!r}",
            )
        return None

    if not isinstance(filas, list) or not filas:
        raise ValueError(f"la capa {nombres[0]!r} de {ruta} necesita 'datos' con al menos una fila")

    anchos = {len(f) for f in filas}
    if len(anchos) != 1:
        raise ValueError(
            f"las filas de 'datos' de {ruta} miden distinto: {sorted(anchos)}",
        )
    return filas


def _normalizar_suelo(fila, catalogo, ruta, numero_fila):
    """Acepta una fila de IDs numericos o, por compatibilidad, de caracteres."""
    if isinstance(fila, str):
        ids = []
        for caracter in fila:
            clave = CLAVE_POR_CARACTER.get(caracter)
            id_tile = catalogo.id_base_de(clave) if clave else None
            if id_tile is None:
                raise ValueError(
                    f"el mapa {ruta} usa el caracter {caracter!r} en la fila {numero_fila},"
                    " que no es ningun terreno conocido",
                )
            ids.append(id_tile)
        return ids

    if isinstance(fila, list):
        return [int(valor) for valor in fila]

    raise ValueError(f"las filas de 'datos' de {ruta} deben ser listas de IDs o cadenas")
