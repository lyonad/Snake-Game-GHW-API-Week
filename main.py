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
BORDER_WIDTH = 3

# Enhanced Color Palette
BG_DARK = (15, 23, 42)  # Dark slate blue background
BG_GRID = (30, 41, 59)  # Slightly lighter grid lines
BORDER_COLOR = (148, 163, 184)  # Light gray border

# Snake colors with gradient effect
SNAKE_HEAD = (34, 197, 94)  # Bright green
SNAKE_BODY_START = (22, 163, 74)  # Medium green
SNAKE_BODY_END = (21, 128, 61)  # Dark green
SNAKE_SHADOW = (16, 185, 129)  # Teal shadow

# Food colors
FOOD_COLOR = (239, 68, 68)  # Bright red
FOOD_GLOW = (248, 113, 113)  # Light red glow
FOOD_CORE = (220, 38, 38)  # Dark red core

# UI colors
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (203, 213, 225)
UI_BG = (30, 41, 59, 200)  # Semi-transparent UI background

# Game over colors
OVERLAY_COLOR = (0, 0, 0, 180)
GO_TEXT_COLOR = (239, 68, 68)
GO_SUBTEXT_COLOR = (203, 213, 225)

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


def draw_rounded_rect(surface, rect, color, radius=4, border=0, border_color=None):
    """Draw a rounded rectangle with optional border."""
    if border > 0 and border_color:
        # Draw border
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
    # Draw filled rounded rectangle
    pygame.draw.rect(surface, color, rect.inflate(-border*2, -border*2) if border > 0 else rect, border_radius=radius)


def draw_grid_background(surface):
    """Draw subtle grid lines on the background."""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, BG_GRID, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, BG_GRID, (0, y), (SCREEN_WIDTH, y), 1)


def draw_snake_segment(surface, pos, is_head=False, segment_index=0, total_segments=1):
    """Draw a snake segment with gradient effect."""
    x, y = pos
    base_x = x * CELL_SIZE
    base_y = y * CELL_SIZE
    
    # Calculate gradient color for body segments
    if is_head:
        color = SNAKE_HEAD
        shadow_color = SNAKE_SHADOW
    else:
        # Gradient from start to end color
        ratio = segment_index / max(total_segments - 1, 1)
        r1, g1, b1 = SNAKE_BODY_START
        r2, g2, b2 = SNAKE_BODY_END
        color = (
            int(r1 + (r2 - r1) * ratio),
            int(g1 + (g2 - g1) * ratio),
            int(b1 + (b2 - b1) * ratio)
        )
        shadow_color = None
    
    # Draw shadow/glow for head
    if shadow_color and is_head:
        shadow_rect = pygame.Rect(base_x + 1, base_y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        draw_rounded_rect(surface, shadow_rect, shadow_color, radius=5)
    
    # Draw main segment
    cell_rect = pygame.Rect(base_x + 2, base_y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
    draw_rounded_rect(surface, cell_rect, color, radius=4, border=1, border_color=(color[0]//2, color[1]//2, color[2]//2))


def draw_food(surface, pos, pulse=0.0):
    """Draw food with glow effect and optional pulse animation."""
    x, y = pos
    base_x = x * CELL_SIZE
    base_y = y * CELL_SIZE
    
    # Pulse effect (slight size variation)
    pulse_offset = int(pulse * 2)
    
    # Draw outer glow
    glow_rect = pygame.Rect(
        base_x + 4 - pulse_offset, 
        base_y + 4 - pulse_offset,
        CELL_SIZE - 8 + pulse_offset * 2,
        CELL_SIZE - 8 + pulse_offset * 2
    )
    draw_rounded_rect(surface, glow_rect, FOOD_GLOW, radius=6)
    
    # Draw main food circle
    food_rect = pygame.Rect(
        base_x + 6 - pulse_offset//2,
        base_y + 6 - pulse_offset//2,
        CELL_SIZE - 12 + pulse_offset,
        CELL_SIZE - 12 + pulse_offset
    )
    draw_rounded_rect(surface, food_rect, FOOD_COLOR, radius=5)
    
    # Draw core highlight
    core_rect = pygame.Rect(
        base_x + CELL_SIZE // 2 - 3,
        base_y + CELL_SIZE // 2 - 3,
        6, 6
    )
    draw_rounded_rect(surface, core_rect, FOOD_CORE, radius=3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game - Enhanced Edition")
    clock = pygame.time.Clock()
    
    # Better fonts
    try:
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
    except:
        font_large = pygame.font.SysFont("arial", 36, bold=True)
        font_medium = pygame.font.SysFont("arial", 28, bold=True)
        font_small = pygame.font.SysFont("arial", 24)

    # Initialize game state
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
    direction = RIGHT
    food = random_food_position(snake)
    score = 0
    game_over = False
    food_pulse = 0.0  # Animation counter for food
    frame_count = 0  # For animations

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key in (pygame.K_UP, pygame.K_w) and direction != DOWN:
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
                    food_pulse = 0.0
                    frame_count = 0

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
                    food_pulse = 3.0  # Pulse effect when food is eaten
                else:
                    snake.pop()
            
            # Update animations
            frame_count += 1
            food_pulse = max(0.0, food_pulse - 0.2)  # Decay pulse effect

        # Draw
        screen.fill(BG_DARK)
        
        # Draw grid background
        draw_grid_background(screen)

        # Draw border around game area
        border_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, BORDER_COLOR, border_rect, BORDER_WIDTH)

        # Draw food with pulse effect
        draw_food(screen, food, food_pulse)

        # Draw snake with gradient
        for i, segment in enumerate(snake):
            is_head = (i == 0)
            draw_snake_segment(screen, segment, is_head, i, len(snake))

        # Draw score with styled UI
        score_bg = pygame.Surface((150, 40), pygame.SRCALPHA)
        score_bg.fill(UI_BG)
        screen.blit(score_bg, (10, 10))
        
        score_text = font_medium.render(f"Score: {score}", True, TEXT_WHITE)
        score_rect = score_text.get_rect(center=(85, 30))
        screen.blit(score_text, score_rect)

        # Game over message with enhanced design
        if game_over:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(OVERLAY_COLOR)
            screen.blit(overlay, (0, 0))
            
            # Game over panel
            panel_width = 500
            panel_height = 150
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = (SCREEN_HEIGHT - panel_height) // 2
            
            panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel.fill((30, 41, 59, 240))
            pygame.draw.rect(panel, BORDER_COLOR, panel.get_rect(), 3, border_radius=10)
            screen.blit(panel, (panel_x, panel_y))
            
            # Game over text
            go_title = font_large.render("GAME OVER", True, GO_TEXT_COLOR)
            title_rect = go_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(go_title, title_rect)
            
            # Final score
            final_score_text = font_medium.render(f"Final Score: {score}", True, TEXT_WHITE)
            score_rect_final = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(final_score_text, score_rect_final)
            
            # Restart instruction
            restart_text = font_small.render("Press R to restart | ESC to quit", True, GO_SUBTEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
