import random
import pygame
import colorsys

pygame.init()

WHITE = (255, 255, 255)
GREY = (20, 20, 20)
BLACK = (0, 0, 0)
PURPLE = (100, 0, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCREEN_SIZE_PX = (500, 500)
screen = pygame.display.set_mode(SCREEN_SIZE_PX)
pygame.display.set_caption("Maze Generator")

done = False
clock = pygame.time.Clock()

NODE_WIDTH = 10
NODE_COLS = int(SCREEN_SIZE_PX[0] / NODE_WIDTH)
NODE_ROWS = int(SCREEN_SIZE_PX[1] / NODE_WIDTH)


def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


class Cell:
    def __init__(self, x, y):
        self.x = x * NODE_WIDTH
        self.y = y * NODE_WIDTH
        self.visited = False
        self.current = False
        self.walls = [True, True, True, True]  # top, right, bottom, left
        self.neighbors = []
        self.top = 0
        self.right = 0
        self.bottom = 0
        self.left = 0
        self.next_cell = 0

    def check_neighbors(self, grid):
        if int(self.y / NODE_WIDTH) - 1 >= 0:
            self.top = grid[int(self.y / NODE_WIDTH) - 1][int(self.x / NODE_WIDTH)]
        if int(self.x / NODE_WIDTH) + 1 <= NODE_COLS - 1:
            self.right = grid[int(self.y / NODE_WIDTH)][int(self.x / NODE_WIDTH) + 1]
        if int(self.y / NODE_WIDTH) + 1 <= NODE_ROWS - 1:
            self.bottom = grid[int(self.y / NODE_WIDTH) + 1][int(self.x / NODE_WIDTH)]
        if int(self.x / NODE_WIDTH) - 1 >= 0:
            self.left = grid[int(self.y / NODE_WIDTH)][int(self.x / NODE_WIDTH) - 1]

        if self.top and not self.top.visited:
            self.neighbors.append(self.top)
        if self.right and not self.right.visited:
            self.neighbors.append(self.right)
        if self.bottom and not self.bottom.visited:
            self.neighbors.append(self.bottom)
        if self.left and not self.left.visited:
            self.neighbors.append(self.left)

        if self.neighbors:
            self.next_cell = random.choice(self.neighbors)
            return self.next_cell
        return False


class MazeGenerator:
    def __init__(self):
        self.grid = [[Cell(x, y) for x in range(NODE_COLS)] for y in range(NODE_ROWS)]
        self.current_cell = self.grid[0][0]
        self.stack = []

    def select_current_cell(self, cell):
        self.current_cell.current = False
        self.current_cell = cell
        self.current_cell.visited = True
        self.current_cell.current = True

    def generate_next_frame(self):
        self.current_cell.visited = True
        self.current_cell.current = True
        next_cell = self.current_cell.check_neighbors(self.grid)
        if next_cell:
            self.current_cell.neighbors = []
            self.stack.append(self.current_cell)
            self.remove_walls(self.current_cell, next_cell)
            self.select_current_cell(next_cell)
        elif self.stack:
            self.select_current_cell(self.stack.pop())
        else:
            self.reset_maze()

    def remove_walls(self, current_cell, next_cell):
        x = int(current_cell.x / NODE_WIDTH) - int(next_cell.x / NODE_WIDTH)
        y = int(current_cell.y / NODE_WIDTH) - int(next_cell.y / NODE_WIDTH)
        if x == -1:  # right of current
            current_cell.walls[1] = False
            next_cell.walls[3] = False
        elif x == 1:  # left of current
            current_cell.walls[3] = False
            next_cell.walls[1] = False
        elif y == -1:  # bottom of current
            current_cell.walls[2] = False
            next_cell.walls[0] = False
        elif y == 1:  # top of current
            current_cell.walls[0] = False
            next_cell.walls[2] = False

    def reset_maze(self):
        self.grid = [[Cell(x, y) for x in range(NODE_COLS)] for y in range(NODE_ROWS)]
        self.select_current_cell(self.grid[0][0])
        self.stack = []


class MazeDisplay:
    def __init__(self, screen):
        self.screen = screen

    def draw(self, grid, stack, neighbors):
        self.screen.fill(GREY)
        for row in grid:
            for cell in row:
                self.draw_cell(cell)
        self.draw_stack(stack)
        self.draw_neighbors(neighbors)
        pygame.display.flip()

    def draw_cell(self, cell):
        if cell.visited:
            pygame.draw.rect(self.screen, WHITE, (cell.x, cell.y, NODE_WIDTH, NODE_WIDTH))
            if cell.walls[0]:
                pygame.draw.line(self.screen, BLACK, (cell.x, cell.y), (cell.x + NODE_WIDTH, cell.y), 1)  # top
            if cell.walls[1]:
                pygame.draw.line(self.screen, BLACK, (cell.x + NODE_WIDTH, cell.y), (cell.x + NODE_WIDTH, cell.y + NODE_WIDTH), 1)  # right
            if cell.walls[2]:
                pygame.draw.line(self.screen, BLACK, (cell.x + NODE_WIDTH, cell.y + NODE_WIDTH), (cell.x, cell.y + NODE_WIDTH), 1)  # bottom
            if cell.walls[3]:
                pygame.draw.line(self.screen, BLACK, (cell.x, cell.y + NODE_WIDTH), (cell.x, cell.y), 1)  # left

        if cell.current:
            pygame.draw.rect(self.screen, RED, (cell.x, cell.y, NODE_WIDTH, NODE_WIDTH))

    def draw_stack(self, stack):
        oldest_stack_member_index = len(stack)
        for i, cell in enumerate(stack):
            percent_through_stack = (i / oldest_stack_member_index)
            # pygame.draw.rect(self.screen, [int(value * percent_through_stack) for value in PURPLE], (cell.x, cell.y, NODE_WIDTH, NODE_WIDTH))
            pygame.draw.rect(self.screen, hsv2rgb(percent_through_stack * 0.9, 1, 1), (cell.x, cell.y, NODE_WIDTH, NODE_WIDTH))

    def draw_neighbors(self, neighbors):
        for cell in neighbors:
            pygame.draw.rect(self.screen, BLUE, (cell.x, cell.y, NODE_WIDTH, NODE_WIDTH))


def main():
    global done
    maze_generator = MazeGenerator()
    maze_display = MazeDisplay(screen)
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        maze_generator.generate_next_frame()
        maze_display.draw(maze_generator.grid, maze_generator.stack, maze_generator.current_cell.neighbors)
    pygame.quit()


if __name__ == "__main__":
    main()
