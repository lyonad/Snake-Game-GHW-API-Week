import pygame
import sys
import random

# Config
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def random_food_position(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos


def draw_cell(surface, pos, color):
    x, y = pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Snake")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    # Initialize game state
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
    direction = RIGHT
    food = random_food_position(snake)
    score = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != DOWN:
                    direction = UP
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != UP:
                    direction = DOWN
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != RIGHT:
                    direction = LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != LEFT:
                    direction = RIGHT
                elif event.key == pygame.K_r and game_over:
                    # Restart
                    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
                    direction = RIGHT
                    food = random_food_position(snake)
                    score = 0
                    game_over = False

        if not game_over:
            # Move snake
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            # Check collisions with walls
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                game_over = True
            # Check collisions with self
            elif new_head in snake:
                game_over = True
            else:
                snake.insert(0, new_head)
                # Check food
                if new_head == food:
                    score += 1
                    food = random_food_position(snake)
                else:
                    snake.pop()

        # Draw
        screen.fill(BLACK)

        # Draw food
        draw_cell(screen, food, RED)

        # Draw snake
        for i, segment in enumerate(snake):
            color = DARK_GREEN if i == 0 else GREEN
            draw_cell(screen, segment, color)

        # Draw score
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (8, 8))

        # Game over message
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            go_surf = font.render("GAME OVER - Press R to restart or close window", True, WHITE)
            rect = go_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(go_surf, rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
