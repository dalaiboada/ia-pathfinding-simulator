# 🤖 Simulador de Rutas y Movimiento en Espacios de Estado

<img src="https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54" align="center"> &nbsp;&nbsp; <img src="https://www.pygame.org/docs/_images/pygame_logo.png" width="100" alt="Pygame" align="center">

Este repositorio contiene un proyecto académico desarrollado formalmente para la cátedra de **Inteligencia Artificial** en el marco de mis **estudios universitarios**. 

Su propósito principal es servir como un banco de pruebas interactivo, programado en Python y Pygame, diseñado para **apreciar, analizar y comparar el funcionamiento de los algoritmos de búsqueda en espacios de estado** (tanto ciegos como informados).

## 🎓 Contexto Académico
* **Materia:** Inteligencia Artificial
* **Nivel:** Educación Superior / Universitaria
* **Objetivo Teórico:** Modelado de entornos mediante grafos de rejilla, evaluación de funciones heurísticas, expansión de nodos y recolección de métricas de rendimiento en algoritmos de *Pathfinding*.

---

## Características Principales
* **Visualización en Tiempo Real:** Observa detalladamente cómo exploran el espacio de estados los algoritmos clásicos (**BFS, Dijkstra y A***).
* **Panel de Telemetría:** Módulo de estadísticas cyberpunk para recolectar y contrastar las métricas reales de cada búsqueda (nodos expandidos, tiempo de ejecución, costo del camino).
* **Entorno de Rejilla Editable:** Soporte para mapas dinámicos a través de archivos JSON (`mapas/exploracion.json`) que permiten modificar muros y costes de terreno.
* **Comportamiento de Agentes (Enemigos):** Vista dedicada a la persecución de objetivos esquivando obstáculos de forma inteligente.
