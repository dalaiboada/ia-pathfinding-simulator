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
**apreciar el funcionamiento de los algoritmos de búsqueda** (BFS, Dijkstra, A\*).

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

| Archivo                                     | Uso                                                       |
| ------------------------------------------- | --------------------------------------------------------- |
| `assets/img/juego/fondo.jpg`                | Fondo del menú (1920×1080, escalado a 1300×670)           |
| `assets/img/juego/ironman.png`              | Hoja del jugador, 576×384 = rejilla 9×6 de celdas 64×64   |
| `assets/img/juego/ultron.png`               | Hoja del enemigo (reservada para Persecución)             |
| `assets/img/mapa/tileset.jpg`               | Hoja de tiles 512×384 = 16×12 celdas de 32 px (suelo)     |
| `assets/img/juego/objetos/Animation2.png`   | Spritesheet de árbol animado (skin 1)                     |
| `assets/img/juego/objetos/Animation4.png`   | Spritesheet de árbol animado (skin 2)                     |
| `assets/img/juego/objetos/Animation5.png`   | Spritesheet de árbol animado (skin 3)                     |
| `assets/img/interfaz/cursor.png`            | Cursor personalizado (32×32)                              |
| `assets/img/interfaz/cursor_click.png`      | Rastro del cursor (32×32)                                 |
| `assets/fuentes/game.ttf`                   | Tipografía pixelada: títulos, botones, HUD                |
| `assets/audio/interfaz/presionar_boton.ogg` | Sonido de clic en botón                                   |
| `assets/audio/interfaz/hover_boton.ogg`     | Sonido al pasar por encima de un botón                    |
| `assets/audio/pisadas_pavimento.ogg`        | Pisadas sobre pavimento (usado por `TerrenoPavimento`)    |
| `assets/audio/pisadas_hierba.ogg`           | Pisadas sobre hierba (usado por `TerrenoHierba`)          |
| `assets/audio/interfaz/theme_menu.mp3`      | Tema del menú (otorga `musica.py`, en bucle)              |
| `assets/audio/interfaz/theme_vistas.mp3`    | Tema de las vistas de mapa (otorga `musica.py`, en bucle) |
| `mapas/exploracion.json`                    | Mapa de la vista Exploración (esquema v2)                 |
| `mapas/persecucion.json`                    | Mapa de la vista Persecución (esquema v2)                 |
| `mapas/rutas.json`                          | Mapa editable de la vista Rutas (esquema v2)              |

### Código

| Archivo                  | Rol                                                                    | Estado                      |
| ------------------------ | ---------------------------------------------------------------------- | --------------------------- |
| `IA.py`                  | **El juego.** `main()`, punto de entrada.                              | Activo                      |
| `config.py`              | Medidas, rutas de assets (tileset/audios), marcas, costo de referencia | Activo, sin pygame          |
| `paleta.py`              | Colores + `mezclar()`                                                  | Activo, sin pygame          |
| `arranque.py`            | `iniciar()`, `fuente()`, `comprobar_iniciado()`                        | Activo                      |
| `dibujo.py`              | Velo, rejilla, tarjeta, HUD, texto centrado                            | Activo                      |
| `busqueda.py`            | BFS, DFS, Dijkstra, A\*, Greedy y `ResultadoBusqueda`                  | Activo, sin pygame          |
| `motor.py`               | `Juego`: bucle principal, navegación y algoritmo activo                | Activo                      |
| `musica.py`              | Temas de fondo por vista: menú vs. vistas de mapa                      | Activo                      |
| `mapas/exploracion.json` | Mapa de la vista Exploración                                           | Activo, se recarga con `F5` |
| `mapas/persecucion.json` | Mapa de la vista Persecución                                           | Activo, se recarga con `F5` |
| `mapas/rutas.json`       | Mapa editable de la vista Rutas                                        | Activo, se recarga con `F5` |

```
simulador/
├── IA.py                          main(): iniciar() + Juego().ejecutar()
├── __init__.py                    reexporta Juego, iniciar, fuente, comprobar_iniciado
├── config.py                      medidas, rutas de assets, marcas, costo   (sin pygame)
├── paleta.py                      colores + mezclar()               (sin pygame)
├── arranque.py                    iniciar(), fuente(), comprobar_iniciado()
├── dibujo.py                      velo, rejilla, tarjeta, HUD, texto centrado
├── busqueda.py                    BFS, DFS, Dijkstra, A*, Greedy       (sin pygame)
├── motor.py                       Juego: bucle principal, navegación y algoritmo
├── musica.py                      temas de fondo: theme_menu.mp3 / theme_vistas.mp3
├── assets/
│   ├── img/
│   │   ├── juego/                 fondo.jpg, ironman.png, ultron.png
│   │   ├── mapa/                  tileset.jpg (512x384, tiles de 32 px)
│   │   └── interfaz/              cursor.png, cursor_click.png
│   ├── fuentes/                   game.ttf
│   └── audio/
│       ├── interfaz/              presionar_boton.ogg, hover_boton.ogg
│       ├── pisadas_pavimento.ogg
│       └── pisadas_hierba.ogg
├── mapas/
│   ├── exploracion.json           17 x 40 celdas, 3 capas (esquema v2)
│   ├── persecucion.json           17 x 40 celdas, 3 capas (esquema v2)
│   └── rutas.json                 17 x 30 celdas, 3 capas (esquema v2)
├── entidades/
│   ├── proyectil.py               Proyectil
│   ├── jugador.py                 Jugador + obtener_sub_cuadros()
│   └── enemigo.py                 Enemigo (sprite ultron.png, 4 direcciones)
├── mundo/
│   ├── terreno.py                 Terreno y subclases (física)        (sin pygame)
│   ├── objetos.py                 ObjetoMapa y ObjetoCofre
│   ├── catalogo.py                Catalogo: tileset, audios, IDs
│   ├── mapa_terreno.py            MapaTerreno: capas suelo/objetos, colisión, render
│   └── mapa.py                    MapaRutas, la rejilla editable de Rutas
├── interfaz/
│   ├── boton.py                   BotonTexto
│   ├── cursor.py                  CustomMouse
│   ├── deslizador.py              DeslizadorCyber
│   └── selector.py                SelectorCyber
└── vistas/
    ├── base.py                    Vista
    ├── menu.py                    VistaMenu
    ├── exploracion.py             VistaExploracion
    ├── rutas.py                   VistaControladorRutas
    └── persecucion.py             VistaPersecucion
```

Son 29 módulos `.py` con responsabilidad única.

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

| Sección           | Contenido                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| Configuración     | Medidas, rutas de assets, FPS, marcas de búsqueda, costos, ritmo del deslizador                    |
| Paleta            | Paleta cyberpunk + `mezclar()`                                                                     |
| Arranque          | `init()`, `font.init()`, `display.set_mode()`, fuentes                                             |
| Helpers de dibujo | `obtener_sub_cuadros`, `crear_velo`, rejilla, tarjeta, HUD                                         |
| Componentes       | `BotonTexto`, `CustomMouse`, `DeslizadorCyber`, `Proyectil`, `Jugador`, `MapaTerreno`, `MapaRutas` |
| Vistas            | `Vista` (base) + menú, exploración, rutas, persecución                                             |
| Juego             | `Juego` con el bucle principal, y `main()` en `IA.py`                                              |

### Punto de arranque

`arranque.py` es el **único** sitio que abre la ventana. Expone:

| Función                | Qué hace                                                                                                                   |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `iniciar()`            | `init()`, `mixer.init()` (tolerante a fallos), `font.init()`, `set_mode()`, `set_caption()`, reloj y fuentes. Idempotente. |
| `fuente(clave)`        | Devuelve una fuente por clave; el `KeyError` lista las claves válidas.                                                     |
| `comprobar_iniciado()` | Lanza `RuntimeError` con mensaje claro si se usa el juego antes de `iniciar()`.                                            |

Claves de fuente: `titulo_menu`, `subtitulo_menu`, `boton`, `hud`, `cyber_titulo`,
`cyber_etiqueta`, `cyber_valor`, `instrucciones`, `cyber_diminuta`.

Antes era un juego monolítico de más de mil líneas en un `IA.py`; ahora `IA.py`
son 13 líneas y cada módulo tiene una sola responsabilidad.

### Grafo de dependencias (acíclico)

Nombres planos desde la raíz de `simulador/`:

```
config, paleta          → nada
busqueda                → nada                              (sin pygame)
arranque                → config
dibujo                  → arranque, config, paleta
mundo.terreno           → config                          (sin pygame)
mundo.objetos           → pygame
mundo.catalogo          → config, pygame, mundo.terreno, mundo.objetos
mundo.mapa_terreno      → config, paleta, pygame, mundo.catalogo, busqueda
mundo.mapa              → pygame, mundo.mapa_terreno
entidades.proyectil     → paleta
entidades.jugador       → config, entidades.proyectil
entidades.enemigo       → busqueda, config, paleta
interfaz.boton          → config, pygame
interfaz.cursor         → pygame
interfaz.deslizador     → paleta
interfaz.selector       → arranque, paleta
vistas.base             → nada
vistas.*                → arranque, busqueda, config, paleta, dibujo, y lo que necesitan
motor                   → arranque, config, vistas, interfaz.cursor, musica
musica                  → config                                 (pygame: mixer.music)
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

| Estado     | Fila         | Cuadros | Velocidad de fotograma |
| ---------- | ------------ | ------- | ---------------------- |
| `reposo`   | 0            | 3       | 0.15                   |
| `caminar`  | 1            | 6       | 0.15                   |
| `disparo`  | 2 (cols 3–5) | 3       | 0.18                   |
| `agachado` | 2 (cols 6–8) | 3       | 0.15                   |
| `golpe`    | 3            | 4       | 0.18                   |
| `correr`   | 4            | 6       | 0.22                   |

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

**Pisadas:** cada fotograma, `_actualizar_pasos()` mira el avance real del rect.
Si se movió al menos un píxel, consulta `mapa.terreno_bajo()` en los pies
(`rect.bottom - 2`), y reproduce su `sonido` cuando pasa su `intervalo_pasos_ms`
(500 ms en hierba, 350 en pavimento). Al detenerse, el temporizador se reinicia.
Si el audio no está disponible (`Terreno.sonido is None`), no pasa nada.

### Terreno

`mundo/terreno.py` define los tipos de celda **orientados a objetos**. Módulo de
datos puros, sin pygame, como `config.py`. Cada tipo encapsula su física:

| Clase              | Clave       | Nombre    | Transitable | Costo  | `factor_vel` | Pisadas                         |
| ------------------ | ----------- | --------- | ----------- | ------ | ------------ | ------------------------------- |
| `TerrenoHierba`    | `hierba`    | Hierba    | sí          | `2.0`  | `0.5`        | 500 ms, `pisadas_hierba.ogg`    |
| `TerrenoPavimento` | `pavimento` | Pavimento | sí          | `1.0`  | `1.0`        | 350 ms, `pisadas_pavimento.ogg` |
| `TerrenoMuro`      | `muro`      | Muro      | no          | `null` | `null`       | —                               |

`costo` es `None` **exactamente** cuando el terreno es intransitable, y siempre
positivo cuando es transitable. Cargar un catálogo que rompa ese invariante es un
error, no algo que se normalice en silencio.

La velocidad **se deriva del costo** (no hay una segunda fuente de verdad):

```
factor_vel = COSTO_REFERENCIA / costo
velocidad  = max(VELOCIDAD_MINIMA, base * factor_vel)
```

Con `COSTO_REFERENCIA = 1.0` y `VELOCIDAD_MINIMA = 1.0`: pavimento no penaliza,
la hierba divide la velocidad por dos, y ningún terreno puede inmovilizar al
jugador. El `intervalo_pasos_ms` y el sonido sí se declaran por clase, porque no
se pueden deducir del costo.

El catálogo se arma con `cargar_catalogo()` a partir del bloque `terrenos` del
JSON (la clave elige la clase y los campos sobreescriben sus valores por defecto).
Sin bloque, `catalogo_por_defecto()` devuelve los tres tipos.

### MapaTerreno

Rejilla de celdas organizada en **tres capas**, como en el ejemplo de referencia
(ya eliminado del repo):

| Capa      | Matriz    | Contenido                                                      |
| --------- | --------- | -------------------------------------------------------------- |
| Suelo     | `suelo`   | ID de tile del tileset (base, bordes y esquinas de pavimento). |
| Objetos   | `objetos` | ID de objeto estático (cofres) o `OBJETO_NINGUNO`.             |
| Entidades | —         | Los sprites dinámicos, que dibuja la vista por encima.         |
| Búsqueda  | `marcas`  | `MARCA_NINGUNA` / `MARCA_VISITADA` / `MARCA_CAMINO`.           |

`inicio` y `meta` son **coordenadas**, no estados de celda. Se dibujan como anillos
con cruz (`COLOR_INICIO` cian, `COLOR_META` magenta) por encima de objetos y bajo
la rejilla. Son únicos: al mover uno, su celda anterior recupera el suelo por
defecto (`_liberar_celda_anterior`).

`preparar_capa()` pre-renderiza `capa_suelo` y `capa_objetos`. El orden de apilado
es suelo → objetos → marcas → inicio/meta → rejilla → entidades. La rejilla
(`mostrar_rejilla`) arranca **oculta** por defecto y cada vista la alterna con
`TAB`; `F5` conserva el estado. Las **marcas de la búsqueda** (visitados/camino)
solo se dibujan si la rejilla está visible: `dibujar_marcas` no pinta nada cuando
`mostrar_rejilla` es `False`.

**Colisión:** una celda está `bloqueada` si su suelo es intransitable **o** si
contiene un objeto sólido (`objeto.es_solido`). `superficie_libre`, `desplazar` y
`punto_libre_cerca` usan esa definición, así que el jugador choca tanto con muros
como con cofres.

**Enganche de la búsqueda:** `marca_en`, `marcar`, `limpiar_marcas` y
`celdas_marcadas` existen y funcionan. `buscar_camino` invoca `marcar` mientras
expande, pinta el resultado con `dibujar_marcas` y llama a `limpiar_marcas()`
antes de la siguiente ejecución.

Métodos de colisión que usa el jugador:

| Método                              | Qué hace                                              |
| ----------------------------------- | ----------------------------------------------------- |
| `superficie_libre(rect)`            | El rect cabe entero y no toca suelo ni objeto sólido. |
| `desplazar(rect, dx, dy)`           | Devuelve lo que se admite, resolviendo eje a eje.     |
| `punto_libre_cerca(centro, tamaño)` | Busca a anillos crecientes un sitio válido.           |

`desplazar` **devuelve** el desplazamiento y no mueve el rect: primero prueba el
movimiento entero y, si choca, prueba X e Y por separado para que el jugador
deslice por el eje despejado.

### Catálogo y objetos

`mundo/catalogo.py` es el gestor central (equivalente a la clase `Catalogo` del
ejemplo). Carga **una sola vez** el tileset (`assets/img/mapa/tileset.jpg`) y los
audios, y traduce los IDs de las matrices:

- `tile(id)` → superficie recortada del tileset (con el giro ya aplicado);
- `terreno(id)` → instancia de `Terreno`, para la física;
- `objeto(id)` → instancia de `ObjetoMapa`.

`Catalogo.por_defecto()` reproduce el mapeo del ejemplo (hierba `0`, pavimento
base `1`, bordes `2–5`, esquinas `6–9`, muro `100`, cofre `101`).
`Catalogo.desde_json()` lo construye desde el bloque `tiles` del mapa.

`mundo/objetos.py` define:

- `ObjetoMapa` (base: `es_solido`, `imagen`, `interactuar()`)
- `ObjetoCofre` (sólido e interactivo)
- `ObjetoAnimado` (base para objetos con spritesheets animados)
- `ObjetoArbol` (árbol animado, sólido, con spritesheet de 6×3 frames)

La imagen estática se toma del tileset si el JSON declara `tile: [col, fila]`;
si no, hay un dibujo procedural. Para objetos animados, se usa `spritesheet`
con la ruta del archivo PNG (relativa a la carpeta del mapa o absoluta).

**Objetos animados:** `ObjetoAnimado` carga spritesheets divididos en filas y columnas,
extrae los frames con `subsurface` y actualiza `imagen` en cada `actualizar()`. Cada
instancia mantiene su propio índice de animación. `MapaTerreno.actualizar_objetos_animados()`
llama a `actualizar()` en todos los objetos animados y reconstruye `capa_objetos`
para que se reflejen los nuevos frames en la renderización.

`MapaTerreno` rastrea objetos animados en una lista (`objetos_animados`) que se
construye al cargar el mapa: cualquier objeto cuya clase herede de `ObjetoAnimado`
se agrega automáticamente. Las vistas (`exploracion.py`, `persecucion.py`, `rutas.py`)
llaman a `mapa.actualizar_objetos_animados()` en su ciclo `actualizar()`.

### Formato del JSON

```json
{
  "version": 2,
  "nombre": "Patio de pruebas",
  "tamano_celda": 32,
  "tileset": "../assets/img/mapa/tileset.jpg",
  "terrenos": [{ "clave": "hierba", "costo": 2.0, "intervalo_pasos_ms": 500 }],
  "tiles": [
    { "id": 0, "terreno": "hierba", "col": 0, "fila": 0 },
    { "id": 3, "terreno": "pavimento", "col": 6, "fila": 4, "giro": 180 }
  ],
  "objetos": [
    { "id": 101, "tipo": "cofre", "solido": true },
    {
      "id": 102,
      "tipo": "arbol_animado",
      "spritesheet": "../assets/img/juego/objetos/Animation5.png",
      "solido": true
    }
  ],
  "capas": [
    {
      "nombre": "suelo",
      "datos": [
        [0, 1, 1, 0],
        [0, 0, 100, 0]
      ]
    },
    {
      "nombre": "objetos",
      "datos": [
        [0, 0, 0, 0],
        [0, 101, 0, 0]
      ]
    }
  ],
  "inicio": { "fila": 0, "col": 0 },
  "meta": { "fila": 1, "col": 3 }
}
```

**Objetos animados en JSON:** además de `tipo` y `solido`, pueden incluir:

- `spritesheet`: ruta al PNG con la hoja de animación (relativa a la carpeta del mapa o absoluta)
- `tile`: opcional, para imagen estática del tileset (se ignora si hay spritesheet)

Para objetos estáticos (como `cofre`), `tile` es opcional; si no se proporciona, se usa
un dibujo procedural. Para objetos animados, `spritesheet` es obligatorio.

Decisiones que conviene no cambiar sin pensarlo:

- Las matrices usan **IDs numéricos explícitos** (como en el ejemplo). El loader
  acepta además filas de texto (`p`/`t`/`#`) por compatibilidad.
- Las filas de `datos` deben medir **lo mismo** entre sí.
- La capa de suelo se busca entre `NOMBRE_CAPAS_SUELO` (`suelo`, `terreno`,
  `terrenos`); la de objetos entre `NOMBRE_CAPAS_OBJETOS` (`objetos`, ...) y es
  opcional.
- `inicio` es **obligatorio** y debe caer en una celda no bloqueada. `meta` es
  opcional.
- Un mapa **más grande que la vista es un error, no un recorte**. Un mapa más
  pequeño sí cabe: las celdas que sobran se rellenan con el suelo por defecto.
- IDs de suelo fuera de la lista `tiles`, o de objeto fuera de `objetos`, son un
  error con fila y columna.

Si el JSON no se puede leer, `VistaExploracion` **avisa por consola y dibuja un
patio generado por código** (perímetro bloqueado y avenida en cruz), para que el
juego siga siendo jugable. `F5` sobrevive a los dos casos.

### MapaRutas

`MapaRutas` hereda de `MapaTerreno` y añade la política de edición de su vista.
Rejilla 30×17 = 510 celdas de 32 px, en el área `(0, 110, 960, 544)`.

Carga `mapas/rutas.json` (el mapa editable de la vista); si falta o está roto,
empieza con `Catalogo.por_defecto()` y todo en hierba. Gestiona `TAB`, `R` y `B`;
la pintura la hace la vista. `B` ejecuta `autotile_pavimento()`, que recalcula
borde/esquina de cada celda de pavimento según sus vecinos (las matrices siguen
guardando IDs explícitos). `F5` la recarga desde disco.

### Búsqueda de caminos

`busqueda.py` es lógica pura (sin pygame) y no sabe de mapas ni de sprites: solo
de una "rejilla" que exponga `filas`, `columnas`, `bloqueada(fila, col)` y
`costo_en(fila, col)` (coste de **entrar** en la celda). El movimiento es cardinal
(4 vecinos), igual que el del jugador.

| Función                                    | Optimiza    | Notas                                                      |
| ------------------------------------------ | ----------- | ---------------------------------------------------------- |
| `buscar_bfs`                               | nº de pasos | Ignora el coste.                                           |
| `buscar_dfs`                               | —           | Rápido, caminos largos y sinuosos.                         |
| `buscar_dijkstra`                          | coste real  | No se expone en la UI.                                     |
| `buscar_astar`                             | coste real  | `coste` + heurística Manhattan (`COSTO_MINIMO` admisible). |
| `buscar_greedy`                            | —           | Solo heurística; rápido, no óptimo.                        |
| `buscar(algoritmo, rejilla, inicio, meta)` | —           | Despacha; `ValueError` si el nombre no existe.             |

`ALGORITMOS = ("astar", "bfs", "dfs", "greedy")` es lo que ofrece la UI;
`NOMBRES_ALGORITMO` da las etiquetas. `buscar` devuelve un `ResultadoBusqueda` con
`camino` (incluye inicio y meta), `visitados` (orden de expansión), `costo` y
`algoritmo`.

`MapaTerreno.buscar_camino(inicio, meta, algoritmo, rejilla=None)` ejecuta el
algoritmo, pinta `MARCA_VISITADA` sobre los visitados y `MARCA_CAMINO` sobre el
camino, y devuelve el resultado. `rejilla_para(tamano)` devuelve una
`RejillaEntidad`: una celda se bloquea si el rect de la entidad (su tamaño en px)
centrado en ella no cabe sin tocar suelo intransitable ni objeto sólido. El
jugador mide 64 px (2×2 celdas), así que usa su propia rejilla; los enemigos
(≈62 px) usan el mapa tal cual.

El **estado activo** vive en `Juego`: `algoritmo_busqueda` (personaje, por
defecto `ALGORITMO_INICIAL = "astar"`, se elige en Rutas) y `algoritmo_enemigo`
(enemigos, `ALGORITMO_ENEMIGO_INICIAL = "astar"`, se elige en Persecución).
`Jugador.fijar_ruta(waypoints)` guarda los centros de celda a seguir y
`avanzar_por_ruta()` los recorre un eje por fotograma; `cancelar_ruta()` la
descarta.

`entidades/enemigo.py` usa la hoja `ultron.png` (576×384 = 12×8 cuadros de 48 px):
cuatro animaciones de tres cuadros (filas 0 abajo, 1 izquierda, 2 derecha, 3
arriba), escaladas por `ESCALA_ENEMIGO` (1.3 → sprite de ≈62 px) igual que en la
demo de `villain3.png`. Al moverse orienta el sprite y avanza de cuadro a
`VELOCIDAD_ANIMACION_ENEMIGO`; en reposo se queda en el cuadro central. Si la
imagen no carga, cae a un cuadrado plano para no romper la vista.

Ve al jugador si está a ≤ `CAMPO_VISION_ENEMIGO` celdas (Chebyshev) con línea de
visión libre (Bresenham); a partir de ahí **queda alerta para siempre**. Con
`"ninguno"` persigue en línea recta; con un algoritmo, recalcula ruta cada
`RECALCULO_RUTA_ENEMIGA` fotogramas o si el jugador cambia de celda.

---

## 7. Las cuatro vistas

`musica.py` da a cada pantalla su tema de fondo en bucle: `theme_menu.mp3` suena
solo en el menú y `theme_vistas.mp3` en las tres vistas de mapa. `Juego.ir_a()`
cambia el tema en cada navegación y no reinicia una pista que ya está sonando; si
el `mixer` no está disponible o falta el archivo, se queda en silencio sin romper.

### Menú

Fondo `assets/img/juego/fondo.jpg` con un velo degradado para dar legibilidad al
texto. Tres botones `BotonTexto` que enlazan con `juego.ir_a(...)`. Cada botón
tarda 400 ms en su animación de destello antes de navegar. Los botones suenan al
pasar por encima y al hacer clic (`hover_boton.ogg` / `presionar_boton.ogg`).

### Exploración

El patio de pruebas. El mapa sale de `mapas/exploracion.json` (17 filas × 40
columnas) y se recarga con `F5`.

El jugador nace en la celda `inicio` del JSON. Al hacer clic izquierdo se planifica
una ruta con el algoritmo activo (`juego.algoritmo_busqueda`, A\* por defecto) hasta
la celda del cursor, se pintan `MARCA_VISITADA`/`MARCA_CAMINO` y el jugador la sigue
rodeando los obstáculos. Con WASD sigue habiendo movimiento cardinal libre, con un
marcador de ondas cian en el destino del clic. Choca contra los obstáculos y los
cofres, y va más despacio por la hierba que por el pavimento.

Si el JSON falta o está roto, avisa por consola y dibuja un patio de respaldo
generado por código.

### Controlador de rutas

El reparto pedido en el enunciado: mapa **más ancho** que el panel.

- **Mapa** (izquierda, 960 px): rejilla 30×17 = 510 celdas, que carga
  `mapas/rutas.json` (o toda hierba si falta); en ella nacen un jugador (en
  `inicio`) y un marcador de meta, y el jugador recorre la ruta.
- **Panel** (derecha, 340 px): selector de algoritmo, paleta de 3 terrenos + cofre, 6
  tarjetas y el deslizador.

Reparto vertical del panel:

| Banda                 | Y         | Altura |
| --------------------- | --------- | ------ |
| Título y estado       | 18 – 68   | —      |
| Selector de algoritmo | 92        | 30     |
| Paleta de 3 terrenos  | 138       | 34     |
| 6 tarjetas, paso 56   | 184 → 512 | 48     |
| Divisor               | 522       | —      |
| Etiqueta de velocidad | 536       | —      |
| Deslizador            | 566       | 10     |

Un `SelectorCyber` de 4 opciones (A\*, BFS, DFS, Greedy) elige el algoritmo del
personaje; escribirlo en `juego.algoritmo_busqueda`. `ESPACIO` ejecuta la búsqueda
de `inicio` a `meta`, anima al jugador a lo largo de la ruta y llena la telemetría:
`Nodos Explorados` (tamaño de `visitados`) y `Costo Ruta` (coste real del camino,
que lleva el nombre del algoritmo elegido). Cualquier edición del mapa (pintar,
borrar, `TAB`, `R`, `B`, mover `1`/`2`) limpia marcas y telemetría.

Las tarjetas de `Posición`, `Inicio` y `Meta` leen en vivo la celda bajo el ratón.
`Terreno` muestra el tipo de la celda apuntada con su costo, o `BLOQUEA` si es
intransitable.

La paleta incluye los tres terrenos y el cofre. Al pintar pavimento se guarda el
ID base; `B` recalcula los bordes y esquinas de todo el pavimento. El clic derecho
restaura el suelo por defecto y borra el objeto de la celda.

### Persecución

El jugador escapa por un mapa real de 3 capas (carga `mapas/persecucion.json`, se
recarga con `F5`, con respaldo generado por código si falta) y 5 enemigos arrancan
en fila por la parte superior. El clic izquierdo lanza al jugador con el algoritmo
activo (`juego.algoritmo_busqueda`), con el mismo comportamiento que en
Exploración.

Un `SelectorCyber` de 5 opciones (Ninguno, A\*, BFS, DFS, Greedy) elige la IA
enemiga (`juego.algoritmo_enemigo`). El círculo rosa translúcido de cada enemigo
marca su campo de visión: cuando el jugador entra en él con línea de visión libre,
el enemigo queda alerta para siempre y empieza a perseguir usando sus animaciones
de `ultron.png`.

---

## 8. Controles

| Vista                     | Entrada          | Efecto                                                     |
| ------------------------- | ---------------- | ---------------------------------------------------------- |
| Menú                      | Clic en botón    | Navega a la vista correspondiente (tras 400 ms)            |
| Todas                     | `ESC`            | Vuelve al menú                                             |
| Todas                     | `TAB`            | Muestra u oculta la rejilla (oculta por defecto)           |
| Exploración               | Clic izquierdo   | Planifica una ruta con el algoritmo activo hasta el cursor |
| Exploración               | `WASD` / flechas | Movimiento cardinal libre (se ignora mientras hay ruta)    |
| Exploración               | `SHIFT`          | Correr                                                     |
| Exploración               | `J` / `K` / `C`  | Disparar / golpear / agacharse                             |
| Rutas                     | Clic izquierdo   | Pinta el terreno/objeto elegido en la paleta               |
| Rutas                     | Clic derecho     | Restaura el suelo y borra el objeto de la celda            |
| Rutas                     | Selector         | Elige el algoritmo que usa el personaje                    |
| Rutas                     | `ESPACIO`        | Ejecuta la búsqueda `inicio` → `meta` y anima la ruta      |
| Rutas                     | `1` / `2`        | Coloca inicio / meta en la celda bajo el ratón             |
| Rutas                     | `B`              | Recalcula bordes y esquinas del pavimento                  |
| Rutas                     | `R`              | Limpia el mapa                                             |
| Rutas                     | Deslizador       | Ritmo del jugador y de sus animaciones (ver §9)            |
| Persecución               | Clic izquierdo   | Lanza al jugador por la ruta hasta el cursor               |
| Persecución               | Selector         | Elige la IA de los enemigos (incluye "Ninguno")            |
| Exploración / Persecución | `F5`             | Recarga el mapa de la vista activa                         |
| Rutas                     | `F5`             | Recarga `mapas/rutas.json`                                 |

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
4. **El juego no guarda los mapas editados.** Rutas recarga `rutas.json` con `F5`
   desde el disco, pero la pintura en vivo no se serializa: si quieres conservar
   un diseño, edita el JSON a mano.
5. **El movimiento clásico del ratón convive con las rutas.** El clic ya planifica
   un camino (`buscar_camino` + `fijar_ruta`), pero `avanzar_hacia_objetivo()`
   —el avance cardinal directo que abandona si no progresa— sigue en el código por
   si alguna vista lo usa; ya no es lo que dispara el clic izquierdo.
6. **El muro no tiene tile en el tileset** (id `100` usa un color plano de
   respaldo). Los pasillos de una sola celda de ancho usan el tile base de
   pavimento: el esquema de bordes del tileset no tiene una variante "recta".
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
- El catálogo: los tres terrenos con su costo y `factor_vel` derivado, ids de tile
  dentro del recorte del tileset, y que rechace costo 0, un intransitable con
  costo, tipos desconocidos y referencias a tiles u objetos inexistentes.
- Los tres JSON de `mapas/` (exploración y persecución de 17×40, rutas de 17×30):
  inicio y meta válidos, una sola región transitable, y que la capa de objetos
  solo contenga ids declarados.
- Colisión (suelo intransitable **y** objeto sólido), deslizamiento por el eje
  libre, movimiento cardinal y abandono de un destino inalcanzable.
- Que las cuatro vistas arrancan y dibujan, la navegación y el `ESC` funcionan, y
  `F5` recarga el JSON recolocando al jugador en un sitio libre.
- El editor de Rutas: paleta de terrenos + objetos, pintado, restaurar, `TAB`, `R`,
  `B` (auto-borde), `1`/`2`, y que un clic en el panel no toque la rejilla.
- La búsqueda: los cuatro algoritmos encuentran camino entre inicio y meta, BFS y
  A\* respetan la interfaz de la rejilla, `buscar_camino` pinta visitados y camino,
  y `rejilla_para(64)` bloquea lo que no cabe.
- La persecución: los enemigos solo se mueven tras ver al jugador (campo de visión
  - línea de visión), con `"ninguno"` en línea recta y con un algoritmo rodeando
    obstáculos.
- Las pisadas: `terreno_bajo()` devuelve el terreno correcto bajo los pies y el
  temporizador respeta `intervalo_pasos_ms`.
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
- El mapa de 3 capas carga `exploracion.json` y dibuja suelo y objetos; el muro y
  las variantes de pavimento se recortan del tileset (el muro, por color plano).
- `B` recalcula bordes y esquinas del pavimento; los cofres bloquean la colisión y
  el clic derecho los borra.
- `terreno_bajo()` devuelve el terreno correcto bajo los pies del jugador; las
  pisadas suenan con su `intervalo_pasos_ms` cuando hay audio disponible.
- La búsqueda funciona de punta a punta: A\* da coste 54 (todo hierba) con 252 nodos
  explorados frente a los 364 de BFS en la rejilla de 30×17; el selector cambia
  `juego.algoritmo_busqueda` y `ESPACIO` llena `Nodos Explorados`/`Costo Ruta`.
- En Persecución hay 5 enemigos con sprite de `ultron.png` que ciclan las 4
  animaciones de 3 cuadros (escala 1.3 → 62 px) y se activan al entrar el jugador
  en su campo de visión; en la prueba headless, 2 de 5 quedaron alertados.
- Los tres mapas se generaron y cargan: `exploracion.json` (17×40, inicio (2,2),
  meta (14,37)), `rutas.json` (17×30, inicio (8,1), meta (8,28)) y
  `persecucion.json` (17×40, inicio (14,20)); todos con inicio/meta en celda libre.
- `TAB` alterna la rejilla en las tres vistas de mapa (arranca oculta) y `F5`
  conserva su estado al recargar.
- Rutas ya carga `mapas/rutas.json`: con el mapa nuevo, `ESPACIO` da 28 nodos
  explorados, costo 27 y camino de 28 celdas (A\*).
- `logica_de_mapa/` (demo de referencia) se eliminó una vez integrados su tileset
  y sus sonidos.
