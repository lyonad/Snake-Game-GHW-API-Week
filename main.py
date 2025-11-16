import pygame
import sys
import random
import math

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
FOOD_SPARKLE = (255, 255, 255)  # White sparkle

# UI colors
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (203, 213, 225)
UI_BG = (30, 41, 59, 200)  # Semi-transparent UI background
TEXT_SHADOW = (0, 0, 0, 150)  # Text shadow

# Game over colors
OVERLAY_COLOR = (0, 0, 0, 180)
GO_TEXT_COLOR = (239, 68, 68)
GO_SUBTEXT_COLOR = (203, 213, 225)

# Particle colors
PARTICLE_COLOR = (255, 215, 0)  # Gold particles
PARTICLE_COLORS = [
    (255, 215, 0),  # Gold
    (255, 165, 0),  # Orange
    (255, 140, 0),  # Dark orange
    (255, 200, 100),  # Light orange
]

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Particle class for effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 1.0
        self.size = random.uniform(2, 4)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.life -= 0.05
        self.size *= 0.98
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * self.life)
            color_with_alpha = (*self.color[:3], alpha)
            size = int(self.size)
            if size > 0:
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
                surface.blit(particle_surf, (self.x - size, self.y - size))


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


def draw_grid_background(surface, time=0):
    """Draw subtle animated grid lines on the background."""
    # Subtle pulsing effect
    intensity = 0.5 + 0.1 * math.sin(time * 0.1)
    grid_color = tuple(int(c * intensity) for c in BG_GRID)
    
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, grid_color, (0, y), (SCREEN_WIDTH, y), 1)


def draw_snake_segment(surface, pos, is_head=False, segment_index=0, total_segments=1, direction=None):
    """Draw a snake segment with gradient effect and eyes on head."""
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
    
    # Draw glow effect for head (multiple layers for better glow)
    if shadow_color and is_head:
        for i in range(3, 0, -1):
            glow_size = CELL_SIZE - i * 2
            glow_x = base_x + (CELL_SIZE - glow_size) // 2
            glow_y = base_y + (CELL_SIZE - glow_size) // 2
            glow_rect = pygame.Rect(glow_x, glow_y, glow_size, glow_size)
            glow_alpha = 50 // i
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            glow_color_alpha = (*shadow_color[:3], glow_alpha)
            pygame.draw.rect(glow_surf, glow_color_alpha, glow_surf.get_rect(), border_radius=5)
            surface.blit(glow_surf, (glow_x, glow_y))
    
    # Draw main segment
    cell_rect = pygame.Rect(base_x + 2, base_y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
    draw_rounded_rect(surface, cell_rect, color, radius=4, border=1, border_color=(max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40)))
    
    # Draw highlight on segment
    highlight_rect = pygame.Rect(base_x + 4, base_y + 4, CELL_SIZE // 3, CELL_SIZE // 3)
    highlight_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
    draw_rounded_rect(surface, highlight_rect, highlight_color, radius=2)
    
    # Draw eyes on head
    if is_head and direction:
        eye_size = 3
        center_x = base_x + CELL_SIZE // 2
        center_y = base_y + CELL_SIZE // 2
        eye_offset = 4
        
        # Determine eye positions based on direction
        if direction == RIGHT:
            eye1_pos = (center_x + 2, center_y - eye_offset)
            eye2_pos = (center_x + 2, center_y + eye_offset)
        elif direction == LEFT:
            eye1_pos = (center_x - 2, center_y - eye_offset)
            eye2_pos = (center_x - 2, center_y + eye_offset)
        elif direction == UP:
            eye1_pos = (center_x - eye_offset, center_y - 2)
            eye2_pos = (center_x + eye_offset, center_y - 2)
        else:  # DOWN
            eye1_pos = (center_x - eye_offset, center_y + 2)
            eye2_pos = (center_x + eye_offset, center_y + 2)
        
        # Draw white eyes
        pygame.draw.circle(surface, (255, 255, 255), eye1_pos, eye_size)
        pygame.draw.circle(surface, (255, 255, 255), eye2_pos, eye_size)
        
        # Draw black pupils
        pupil_size = 2
        pygame.draw.circle(surface, (0, 0, 0), eye1_pos, pupil_size)
        pygame.draw.circle(surface, (0, 0, 0), eye2_pos, pupil_size)


def draw_food(surface, pos, pulse=0.0, rotation=0.0):
    """Draw food with glow effect, pulse animation, and sparkles."""
    x, y = pos
    base_x = x * CELL_SIZE
    base_y = y * CELL_SIZE
    center_x = base_x + CELL_SIZE // 2
    center_y = base_y + CELL_SIZE // 2
    
    # Pulse effect with smooth animation
    pulse_offset = int(pulse * 2)
    pulse_alpha = int(min(255, pulse * 80))
    
    # Draw animated outer glow (multiple layers)
    for layer in range(3, 0, -1):
        layer_offset = (pulse_offset + layer * 2)
        layer_alpha = int((pulse_alpha + 40) / (layer + 1))
        glow_size = CELL_SIZE - 8 + layer_offset * 2
        
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_rect = pygame.Rect(0, 0, glow_size, glow_size)
        glow_color_alpha = (*FOOD_GLOW[:3], layer_alpha)
        pygame.draw.rect(glow_surf, glow_color_alpha, glow_rect, border_radius=6)
        surface.blit(glow_surf, (center_x - glow_size // 2, center_y - glow_size // 2))
    
    # Draw main food with gradient effect
    food_size = CELL_SIZE - 12 + pulse_offset
    food_surf = pygame.Surface((food_size, food_size), pygame.SRCALPHA)
    food_rect = pygame.Rect(0, 0, food_size, food_size)
    pygame.draw.rect(food_surf, FOOD_COLOR, food_rect, border_radius=5)
    
    # Add gradient highlight
    highlight_rect = pygame.Rect(0, 0, food_size, food_size // 2)
    highlight_color = (min(255, FOOD_COLOR[0] + 40), min(255, FOOD_COLOR[1] + 40), FOOD_COLOR[2], 100)
    pygame.draw.rect(food_surf, highlight_color, highlight_rect, border_radius=5)
    
    surface.blit(food_surf, (center_x - food_size // 2, center_y - food_size // 2))
    
    # Draw rotating sparkles around food
    sparkle_count = 4
    sparkle_radius = 8
    for i in range(sparkle_count):
        angle = rotation + (i * 2 * math.pi / sparkle_count)
        sparkle_x = center_x + math.cos(angle) * sparkle_radius
        sparkle_y = center_y + math.sin(angle) * sparkle_radius
        sparkle_size = 2
        sparkle_alpha = int(150 + 50 * math.sin(rotation * 2 + i))
        sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
        sparkle_color_alpha = (*FOOD_SPARKLE[:3], sparkle_alpha)
        pygame.draw.circle(sparkle_surf, sparkle_color_alpha, (sparkle_size, sparkle_size), sparkle_size)
        surface.blit(sparkle_surf, (sparkle_x - sparkle_size, sparkle_y - sparkle_size))
    
    # Draw core highlight
    core_size = 6
    core_rect = pygame.Rect(
        center_x - core_size // 2,
        center_y - core_size // 2,
        core_size, core_size
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
    food_rotation = 0.0  # Rotation for food sparkles
    frame_count = 0  # For animations
    particles = []  # Particle effects list

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
                    food_rotation = 0.0
                    frame_count = 0
                    particles = []  # Clear particles on restart

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
                    # Create particle explosion
                    food_x = food[0] * CELL_SIZE + CELL_SIZE // 2
                    food_y = food[1] * CELL_SIZE + CELL_SIZE // 2
                    for _ in range(12):
                        particle_color = random.choice(PARTICLE_COLORS)
                        particles.append(Particle(food_x, food_y, particle_color))
                    
                    food = random_food_position(snake)
                    food_pulse = 3.0  # Pulse effect when food is eaten
                    food_rotation = 0.0  # Reset rotation
                else:
                    snake.pop()
            
            # Update animations
            frame_count += 1
            food_pulse = max(0.0, food_pulse - 0.2)  # Decay pulse effect
            food_rotation += 0.15  # Rotate sparkles
            
            # Update particles
            particles = [p for p in particles if p.life > 0]
            for particle in particles:
                particle.update()

        # Draw
        screen.fill(BG_DARK)
        
        # Draw animated grid background
        draw_grid_background(screen, frame_count)

        # Draw border around game area with gradient effect
        border_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, BORDER_COLOR, border_rect, BORDER_WIDTH)
        
        # Draw inner border for depth
        inner_border = pygame.Rect(BORDER_WIDTH, BORDER_WIDTH, 
                                   SCREEN_WIDTH - BORDER_WIDTH * 2, 
                                   SCREEN_HEIGHT - BORDER_WIDTH * 2)
        pygame.draw.rect(screen, (BORDER_COLOR[0]//2, BORDER_COLOR[1]//2, BORDER_COLOR[2]//2), 
                        inner_border, 1)

        # Draw particles (behind food and snake)
        for particle in particles:
            particle.draw(screen)

        # Draw food with pulse effect and rotation
        draw_food(screen, food, food_pulse, food_rotation)

        # Draw snake with gradient and eyes
        for i, segment in enumerate(snake):
            is_head = (i == 0)
            draw_snake_segment(screen, segment, is_head, i, len(snake), direction if is_head else None)

        # Draw score with styled UI and shadow
        score_bg = pygame.Surface((160, 45), pygame.SRCALPHA)
        
        # Add gradient effect to score background
        for i in range(45):
            alpha = max(0, 200 - i * 3)
            color = (30, 41, 59, alpha)
            line_surf = pygame.Surface((160, 1), pygame.SRCALPHA)
            line_surf.fill(color)
            score_bg.blit(line_surf, (0, i))
        
        screen.blit(score_bg, (10, 10))
        
        # Draw score text with shadow
        score_text_shadow = font_medium.render(f"Score: {score}", True, (0, 0, 0))
        score_text = font_medium.render(f"Score: {score}", True, TEXT_WHITE)
        score_rect = score_text.get_rect(center=(90, 32))
        screen.blit(score_text_shadow, (score_rect.x + 1, score_rect.y + 1))
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
            
            # Game over text with glow effect
            go_title_shadow = font_large.render("GAME OVER", True, (0, 0, 0))
            go_title = font_large.render("GAME OVER", True, GO_TEXT_COLOR)
            title_rect = go_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            # Draw shadow multiple times for glow
            for offset in [(2, 2), (1, 1), (-1, -1), (-2, -2)]:
                screen.blit(go_title_shadow, (title_rect.x + offset[0], title_rect.y + offset[1]))
            screen.blit(go_title, title_rect)
            
            # Final score with shadow
            final_score_shadow = font_medium.render(f"Final Score: {score}", True, (0, 0, 0))
            final_score_text = font_medium.render(f"Final Score: {score}", True, TEXT_WHITE)
            score_rect_final = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(final_score_shadow, (score_rect_final.x + 1, score_rect_final.y + 1))
            screen.blit(final_score_text, score_rect_final)
            
            # Restart instruction with shadow
            restart_shadow = font_small.render("Press R to restart | ESC to quit", True, (0, 0, 0))
            restart_text = font_small.render("Press R to restart | ESC to quit", True, GO_SUBTEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(restart_shadow, (restart_rect.x + 1, restart_rect.y + 1))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
