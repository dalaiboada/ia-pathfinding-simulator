"""Héroe principal (mi ironman hehe)"""

from pygame import *

from config import (
    COSTO_REFERENCIA,
    FACTOR_MINIMO,
    STEP_ANGULOS,
    STEP_UMBRAL_CARRERA,
    VELOCIDADES_FOTOGRAMA,
)
from .proyectil import Proyectil

# helper 
def obtener_sub_cuadros(hoja, fila, col_inicio, num_cuadros, ancho_c, alto_c):
    """Recorta una fila de la hoja de sprites y genera la version espejada"""
    
    frames_izq = []
    frames_der = []

    for col in range(col_inicio, col_inicio + num_cuadros):
        rect = Rect(col * ancho_c, fila * alto_c, ancho_c, alto_c)
        sub_img = hoja.subsurface(rect).copy()

        frames_izq.append(sub_img)
        frames_der.append(transform.flip(sub_img, True, False))

    return {"izquierda": frames_izq, "derecha": frames_der}


class Jugador(sprite.Sprite):
    UMBRAL_LLEGADA = 6
    UMBRAL_CARRERA = 130

    # Piso de velocidad
    VELOCIDAD_MINIMA = 1.0

    # Vigilancia de atasco
    FOTOGRAMAS_SIN_PROGRESO = 45
    PROGRESO_MINIMO = 1.0

    # Factor de ritmo
    multiplicador = 1.0

    @classmethod
    def fijar_multiplicador(cls, porcentaje):
        """Traduce el porcentaje del deslizador a un factor de ritmo.

        El 100% es el ritmo original de sprites.py. El suelo existe porque por
        debajo de ~5% el jugador dejaria de ser observable y la colision no se
        podria ni ver ni comprobar.
        """
        factor = porcentaje / 100.0
        if factor > 1.0:
            factor = 1.0
        if factor < FACTOR_MINIMO:
            factor = FACTOR_MINIMO
        cls.multiplicador = factor
        return factor

    def actualizar_paciencia(self):
        """Estira la vigilancia de atasco cuando el jugador va mas lento."""
        self.avances_por_llegada = max(
            2, int(round(self.FOTOGRAMAS_SIN_PROGRESO / self.multiplicador)),
        )
        return self.avances_por_llegada

    def __init__(
        self,
        ruta_imagen,
        centro_x,
        centro_y,
        area_movimiento,
        grupo_proyectiles=None,
        mapa=None,
    ):
        sprite.Sprite.__init__(self)

        self.hoja = image.load(ruta_imagen).convert_alpha()
        ancho_total, alto_total = self.hoja.get_size()
        self.ancho_c = ancho_total // 9
        self.alto_c = alto_total // 6

        self.animaciones = {
            "reposo": obtener_sub_cuadros(
                self.hoja, fila=0, col_inicio=0, num_cuadros=3,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
            "caminar": obtener_sub_cuadros(
                self.hoja, fila=1, col_inicio=0, num_cuadros=6,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
            "disparo": obtener_sub_cuadros(
                self.hoja, fila=2, col_inicio=3, num_cuadros=3,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
            "agachado": obtener_sub_cuadros(
                self.hoja, fila=2, col_inicio=6, num_cuadros=3,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
            "golpe": obtener_sub_cuadros(
                self.hoja, fila=3, col_inicio=0, num_cuadros=4,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
            "correr": obtener_sub_cuadros(
                self.hoja, fila=4, col_inicio=0, num_cuadros=6,
                ancho_c=self.ancho_c, alto_c=self.alto_c,
            ),
        }

        self.direccion = "derecha"
        self.estado = "reposo"
        self.indice_cuadro = 0.0
        self.bloqueo_accion = False
        self.disparo_ejecutado = False

        self.area_movimiento = area_movimiento
        self.proyectiles = grupo_proyectiles if grupo_proyectiles is not None else sprite.Group()
        self.objetivo = None
        self.mapa = mapa
        self.ultimo_avance = (centro_x, centro_y)
        self.fotogramas_sin_avance = 0
        # El factor se fija por fotograma desde la vista; la paciencia con la
        # vigilancia de atasco se recalcula entonces, para que un jugador lento
        # no se de por atascado solo por ir despacio.
        self.actualizar_paciencia()

        self.image = self.animaciones["reposo"][self.direccion][0]
        self.rect = self.image.get_rect(center=(centro_x, centro_y))

        # Pisadas: se vigila el avance real por fotograma para saber si camina
        self._centro_pasos = self.rect.center
        self._ultimo_paso_ms = 0

    # ------------------------------------------------------- terreno y colision

    def fijar_objetivo(self, posicion):
        """Fija destino, corrigiendolo si cae sobre un obstaculo."""
        if self.mapa is None:
            self.objetivo = (posicion[0], posicion[1])
            return self.objetivo
        seguro = self.mapa.punto_libre_cerca(posicion, self.rect.size)
        self.objetivo = seguro
        self.ultimo_avance = self.rect.center
        self.fotogramas_sin_avance = 0
        return seguro

    def aplicar_desplazamiento(self, desplazamiento_x, desplazamiento_y):
        """Mueve el sprite resolviendo obstaculos, si hay mapa."""
        if self.mapa is not None:
            desplazamiento_x, desplazamiento_y = self.mapa.desplazar(
                self.rect, desplazamiento_x, desplazamiento_y,
            )
        self.rect.x += desplazamiento_x
        self.rect.y += desplazamiento_y

    def velocidad_sobre_terreno(self, velocidad_base):
        """Escala la velocidad segun lo que cuesta el terreno que se pisa."""
        if self.mapa is None:
            return velocidad_base
        costo = self.mapa.costo_bajo(self.rect.center)
        if costo is None:
            return velocidad_base
        return max(self.VELOCIDAD_MINIMA, velocidad_base * (COSTO_REFERENCIA / costo))

    def _actualizar_pasos(self):
        """Reproduce el sonido de pisadas del terreno que se pisa, con su intervalo."""
        centro = self.rect.center
        se_mueve = (
            abs(centro[0] - self._centro_pasos[0]) >= 1
            or abs(centro[1] - self._centro_pasos[1]) >= 1
        )
        self._centro_pasos = centro

        if not se_mueve:
            self._ultimo_paso_ms = 0
            return
        if self.mapa is None:
            return

        terreno = self.mapa.terreno_bajo((self.rect.centerx, self.rect.bottom - 2))
        if terreno is None or terreno.sonido is None:
            return

        intervalo = terreno.intervalo_pasos_ms or 400
        ahora = time.get_ticks()
        if ahora - self._ultimo_paso_ms >= intervalo:
            terreno.sonido.play()
            self._ultimo_paso_ms = ahora

    def _registrar_avance(self):
        """Vigila que el jugador siga avanzando y no se quede empujando un muro."""
        if abs(self.rect.centerx - self.ultimo_avance[0]) < self.PROGRESO_MINIMO and \
           abs(self.rect.centery - self.ultimo_avance[1]) < self.PROGRESO_MINIMO:
            self.fotogramas_sin_avance += 1
        else:
            self.fotogramas_sin_avance = 0
            self.ultimo_avance = self.rect.center
        return self.fotogramas_sin_avance < self.avances_por_llegada

    def dibujar(self, superficie):
        superficie.blit(self.image, self.rect)

    def cambiar_estado(self, nuevo_estado):
        if self.estado != nuevo_estado:
            self.estado = nuevo_estado
            self.indice_cuadro = 0.0

    def disparar(self):
        spawn_x = self.rect.right if self.direccion == "derecha" else self.rect.left
        self.proyectiles.add(Proyectil(spawn_x, self.rect.centery - 6, self.direccion, self.area_movimiento))

    def procesar_eventos(self, eventos):
        for e in eventos:
            if e.type == KEYDOWN:
                if e.key == K_j and not self.bloqueo_accion:
                    self.cambiar_estado("disparo")
                    self.bloqueo_accion = True
                    self.disparo_ejecutado = False

                elif e.key == K_k and not self.bloqueo_accion:
                    self.cambiar_estado("golpe")
                    self.bloqueo_accion = True

    def update(self):
        teclas = key.get_pressed()
        self.actualizar_paciencia()
        self._actualizar_pasos()

        if self.estado == "golpe":
            self.actualizar_animacion()
            return

        if teclas[K_c] and self.estado != "disparo":
            self.cambiar_estado("agachado")
            self.actualizar_animacion()
            return

        if self.objetivo is not None:
            self.avanzar_hacia_objetivo()
            self.actualizar_animacion()
            self.rect.clamp_ip(self.area_movimiento)
            return

        # Movimiento cardinal: un solo eje por fotograma, nunca en diagonal
        desplazamiento_x = 0
        desplazamiento_y = 0
        corriendo = teclas[K_LSHIFT] or teclas[K_RSHIFT]
        paso_base = STEP_ANGULOS[1] if corriendo else STEP_ANGULOS[0]
        velocidad_actual = self.velocidad_sobre_terreno(paso_base * self.multiplicador)

        if teclas[K_RIGHT] or teclas[K_d]:
            desplazamiento_x = velocidad_actual
            self.direccion = "derecha"

        elif teclas[K_LEFT] or teclas[K_a]:
            desplazamiento_x = -velocidad_actual
            self.direccion = "izquierda"

        elif teclas[K_UP] or teclas[K_w]:
            desplazamiento_y = -velocidad_actual

        elif teclas[K_DOWN] or teclas[K_s]:
            desplazamiento_y = velocidad_actual

        self.aplicar_desplazamiento(desplazamiento_x, desplazamiento_y)

        if self.estado != "disparo":
            if desplazamiento_x != 0 or desplazamiento_y != 0:
                self.cambiar_estado("correr" if corriendo else "caminar")
            else:
                self.cambiar_estado("reposo")

        self.actualizar_animacion()
        self.rect.clamp_ip(self.area_movimiento)

    def avanzar_hacia_objetivo(self):
        """Control con ratón: avanza en cardinal al destino y acelera si está lejos."""
        destino = self.objetivo
        if destino is None:
            return

        diferencia_x = destino[0] - self.rect.centerx
        diferencia_y = destino[1] - self.rect.centery

        # Un solo eje: el de mayor distancia restante. Nunca diagonal.
        if abs(diferencia_x) >= abs(diferencia_y):
            paso_x, paso_y = diferencia_x, 0
        else:
            paso_x, paso_y = 0, diferencia_y

        longitud = abs(paso_x) if paso_x else abs(paso_y)

        if longitud <= self.UMBRAL_LLEGADA:
            self.objetivo = None
            self.fotogramas_sin_avance = 0
            if self.estado != "disparo":
                self.cambiar_estado("reposo")
            return

        # El multiplicador del deslizador actua sobre los dos tramos, pero el
        # umbral de carrera sigue en pixeles: es una distancia, no un ritmo.
        if longitud > self.UMBRAL_CARRERA:
            factor_pasada = STEP_ANGULOS[0] * STEP_UMBRAL_CARRERA
            estado_destino = "correr"
        else:
            factor_pasada = STEP_ANGULOS[0]
            estado_destino = "caminar"

        paso = self.velocidad_sobre_terreno(factor_pasada * self.multiplicador)

        if paso_x:
            self.direccion = "derecha" if paso_x > 0 else "izquierda"

        self.aplicar_desplazamiento(paso_x / longitud * paso, paso_y / longitud * paso)

        if not self._registrar_avance():
            # Empujando un muro sin avanzar: el destino no es alcanzable
            self.objetivo = None
            if self.estado != "disparo":
                self.cambiar_estado("reposo")
            return

        if self.estado != "disparo":
            self.cambiar_estado(estado_destino)

    def actualizar_animacion(self):
        cuadros_actuales = self.animaciones[self.estado][self.direccion]

        # El mismo multiplicador gobierna el ritmo de los cuadros: por eso
        # Golpe y Disparo (acciones de un disparo) no dependen del teclado.
        vel_fotograma = VELOCIDADES_FOTOGRAMA[self.estado] * self.multiplicador

        self.indice_cuadro += vel_fotograma

        if self.estado in ("golpe", "disparo"):
            if self.estado == "disparo" and int(self.indice_cuadro) == 1 and not self.disparo_ejecutado:
                self.disparar()
                self.disparo_ejecutado = True

            if self.indice_cuadro >= len(cuadros_actuales):
                self.bloqueo_accion = False
                teclas = key.get_pressed()
                se_mueve = (
                    teclas[K_RIGHT] or teclas[K_d] or
                    teclas[K_LEFT] or teclas[K_a] or
                    teclas[K_UP] or teclas[K_w] or
                    teclas[K_DOWN] or teclas[K_s]
                )
                corriendo = teclas[K_LSHIFT] or teclas[K_RSHIFT]

                if se_mueve:
                    self.cambiar_estado("correr" if corriendo else "caminar")
                else:
                    self.cambiar_estado("reposo")
        else:
            self.indice_cuadro %= len(cuadros_actuales)

        self.image = cuadros_actuales[min(int(self.indice_cuadro), len(cuadros_actuales) - 1)]
