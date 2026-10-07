# Contexto del proyecto — Simulador de rutas y movimiento

Documento de contexto para cualquier persona (o agente) que vaya a retomar este
repositorio. Describe qué es el proyecto, cómo está montado, qué restricciones hay
que respetar y qué falta por construir.

Esta copia es **autocontenida**: todo el juego vive dentro de `simulador/`. No se
incluyen los demos originales de la raíz ni los scripts `verificar_*.py` de la
versión completa del repositorio.

---

## 1. Propósito

Simulador de movimiento con rutas y movimiento de enemigos, construido para
**apreciar el funcionamiento de los algoritmos de búsqueda** (BFS, Dijkstra, A*).

En la práctica el juego es el banco de pruebas: un mapa de rejilla que se puede
editar a mano, un jugador con hoja de animaciones, un panel de telemetría que
recolectará las métricas de la búsqueda, y una vista dedicada a la persecución
de enemigos.

Las cuatro vistas existen y son navegables.

---

## 2. Cómo ejecutar

Desde dentro de `simulador/`:

```bash
cd simulador
python IA.py
```

O desde la carpeta que contiene a `simulador/`:

```bash
python simulador/IA.py
```

Sin dependencias más allá de `pygame` (probado con 2.6.1 / Python 3.13).

Todo el código del proyecto está directamente bajo `simulador/`, así que sus
módulos se importan **planos** (`import motor`, `from config import ...`). Para
que esas importaciones resuelvan, `simulador/` tiene que ser el directorio del
script o de trabajo. No hace falta lanzarse desde una raíz concreta para los
assets: `RUTA_BASE` se resuelve en `config.py` con
`os.path.dirname(os.path.abspath(__file__))` (un solo `dirname`, porque `config.py`
vive en la misma carpeta que `assets/` y `mapas/`), de modo que las rutas funcionan
desde cualquier directorio de trabajo.

`IA.py` es el único punto de entrada y son 13 líneas: define `main()`, que llama a
`iniciar()` y luego a `Juego().ejecutar()`. Importar un módulo **no abre ninguna
ventana**: hace falta `iniciar()`.

`__init__.py` reexporta `Juego`, `iniciar`, `fuente` y `comprobar_iniciado`, y
añade la propia carpeta al `sys.path` para que `import simulador` siga funcionando
aunque se use el estilo plano. El paquete, por tanto, se puede usar de las dos
formas.

---

## 3. Inventario de archivos

### Assets

| Archivo | Uso |
|---|---|
| `assets/img/juego/fondo.jpg` | Fondo del menú (1920×1080, escalado a 1300×670) |
| `assets/img/juego/ironman.png` | Hoja del jugador, 576×384 = rejilla 9×6 de celdas 64×64 |
| `assets/img/juego/ultron.png` | Hoja del enemigo (reservada para Persecución) |
| `assets/img/interfaz/cursor.png` | Cursor personalizado (32×32) |
| `assets/img/interfaz/cursor_click.png` | Rastro del cursor (32×32) |
| `assets/fuentes/game.ttf` | Tipografía pixelada: títulos, botones, HUD |
| `assets/audio/interfaz/presionar_boton.ogg` | Sonido de clic en botón |
| `assets/audio/interfaz/hover_boton.ogg` | Sonido al pasar por encima de un botón |
| `assets/audio/pisadas_pavimento.ogg` | Pisadas sobre pavimento (previsto, sin usar) |
| `assets/audio/pisadas_tierra.ogg` | Pisadas sobre tierra (previsto, sin usar) |
| `mapas/exploracion.json` | Mapa de terreno de la vista Exploración |

### Código

| Archivo | Rol | Estado |
|---|---|---|
| `IA.py` | **El juego.** `main()`, punto de entrada. | Activo |
| `config.py` | Medidas, rutas de assets, marcas, costo de referencia | Activo, sin pygame |
| `paleta.py` | Colores + `mezclar()` | Activo, sin pygame |
| `arranque.py` | `iniciar()`, `fuente()`, `comprobar_iniciado()` | Activo |
| `dibujo.py` | Velo, rejilla, tarjeta, HUD, texto centrado | Activo |
| `motor.py` | `Juego`: bucle principal y navegación | Activo |
| `mapas/exploracion.json` | Mapa de la vista Exploración | Activo, se recarga con `F5` |

```
simulador/
├── IA.py                          main(): iniciar() + Juego().ejecutar()
├── __init__.py                    reexporta Juego, iniciar, fuente, comprobar_iniciado
├── config.py                      medidas, rutas de assets, marcas, costo   (sin pygame)
├── paleta.py                      colores + mezclar()               (sin pygame)
├── arranque.py                    iniciar(), fuente(), comprobar_iniciado()
├── dibujo.py                      velo, rejilla, tarjeta, HUD, texto centrado
├── motor.py                       Juego: bucle principal y navegación
├── assets/
│   ├── img/
│   │   ├── juego/                 fondo.jpg, ironman.png, ultron.png
│   │   └── interfaz/              cursor.png, cursor_click.png
│   ├── fuentes/                   game.ttf
│   └── audio/
│       ├── interfaz/              presionar_boton.ogg, hover_boton.ogg
│       ├── pisadas_pavimento.ogg
│       └── pisadas_tierra.ogg
├── mapas/
│   └── exploracion.json           14 x 32 celdas de 40 px
├── entidades/
│   ├── proyectil.py               Proyectil
│   └── jugador.py                 Jugador + obtener_sub_cuadros()
├── mundo/
│   ├── terreno.py                 TipoTerreno y catálogo             (sin pygame)
│   ├── mapa_terreno.py            MapaTerreno: rejilla, JSON, colisión, render
│   └── mapa.py                    MapaRutas, la rejilla editable de Rutas
├── interfaz/
│   ├── boton.py                   BotonTexto
│   ├── cursor.py                  CustomMouse
│   └── deslizador.py              DeslizadorCyber
└── vistas/
    ├── base.py                    Vista
    ├── menu.py                    VistaMenu
    ├── exploracion.py             VistaExploracion
    ├── rutas.py                   VistaControladorRutas
    └── persecucion.py             VistaPersecucion
```

Son 24 módulos `.py` con responsabilidad única.

---

## 4. Convenciones de código

1. **`from pygame import *`** en lugar de anteponer `pygame.` a todo.
2. **Un solo bloque de importaciones**, arriba del archivo.
3. **Código simple, modular y en español**: nombres de clases, métodos y variables
   en español; sin librerías ni frameworks extra.
4. Assets referenciados por constante de ruta en `config.py`. Nada de rutas
   cableadas en los módulos.
5. Entre módulos del proyecto, **imports planos con nombres explícitos** desde la
   raíz del proyecto (`from config import ...`, `from mundo.mapa import ...`,
   `from interfaz.boton import BotonTexto`), nunca `import *`. Los subpaquetes
   usan relativos **internos** para lo suyo (`from .base import Vista`,
   `from .terreno import ...`). Gracias a esto, `config.py` y `paleta.py` se pueden
   cargar sin pygame.

### Trampas de `from pygame import *` (ya resueltas, no reintroducirlas)

`pygame` **no** queda bound como nombre, y varios símbolos útiles **no** se
exportan. Consecuencias aplicadas en `simulador/`:

- No se puede escribir `pygame.Surface` en una anotación de tipo: las anotaciones
  se evalúan al definir la función, así que en `cursor.py` la anotación
  `evento: pygame.event.Event` habría lanzado `NameError`. Se usa `Surface` y
  `event.Event` a secas.
- `BLEND_RGBA` no se exporta → ver §5.
- `Clock`, `SysFont`, `flip`, `Group`, `subsurface` tampoco: se usan las formas
  cualificadas `time.Clock()`, `font.SysFont()`, `transform.flip()`,
  `sprite.Group()`, `hoja.subsurface()`. Ojo: los **módulos** sí se exportan
  (`image`, `transform`, `time`, `font`, `sprite`, `draw`), así que
  `image.load(...)` y `transform.scale(...)` en `mapa_terreno.py` son válidos. Lo
  que falta son los nombres sueltos de nivel superior.

### Cuidado con la codificación en PowerShell

`Get-Content` y `Set-Content` de PowerShell 5.1 usan la página de códigos local, no
UTF-8. Un `Get-Content -Raw | Set-Content` sobre un archivo con acentos lo
**doblemente codifica**: `á` pasa a ser `Ã¡`. Esto ya pasó antes en el proyecto y
hubo que revertirlo.

Para tocar archivos con acentos, usar las herramientas de edición, o un script de
Python con `encoding="utf-8"` explícito. Si ya se corrompió, se deshace con:

```python
texto.encode("cp1252").decode("utf-8")
```

---

## 5. Decisiones técnicas que conviene conocer

### Alfa del mapa sin `BLEND_RGBA`

El mapa original dibuja celdas RGBA translúcidas esperando que se mezclen con el
fondo, pero `Surface.blit` **no** mezcla por canal alfa salvo que se pase
`BLEND_RGBA` — que no se exporta con `import *`. Tal cual, esas celdas se veían
opacas.

Solución aplicada en dos partes: la función `mezclar(color, fondo, alfa)` de
`paleta.py` pre-mezcla los colores contra el fondo opaco del mapa en tiempo de
carga, y la capa de terreno se dibuja ya opaca. Mismo resultado visual, sin
importar nada extra y con el cálculo hecho una sola vez.

Donde sí hace falta transparencia de verdad —las marcas de la búsqueda y el realce
del cursor— se usa `Surface(..., SRCALPHA)` y se compone con `set_alpha`, que sí
están exportados.

### Geometría derivada, no cableada

Las medidas de rejilla se derivan por aritmética en vez de estar escritas a mano,
para que cambiar `TAM_CELDA` no desaline nada. Con los valores actuales:

```
TAM_CELDA     = 32
ANCHO_MAPA    = ANCHO_VENTANA - ANCHO_PANEL            = 960
COLUMNAS_MAPA = ANCHO_MAPA // TAM_CELDA                = 30
FILAS_MAPA    = (ALTO_VENTANA - ALTO_HUD) // TAM_CELDA = 17
```

`MapaTerreno` recalcula sus propias filas y columnas a partir de las dimensiones
que se le pasan, de modo que no depende de esas constantes globales. Exploración
tiene su propia rejilla, más ancha: `ANCHO_VENTANA // TAM_CELDA` columnas y
`(ALTO_VENTANA - ALTO_HUD) // TAM_CELDA` filas, centrada con
`(ANCHO_VENTANA - columnas * TAM_CELDA) // 2` para que sobre el marco.

---

## 6. Arquitectura de `simulador/`

Orden de secciones, de arriba abajo:

| Sección | Contenido |
|---|---|
| Configuración | Medidas, rutas de assets, FPS, marcas de búsqueda, costos, ritmo del deslizador |
| Paleta | Paleta cyberpunk + `mezclar()` |
| Arranque | `init()`, `font.init()`, `display.set_mode()`, fuentes |
| Helpers de dibujo | `obtener_sub_cuadros`, `crear_velo`, rejilla, tarjeta, HUD |
| Componentes | `BotonTexto`, `CustomMouse`, `DeslizadorCyber`, `Proyectil`, `Jugador`, `MapaTerreno`, `MapaRutas` |
| Vistas | `Vista` (base) + menú, exploración, rutas, persecución |
| Juego | `Juego` con el bucle principal, y `main()` en `IA.py` |

### Punto de arranque

`arranque.py` es el **único** sitio que abre la ventana. Expone:

| Función | Qué hace |
|---|---|
| `iniciar()` | `init()`, `font.init()`, `set_mode()`, `set_caption()`, reloj y fuentes. Idempotente. |
| `fuente(clave)` | Devuelve una fuente por clave; el `KeyError` lista las claves válidas. |
| `comprobar_iniciado()` | Lanza `RuntimeError` con mensaje claro si se usa el juego antes de `iniciar()`. |

Claves de fuente: `titulo_menu`, `subtitulo_menu`, `boton`, `hud`, `cyber_titulo`,
`cyber_etiqueta`, `cyber_valor`, `instrucciones`, `cyber_diminuta`.

Antes era un juego monolítico de más de mil líneas en un `IA.py`; ahora `IA.py`
son 13 líneas y cada módulo tiene una sola responsabilidad.

### Grafo de dependencias (acíclico)

Nombres planos desde la raíz de `simulador/`:

```
config, paleta          → nada
arranque                → config
dibujo                  → arranque, config, paleta
mundo.terreno           → nada
mundo.mapa_terreno      → config, paleta, pygame, mundo.terreno
mundo.mapa              → pygame, mundo.mapa_terreno
entidades.proyectil     → paleta
entidades.jugador       → config, entidades.proyectil
interfaz.boton          → config, pygame
interfaz.cursor         → pygame
interfaz.deslizador     → paleta
vistas.base             → nada
vistas.*                → arranque, config, paleta, dibujo, y lo que necesitan
motor                   → arranque, config, vistas, interfaz.cursor
IA.py                   → motor, arranque
```

Dos detalles que conviene no dar por supuestos:

- `mundo.terreno` es importable **sin pygame**, pero no se puede alcanzar como
  `mundo.terreno` en un proceso sin pygame, porque el `__init__.py` del paquete
  `mundo` importa `mapa`, que sí usa pygame. Para cargarlo suelto hay que hacerlo
  por ruta (`importlib.util.spec_from_file_location`).
- `mundo.mapa` usa constantes de `pygame` (`K_TAB`, `K_r`, `KEYDOWN`) en
  `manejar_tecla`, así que necesita su propio `from pygame import *`.

Cada módulo importa también de forma **autónoma** en un proceso nuevo, lo que
detecta cualquier ciclo de importaciones.

### Modelo de vistas

`Vista` define el ciclo `entrar() → manejar_evento() → actualizar() → dibujar()`.
El bucle de `Juego` itera sobre un registro de vistas y cambia entre ellas con
`juego.ir_a(nombre)`, llamando a `salir()` sobre la vista anterior y `entrar()`
sobre la nueva. El cursor se dibuja al final de cada fotograma, por encima de
todo, para que nunca quede tapado.

`Vista.permite_escape` controla qué vistas responden a `ESC`; el menú lo
desactiva para no salirse de sí mismo.

### Jugador

Hoja de 9×6 con celdas de 64×64 y seis animaciones, cada una disponible en dos
direcciones (la de la izquierda es el espejo generado por `transform.flip`):

| Estado | Fila | Cuadros | Velocidad de fotograma |
|---|---|---|---|
| `reposo` | 0 | 3 | 0.15 |
| `caminar` | 1 | 6 | 0.15 |
| `disparo` | 2 (cols 3–5) | 3 | 0.18 |
| `agachado` | 2 (cols 6–8) | 3 | 0.15 |
| `golpe` | 3 | 4 | 0.18 |
| `correr` | 4 | 6 | 0.22 |

Control por teclado (4 px/frame, 7 con `SHIFT`) o por ratón. El movimiento es
siempre **cardinal**: un solo eje por fotograma, nunca en diagonal. Al hacer clic
se fija `jugador.objetivo` y el jugador avanza hacia él, acelerando a `correr` si
está a más de `UMBRAL_CARRERA` (130 px) y parando al llegar a `UMBRAL_LLEGADA`
(6 px), para no temblar en el sitio. Mientras hay objetivo el teclado queda
ignorado; al llegar, se reactiva.

Si el destino queda encerrado, el jugador no se queda empujando un muro:
`FOTOGRAMAS_SIN_PROGRESO` (45) fotogramas sin ganar ni un píxel en X **ni** en Y
abandonan el destino. Esa paciencia se **divide por el factor de ritmo**, de modo
que un jugador ralentizado por el deslizador no se dé por atascado solo por ir
despacio.

El deslizador "Velocidad de animación" de Rutas gobierna un factor único
(`Jugador.multiplicador`) que escala a la vez el paso por fotograma y los
multiplicadores de cuadro, de `VELOCIDADES_FOTOGRAMA`. El 100% reproduce el
comportamiento original; por encima satura, y por debajo hay un suelo
`FACTOR_MINIMO` (0.05). Rutas lo escribe en `juego.velocidad_animacion` y
Exploración lo aplica cada fotograma, así que el valor sobrevive al salto entre
vistas.

### Terreno

`mundo/terreno.py` define los tipos de celda. Módulo de datos puros, sin pygame,
como `config.py`:

| Clave | Nombre | Transitable | Costo |
|---|---|---|---|
| `p` | Pavimento | sí | `1.0` |
| `t` | Tierra | sí | `2.0` |
| `#` | Obstáculo | no | `null` |

`costo` es `None` **exactamente** cuando el terreno es intransitable, y siempre
positivo cuando es transitable. Cargar un catálogo que rompa ese invariante es un
error, no algo que se normalice en silencio.

El costo modula la velocidad del jugador:

```
velocidad = max(VELOCIDAD_MINIMA, base * (COSTO_REFERENCIA / costo))
```

Con `COSTO_REFERENCIA = 1.0` y `VELOCIDAD_MINIMA = 1.0`: pavimento no penaliza,
tierra divide la velocidad por dos, y ningún terreno puede inmovilizar al jugador.

Cada tipo admite un campo `textura` opcional. Se resuelve **relativa al JSON que la
declara**, se carga una sola vez, se escala a `TAM_CELDA` y se cachea por clave.
Ahora todos los terrenos van por color plano; las texturas están soportadas pero no
hay ninguna imagen en el repo.

### MapaTerreno

Rejilla de celdas. Guarda el terreno y las superposiciones de la búsqueda **en dos
matrices aparte**, para que el camino pueda discurrir por pavimento o por tierra
sin que ambas cosas se pisen:

| Capa | Contenido |
|---|---|
| `celdas` | Clave de terreno, una por celda. |
| `marcas` | `MARCA_NINGUNA` / `MARCA_VISITADA` / `MARCA_CAMINO`. |

`inicio` y `meta` son **coordenadas**, no estados de celda. Se dibujan como anillos
con cruz (`COLOR_INICIO` cian, `COLOR_META` magenta) por encima del terreno y bajo
la rejilla. Son únicos: al mover uno, su celda anterior recupera el terreno por
defecto (`_liberar_celda_anterior`).

**Enganche de la búsqueda:** `marca_en`, `marcar`, `limpiar_marcas` y
`celdas_marcadas` existen y funcionan, pero **nadie los llama todavía**. Un
algoritmo marca mientras expande, dibuja el resultado con `dibujar_marcas` y
llama a `limpiar_marcas()` antes de la siguiente ejecución.

Métodos de colisión que usa el jugador:

| Método | Qué hace |
|---|---|
| `superficie_libre(rect)` | El rect cabe entero y no toca ningún obstáculo. |
| `desplazar(rect, dx, dy)` | Devuelve lo que se admite, resolviendo eje a eje. |
| `punto_libre_cerca(centro, tamaño)` | Busca a anillos crecientes un sitio válido. |

`desplazar` **devuelve** el desplazamiento y no mueve el rect: primero prueba el
movimiento entero y, si choca, prueba X e Y por separado para que el jugador
deslice por el eje despejado.

### Formato del JSON

```json
{
  "version": 1,
  "nombre": "Patio de pruebas",
  "tamano_celda": 40,
  "terrenos": [ { "codigo": "p", "nombre": "Pavimento",
                  "transitable": true, "costo": 1.0,
                  "color": [148, 150, 158], "textura": null } ],
  "capas": [ { "nombre": "terreno", "datos": ["####", "#pp#", "####"] } ],
  "inicio": { "fila": 0, "col": 0 },
  "meta":   { "fila": 3, "col": 3 }
}
```

Decisiones que conviene no cambiar sin pensarlo:

- Las filas de `datos` deben medir **lo mismo** entre sí.
- La capa se busca por nombre entre `NOMBRE_CAPAS_POR_DEFECTO`
  (`terreno`, `terrenos`, `suelo`), para poder añadir capas de objetos después.
- `inicio` es **obligatorio**: sin él el juego no sabe dónde aparece el jugador.
  `meta` es opcional.
- Un mapa **más grande que la vista es un error, no un recorte**. Recortar en
  silencio daría una forma distinta de la que la vista espera, así que
  `cargar_json` se niega y lo dice. Un mapa más pequeño sí cabe: las celdas que
  sobran se rellenan con el terreno por defecto.
- Los caracteres que no están en el catálogo son un error, con fila y columna.

Si el JSON no se puede leer, `VistaExploracion` **avisa por consola y dibuja un
patio generado por código** (perímetro bloqueado y avenida en cruz), para que el
juego siga siendo jugable. `F5` sobrevive a los dos casos.

### MapaRutas

`MapaRutas` hereda de `MapaTerreno` y solo añade la política de edición de su
vista. Rejilla 30×17 = 510 celdas de 32 px, en el área `(0, 110, 960, 544)`.

No carga JSON. Empieza con el catálogo por defecto y todo en tierra, lista para
pintar. Solo gestiona `TAB` y `R`; la pintura la hace la vista.

---

## 7. Las cuatro vistas

### Menú
Fondo `assets/img/juego/fondo.jpg` con un velo degradado para dar legibilidad al
texto. Tres botones `BotonTexto` que enlazan con `juego.ir_a(...)`. Cada botón
tarda 400 ms en su animación de destello antes de navegar. Los botones suenan al
pasar por encima y al hacer clic (`hover_boton.ogg` / `presionar_boton.ogg`).

### Exploración
El patio de pruebas. El mapa sale de `mapas/exploracion.json` (14 filas × 32
columnas; el JSON declara celdas de 40 px, pero la vista impone `TAM_CELDA = 32`)
y se recarga con `F5`.

El jugador nace en la celda `inicio` del JSON y se mueve con clic izquierdo hacia
el cursor (con un marcador de ondas cian en el destino) o con WASD. Choca contra
los obstáculos y va más despacio por la tierra que por el pavimento.

Si el JSON falta o está roto, avisa por consola y dibuja un patio de respaldo
generado por código.

### Controlador de rutas
El reparto pedido en el enunciado: mapa **más ancho** que el panel.

- **Mapa** (izquierda, 960 px): rejilla 30×17 = 510 celdas, toda en tierra.
- **Panel** (derecha, 340 px): paleta de terrenos, 6 tarjetas y el deslizador.

Reparto vertical del panel:

| Banda | Y | Altura |
|---|---|---|
| Título y estado | 25 – 75 | — |
| Paleta de 3 terrenos | 86 | 34 |
| 6 tarjetas, paso 64 | 130 → 506 | 56 |
| Divisor | 520 | — |
| Etiqueta de velocidad | 538 | — |
| Deslizador | 570 | 10 |

Las tarjetas de `Posición`, `Inicio` y `Meta` leen en vivo la celda bajo el ratón.
`Terreno` muestra el tipo de la celda apuntada con su costo, o `BLOQUEA` si es
intransitable. `Nodos Explorados` y `Costo Ruta` están fijas en `0` porque aún no hay
búsqueda que las alimente — son los puntos de enganche del simulador.

### Persecución
Marcador de posición, tal como pedía el enunciado. Es el destino natural del
sistema de IA enemiga (`assets/img/juego/ultron.png` está reservado para ello).

---

## 8. Controles

| Vista | Entrada | Efecto |
|---|---|---|
| Menú | Clic en botón | Navega a la vista correspondiente (tras 400 ms) |
| Todas | `ESC` | Vuelve al menú |
| Exploración | Clic izquierdo | Fija destino; el jugador camina/corre hasta él |
| Exploración | `WASD` / flechas | Movimiento alternativo cuando no hay destino |
| Exploración | `SHIFT` | Correr |
| Exploración | `J` / `K` / `C` | Disparar / golpear / agacharse |
| Rutas | Clic izquierdo | Pone el terreno elegido en la paleta |
| Rutas | Clic derecho | Restaura la celda al terreno por defecto |
| Rutas | `1` / `2` | Coloca inicio / meta en la celda bajo el ratón |
| Rutas | `TAB` | Muestra u oculta la rejilla |
| Rutas | `R` | Limpia el mapa |
| Rutas | Deslizador | Ritmo del jugador y de sus animaciones (ver §9) |

---

## 9. Limitaciones conocidas

Apuntadas para que no se interpreten como errores de implementación:

1. **El deslizador "Velocidad de animación" solo ralentiza, no acelera.** Por
   encima del 100% satura: el factor se queda en 1.0. Se hizo así a propósito,
   porque subirlo rompe la colisión y los rangos de la hoja de sprites. El valor
   inicial es 100: arrancar por debajo dejaba al jugador más lento que en el
   original.
2. **No hay botón de salir en el menú.** Se cierra la ventana con la X. `QUIT` está
   manejado.
3. **Los proyectiles solo se mueven en horizontal**, igual que en el original.
4. **Sin búsqueda implementada**: no hay BFS, Dijkstra ni A*. El panel, la
   rejilla, las marcas y los marcadores de inicio/meta ya están listos para
   alimentarlos.
5. **El jugador no es un buscador de caminos.** Con el ratón avanza en cardinal
   hacia el destino y se detiene si no progresa; en un laberinto con obstáculos
   rodeando el destino **no lo rodea**, abandona. El rodeo es justo lo que dará el
   algoritmo de búsqueda, no el controlador de movimiento.
6. **Los sonidos de pisadas** (`pisadas_pavimento.ogg`, `pisadas_tierra.ogg`) están
   en `assets/audio/` pero todavía no hay código que los reproduzca.
7. **No se pudo revisar la maquetación a ojo** durante el desarrollo, así que el
   aspecto final del menú, del panel y de los marcadores de inicio/meta merece una
   pasada visual manual.

---

## 10. Verificación

Esta copia no incluye la batería de tests headless (`verificar_terreno.py`) ni la
prueba con ventana real (`verificar_ventana_real.py`) de la versión completa. Si se
reintroducen, conviene que sigan comprobando, como mínimo:

- Que importar `simulador` **no abra ventana**, y que `config.py`, `paleta.py` y
  `terreno.py` carguen con `pygame` bloqueado.
- El catálogo: los tres terrenos con su costo, y que rechace costo 0, un
  intransitable con costo, códigos de más de un carácter, colores fuera de
  `0..255`, claves repetidas y texturas inexistentes.
- `mapas/exploracion.json`: 14 filas de 32, inicio y meta válidos, y que las celdas
  transitables formen una sola región alcanzable.
- Colisión, deslizamiento por el eje libre, movimiento cardinal y abandono de un
  destino inalcanzable.
- Que las cuatro vistas arrancan y dibujan, la navegación y el `ESC` funcionan, y
  `F5` recarga el JSON recolocando al jugador en un sitio libre.
- El editor de Rutas: paleta, pintado, restaurar, `TAB`, `R`, `1`/`2`, y que un
  clic en el panel no toque la rejilla.
- El deslizador: que el porcentaje escale el paso real, el ritmo de los cuadros y
  la paciencia de la vigilancia de atasco, y que el valor sobreviva al salto entre
  vistas.

> En el driver `dummy` el ratón **no se mueve**: `mouse.set_pos()` no hace nada y
> `mouse.get_pos()` siempre devuelve `(0, 0)`. Para probar algo que dependa de la
> posición del puntero hay que inyectarla. Lo mismo con las teclas.

---

## 11. Estado de verificación

- `IA.py` compila y abre ventana real sin errores.
- Las cuatro vistas renderizan; la navegación entre ellas y el `ESC` funcionan.
- Geometría: el mapa (960 px) es más ancho que el panel (340 px) y la rejilla cubre
  la ventana sin solaparse con el HUD. Exploración usa `(0, 110, 1300, 560)`.
- Los assets se resuelven por constantes de `config.py`; mover `assets/` y `mapas/`
  dentro de `simulador/` no dejó rutas rotas.
- Los sonidos de interfaz cargan desde `assets/audio/interfaz/`.
- `ironman.png` se recorta correctamente en 6 animaciones × 2 direcciones.
- El jugador llega a su destino sin temblar y se detiene en los bordes.
- El deslizador recorre 1→100 y propaga el valor; los rastros del cursor se
  desvanecen; los botones respetan el retardo de 400 ms.
- El terreno frena al jugador donde toca y los obstáculos bloquean de verdad.
