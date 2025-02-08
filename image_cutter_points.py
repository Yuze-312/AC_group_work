import pygame
import sys
import os

pygame.init()

# --------------------
# Global Constants
# --------------------
FPS = 60
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
screen = pygame.display.set_mode((800, 600))
# --------------------
# Configuration
# --------------------
SOURCE_IMAGE_PATH = "images/environment/background/environment-tiles.png"         # Change this to your PNG file path
OUTPUT_IMAGE_PATH = "cropped_polygon.png"  # Output file name

# --------------------
# Set up Display
# --------------------
# We'll load the image first to get its size
if not os.path.exists(SOURCE_IMAGE_PATH):
    sys.exit(f"Source image '{SOURCE_IMAGE_PATH}' not found.")

source_image = pygame.image.load(SOURCE_IMAGE_PATH).convert_alpha()
img_width, img_height = source_image.get_size()
print("Source image size:", img_width, "x", img_height)

# Set the display to match the image size
screen = pygame.display.set_mode((img_width, img_height))
pygame.display.set_caption("Polygon Crop Tool")
clock = pygame.time.Clock()

# --------------------
# Polygon Selection Variables
# --------------------
polygon_points = []  # List to store clicked points

# --------------------
# Main Loop
# --------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Add a point when left mouse button is pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                polygon_points.append(event.pos)
                print(f"Point added: {event.pos}")

        # Key events for finishing or resetting selection
        elif event.type == pygame.KEYDOWN:
            # Press SPACE to save the selected polygon region
            if event.key == pygame.K_SPACE:
                if len(polygon_points) >= 3:
                    # Create a surface (same size as the source) for the mask
                    mask_surf = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
                    mask_surf.fill((0, 0, 0, 0))
                    # Draw the polygon onto the mask surface in opaque white
                    pygame.draw.polygon(mask_surf, (255, 255, 255, 255), polygon_points)
                    # Create a mask from the surface
                    mask = pygame.mask.from_surface(mask_surf)
                    # Create a new surface to hold the cropped region (with per-pixel alpha)
                    cropped_surf = pygame.Surface((img_width, img_height), pygame.SRCALPHA)
                    # Iterate over each pixel; if it is in the mask, copy it from the source image.
                    for x in range(img_width):
                        for y in range(img_height):
                            if mask.get_at((x, y)):
                                cropped_surf.set_at((x, y), source_image.get_at((x, y)))
                    # Optionally, crop further to the bounding rect of the mask:
                    bbox_list = mask.get_bounding_rects()
                    if bbox_list:
                        bbox = bbox_list[0]
                        final_surf = cropped_surf.subsurface(bbox).copy()
                    else:
                        final_surf = cropped_surf
                    pygame.image.save(final_surf, OUTPUT_IMAGE_PATH)
                    print(f"Cropped polygon saved as '{OUTPUT_IMAGE_PATH}'")
                else:
                    print("Select at least 3 points for a valid polygon.")
            # Press R to reset the selection
            elif event.key == pygame.K_r:
                polygon_points = []
                print("Polygon selection reset.")

    # Draw the source image
    screen.blit(source_image, (0, 0))

    # If points exist, draw lines between them
    if len(polygon_points) >= 2:
        pygame.draw.lines(screen, RED, False, polygon_points, 2)
    # In any case, draw circles at each point.
    for point in polygon_points:
        pygame.draw.circle(screen, WHITE, point, 4)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
