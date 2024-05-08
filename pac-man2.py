import pygame
import random
import math
from queue import PriorityQueue

# Inisialisasi warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Inisialisasi ukuran layar dan grid
CELL_SIZE = 20
GRID_WIDTH = 28
GRID_HEIGHT = 31
MARGIN = 1
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + (GRID_WIDTH + 1) * MARGIN
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + (GRID_HEIGHT + 1) * MARGIN

# Inisialisasi arah pergerakan
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Inisialisasi kecepatan gerakan hantu
GHOST_SPEED = 0.05

# Inisialisasi kelas node
class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.wall = False

# Inisialisasi kelas Pacman
class Pacman:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.score = 0

    def move(self, direction, grid):
        next_row = self.row + direction[1]
        next_col = self.col + direction[0]

        # Periksa apakah sel yang akan dituju bukan dinding
        if 0 <= next_row < GRID_HEIGHT and 0 <= next_col < GRID_WIDTH and not grid[next_row][next_col].wall:
            self.row = next_row
            self.col = next_col

# Inisialisasi kelas Ghost
class Ghost:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.path = []
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])  # Inisialisasi arah acak

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, grid, target):
        open_list = PriorityQueue()
        open_list.put((0, (self.row, self.col)))
        came_from = {}
        cost_so_far = {(self.row, self.col): 0}

        while not open_list.empty():
            current_cost, current_node = open_list.get()

            if current_node == target:
                self.path = self.reconstruct_path(came_from, current_node)
                return

            for direction in [UP, DOWN, LEFT, RIGHT]:
                next_row = current_node[0] + direction[1]
                next_col = current_node[1] + direction[0]

                if not (0 <= next_row < GRID_HEIGHT and 0 <= next_col < GRID_WIDTH):
                    continue

                neighbor = (next_row, next_col)
                new_cost = cost_so_far[current_node] + 1

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(target, neighbor)
                    open_list.put((priority, neighbor))
                    came_from[neighbor] = current_node

    def reconstruct_path(self, came_from, current_node):
        path = []
        while current_node in came_from:
            path.append(current_node)
            current_node = came_from[current_node]
        path.reverse()
        return path

    def move(self, grid):
        if random.random() < GHOST_SPEED:
            # Perbarui arah jika hantu sudah mencapai titik tujuan dalam jalur
            if not self.path or (self.row, self.col) == self.path[-1]:
                self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                self.find_path(grid, (random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1)))

            next_row = self.row + self.direction[1]
            next_col = self.col + self.direction[0]

            # Periksa apakah sel yang akan dituju bukan dinding
            if 0 <= next_row < GRID_HEIGHT and 0 <= next_col < GRID_WIDTH and not grid[next_row][next_col].wall:
                self.row = next_row
                self.col = next_col
            else:
                # Jika bertabrakan dengan dinding, cari arah lain yang kosong
                possible_directions = [UP, DOWN, LEFT, RIGHT]
                random.shuffle(possible_directions)
                for direction in possible_directions:
                    new_row = self.row + direction[1]
                    new_col = self.col + direction[0]
                    if 0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and not grid[new_row][new_col].wall:
                        self.row = new_row
                        self.col = new_col
                        self.direction = direction
                        break

# Fungsi untuk menggambar grid
def draw_grid(grid, screen):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            color = BLACK
            if grid[row][col].wall:
                color = BLUE
            pygame.draw.rect(screen, color, [(MARGIN + CELL_SIZE) * col + MARGIN,
                                              (MARGIN + CELL_SIZE) * row + MARGIN,
                                              CELL_SIZE,
                                              CELL_SIZE])

# Fungsi untuk membuat labirin
def create_maze():
    maze = [[Node(row, col) for col in range(GRID_WIDTH)] for row in range(GRID_HEIGHT)]

    # Inisialisasi semua sel sebagai dinding
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            maze[row][col].wall = True

    # Mulai dari sel tengah dan lakukan rekursi untuk membuka jalan
    start_row, start_col = GRID_HEIGHT // 2, GRID_WIDTH // 2
    maze[start_row][start_col].wall = False
    stack = [(start_row, start_col)]

    while stack:
        current_row, current_col = stack[-1]
        neighbors = [(current_row + 2, current_col), (current_row - 2, current_col),
                     (current_row, current_col + 2), (current_row, current_col - 2)]
        unvisited_neighbors = [(row, col) for row, col in neighbors if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH and maze[row][col].wall]
        if unvisited_neighbors:
            next_row, next_col = random.choice(unvisited_neighbors)
            maze[next_row][next_col].wall = False
            maze[(current_row + next_row) // 2][(current_col + next_col) // 2].wall = False
            stack.append((next_row, next_col))
        else:
            stack.pop()

    return maze

# Fungsi untuk menentukan posisi awal hantu dengan jarak yang cukup jauh dari Pac-Man
def generate_ghost_positions(pacman_row, pacman_col):
    max_distance = 10  # Jarak minimal antara Pac-Man dan hantu
    ghost_positions = []

    while len(ghost_positions) < 3:  # Ubah angka 3 sesuai dengan jumlah hantu
        ghost_row = random.randint(0, GRID_HEIGHT - 1)
        ghost_col = random.randint(0, GRID_WIDTH - 1)
        # Hitung jarak Euclidean antara Pac-Man dan hantu
        distance = math.sqrt((ghost_row - pacman_row) ** 2 + (ghost_col - pacman_col) ** 2)
        if distance >= max_distance:
            ghost_positions.append((ghost_row, ghost_col))

    return ghost_positions

# Fungsi utama
def main():
    pygame.init()

    # Inisialisasi layar
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("Pac-Man")

    # Inisialisasi labirin
    grid = create_maze()

    # Inisialisasi karakter Pac-Man
    pacman = Pacman(13, 15)

    # Inisialisasi hantu
    ghost_positions = generate_ghost_positions(pacman.row, pacman.col)
    ghosts = [Ghost(row, col) for row, col in ghost_positions]

    # Inisialisasi umpan
    food_positions = [(row, col) for row in range(GRID_HEIGHT) for col in range(GRID_WIDTH)
                    if not grid[row][col].wall and (row, col) != (pacman.row, pacman.col)]
    for ghost in ghosts:
        food_positions = [(row, col) for (row, col) in food_positions if (row, col) != (ghost.row, ghost.col)]
    food_positions = random.sample(food_positions, len(food_positions) // 2)  # Ambil setengah dari posisi makanan
    foods = food_positions

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pacman.move(UP, grid)
                elif event.key == pygame.K_DOWN:
                    pacman.move(DOWN, grid)
                elif event.key == pygame.K_LEFT:
                    pacman.move(LEFT, grid)
                elif event.key == pygame.K_RIGHT:
                    pacman.move(RIGHT, grid)

        # Gerakkan hantu
        for ghost in ghosts:
            ghost.move(grid)

        # Hapus makanan yang dimakan oleh Pac-Man
        if (pacman.row, pacman.col) in food_positions:
            food_positions.remove((pacman.row, pacman.col))
            pacman.score += 10

        # Cek tabrakan antara Pac-Man dan hantu
        for ghost in ghosts:
            if (pacman.row, pacman.col) == (ghost.row, ghost.col):
                print("Game Over! Your score:", pacman.score)
                pygame.quit()
                return

        # Clear the screen and draw the grid
        screen.fill(BLACK)  # Ubah latar belakang layar menjadi hitam
        draw_grid(grid, screen)

        # Gambar makanan
        for food in foods:
            pygame.draw.circle(screen, WHITE, ((MARGIN + CELL_SIZE) * food[1] + MARGIN + CELL_SIZE // 2,
                                                (MARGIN + CELL_SIZE) * food[0] + MARGIN + CELL_SIZE // 2), CELL_SIZE // 6)

        # Gambar Pac-Man
        pygame.draw.circle(screen, YELLOW, ((MARGIN + CELL_SIZE) * pacman.col + MARGIN + CELL_SIZE // 2,
                                             (MARGIN + CELL_SIZE) * pacman.row + MARGIN + CELL_SIZE // 2), CELL_SIZE // 2)

        # Gambar hantu
        for ghost in ghosts:
            pygame.draw.circle(screen, RED, ((MARGIN + CELL_SIZE) * ghost.col + MARGIN + CELL_SIZE // 2,
                                              (MARGIN + CELL_SIZE) * ghost.row + MARGIN + CELL_SIZE // 2), CELL_SIZE // 2)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
