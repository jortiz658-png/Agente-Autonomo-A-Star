import pygame
import math
import random
from queue import PriorityQueue

# Inicializar fuente de Pygame
pygame.font.init()

# --- CONFIGURACIÓN DE LA VENTANA ---
WIDTH = 700
ROWS = 25 # Número de filas/columnas (ajustar para cambiar tamaño de celdas)
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Visualizador del Algoritmo A* - Inteligencia Artificial")

# --- COLORES ---
WHITE = (240, 244, 248)    # Fondo / Vacío
BLACK = (47, 62, 70)       # Pared (Obstáculo)
BLUE = (33, 133, 208)      # Inicio
PURPLE = (142, 68, 173)    # Meta
GREEN = (46, 204, 113)     # Frontera (Open Set)
RED = (231, 76, 60)        # Visitado (Closed Set)
YELLOW = (241, 196, 15)    # Ruta Final
LINE_COLOR = (200, 200, 200)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == GREEN
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == BLUE
    def is_end(self): return self.color == PURPLE

    def reset(self): self.color = WHITE
    def make_start(self): self.color = BLUE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = PURPLE
    def make_path(self): self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Abajo
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Arriba
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Derecha
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Izquierda
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

# --- HEURÍSTICA: Distancia de Manhattan ---
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not current.is_start():
            current.make_path()
        draw()

# --- ALGORITMO A* ---
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

# --- FUNCIONES DE DIBUJO Y CREACIÓN ---
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, LINE_COLOR, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, LINE_COLOR, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.display.update()

def generate_random_maze(grid, start, end):
    for row in grid:
        for node in row:
            if node != start and node != end:
                node.reset()
                # 30% de probabilidad de ser pared
                if random.random() < 0.3:
                    node.make_barrier()

def main(win, width):
    grid = make_grid(ROWS, width)
    start = grid[1][1]
    end = grid[ROWS-2][ROWS-2]
    
    start.make_start()
    end.make_end()

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # ESPACIO para iniciar el algoritmo
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # 'R' para generar laberinto aleatorio
                if event.key == pygame.K_r:
                    generate_random_maze(grid, start, end)

                # 'C' para limpiar el tablero
                if event.key == pygame.K_c:
                    start = grid[1][1]
                    end = grid[ROWS-2][ROWS-2]
                    for row in grid:
                        for node in row:
                            node.reset()
                    start.make_start()
                    end.make_end()

            # (Opcional) Dibujar paredes con el click izquierdo del mouse
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                row, col = pos[0] // (width // ROWS), pos[1] // (width // ROWS)
                node = grid[row][col]
                if node != start and node != end:
                    node.make_barrier()

            # (Opcional) Borrar paredes con el click derecho del mouse
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = pos[0] // (width // ROWS), pos[1] // (width // ROWS)
                node = grid[row][col]
                if node != start and node != end:
                    node.reset()

    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)