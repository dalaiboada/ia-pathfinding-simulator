import pygame
import sys

# Inicialización de Pygame
pygame.init()

# Dimensiones de la ventana
VENTANA_ANCHO, VENTANA_ALTO = 640, 480
pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
pygame.display.set_caption("Animación de Sprite en Pygame - 48x48")

# Dimensiones reales de cada celda en la hoja (576 // 12 = 48, 384 // 8 = 48)
FRAME_W = 48
FRAME_H = 48
ESCALA = 1.3  # Escala visual para la ventana
VELOCIDAD = 3

# Cargar la hoja de sprites
try:
    sprite_sheet = pygame.image.load("villain3.png").convert_alpha()
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    pygame.quit()
    sys.exit()

def obtener_frame(hoja, col, fila, w=FRAME_W, h=FRAME_H, escala=ESCALA):
    rect = pygame.Rect(col * w, fila * h, w, h)
    frame = pygame.Surface((w, h), pygame.SRCALPHA)
    frame.blit(hoja, (0, 0), rect)
    if escala != 1:
        frame = pygame.transform.scale(frame, (w * escala, h * escala))
    return frame

# Filas: 0 = Abajo, 1 = Izquierda, 2 = Derecha, 3 = Arriba
animaciones = {
    "down":  [obtener_frame(sprite_sheet, col, 0) for col in range(3)],
    "left":  [obtener_frame(sprite_sheet, col, 1) for col in range(3)],
    "right": [obtener_frame(sprite_sheet, col, 2) for col in range(3)],
    "up":    [obtener_frame(sprite_sheet, col, 3) for col in range(3)],
}

class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direccion = "down"
        self.frame_actual = 1
        self.contador_anim = 0.0
        self.velocidad_anim = 0.15

    def mover(self, dx, dy):
        moviendose = dx != 0 or dy != 0

        if dx < 0:
            self.direccion = "left"
        elif dx > 0:
            self.direccion = "right"
        elif dy < 0:
            self.direccion = "up"
        elif dy > 0:
            self.direccion = "down"

        self.x += dx * VELOCIDAD
        self.y += dy * VELOCIDAD

        if moviendose:
            self.contador_anim += self.velocidad_anim
            self.frame_actual = int(self.contador_anim) % 3
        else:
            self.frame_actual = 1
            self.contador_anim = 1.0

    def dibujar(self, superficie):
        sprite = animaciones[self.direccion][self.frame_actual]
        superficie.blit(sprite, (self.x, self.y))

jugador = Jugador(VENTANA_ANCHO // 2 - (FRAME_W * ESCALA) // 2,
                  VENTANA_ALTO // 2 - (FRAME_H * ESCALA) // 2)

reloj = pygame.time.Clock()

ejecutando = True
while ejecutando:
    reloj.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    teclas = pygame.key.get_pressed()
    dx, dy = 0, 0
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        dx -= 1
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        dx += 1
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
        dy -= 1
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
        dy += 1

    jugador.mover(dx, dy)

    pantalla.fill((40, 44, 52))
    jugador.dibujar(pantalla)

    pygame.display.flip()

pygame.quit()
sys.exit()