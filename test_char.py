import pygame
import sys
import os

pygame.init()

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

def get_image_details(file_path):
    image = pygame.image.load(file_path).convert_alpha()
    width, height = image.get_size()
    print("Image size:", width, "x", height)
    return width, height

def slice_sprite_sheet(sheet, sprite_width=32, sprite_height=32, rows=4):
    """
    Slices a sprite sheet into a list of lists. Each sublist contains sprites from one row.
    """
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

WIDTH, HEIGHT = 800, 600              # Display size (window)
MAP_WIDTH, MAP_HEIGHT = 1200, 800     # Full level (map) size
FPS = 60
# Set up a display window sized to the boss frame.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("I Don't Wanna Be The Guy")
clock = pygame.time.Clock()

# load and slice the boss sheet.....
boss_image_path = "images/environment/boss/mage-1-85x94.png"
sheet_width, sheet_height = get_image_details(boss_image_path)
boss_sheet = load_image(boss_image_path, sheet_width, sheet_height)
# Assume there are 4 columns and 4 rows (adjust if needed)
cols, rows = 4, 4
boss_width = sheet_width // cols
boss_height = sheet_height // rows
print("Each sprite is:", boss_width, "x", boss_height)
all_boss_frames = slice_sprite_sheet(boss_sheet, boss_width, boss_height, rows)
# Choose one row for the player's animation (here, row 1)
boss_frames = all_boss_frames[1]

# Load boss sprite sheet using the boss image path
sheet_width, sheet_height = get_image_details(boss_image_path)
boss_sheet = load_image(boss_image_path, sheet_width, sheet_height)

# Assume there are 4 columns and 4 rows in the boss sprite sheet.
cols, rows = 4, 2
boss_width = sheet_width // cols
boss_height = sheet_height // rows
print("Each boss sprite is:", boss_width, "x", boss_height)

# Slice the boss sheet into frames.
all_boss_frames = slice_sprite_sheet(boss_sheet, boss_width, boss_height, rows)
# Choose one row for testing (e.g., row 1)
print(len(all_boss_frames))
boss_frames = all_boss_frames[1]


current_frame = 0
frame_duration = 100  # milliseconds per frame
last_update = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = pygame.time.get_ticks()
    if now - last_update > frame_duration:
        last_update = now
        current_frame = (current_frame + 1) % len(boss_frames)

    screen.fill((0, 0, 0))
    screen.blit(boss_frames[current_frame], (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
