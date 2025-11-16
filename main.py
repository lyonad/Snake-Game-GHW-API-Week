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
FPS = 60  # High FPS for smooth rendering
GAME_SPEED = 8  # Snake moves per second (slower for easier gameplay)
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

# Food types
FOOD_NORMAL = 0
FOOD_BONUS = 1  # 3x points
FOOD_SPECIAL = 2  # 5x points, rare
FOOD_COUNT = 3

# Power-up types
POWERUP_SPEED = 0
POWERUP_SLOW = 1
POWERUP_DOUBLE = 2
POWERUP_INVINCIBLE = 3
POWERUP_COUNT = 4

# Power-up colors
POWERUP_COLORS = {
    POWERUP_SPEED: (59, 130, 246),      # Blue - speed boost
    POWERUP_SLOW: (139, 92, 246),       # Purple - slow motion
    POWERUP_DOUBLE: (251, 191, 36),     # Yellow - double points
    POWERUP_INVINCIBLE: (236, 72, 153), # Pink - invincibility
}

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
        
    def update_with_dt(self, dt):
        """Update particle with delta time for frame-rate independence."""
        self.x += self.vx * dt * 60  # Scale by 60 to maintain original speed
        self.y += self.vy * dt * 60
        self.vy += 0.1 * dt * 60  # Gravity
        self.life -= 0.75 * dt  # Decay life
        self.size *= (0.98 ** (dt * 60))  # Scale size decay
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * self.life)
            color_with_alpha = (*self.color[:3], alpha)
            size = int(self.size)
            if size > 0:
                particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
                surface.blit(particle_surf, (self.x - size, self.y - size))


def random_food_position(snake, exclude_positions=None):
    """Generate random food position, excluding snake and other positions."""
    exclude = set(snake)
    if exclude_positions:
        exclude.update(exclude_positions)
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in exclude:
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
    # Subtle pulsing effect (time in seconds)
    intensity = 0.5 + 0.1 * math.sin(time * 0.5)
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


def draw_food(surface, pos, food_type=FOOD_NORMAL, pulse=0.0, rotation=0.0):
    """Draw food with glow effect, pulse animation, and sparkles. Different types have different colors."""
    x, y = pos
    base_x = x * CELL_SIZE
    base_y = y * CELL_SIZE
    center_x = base_x + CELL_SIZE // 2
    center_y = base_y + CELL_SIZE // 2
    
    # Different colors for different food types
    if food_type == FOOD_BONUS:
        food_color = (255, 215, 0)  # Gold
        food_glow = (255, 235, 100)  # Light gold
        food_core = (255, 185, 0)  # Dark gold
        sparkle_count = 6
    elif food_type == FOOD_SPECIAL:
        food_color = (168, 85, 247)  # Purple
        food_glow = (196, 181, 253)  # Light purple
        food_core = (139, 92, 246)  # Dark purple
        sparkle_count = 8
    else:
        food_color = FOOD_COLOR
        food_glow = FOOD_GLOW
        food_core = FOOD_CORE
        sparkle_count = 4
    
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
        glow_color_alpha = (*food_glow[:3], layer_alpha)
        pygame.draw.rect(glow_surf, glow_color_alpha, glow_rect, border_radius=6)
        surface.blit(glow_surf, (center_x - glow_size // 2, center_y - glow_size // 2))
    
    # Draw main food with gradient effect
    food_size = CELL_SIZE - 12 + pulse_offset
    food_surf = pygame.Surface((food_size, food_size), pygame.SRCALPHA)
    food_rect = pygame.Rect(0, 0, food_size, food_size)
    pygame.draw.rect(food_surf, food_color, food_rect, border_radius=5)
    
    # Add gradient highlight
    highlight_rect = pygame.Rect(0, 0, food_size, food_size // 2)
    highlight_color = (min(255, food_color[0] + 40), min(255, food_color[1] + 40), min(255, food_color[2] + 40), 100)
    pygame.draw.rect(food_surf, highlight_color, highlight_rect, border_radius=5)
    
    surface.blit(food_surf, (center_x - food_size // 2, center_y - food_size // 2))
    
    # Draw rotating sparkles around food (more for special foods)
    sparkle_radius = 8 + (food_type * 2)  # Bigger radius for special foods
    for i in range(sparkle_count):
        angle = rotation + (i * 2 * math.pi / sparkle_count)
        sparkle_x = center_x + math.cos(angle) * sparkle_radius
        sparkle_y = center_y + math.sin(angle) * sparkle_radius
        sparkle_size = 2 + food_type  # Bigger sparkles for special foods
        sparkle_alpha = int(150 + 50 * math.sin(rotation * 2 + i))
        sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
        sparkle_color_alpha = (*FOOD_SPARKLE[:3], sparkle_alpha)
        pygame.draw.circle(sparkle_surf, sparkle_color_alpha, (sparkle_size, sparkle_size), sparkle_size)
        surface.blit(sparkle_surf, (sparkle_x - sparkle_size, sparkle_y - sparkle_size))
    
    # Draw core highlight
    core_size = 6 + food_type
    core_rect = pygame.Rect(
        center_x - core_size // 2,
        center_y - core_size // 2,
        core_size, core_size
    )
    draw_rounded_rect(surface, core_rect, food_core, radius=3)


def draw_powerup(surface, pos, powerup_type, rotation=0.0):
    """Draw a power-up with distinct visual style."""
    x, y = pos
    base_x = x * CELL_SIZE
    base_y = y * CELL_SIZE
    center_x = base_x + CELL_SIZE // 2
    center_y = base_y + CELL_SIZE // 2
    
    color = POWERUP_COLORS[powerup_type]
    
    # Animated pulsing glow
    pulse = math.sin(rotation * 2) * 2
    
    # Draw outer glow
    glow_size = CELL_SIZE - 4 + int(pulse)
    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    glow_rect = pygame.Rect(0, 0, glow_size, glow_size)
    glow_alpha = int(100 + 50 * math.sin(rotation * 3))
    glow_color_alpha = (*color[:3], glow_alpha)
    pygame.draw.rect(glow_surf, glow_color_alpha, glow_rect, border_radius=8)
    surface.blit(glow_surf, (center_x - glow_size // 2, center_y - glow_size // 2))
    
    # Draw power-up shape (star-like)
    powerup_size = CELL_SIZE - 8
    powerup_surf = pygame.Surface((powerup_size, powerup_size), pygame.SRCALPHA)
    points = []
    for i in range(8):
        angle = rotation * 2 + (i * 2 * math.pi / 8)
        if i % 2 == 0:
            radius = powerup_size // 2
        else:
            radius = powerup_size // 4
        px = powerup_size // 2 + math.cos(angle) * radius
        py = powerup_size // 2 + math.sin(angle) * radius
        points.append((px, py))
    
    pygame.draw.polygon(powerup_surf, color, points)
    surface.blit(powerup_surf, (center_x - powerup_size // 2, center_y - powerup_size // 2))


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
        font_tiny = pygame.font.Font(None, 20)
    except:
        font_large = pygame.font.SysFont("arial", 36, bold=True)
        font_medium = pygame.font.SysFont("arial", 28, bold=True)
        font_small = pygame.font.SysFont("arial", 24)
        font_tiny = pygame.font.SysFont("arial", 20)

    # Initialize game state
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
    direction = RIGHT
    food = random_food_position(snake)
    food_type = FOOD_NORMAL
    powerup = None  # (position, type, rotation, timer)
    powerup_rotation = 0.0
    score = 0
    score_multiplier = 1
    current_game_speed = GAME_SPEED
    game_over = False
    food_pulse = 0.0  # Animation counter for food
    food_rotation = 0.0  # Rotation for food sparkles
    frame_count = 0  # For animations
    particles = []  # Particle effects list
    move_timer = 0.0  # Timer for snake movement (frame-rate independent)
    
    # Power-up effects
    powerup_speed_timer = 0.0  # Speed boost duration
    powerup_slow_timer = 0.0  # Slow motion duration
    powerup_double_timer = 0.0  # Double points duration
    powerup_invincible_timer = 0.0  # Invincibility duration
    
    powerup_spawn_timer = 0.0  # Timer for spawning power-ups

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
                    food_type = FOOD_NORMAL
                    powerup = None
                    powerup_rotation = 0.0
                    score = 0
                    score_multiplier = 1
                    current_game_speed = GAME_SPEED
                    game_over = False
                    food_pulse = 0.0
                    food_rotation = 0.0
                    frame_count = 0
                    particles = []  # Clear particles on restart
                    move_timer = 0.0
                    powerup_speed_timer = 0.0
                    powerup_slow_timer = 0.0
                    powerup_double_timer = 0.0
                    powerup_invincible_timer = 0.0
                    powerup_spawn_timer = 0.0

        # Calculate delta time for frame-rate independent animations
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds
        dt = max(dt, 0.001)  # Prevent division by zero on very fast systems
        
        # Frame-rate independent animation updates (always update)
        frame_count += 1
        food_pulse = max(0.0, food_pulse - 3.0 * dt)  # Decay pulse effect
        food_rotation += 2.5 * dt  # Rotate sparkles (radians per second)
        powerup_rotation += 3.0 * dt  # Rotate power-ups
        
        # Update particles (frame-rate independent, continue during game over)
        particles = [p for p in particles if p.life > 0]
        for particle in particles:
            particle.update_with_dt(dt)
        
        # Update power-up timers
        powerup_speed_timer = max(0.0, powerup_speed_timer - dt)
        powerup_slow_timer = max(0.0, powerup_slow_timer - dt)
        powerup_double_timer = max(0.0, powerup_double_timer - dt)
        powerup_invincible_timer = max(0.0, powerup_invincible_timer - dt)
        
        # Update score multiplier
        score_multiplier = 1
        if powerup_double_timer > 0:
            score_multiplier = 2
        
        # Update game speed based on power-ups and score
        speed_multiplier = 1.0
        if powerup_speed_timer > 0:
            speed_multiplier = 1.8  # 80% faster
        elif powerup_slow_timer > 0:
            speed_multiplier = 0.5  # 50% slower
        
        # Increase difficulty with score (every 20 points = +1 speed, slower progression)
        difficulty_bonus = min(score // 20, 10)  # Cap at 10, slower increase
        current_game_speed = GAME_SPEED + difficulty_bonus
        current_game_speed *= speed_multiplier
        
        if not game_over:
            # Frame-rate independent snake movement
            move_timer += dt
            move_interval = 1.0 / current_game_speed  # Time between moves
            
            if move_timer >= move_interval:
                move_timer = 0.0
                
                # Move snake
                head_x, head_y = snake[0]
                dx, dy = direction
                new_head = (head_x + dx, head_y + dy)

                # Check collisions with walls (skip if invincible)
                if powerup_invincible_timer <= 0:
                    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                        game_over = True
                    # Check collisions with self
                    elif new_head in snake:
                        game_over = True
                
                # Allow movement even if collision (invincibility or walls)
                if not game_over:
                    snake.insert(0, new_head)
                    
                    # Check food collision
                    if new_head == food:
                        # Calculate points based on food type
                        points = 1
                        if food_type == FOOD_BONUS:
                            points = 3
                        elif food_type == FOOD_SPECIAL:
                            points = 5
                        
                        points *= score_multiplier
                        score += points
                        
                        # Create particle explosion
                        food_x = food[0] * CELL_SIZE + CELL_SIZE // 2
                        food_y = food[1] * CELL_SIZE + CELL_SIZE // 2
                        particle_count = 12 + food_type * 4
                        for _ in range(particle_count):
                            particle_color = random.choice(PARTICLE_COLORS)
                            particles.append(Particle(food_x, food_y, particle_color))
                        
                        # Spawn new food with random type (more special foods for easier gameplay)
                        rand = random.random()
                        if rand < 0.08:  # 8% chance for special (was 5%)
                            food_type = FOOD_SPECIAL
                        elif rand < 0.25:  # 25% chance for bonus (was 15%)
                            food_type = FOOD_BONUS
                        else:
                            food_type = FOOD_NORMAL
                        
                        food = random_food_position(snake, [powerup[0]] if powerup else None)
                        food_pulse = 3.0  # Pulse effect when food is eaten
                        food_rotation = 0.0  # Reset rotation
                    # Check power-up collision
                    elif powerup and new_head == powerup[0]:
                        powerup_type = powerup[1]
                        powerup_x = powerup[0][0] * CELL_SIZE + CELL_SIZE // 2
                        powerup_y = powerup[0][1] * CELL_SIZE + CELL_SIZE // 2
                        
                        # Apply power-up effect (longer durations for easier gameplay)
                        if powerup_type == POWERUP_SPEED:
                            powerup_speed_timer = 7.0  # 7 seconds (was 5)
                        elif powerup_type == POWERUP_SLOW:
                            powerup_slow_timer = 8.0  # 8 seconds (was 5)
                        elif powerup_type == POWERUP_DOUBLE:
                            powerup_double_timer = 12.0  # 12 seconds (was 8)
                        elif powerup_type == POWERUP_INVINCIBLE:
                            powerup_invincible_timer = 6.0  # 6 seconds (was 4)
                        
                        # Particle effect
                        for _ in range(20):
                            color = POWERUP_COLORS[powerup_type]
                            particles.append(Particle(powerup_x, powerup_y, color))
                        
                        powerup = None
                        powerup_spawn_timer = 0.0
                    else:
                        snake.pop()
            
            # Spawn power-ups randomly (more frequent for easier gameplay)
            powerup_spawn_timer += dt
            if not powerup and powerup_spawn_timer >= 8.0:  # Every 8 seconds (was 10)
                if random.random() < 0.75:  # 75% chance to spawn (was 60%)
                    powerup_type = random.randint(0, POWERUP_COUNT - 1)
                    powerup_pos = random_food_position(snake, [food])
                    powerup = (powerup_pos, powerup_type, 0.0, 20.0)  # 20 second lifetime (was 15)
                    powerup_spawn_timer = 0.0
            
            # Update power-up lifetime
            if powerup:
                powerup = (powerup[0], powerup[1], powerup[2], powerup[3] - dt)
                if powerup[3] <= 0:
                    powerup = None

        # Draw
        screen.fill(BG_DARK)
        
        # Draw animated grid background (convert frame_count to approximate time)
        draw_grid_background(screen, frame_count / FPS)

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

        # Draw power-up if exists
        if powerup:
            draw_powerup(screen, powerup[0], powerup[1], powerup_rotation)
        
        # Draw food with pulse effect and rotation
        draw_food(screen, food, food_type, food_pulse, food_rotation)

        # Draw snake with gradient and eyes
        for i, segment in enumerate(snake):
            is_head = (i == 0)
            draw_snake_segment(screen, segment, is_head, i, len(snake), direction if is_head else None)

        # Draw score with styled UI and shadow (compact size)
        score_bg_width = 110
        score_bg_height = 50
        score_bg = pygame.Surface((score_bg_width, score_bg_height), pygame.SRCALPHA)
        
        # Add gradient effect to score background
        for i in range(score_bg_height):
            alpha = max(0, 200 - i * 4)
            color = (30, 41, 59, alpha)
            line_surf = pygame.Surface((score_bg_width, 1), pygame.SRCALPHA)
            line_surf.fill(color)
            score_bg.blit(line_surf, (0, i))
        
        screen.blit(score_bg, (10, 10))
        
        # Draw score text with shadow (smaller font)
        score_text_shadow = font_tiny.render(f"Score: {score}", True, (0, 0, 0))
        score_text = font_tiny.render(f"Score: {score}", True, TEXT_WHITE)
        score_rect = score_text.get_rect(center=(score_bg_width // 2 + 10, 22))
        screen.blit(score_text_shadow, (score_rect.x + 1, score_rect.y + 1))
        screen.blit(score_text, score_rect)
        
        # Draw active power-ups (compact text)
        y_offset = 32
        if score_multiplier > 1:
            mult_text = font_tiny.render(f"x{score_multiplier} Points", True, (251, 191, 36))
            screen.blit(mult_text, (15, y_offset))
            y_offset += 14
        
        if powerup_speed_timer > 0:
            speed_text = font_tiny.render(f"Speed: {int(powerup_speed_timer)}s", True, (59, 130, 246))
            screen.blit(speed_text, (15, y_offset))
            y_offset += 14
        
        if powerup_slow_timer > 0:
            slow_text = font_tiny.render(f"Slow: {int(powerup_slow_timer)}s", True, (139, 92, 246))
            screen.blit(slow_text, (15, y_offset))
            y_offset += 14
        
        if powerup_invincible_timer > 0:
            inv_text = font_tiny.render(f"Inv: {int(powerup_invincible_timer)}s", True, (236, 72, 153))
            screen.blit(inv_text, (15, y_offset))
        
        # Draw invincibility effect
        if powerup_invincible_timer > 0:
            # Draw pulsing border around snake head
            head_x, head_y = snake[0]
            center_x = head_x * CELL_SIZE + CELL_SIZE // 2
            center_y = head_y * CELL_SIZE + CELL_SIZE // 2
            pulse = int(5 * math.sin(frame_count * 0.3))
            inv_rect = pygame.Rect(
                center_x - CELL_SIZE // 2 - pulse - 2,
                center_y - CELL_SIZE // 2 - pulse - 2,
                CELL_SIZE + pulse * 2 + 4,
                CELL_SIZE + pulse * 2 + 4
            )
            inv_color = (236, 72, 153, int(150 + 50 * math.sin(frame_count * 0.3)))
            inv_surf = pygame.Surface((inv_rect.width, inv_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(inv_surf, inv_color, inv_surf.get_rect(), 2, border_radius=6)
            screen.blit(inv_surf, (inv_rect.x, inv_rect.y))

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
        # Note: dt is calculated at the start of the loop


if __name__ == "__main__":
    main()
