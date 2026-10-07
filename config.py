"""Medidas de la ventana, rutas de los assets y estados de celda.
"""

import os

# --- VENTANA
ANCHO_VENTANA = 1300
ALTO_VENTANA = 670

# controlador de rutas
ANCHO_PANEL = 340
ANCHO_MAPA = ANCHO_VENTANA - ANCHO_PANEL

# rejilla del mapa
TAM_CELDA = 32
ALTO_HUD = 110
COLUMNAS_MAPA = ANCHO_MAPA // TAM_CELDA
FILAS_MAPA = (ALTO_VENTANA - ALTO_HUD) // TAM_CELDA

# JUEGO
FPS = 60
TITULO_JUEGO = "Avengers: La Era de Últrón"

VELOCIDAD_ANIMACION_MIN = 1
VELOCIDAD_ANIMACION_MAX = 100
VELOCIDAD_ANIMACION_INICIAL = 100

# Suelo del factor, para que al 1% el jugador siga siendo observable
FACTOR_MINIMO = 0.05

# Multiplicadores de fotograma por estado
VELOCIDADES_FOTOGRAMA = {
    "reposo": 0.15,
    "caminar": 0.15,
    "correr": 0.22,
    "golpe": 0.18,
    "disparo": 0.18,
    "agachado": 0.15,
}

# Paso por fotograma: (caminar, correr) con teclado
STEP_ANGULOS = (4, 7)
STEP_UMBRAL_CARRERA = 3    # con el raton: correr a partir de 3x el paso

# --- ASSETS
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_IMAGENES = os.path.join(RUTA_BASE, "assets", "img")
RUTA_FUENTES = os.path.join(RUTA_BASE, "assets", "fuentes")
RUTA_AUDIO = os.path.join(RUTA_BASE, "assets", "audio")
RUTA_MAPAS = os.path.join(RUTA_BASE, "mapas")

# FONDO
RUTA_FONDO_MENU = os.path.join(RUTA_IMAGENES, "juego", "fondo.jpg")

# JUEGO
RUTA_JUGADOR = os.path.join(RUTA_IMAGENES, "juego", "ironman.png")
RUTA_ENEMIGO = os.path.join(RUTA_IMAGENES, "juego", "ultron.png")

# INTERFAZ
#img
RUTA_CURSOR = os.path.join(RUTA_IMAGENES, "interfaz", "cursor.png")
RUTA_RASTRO = os.path.join(RUTA_IMAGENES, "interfaz", "cursor_click.png")

# fuentes
RUTA_FONTE = os.path.join(RUTA_FUENTES, "game.ttf")

# audio
RUTA_AUDIO_PRESIONAR_BOTON = os.path.join(RUTA_AUDIO, "interfaz", "presionar_boton.ogg")
RUTA_AUDIO_HOVER_BOTON = os.path.join(RUTA_AUDIO, "interfaz", "hover_boton.ogg")
RUTA_AUDIO_PISADAS_HIERBA = os.path.join(RUTA_AUDIO, "pisadas_hierba.ogg")
RUTA_AUDIO_PISADAS_PAVIMENTO = os.path.join(RUTA_AUDIO, "pisadas_pavimento.ogg")

# MAPAS y texturas de terreno
RUTA_CARPETA_TEXTURAS = os.path.join(RUTA_MAPAS, "texturas")
RUTA_MAPA_EXPLORACION = os.path.join(RUTA_MAPAS, "exploracion.json")
RUTA_TILESET = os.path.join(RUTA_IMAGENES, "mapa", "tileset.jpg")

# Capas del mapa (mismo orden en el que se apilan)
CAPA_SUELO = "suelo"
CAPA_OBJETOS = "objetos"
CAPA_ENTIDADES = "entidades"
NOMBRE_CAPAS_SUELO = ("suelo", "terreno", "terrenos")
NOMBRE_CAPAS_OBJETOS = ("objetos", "objectos", "cosas")

# ID que representa "ningun objeto" en la capa de objetos
OBJETO_NINGUNO = 0

# Volumen con el que suenan las pisadas
VOLUMEN_PISADAS = 0.35

# Costo de referencia: el terreno mas barato se mueve a la velocidad base
COSTO_REFERENCIA = 1.0

# Superposiciones de la busqueda sobre el terreno
MARCA_NINGUNA = 0
MARCA_VISITADA = 1
MARCA_CAMINO = 2

# --- IA / busqueda de caminos
ALGORITMO_INICIAL = "astar"        # el personaje arranca con A*
ALGORITMO_ENEMIGO_INICIAL = "astar"

# Persecucion
NUMERO_ENEMIGOS = 5
LADO_ENEMIGO = 24                  # px del cuadrado representativo
VELOCIDAD_ENEMIGO = 1.0            # px por fotograma
CAMPO_VISION_ENEMIGO = 7           # radio de vision en celdas
RECALCULO_RUTA_ENEMIGA = 10        # fotogramas entre recalculos de ruta
