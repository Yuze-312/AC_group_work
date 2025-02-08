import pygame
import sys

# Initialize Pygame
pygame.init()

# Window dimensions
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 240
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tile Background Example")

# Load images
corner1 = pygame.image.load("corner_1.png").convert_alpha()
corner2 = pygame.image.load("corner_2.png").convert_alpha()
corner3 = pygame.image.load("corner_3.png").convert_alpha()
corner4 = pygame.image.load("corner_4.png").convert_alpha()
edge    = pygame.image.load("straight_edge.png").convert_alpha()
wall    = pygame.image.load("wall.png").convert_alpha()
tree    = pygame.image.load("tree.png").convert_alpha()

# (Optional) Determine tile size from one of the corner tiles
TILE_WIDTH = corner1.get_width()
TILE_HEIGHT = corner1.get_height()

# Example layout in a grid:
# We'll create a small 5x3 "platform" with corners, edges, and walls.
# Then place a tree somewhere in the scene.

# We'll define a 2D list: 0 for empty, or a tile code for each cell.
# For instance:
#    c1 = corner_1, c2 = corner_2, c3 = corner_3, c4 = corner_4
#    e  = edge,      w  = wall
#
# Grid notation (row by row)
# top row:    [c1, e,  e,  e,  c2]
# middle row: [w,  w,  w,  w,  w ]
# bottom row: [c3, e,  e,  e,  c4]
# We'll place this block at (x=0, y=0) for simplicity.

tile_map = [
    ["c1", "e",  "e",  "e",  "c2"],
    ["w",  "w",  "w",  "w",  "w" ],
    ["c3", "e",  "e",  "e",  "c4"]
]

def draw_tile(tile_type, x, y):
    """Draw a single tile image based on tile_type at (x, y)."""
    if tile_type == "c1":
        screen.blit(corner1, (x, y))
    elif tile_type == "c2":
        screen.blit(corner2, (x, y))
    elif tile_type == "c3":
        screen.blit(corner3, (x, y))
    elif tile_type == "c4":
        screen.blit(corner4, (x, y))
    elif tile_type == "e":
        screen.blit(edge, (x, y))
    elif tile_type == "w":
        screen.blit(wall, (x, y))
    # If empty or unknown, do nothing

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill background with a solid color (e.g., sky)
    screen.fill((110, 180, 160))  # any color you want

    # Draw the tile map in the top-left corner of the screen
    for row_index, row in enumerate(tile_map):
        for col_index, tile_code in enumerate(row):
            x_pos = col_index * TILE_WIDTH
            y_pos = row_index * TILE_HEIGHT
            draw_tile(tile_code, x_pos, y_pos)

    # Place the tree somewhere in the background.
    # For example, at (x=150, y=10).
    screen.blit(tree, (150, 10))

    # Flip the display
    pygame.display.update()
    clock.tick(60)  # Limit to 60 FPS
