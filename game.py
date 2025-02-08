import pygame
import random
import sys
import os
import math  # For boss attack angle calculations

pygame.init()

# --------------------
# Global Constants
# --------------------
WIDTH, HEIGHT = 800, 600              # Display (window) size
MAP_WIDTH, MAP_HEIGHT = 1200, 800     # Full level (map) size
FPS = 60

# Colors (fallback colors)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
GOLD   = (255, 215, 0)
YELLOW = (255, 255, 0)  # For projectiles/spells

# --------------------
# Set up the Display
# --------------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I Don't Wanna Be The Guy")
clock = pygame.time.Clock()

# Difficulty multipliers (scale obstacle speeds)
DIFFICULTY = {
    "Easy": 1,
    "Medium": 1.5,
    "Hard": 2,
}
selected_difficulty = "Easy"  # Selected in the main menu

# --------------------
# Global Sprite Groups
# --------------------
bullet_group = pygame.sprite.Group()       # For player spells
boss_projectiles = pygame.sprite.Group()     # For boss attack projectiles

# --------------------
# Image Cache & Loader Functions
# --------------------
image_cache = {}

def show_about_screen():
    about = True
    font_title = pygame.font.SysFont(None, 60)
    font_text = pygame.font.SysFont(None, 36)
    instructions = [
        "Welcome to I Wanna Be The Guy Tribute!",
        "",
        "How to Play:",
        "  - Use LEFT/RIGHT arrow keys to move.",
        "  - Press SPACE to jump.",
        "  - Press F to cast a spell (costs mana).",
        "  - Collect health and mana pickups.",
        "  - Avoid obstacles and reach the goal to progress.",
        "",
        "Press any key to continue..."
    ]
    while about:
        screen.fill(BLACK)
        title_surface = font_title.render("How to Play", True, WHITE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))
        for i, line in enumerate(instructions):
            text_surface = font_text.render(line, True, WHITE)
            screen.blit(text_surface, (50, 150 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                about = False
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(FPS)

def load_image(path, w, h):
    if path in image_cache:
        return image_cache[path]
    if not os.path.exists(path):
        print(f"Warning: Image file '{path}' not found.")
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (w, h))
        image_cache[path] = image
        return image
    except pygame.error as e:
        print(f"Error loading image '{path}': {e}")
        return None

def get_image_details(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    image = pygame.image.load(file_path).convert_alpha()
    width, height = image.get_size()
    print("Image size:", width, "x", height)
    return width, height

def slice_sprite_sheet(sheet, sprite_width=32, sprite_height=32, rows=4):
    sheet_width, sheet_height = sheet.get_size()
    columns = sheet_width // sprite_width
    sprites = []
    for row in range(rows):
        row_sprites = []
        for col in range(columns):
            rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
            sprite = sheet.subsurface(rect).copy()
            row_sprites.append(sprite)
        sprites.append(row_sprites)
    return sprites

# --------------------
# Load and Slice the Sprite Sheet for the Player
# --------------------
sprite_image_path = "images/characters.png"  
sheet_width, sheet_height = get_image_details(sprite_image_path)
sprite_sheet = load_image(sprite_image_path, sheet_width, sheet_height)
cols, rows = 23, 4
sprite_width = sheet_width // cols
sprite_height = sheet_height // rows
print("Each sprite is:", sprite_width, "x", sprite_height)
all_sprite_frames = slice_sprite_sheet(sprite_sheet, sprite_width, sprite_height, rows)
player_frames = all_sprite_frames[1]  # Use row 1 for the player

# --------------------
# Load and Slice the Boss Sprite Sheet
# --------------------
boss_image_path = "images/environment/boss/mage-1-85x94.png"
boss_sheet_width, boss_sheet_height = get_image_details(boss_image_path)
boss_sheet = load_image(boss_image_path, boss_sheet_width, boss_sheet_height)
boss_cols, boss_rows = 4, 2  # Assume 4 columns and 2 rows for the boss sheet
boss_width = boss_sheet_width // boss_cols
boss_height = boss_sheet_height // boss_rows
print("Each boss sprite is:", boss_width, "x", boss_height)
all_boss_frames = slice_sprite_sheet(boss_sheet, boss_width, boss_height, boss_rows)
boss_frames = all_boss_frames[1]  # Use row 1 for boss animation

# --------------------
# Utility Function for Tiled Platforms
# --------------------
def check_trap_collision(player, tiled_platform):
    local_x = player.rect.centerx - tiled_platform.rect.left
    local_y = player.rect.bottom - tiled_platform.rect.top
    col = int(local_x // tiled_platform.tile_width)
    row = int(local_y // tiled_platform.tile_height)
    if 0 <= row < len(tiled_platform.tile_map) and 0 <= col < len(tiled_platform.tile_map[0]):
        return tiled_platform.tile_map[row][col] == 1
    return False

# --------------------
# Player Class (Animated, with Mana)
# --------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, frames=None, frame_duration=100):
        super().__init__()
        if frames:
            self.frames = frames
            self.current_frame = 0
            self.frame_duration = frame_duration  # milliseconds per frame
            self.last_update = pygame.time.get_ticks()
            self.image = self.frames[self.current_frame]
        else:
            self.image = pygame.Surface((80, 120))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.speed = 5
        self.jump_strength = -15
        self.on_ground = False
        self.facing = 1
        self.health = 100
        self.mana = 100
        self.damage_cooldown = 0

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.facing = -1
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.facing = 1
            self.rect.x += self.speed

        self.vel_y += 0.8
        self.rect.y += self.vel_y

        self.on_ground = False
        # Loop through platforms and check for collisions.
        # Allow drop-through on non-base platforms if DOWN key is pressed.
        for plat in platforms:
            if keys[pygame.K_DOWN] and not isinstance(plat, TiledBasePlatform):
                continue  # Skip collision with non-base platforms when DOWN is pressed
            if self.rect.colliderect(plat.rect) and self.vel_y >= 0:
                if isinstance(plat, TiledBasePlatform):
                    if check_trap_collision(self, plat):
                        self.health = 0
                        print("Stepped on a trap tile!")
                        continue
                self.rect.bottom = plat.rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH
        if self.rect.top > MAP_HEIGHT:
            self.rect.topleft = (50, MAP_HEIGHT - 100)
            self.vel_y = 0
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            if self.facing == -1:
                self.image = pygame.transform.flip(self.image, True, False)

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_strength

# --------------------
# Platform Classes
# --------------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=RED, image_path=None):
        super().__init__()
        if image_path:
            loaded_image = load_image(image_path, w, h)
            self.image = loaded_image if loaded_image else pygame.Surface((w, h))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, color=GREEN, image_path=None, speed=2, direction=(1, 0), boundaries=None):
        super().__init__(x, y, w, h, color, image_path)
        self.speed = speed
        self.direction = pygame.math.Vector2(direction)
        if boundaries is None:
            self.boundaries = (x, x + 300, y, y)
        else:
            self.boundaries = tuple(boundaries)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        if self.rect.left <= self.boundaries[0] or self.rect.right >= self.boundaries[1]:
            self.direction.x *= -1
            print(f"[DEBUG] MovingPlatform at {self.rect.topleft} reversed horizontal direction; new direction: {self.direction}")
        if self.rect.top <= self.boundaries[2] or self.rect.bottom >= self.boundaries[3]:
            self.direction.y *= -1
            print(f"[DEBUG] MovingPlatform at {self.rect.topleft} reversed vertical direction; new direction: {self.direction}")

class TiledBasePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_map, tile_width, tile_height, tile_images=None):
        super().__init__()
        self.tile_map = tile_map
        self.tile_width = tile_width
        self.tile_height = tile_height
        rows = len(tile_map)
        cols = len(tile_map[0]) if rows > 0 else 0
        width = cols * tile_width
        height = rows * tile_height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        if tile_images is None:
            tile_images = {
                0: "images/base_platform_tile.png",
                1: "images/base_platform_trap.png"
            }
        self.tile_images = {}
        for tile_type, path in tile_images.items():
            img = load_image(path, tile_width, tile_height)
            if img is None:
                fallback = pygame.Surface((tile_width, tile_height))
                fallback.fill(GREEN if tile_type == 0 else RED)
                self.tile_images[tile_type] = fallback
            else:
                self.tile_images[tile_type] = img
        for r in range(rows):
            for c in range(cols):
                tile_type = tile_map[r][c]
                tile_img = self.tile_images.get(tile_type)
                if tile_img:
                    self.image.blit(tile_img, (c * tile_width, r * tile_height))

# --------------------
# Obstacle Class (with Dynamic Behavior)
# --------------------
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, image_path=None, dynamic=False):
        super().__init__()
        if image_path:
            loaded_image = load_image(image_path, w, h)
            self.image = loaded_image if loaded_image else pygame.Surface((w, h))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.vertical = False  # default horizontal movement
        self.dynamic = dynamic
        self.timer = 0

    def update(self):
        if self.dynamic:
            self.timer += 1
            if self.timer >= 60:
                old_speed = self.speed
                multiplier = random.uniform(0.5, 1.5)
                if random.choice([True, False]):
                    self.speed = -abs(self.speed) * multiplier
                else:
                    self.speed = abs(self.speed) * multiplier
                print(f"[DEBUG] Obstacle at {self.rect.topleft} changed speed: {old_speed:.2f} -> {self.speed:.2f}")
                self.timer = 0
        if self.vertical:
            self.rect.y += self.speed
            if self.rect.top <= 0 or self.rect.bottom >= MAP_HEIGHT:
                self.speed = -self.speed
                print(f"[DEBUG] Vertical obstacle at {self.rect.topleft} bounced; new speed: {self.speed:.2f}")
        else:
            self.rect.x += self.speed
            if self.rect.left <= 0 or self.rect.right >= MAP_WIDTH:
                self.speed = -self.speed
                print(f"[DEBUG] Horizontal obstacle at {self.rect.topleft} bounced; new speed: {self.speed:.2f}")

# --------------------
# Pickup Class (for Health and Mana)
# --------------------
class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, ptype, value, image_path=None):
        super().__init__()
        self.ptype = ptype  # "health" or "bullet" (bullet is used for mana)
        self.value = value
        if image_path:
            loaded_image = load_image(image_path, w, h)
            self.image = loaded_image if loaded_image else pygame.Surface((w, h))
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(GREEN if ptype=="health" else YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

# --------------------
# Bullet Class (Spell Projectile)
# --------------------
# Modified to accept an optional velocity tuple for multi-direction attacks.
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1, image_path="images/environment/spells/fire_ball_spell.png", width=50, height=50, velocity=None):
        super().__init__()
        self.image = load_image(image_path, width, height)
        if self.image is None:
            self.image = pygame.Surface((width, height))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        if velocity is not None:
            self.vx, self.vy = velocity
        else:
            self.vx = 10 * direction
            self.vy = 0

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.right < 0 or self.rect.left > MAP_WIDTH or 
            self.rect.bottom < 0 or self.rect.top > MAP_HEIGHT):
            self.kill()

# --------------------
# Boss Classes
# --------------------
# Small Boss – inherits from Obstacle and flips its image based on movement direction.
class SmallBoss(Obstacle):
    def __init__(self, x, y, w, h, speed, image_path=None, dynamic=False):
        super().__init__(x, y, w, h, speed, image_path, dynamic)
        self.original_image = self.image.copy()
    def update(self):
        super().update()
        if not self.vertical:
            if self.speed < 0:
                self.image = pygame.transform.flip(self.original_image, True, False)
            else:
                self.image = self.original_image.copy()

# Big Boss – uses a list of frames for animation, has phases, moves randomly in the map,
# and attacks by spawning projectiles into the global boss_projectiles group.
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, frames, dynamic=False, boundaries=(300,700)):
        super().__init__()
        # Scale each frame to (w, h)
        self.frames = [pygame.transform.scale(frame, (w, h)) for frame in frames]
        self.current_frame = 0
        self.frame_duration = 100  # milliseconds per frame
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        # Instead of a fixed speed, we use separate vx and vy for random movement.
        self.vx = speed
        self.vy = 0
        self.dynamic = dynamic
        self.vertical = False
        self.timer = 0
        self.attack_timer = 0
        self.move_timer = 0
        self.phase = 1
        self.max_health = 200
        self.health = self.max_health
        self.attack_interval = 2000  # ms for phase 1
        self.boundaries = boundaries  # horizontal movement range for fallback if needed
        self.last_time = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        delta = now - self.last_time
        self.last_time = now

        # Randomize movement every 1000 ms
        self.move_timer += delta
        if self.move_timer >= 1000:
            self.vx = random.choice([-1, 1]) * random.uniform(1, 3)
            self.vy = random.choice([-1, 1]) * random.uniform(1, 3)
            self.move_timer = 0

        self.rect.x += self.vx
        self.rect.y += self.vy

        # Constrain boss within the map boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = -self.vx
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH
            self.vx = -self.vx
        if self.rect.top < 0:
            self.rect.top = 0
            self.vy = -self.vy
        if self.rect.bottom > MAP_HEIGHT:
            self.rect.bottom = MAP_HEIGHT
            self.vy = -self.vy

        # Phase transitions based on health thresholds
        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.attack_interval = 1500
            print("Boss leveled up to Phase 2!")
        elif self.health < self.max_health * 0.25 and self.phase == 2:
            self.phase = 3
            self.attack_interval = 1000
            print("Boss leveled up to Phase 3!")

        self.attack_timer += delta
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            self.attack()

        # Update animation
        if delta > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            if self.vx < 0:
                self.image = pygame.transform.flip(self.image, True, False)
    def attack(self):
        print(f"Boss attacking in Phase {self.phase}!")
        # Advanced attack pattern:
        if self.phase == 1:
            # Shoot one bullet straight downward
            new_bullet = Bullet(self.rect.centerx, self.rect.bottom, velocity=(0, 10),
                                  image_path="images/environment/spells/bluefire.gif", width=40, height=40)
            boss_projectiles.add(new_bullet)
        elif self.phase == 2:
            # Shoot two bullets diagonally downward
            new_bullet1 = Bullet(self.rect.centerx, self.rect.bottom, velocity=(-7, 7),
                                  image_path="images/environment/spells/bluefire.gif", width=40, height=40)
            new_bullet2 = Bullet(self.rect.centerx, self.rect.bottom, velocity=(7, 7),
                                  image_path="images/environment/spells/bluefire.gif", width=40, height=40)
            boss_projectiles.add(new_bullet1)
            boss_projectiles.add(new_bullet2)
        elif self.phase == 3:
            # 360-degree attack: fire 12 bullets in all directions
            num_bullets = 12
            bullet_speed = 10
            for i in range(num_bullets):
                angle_deg = i * (360 / num_bullets)
                angle_rad = math.radians(angle_deg)
                vx = bullet_speed * math.cos(angle_rad)
                vy = bullet_speed * math.sin(angle_rad)
                new_bullet = Bullet(self.rect.centerx, self.rect.centery, velocity=(vx, vy),
                                      image_path="images/environment/spells/fire_ball_spell.png", width=40, height=40)
                boss_projectiles.add(new_bullet)
    def draw_health_bar(self, surface, camera_offset):
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.health / self.max_health
        health_bar_width = int(bar_width * health_ratio)
        bar_x = self.rect.x - camera_offset[0]
        bar_y = self.rect.y - 10 - camera_offset[1]
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_bar_width, bar_height))

# --------------------
# TiledBasePlatform Class
# --------------------
class TiledBasePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_map, tile_width, tile_height, tile_images=None):
        super().__init__()
        self.tile_map = tile_map
        self.tile_width = tile_width
        self.tile_height = tile_height
        rows = len(tile_map)
        cols = len(tile_map[0]) if rows > 0 else 0
        width = cols * tile_width
        height = rows * tile_height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        if tile_images is None:
            tile_images = {
                0: "images/base_platform_tile.png",
                1: "images/base_platform_trap.png"
            }
        self.tile_images = {}
        for tile_type, path in tile_images.items():
            img = load_image(path, tile_width, tile_height)
            if img is None:
                fallback = pygame.Surface((tile_width, tile_height))
                fallback.fill(GREEN if tile_type == 0 else RED)
                self.tile_images[tile_type] = fallback
            else:
                self.tile_images[tile_type] = img
        for r in range(rows):
            for c in range(cols):
                tile_type = tile_map[r][c]
                tile_img = self.tile_images.get(tile_type)
                if tile_img:
                    self.image.blit(tile_img, (c * tile_width, r * tile_height))

# --------------------
# Utility Functions
# --------------------
def reset_game(player):
    print("Game Over! Restarting from the beginning...")
    player.health = 100
    player.mana = 100  # Reset mana to full
    player.damage_cooldown = 0
    player.rect.topleft = (50, MAP_HEIGHT - 100)
    player.vel_y = 0
    return 0

def draw_sprite_group(group, screen, camera_offset):
    for sprite in group:
        screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))

def get_camera_offset(player):
    camera_x = player.rect.centerx - WIDTH//2
    camera_y = player.rect.centery - HEIGHT//2
    camera_x = max(0, min(camera_x, MAP_WIDTH - WIDTH))
    camera_y = max(0, min(camera_y, MAP_HEIGHT - HEIGHT))
    return (camera_x, camera_y)

# --------------------
# Level Configurations
# --------------------
levels_config = [
    # Level 1: Getting Guy'd
    {
        "background_color": (20, 20, 20),
        "background_image": "images/environment/background/environment-background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0,0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0]],
             "tile_images": {0: "images/environment/background/ground_1.png", 1: "images/environment/background/water.gif"}},
            {"x": 50, "y": 600, "w": 200, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 300, "y": 500, "w": 150, "h": 20, "image": "images/environment/background/float_plat.png",
             "moving": True, "speed": 2, "direction": (1, 0), "boundaries": [300,600,500,500]}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "small", "x": 120, "y": 580, "w": 60, "h": 60,
             "speed": 3, "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True}
        ],
        "pickups": [
            {"type": "health", "x": 500, "y": 550, "w": 50, "h": 50,
             "value": 20, "image": "images/environment/spells/Heart.png"},
            {"type": "bullet", "x": 700, "y": 550, "w": 50, "h": 50,
             "value": 1, "image": "images/environment/spells/mana_poition.png"}
        ],
        "goal": {"x": 1000, "y": MAP_HEIGHT - 90, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Level 1: Getting Guy'd"
    },
    # Level 2: Sudden Death!
    {
        "background_color": (0, 0, 0),
        "background_image": "images/environment/background/environment-background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0,0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0]],
             "tile_images": {0: "images/environment/background/ground_1.png", 1: "images/environment/background/water.gif"}},
            {"x": 100, "y": 650, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 250, "y": 550, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 400, "y": 450, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 550, "y": 350, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 700, "y": 200, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "small", "x": 120, "y": 580, "w": 60, "h": 60,
             "speed": 3, "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True},
            {"x": 280, "y": 530, "w": 30, "h": 30, "speed": 4, "vertical": False,
             "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True},
            {"x": 430, "y": 430, "w": 30, "h": 30, "speed": 4, "vertical": False,
             "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True},
            {"x": 580, "y": 330, "w": 30, "h": 30, "speed": 4, "vertical": False,
             "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True},
            {"x": 300, "y": 300, "w": 30, "h": 30, "speed": 3, "vertical": True,
             "image": "images/environment/small_boss/small_boss_1.png", "dynamic": True}
        ],
        "pickups": [
            {"type": "health", "x": 500, "y": 500, "w": 50, "h": 50,
             "value": 20, "image": "images/environment/spells/Heart.png"}
        ],
        "goal": {"x": 1000, "y": 250, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Level 2: Sudden Death!"
    },
    # Level 3: The Gauntlet
    {
        "background_color": (30, 0, 50),
        "background_image": "images/environment/background/environment-background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0,0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0]],
             "tile_images": {0: "images/environment/background/ground_1.png", 1: "images/environment/background/water.gif"}},
            {"x": 50, "y": 650, "w": 120, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 220, "y": 600, "w": 150, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 400, "y": 500, "w": 120, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 580, "y": 400, "w": 150, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 300, "y": 350, "w": 120, "h": 20, "image": "images/environment/background/float_plat.png"}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "small", "x": 70, "y": 630, "w": 40, "h": 40,
             "speed": 5, "vertical": False, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True},
            {"boss": True, "boss_type": "small", "x": 250, "y": 580, "w": 40, "h": 40,
             "speed": 5, "vertical": False, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True},
            {"boss": True, "boss_type": "small", "x": 420, "y": 530, "w": 40, "h": 40,
             "speed": 5, "vertical": False, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True},
            {"boss": True, "boss_type": "small", "x": 600, "y": 480, "w": 40, "h": 40,
             "speed": 5, "vertical": False, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True},
            {"boss": True, "boss_type": "small", "x": 320, "y": 330, "w": 40, "h": 40,
             "speed": 5, "vertical": False, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True},
            {"boss": True, "boss_type": "small", "x": 400, "y": 200, "w": 40, "h": 40,
             "speed": 4, "vertical": True, "image": "images\\environment\\small_boss\\small_boss_2.png", "dynamic": True}
        ],
        "pickups": [
            {"type": "bullet", "x": 700, "y": 300, "w": 50, "h": 50,
             "value": 1, "image": "images/environment/spells/mana_poition.png"}
        ],
        "goal": {"x": 1100, "y": MAP_HEIGHT - 90, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Level 3: The Gauntlet"
    },
    # Level 4: Final Challenge
    {
        "background_color": (0, 0, 0),
        "background_image": "images/environment/background/environment-background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0,0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0]],
             "tile_images": {0: "images/environment/background/ground_1.png", 1: "images/environment/background/water.gif"}},
            {"x": 50, "y": 700, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 200, "y": 650, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 320, "y": 600, "w": 60, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 420, "y": 550, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 540, "y": 500, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 680, "y": 450, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "small", "x": 70, "y": 680, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/environment/small_boss/small_boss_2.png"},
            {"boss": True, "boss_type": "small", "x": 220, "y": 630, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/spike.png"},
            {"boss": True, "boss_type": "small", "x": 340, "y": 580, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/environment/small_boss/small_boss_2.png"},
            {"boss": True, "boss_type": "small", "x": 440, "y": 530, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/spike.png"},
            {"boss": True, "boss_type": "small", "x": 560, "y": 480, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/environment/small_boss/small_boss_2.png"},
            {"boss": True, "boss_type": "small", "x": 700, "y": 430, "w": 40, "h": 40,
             "speed": 6, "vertical": False, "image": "images/spike.png"},
            {"boss": True, "boss_type": "small", "x": 400, "y": 400, "w": 40, "h": 40,
             "speed": 6, "vertical": True, "image": "images/environment/small_boss/small_boss_2.png"}
        ],
        "pickups": [
            {"type": "health", "x": 600, "y": 380, "w": 50, "h": 50,
             "value": 20, "image": "images/environment/spells/Heart.png"},
            {"type": "bullet", "x": 800, "y": 380, "w": 50, "h": 50,
             "value": 1, "image": "images/environment/spells/mana_poition.png"}
        ],
        "goal": {"x": 1100, "y": 100, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Final Challenge: Prove You're The Guy!"
    },
    # Level 5: Big Boss Fight
    {
        "background_color": (10, 10, 10),
        "background_image": "images/environment/background/boss_background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
             "tile_images": {0: "images/environment/background/ground_1.png", 1: "images/environment/background/water.gif"}},
            {"x": 50, "y": 700, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 200, "y": 650, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 320, "y": 600, "w": 60, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 420, "y": 550, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 540, "y": 500, "w": 100, "h": 20, "image": "images/environment/background/float_plat.png"},
            {"x": 680, "y": 450, "w": 80, "h": 20, "image": "images/environment/background/float_plat.png"}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "big", "x": 300, "y": 400, "w": 120, "h": 120,
             "speed": 2, "dynamic": True, "boundaries": [100, 1000]}
        ],
        "pickups": [
            {"type": "health", "x": 300, "y": 450, "w": 50, "h": 50,
             "value": 30, "image": "images/environment/spells/Heart.png"},
            {"type": "bullet", "x": 650, "y": 450, "w": 50, "h": 50,
             "value": 2, "image": "images/environment/spells/mana_poition.png"}
        ],
        "goal": {"x": 1100, "y": MAP_HEIGHT - 90, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Big Boss Fight: Show Your Might!"
    },
    # Level 6: Ultimate Boss Challenge
    {
        "background_color": (0, 0, 0),
        "background_image": "images/environment/background/dark_boss_background.png",
        "platforms": [
            {"tiled": True, "x": 0, "y": MAP_HEIGHT - 40,
             "tile_width": 50, "tile_height": 60,
             "tiles": [[0] * 24],
             "tile_images": {0: "images/environment/background/ground_boss_dark.png"}},
            {"x": 200, "y": 550, "w": 250, "h": 20, "image": "images/environment/background/float_plat_boss.png"}
        ],
        "obstacles": [
            {"boss": True, "boss_type": "big", "x": 600, "y": 180, "w": 140, "h": 140,
             "speed": 2.5, "dynamic": True}
        ],
        "pickups": [
            {"type": "health", "x": 400, "y": 500, "w": 50, "h": 50,
             "value": 30, "image": "images/environment/spells/Heart.png"},
            {"type": "bullet", "x": 700, "y": 500, "w": 50, "h": 50,
             "value": 2, "image": "images/environment/spells/mana_poition.png"}
        ],
        "goal": {"x": 1100, "y": MAP_HEIGHT - 90, "w": 50, "h": 50,
                 "color": GOLD, "image": "images/environment/open_gate.png"},
        "challenge_message": "Level 6: The Ultimate Boss!"
    }
]

# --------------------
# Level Class
# --------------------
class Level:
    def __init__(self, config, difficulty_multiplier):
        self.config = config
        self.platforms = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.background_color = self.config.get("background_color", BLACK)
        self.difficulty_multiplier = difficulty_multiplier
        self.background_image_path = self.config.get("background_image", None)
        if self.background_image_path:
            self.background_image = load_image(self.background_image_path, MAP_WIDTH, MAP_HEIGHT)
        else:
            self.background_image = None

        for plat_conf in self.config.get("platforms", []):
            if plat_conf.get("moving", False):
                platform = MovingPlatform(
                    plat_conf["x"],
                    plat_conf["y"],
                    plat_conf["w"],
                    plat_conf["h"],
                    plat_conf.get("color", RED),
                    plat_conf.get("image", None),
                    plat_conf.get("speed", 2),
                    plat_conf.get("direction", (1, 0)),
                    plat_conf.get("boundaries", (plat_conf["x"], plat_conf["x"] + 300, plat_conf["y"], plat_conf["y"]))
                )
            elif plat_conf.get("tiled", False):
                platform = TiledBasePlatform(
                    plat_conf["x"],
                    plat_conf["y"],
                    plat_conf["tiles"],
                    plat_conf["tile_width"],
                    plat_conf["tile_height"],
                    plat_conf.get("tile_images", None)
                )
            else:
                platform = Platform(
                    plat_conf["x"],
                    plat_conf["y"],
                    plat_conf["w"],
                    plat_conf["h"],
                    plat_conf.get("color", RED),
                    plat_conf.get("image", None)
                )
            self.platforms.add(platform)

        for obs_conf in self.config.get("obstacles", []):
            speed = obs_conf.get("speed", 2) * self.difficulty_multiplier
            image_path = obs_conf.get("image", None)
            if obs_conf.get("boss", False):
                boss_type = obs_conf.get("boss_type", "small")
                if boss_type == "small":
                    obstacle = SmallBoss(
                        obs_conf["x"],
                        obs_conf["y"],
                        obs_conf["w"],
                        obs_conf["h"],
                        speed,
                        image_path,
                        obs_conf.get("dynamic", False)
                    )
                elif boss_type == "big":
                    obstacle = Boss(
                        obs_conf["x"],
                        obs_conf["y"],
                        obs_conf["w"],
                        obs_conf["h"],
                        speed,
                        boss_frames,
                        obs_conf.get("dynamic", False)
                    )
                else:
                    obstacle = SmallBoss(
                        obs_conf["x"],
                        obs_conf["y"],
                        obs_conf["w"],
                        obs_conf["h"],
                        speed,
                        image_path,
                        obs_conf.get("dynamic", False)
                    )
            else:
                obstacle = Obstacle(
                    obs_conf["x"],
                    obs_conf["y"],
                    obs_conf["w"],
                    obs_conf["h"],
                    speed,
                    image_path,
                    obs_conf.get("dynamic", False)
                )
            if obs_conf.get("vertical", False):
                obstacle.vertical = True
            self.obstacles.add(obstacle)

        for pickup_conf in self.config.get("pickups", []):
            ptype = pickup_conf.get("type", "health")
            value = pickup_conf.get("value", 20 if ptype=="health" else 1)
            image_path = pickup_conf.get("image", None)
            pickup = Pickup(
                pickup_conf["x"],
                pickup_conf["y"],
                pickup_conf["w"],
                pickup_conf["h"],
                ptype,
                value,
                image_path
            )
            self.pickups.add(pickup)

        goal_conf = self.config.get("goal", {"x": MAP_WIDTH - 100,
                                               "y": MAP_HEIGHT - 150,
                                               "w": 50,
                                               "h": 50,
                                               "color": GOLD})
        self.goal = pygame.Rect(
            goal_conf.get("x", MAP_WIDTH - 100),
            goal_conf.get("y", MAP_HEIGHT - 150),
            goal_conf.get("w", 50),
            goal_conf.get("h", 50)
        )
        self.goal_color = goal_conf.get("color", GOLD)
        self.goal_image_path = goal_conf.get("image", None)
        if self.goal_image_path:
            self.goal_image = load_image(self.goal_image_path, self.goal.width, self.goal.height)
        else:
            self.goal_image = None

        self.challenge_message = self.config.get("challenge_message", None)

    def draw(self, screen, camera_offset):
        if self.background_image:
            screen.blit(self.background_image, (-camera_offset[0], -camera_offset[1]))
        else:
            screen.fill(self.background_color)
        for sprite in self.platforms:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        for sprite in self.obstacles:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        for sprite in self.pickups:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        if self.goal_image:
            screen.blit(self.goal_image, (self.goal.x - camera_offset[0], self.goal.y - camera_offset[1]))
        else:
            pygame.draw.rect(screen, self.goal_color,
                             (self.goal.x - camera_offset[0], self.goal.y - camera_offset[1],
                              self.goal.width, self.goal.height))
        if self.challenge_message:
            font = pygame.font.SysFont(None, 36)
            message = font.render(self.challenge_message, True, WHITE)
            screen.blit(message, (WIDTH//2 - message.get_width()//2, 20))

    def update(self):
        self.obstacles.update()
        for platform in self.platforms:
            if hasattr(platform, 'update'):
                platform.update()

# --------------------
# Main Menu and Game Loop
# --------------------
def main_menu():
    global selected_difficulty
    show_about_screen()
    font = pygame.font.SysFont(None, 48)
    while True:
        screen.fill(BLACK)
        title_text = font.render("Select Difficulty", True, WHITE)
        easy_text = font.render("1. Easy", True, WHITE)
        medium_text = font.render("2. Medium", True, WHITE)
        hard_text = font.render("3. Hard", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        screen.blit(easy_text, (WIDTH//2 - easy_text.get_width()//2, 200))
        screen.blit(medium_text, (WIDTH//2 - medium_text.get_width()//2, 300))
        screen.blit(hard_text, (WIDTH//2 - hard_text.get_width()//2, 400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_difficulty = "Easy"
                    return
                elif event.key == pygame.K_2:
                    selected_difficulty = "Medium"
                    return
                elif event.key == pygame.K_3:
                    selected_difficulty = "Hard"
                    return
        clock.tick(FPS)

def get_camera_offset(player):
    camera_x = player.rect.centerx - WIDTH//2
    camera_y = player.rect.centery - HEIGHT//2
    camera_x = max(0, min(camera_x, MAP_WIDTH - WIDTH))
    camera_y = max(0, min(camera_y, MAP_HEIGHT - HEIGHT))
    return (camera_x, camera_y)

def game_loop():
    difficulty_multiplier = DIFFICULTY[selected_difficulty]
    current_level_index = 4  # For testing, you can adjust the starting level here.
    total_levels = len(levels_config)
    MANA_COST = 10
    desired_width = 64
    desired_height = 64
    scaled_player_frames = [pygame.transform.scale(frame, (desired_width, desired_height))
                            for frame in player_frames]
    player = Player(50, MAP_HEIGHT - 100, frames=scaled_player_frames, frame_duration=100)
    player_group = [player]
    while True:
        level = Level(levels_config[current_level_index], difficulty_multiplier)
        level_running = True
        while level_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    pressed_key = event.unicode.lower()
                    if pressed_key == 'f' or pressed_key == 'ｆ':
                        if player.mana >= MANA_COST:
                            print("Spell fired!")
                            new_bullet = Bullet(player.rect.centerx, player.rect.centery, player.facing,
                                                 image_path="images/environment/spells/fire_ball_spell.png")
                            bullet_group.add(new_bullet)
                            player.mana -= MANA_COST
                        else:
                            print("Not enough mana!")
            player.update(level.platforms.sprites())
            bullet_group.update()
            boss_projectiles.update()
            level.update()
            # Process bullet collisions (now manually so that boss damage is gradual)
            for bullet in bullet_group:
                for obstacle in level.obstacles:
                    if bullet.rect.colliderect(obstacle.rect):
                        if isinstance(obstacle, Boss):
                            obstacle.health -= 10  # Reduced damage per bullet
                            bullet.kill()
                            if obstacle.health <= 0:
                                obstacle.kill()
                        else:
                            bullet.kill()
                            obstacle.kill()
            # Check collision with boss projectiles
            if pygame.sprite.spritecollide(player, boss_projectiles, True):
                player.health -= 10
                print("Player hit by a boss projectile!")
            # Check collision with other obstacles
            if pygame.sprite.spritecollide(player, level.obstacles, False) and player.damage_cooldown == 0:
                player.health -= 20
                player.damage_cooldown = 30
                player.rect.topleft = (50, MAP_HEIGHT - 100)
                player.vel_y = 0
            pickup_hits = pygame.sprite.spritecollide(player, level.pickups, True)
            for pickup in pickup_hits:
                if pickup.ptype == "health":
                    player.health = min(100, player.health + pickup.value)
                    print("Picked up health!")
                elif pickup.ptype == "bullet":
                    player.mana = min(100, player.mana + pickup.value * 10)
                    print("Picked up mana!")
            # For levels with bosses, lock the goal until all bosses are defeated.
            goal_reached = player.rect.colliderect(level.goal)
            boss_alive = False
            for obstacle in level.obstacles:
                if isinstance(obstacle, Boss) and obstacle.health > 0:
                    boss_alive = True
                    break
            if goal_reached and not boss_alive:
                print(f"Level {current_level_index + 1} complete!")
                player.mana = 100
                current_level_index += 1
                if current_level_index >= total_levels:
                    print("You've completed all levels! Congratulations!")
                    pygame.quit()
                    sys.exit()
                else:
                    player.rect.topleft = (50, MAP_HEIGHT - 100)
                    player.vel_y = 0
                    bullet_group.empty()
                    boss_projectiles.empty()
                    level_running = False
            if player.health <= 0:
                current_level_index = reset_game(player)
                bullet_group.empty()
                boss_projectiles.empty()
                break
            camera_offset = get_camera_offset(player)
            level.draw(screen, camera_offset)
            for spr in player_group:
                screen.blit(spr.image, (spr.rect.x - camera_offset[0], spr.rect.y - camera_offset[1]))
            draw_sprite_group(bullet_group, screen, camera_offset)
            draw_sprite_group(boss_projectiles, screen, camera_offset)
            # Draw Player Health Bar
            bar_width = 200
            bar_height = 20
            health_percentage = player.health / 100
            current_bar_width = int(bar_width * health_percentage)
            pygame.draw.rect(screen, RED, (20, 20, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (20, 20, current_bar_width, bar_height))
            # Draw Player Mana Bar
            mana_bar_width = 200
            mana_bar_height = 20
            mana_percentage = player.mana / 100
            current_mana_width = int(mana_bar_width * mana_percentage)
            pygame.draw.rect(screen, (0, 0, 100), (20, 50, mana_bar_width, mana_bar_height))
            pygame.draw.rect(screen, (0, 0, 255), (20, 50, current_mana_width, mana_bar_height))
            mana_text = pygame.font.SysFont(None, 36).render(f"Mana: {player.mana}", True, WHITE)
            screen.blit(mana_text, (WIDTH - mana_text.get_width() - 20, 50))
            # Draw Boss Health Bar for any Boss in the level
            for obstacle in level.obstacles:
                if isinstance(obstacle, Boss):
                    obstacle.draw_health_bar(screen, camera_offset)
            pygame.display.flip()
            clock.tick(FPS)

# --------------------
# Main Execution
# --------------------
if __name__ == "__main__":
    main_menu()
    game_loop()
    pygame.quit()
