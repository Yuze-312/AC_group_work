import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# --------------------
# Global Constants
# --------------------
# Display size (the window)
WIDTH, HEIGHT = 800, 600  
# Map (level) size (larger than the display)
MAP_WIDTH, MAP_HEIGHT = 1200, 800  

FPS = 60

# Colors (fallback colors)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
GOLD   = (255, 215, 0)
YELLOW = (255, 255, 0)  # For bullets

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I Wanna Be The Guy Tribute with Pickups & Camera")
clock = pygame.time.Clock()

# Difficulty multipliers (scale obstacle speeds)
DIFFICULTY = {
    "Easy": 1,
    "Medium": 1.5,
    "Hard": 2,
}
selected_difficulty = "Easy"  # Selected in the main menu

# --------------------
# Image Cache & Loader
# --------------------
image_cache = {}

def load_image(path, w, h):
    """
    Loads an image from 'path', scales it to (w, h), and caches it.
    Returns None if the image file is not found.
    """
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

# --------------------
# About Screen Function
# --------------------
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
        "  - Press F to shoot (ammo is limited).",
        "  - Collect health and ammo pickups to heal and gain bullets.",
        "  - Avoid obstacles and reach the goal to progress.",
        "",
        "Press any key to continue..."
    ]
    while about:
        screen.fill(BLACK)
        title_surface = font_title.render("How to Play", True, WHITE)
        screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 50))
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

# --------------------
# Level Configurations
# (Inspired by I Wanna Be The Guy – positions now use the larger MAP dimensions.
#  Pickups have been added. Adjust image names as needed.)
# --------------------
levels_config = [
    # Level 1: Getting Guy'd
    {
        "background_color": (20, 20, 20),
        "background_image": "bg_level1.png",  # Should be sized for the full map (MAP_WIDTH x MAP_HEIGHT)
        "platforms": [
            {"x": 0, "y": MAP_HEIGHT - 40, "w": MAP_WIDTH, "h": 40, "color": (50, 50, 50), "image": "platform.png"},
            {"x": 50, "y": 600, "w": 200, "h": 20, "image": "platform.png"},
            {"x": 300, "y": 500, "w": 150, "h": 20, "image": "platform.png"}
        ],
        "obstacles": [
            {"x": 120, "y": 580, "w": 30, "h": 30, "speed": 3, "vertical": False, "image": "spike.png"}
        ],
        "pickups": [
            # A health pack (heals +20)
            {"type": "health", "x": 500, "y": 550, "w": 30, "h": 30, "value": 20, "image": "health.png"},
            # An ammo pack (adds one bullet)
            {"type": "bullet", "x": 700, "y": 550, "w": 30, "h": 30, "value": 1, "image": "ammo.png"}
        ],
        "goal": {"x": 1000, "y": MAP_HEIGHT - 90, "w": 50, "h": 50, "color": GOLD, "image": "goal.png"},
        "challenge_message": "Level 1: Getting Guy'd"
    },
    # Level 2: Sudden Death!
    {
        "background_color": (0, 0, 0),
        "background_image": "bg_level2.png",
        "platforms": [
            {"x": 0, "y": MAP_HEIGHT - 40, "w": MAP_WIDTH, "h": 40, "color": (30,30,30), "image": "platform.png"},
            {"x": 100, "y": 650, "w": 100, "h": 20, "image": "platform.png"},
            {"x": 250, "y": 550, "w": 100, "h": 20, "image": "platform.png"},
            {"x": 400, "y": 450, "w": 100, "h": 20, "image": "platform.png"},
            {"x": 550, "y": 350, "w": 100, "h": 20, "image": "platform.png"}
        ],
        "obstacles": [
            {"x": 130, "y": 630, "w": 30, "h": 30, "speed": 4, "vertical": False, "image": "spike.png"},
            {"x": 280, "y": 530, "w": 30, "h": 30, "speed": 4, "vertical": False, "image": "spike.png"},
            {"x": 430, "y": 430, "w": 30, "h": 30, "speed": 4, "vertical": False, "image": "spike.png"},
            {"x": 580, "y": 330, "w": 30, "h": 30, "speed": 4, "vertical": False, "image": "spike.png"},
            {"x": 300, "y": 300, "w": 30, "h": 30, "speed": 3, "vertical": True, "image": "spike.png"}
        ],
        "pickups": [
            {"type": "health", "x": 500, "y": 500, "w": 30, "h": 30, "value": 20, "image": "health.png"}
        ],
        "goal": {"x": 1000, "y": 250, "w": 50, "h": 50, "color": GOLD, "image": "goal.png"},
        "challenge_message": "Level 2: Sudden Death!"
    },
    # Level 3: The Gauntlet
    {
        "background_color": (30, 0, 50),
        "background_image": "bg_level3.png",
        "platforms": [
            {"x": 0, "y": MAP_HEIGHT - 40, "w": MAP_WIDTH, "h": 40, "color": (40, 40, 40), "image": "platform.png"},
            {"x": 50, "y": 650, "w": 120, "h": 20, "image": "platform.png"},
            {"x": 220, "y": 600, "w": 150, "h": 20, "image": "platform.png"},
            {"x": 400, "y": 500, "w": 120, "h": 20, "image": "platform.png"},
            {"x": 580, "y": 400, "w": 150, "h": 20, "image": "platform.png"},
            {"x": 300, "y": 350, "w": 120, "h": 20, "image": "platform.png"}
        ],
        "obstacles": [
            {"x": 70, "y": 630, "w": 30, "h": 30, "speed": 5, "vertical": False, "image": "spike.png"},
            {"x": 250, "y": 580, "w": 30, "h": 30, "speed": 5, "vertical": False, "image": "spike.png"},
            {"x": 420, "y": 530, "w": 30, "h": 30, "speed": 5, "vertical": False, "image": "spike.png"},
            {"x": 600, "y": 480, "w": 30, "h": 30, "speed": 5, "vertical": False, "image": "spike.png"},
            {"x": 320, "y": 330, "w": 30, "h": 30, "speed": 5, "vertical": False, "image": "spike.png"},
            {"x": 400, "y": 200, "w": 30, "h": 30, "speed": 4, "vertical": True, "image": "spike.png"}
        ],
        "pickups": [
            {"type": "bullet", "x": 700, "y": 300, "w": 30, "h": 30, "value": 1, "image": "ammo.png"}
        ],
        "goal": {"x": 1100, "y": MAP_HEIGHT - 90, "w": 50, "h": 50, "color": GOLD, "image": "goal.png"},
        "challenge_message": "Level 3: The Gauntlet"
    },
    # Level 4: Final Challenge
    {
        "background_color": (0, 0, 0),
        "background_image": "bg_level4.png",
        "platforms": [
            {"x": 0, "y": MAP_HEIGHT - 40, "w": MAP_WIDTH, "h": 40, "color": (20,20,20), "image": "platform.png"},
            {"x": 50, "y": 700, "w": 100, "h": 20, "image": "platform.png"},
            {"x": 200, "y": 650, "w": 80, "h": 20, "image": "platform.png"},
            {"x": 320, "y": 600, "w": 60, "h": 20, "image": "platform.png"},
            {"x": 420, "y": 550, "w": 80, "h": 20, "image": "platform.png"},
            {"x": 540, "y": 500, "w": 100, "h": 20, "image": "platform.png"},
            {"x": 680, "y": 450, "w": 80, "h": 20, "image": "platform.png"}
        ],
        "obstacles": [
            {"x": 70, "y": 680, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 220, "y": 630, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 340, "y": 580, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 440, "y": 530, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 560, "y": 480, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 700, "y": 430, "w": 30, "h": 30, "speed": 6, "vertical": False, "image": "spike.png"},
            {"x": 400, "y": 400, "w": 30, "h": 30, "speed": 6, "vertical": True, "image": "spike.png"}
        ],
        "pickups": [
            {"type": "health", "x": 600, "y": 380, "w": 30, "h": 30, "value": 20, "image": "health.png"},
            {"type": "bullet", "x": 800, "y": 380, "w": 30, "h": 30, "value": 1, "image": "ammo.png"}
        ],
        "goal": {"x": 1100, "y": 100, "w": 50, "h": 50, "color": GOLD, "image": "goal.png"},
        "challenge_message": "Final Challenge: Prove You're The Guy!"
    }
]

# --------------------
# New Pickup Class
# --------------------
class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, ptype, value, image_path=None):
        super().__init__()
        self.ptype = ptype  # 'health' or 'bullet'
        self.value = value
        if image_path:
            loaded_image = load_image(image_path, w, h)
            if loaded_image:
                self.image = loaded_image
            else:
                self.image = pygame.Surface((w, h))
                self.image.fill(GREEN if ptype=="health" else YELLOW)
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(GREEN if ptype=="health" else YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

# --------------------
# New Bullet Class
# --------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction  # 1 for right, -1 for left

    def update(self):
        self.rect.x += self.speed
        # IMPORTANT: Use MAP_WIDTH for boundary checking instead of WIDTH
        if self.rect.right < 0 or self.rect.left > MAP_WIDTH:
            self.kill()

# --------------------
# Game Classes
# --------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Represented by a blue rectangle.
        self.image = pygame.Surface((40, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.speed = 5
        self.jump_strength = -15
        self.on_ground = False
        self.facing = 1  # 1 for right, -1 for left

        # New attributes for health and bullet count.
        self.health = 100
        self.bullet_count = 10
        self.damage_cooldown = 0  # Frames of invulnerability after damage

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.facing = -1
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.facing = 1
            self.rect.x += self.speed

        # Apply gravity.
        self.vel_y += 0.8
        self.rect.y += self.vel_y

        # Platform collision (only when falling).
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect) and self.vel_y >= 0:
                self.rect.bottom = plat.rect.top
                self.vel_y = 0
                self.on_ground = True

        # Clamp horizontal movement.
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH

        # Reset if falling below the map.
        if self.rect.top > MAP_HEIGHT:
            self.rect.topleft = (50, MAP_HEIGHT - 100)
            self.vel_y = 0

        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_strength

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=GREEN, image_path=None):
        super().__init__()
        if image_path:
            loaded_image = load_image(image_path, w, h)
            if loaded_image:
                self.image = loaded_image
            else:
                self.image = pygame.Surface((w, h))
                self.image.fill(color)
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, image_path=None):
        super().__init__()
        if image_path:
            loaded_image = load_image(image_path, w, h)
            if loaded_image:
                self.image = loaded_image
            else:
                self.image = pygame.Surface((w, h))
                self.image.fill(RED)
        else:
            self.image = pygame.Surface((w, h))
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.vertical = False  # Default: horizontal movement

    def update(self):
        if self.vertical:
            self.rect.y += self.speed
            if self.rect.top <= 0 or self.rect.bottom >= MAP_HEIGHT:
                self.speed = -self.speed
        else:
            self.rect.x += self.speed
            if self.rect.left <= 0 or self.rect.right >= MAP_WIDTH:
                self.speed = -self.speed

class Level:
    def __init__(self, config, difficulty_multiplier):
        self.config = config
        self.platforms = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.background_color = self.config.get("background_color", BLACK)
        self.difficulty_multiplier = difficulty_multiplier

        # Load the background image scaled to the full map size.
        self.background_image_path = self.config.get("background_image", None)
        if self.background_image_path:
            self.background_image = load_image(self.background_image_path, MAP_WIDTH, MAP_HEIGHT)
        else:
            self.background_image = None

        # Create platforms.
        for plat_conf in self.config.get("platforms", []):
            color = plat_conf.get("color", GREEN)
            image_path = plat_conf.get("image", None)
            platform = Platform(plat_conf["x"], plat_conf["y"],
                                plat_conf["w"], plat_conf["h"], color, image_path)
            self.platforms.add(platform)

        # Create obstacles.
        for obs_conf in self.config.get("obstacles", []):
            speed = obs_conf.get("speed", 2) * self.difficulty_multiplier
            image_path = obs_conf.get("image", None)
            obstacle = Obstacle(obs_conf["x"], obs_conf["y"],
                                obs_conf["w"], obs_conf["h"], speed, image_path)
            if obs_conf.get("vertical", False):
                obstacle.vertical = True
            self.obstacles.add(obstacle)

        # Create pickups.
        for pickup_conf in self.config.get("pickups", []):
            ptype = pickup_conf.get("type", "health")
            value = pickup_conf.get("value", 20 if ptype=="health" else 1)
            image_path = pickup_conf.get("image", None)
            pickup = Pickup(pickup_conf["x"], pickup_conf["y"],
                            pickup_conf["w"], pickup_conf["h"], ptype, value, image_path)
            self.pickups.add(pickup)

        # Set up the goal.
        goal_conf = self.config.get("goal", {"x": MAP_WIDTH - 100,
                                               "y": MAP_HEIGHT - 150,
                                               "w": 50,
                                               "h": 50,
                                               "color": GOLD})
        self.goal = pygame.Rect(goal_conf.get("x", MAP_WIDTH - 100),
                                goal_conf.get("y", MAP_HEIGHT - 150),
                                goal_conf.get("w", 50),
                                goal_conf.get("h", 50))
        self.goal_color = goal_conf.get("color", GOLD)
        self.goal_image_path = goal_conf.get("image", None)
        if self.goal_image_path:
            self.goal_image = load_image(self.goal_image_path, self.goal.width, self.goal.height)
        else:
            self.goal_image = None

        self.challenge_message = self.config.get("challenge_message", None)

    def draw(self, screen, camera_offset):
        # Draw background.
        if self.background_image:
            screen.blit(self.background_image, (-camera_offset[0], -camera_offset[1]))
        else:
            screen.fill(self.background_color)
        # Draw platforms.
        for sprite in self.platforms:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        # Draw obstacles.
        for sprite in self.obstacles:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        # Draw pickups.
        for sprite in self.pickups:
            screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))
        # Draw goal.
        if self.goal_image:
            screen.blit(self.goal_image, (self.goal.x - camera_offset[0], self.goal.y - camera_offset[1]))
        else:
            pygame.draw.rect(screen, self.goal_color, 
                             (self.goal.x - camera_offset[0], self.goal.y - camera_offset[1],
                              self.goal.width, self.goal.height))
        # Draw challenge message (fixed to the screen, not scrolling).
        if self.challenge_message:
            font = pygame.font.SysFont(None, 36)
            message = font.render(self.challenge_message, True, WHITE)
            screen.blit(message, (WIDTH//2 - message.get_width()//2, 20))

    def update(self):
        self.obstacles.update()

# --------------------
# Utility Functions
# --------------------
def reset_game(player):
    print("Game Over! Restarting from the beginning...")
    player.health = 100
    player.bullet_count = 10
    player.damage_cooldown = 0
    player.rect.topleft = (50, MAP_HEIGHT - 100)
    player.vel_y = 0
    return 0  # Reset level index to 0

def draw_sprite_group(group, screen, camera_offset):
    for sprite in group:
        screen.blit(sprite.image, (sprite.rect.x - camera_offset[0], sprite.rect.y - camera_offset[1]))

# --------------------
# Menu and Game Loop
# --------------------
def main_menu():
    global selected_difficulty
    # Show the about/instructions screen first.
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

def game_loop():
    difficulty_multiplier = DIFFICULTY[selected_difficulty]
    current_level_index = 0
    total_levels = len(levels_config)

    # Create the player and groups.
    player = Player(50, MAP_HEIGHT - 100)
    player_group = [player]  # We'll draw the player manually with offset.
    bullet_group = pygame.sprite.Group()

    while True:
        # Load the current level.
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
                    if event.key == pygame.K_f and player.bullet_count > 0:
                        bullet = Bullet(player.rect.centerx, player.rect.centery, player.facing)
                        bullet_group.add(bullet)
                        player.bullet_count -= 1

            player.update(level.platforms.sprites())
            bullet_group.update()
            level.update()

            # Check for bullet-obstacle collisions.
            hits = pygame.sprite.groupcollide(bullet_group, level.obstacles, True, True)
            if hits:
                print("Boom! An obstacle was destroyed.")

            # Check for player-obstacle collisions.
            if pygame.sprite.spritecollide(player, level.obstacles, False) and player.damage_cooldown == 0:
                player.health -= 20
                player.damage_cooldown = 30  # About 0.5 sec invulnerability at 60 FPS
                player.rect.topleft = (50, MAP_HEIGHT - 100)
                player.vel_y = 0

            # Check for pickup collisions.
            pickup_hits = pygame.sprite.spritecollide(player, level.pickups, True)
            for pickup in pickup_hits:
                if pickup.ptype == "health":
                    player.health = min(100, player.health + pickup.value)
                    print("Picked up health!")
                elif pickup.ptype == "bullet":
                    player.bullet_count += pickup.value
                    print("Picked up ammo!")

            # If player's health drops to 0, reset the game.
            if player.health <= 0:
                current_level_index = reset_game(player)
                bullet_group.empty()
                break

            # If the player reaches the goal, refill bullets and go to next level.
            if player.rect.colliderect(level.goal):
                print(f"Level {current_level_index + 1} complete!")
                player.bullet_count = 10  # Refill bullets on level change.
                current_level_index += 1
                if current_level_index >= total_levels:
                    print("You've completed all levels! Congratulations!")
                    pygame.quit()
                    sys.exit()
                else:
                    player.rect.topleft = (50, MAP_HEIGHT - 100)
                    player.vel_y = 0
                    bullet_group.empty()
                    level_running = False

            # --- Camera Calculation ---
            # Center the camera on the player's center, clamped to the map.
            camera_x = player.rect.centerx - WIDTH // 2
            camera_y = player.rect.centery - HEIGHT // 2
            camera_x = max(0, min(camera_x, MAP_WIDTH - WIDTH))
            camera_y = max(0, min(camera_y, MAP_HEIGHT - HEIGHT))
            camera_offset = (camera_x, camera_y)

            # Draw everything with camera offset.
            level.draw(screen, camera_offset)
            # Draw player.
            for spr in player_group:
                screen.blit(spr.image, (spr.rect.x - camera_offset[0], spr.rect.y - camera_offset[1]))
            # Draw bullets.
            draw_sprite_group(bullet_group, screen, camera_offset)

            # Draw the health bar.
            bar_width = 200
            bar_height = 20
            health_percentage = player.health / 100
            current_bar_width = int(bar_width * health_percentage)
            pygame.draw.rect(screen, RED, (20, 20, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (20, 20, current_bar_width, bar_height))
            # Draw bullet count text.
            font = pygame.font.SysFont(None, 36)
            bullet_text = font.render(f"Bullets: {player.bullet_count}", True, WHITE)
            screen.blit(bullet_text, (WIDTH - bullet_text.get_width() - 20, 20))

            pygame.display.flip()
            clock.tick(FPS)

# --------------------
# Main Execution
# --------------------
if __name__ == "__main__":
    main_menu()
    game_loop()
    pygame.quit()
