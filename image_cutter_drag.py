import pygame, sys, os

pygame.init()
FPS = 60
clock = pygame.time.Clock()

# Set up display (we later adjust to image size)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Drag to Crop")

# File paths
SOURCE_IMAGE_PATH = "images/environment/rpgcritters2.png"
OUTPUT_IMAGE_PATH = "cropped.png"

# Load source image and resize window to match its size
if not os.path.exists(SOURCE_IMAGE_PATH):
    sys.exit(f"Source image '{SOURCE_IMAGE_PATH}' not found.")

source_image = pygame.image.load(SOURCE_IMAGE_PATH).convert_alpha()
img_width, img_height = source_image.get_size()
screen = pygame.display.set_mode((img_width, img_height))

# Function to create a rectangle from two points.
def get_rect(start, end):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    width = abs(start[0] - end[0])
    height = abs(start[1] - end[1])
    return pygame.Rect(x, y, width, height)

selecting = False
start_pos = None
selection_rect = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Start the drag selection
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                start_pos = event.pos
                selecting = True
        # Update the rectangle as you drag
        if event.type == pygame.MOUSEMOTION and selecting:
            end_pos = event.pos
            selection_rect = get_rect(start_pos, end_pos)
        # Finalize selection when mouse button is released
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and selecting:
                end_pos = event.pos
                selection_rect = get_rect(start_pos, end_pos)
                selecting = False
        # Press SPACE to save the cropped area; press SHIFT to cancel the selection.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if selection_rect and selection_rect.width > 0 and selection_rect.height > 0:
                    cropped_image = source_image.subsurface(selection_rect).copy()
                    pygame.image.save(cropped_image, OUTPUT_IMAGE_PATH)
                    print(f"Cropped image saved as '{OUTPUT_IMAGE_PATH}'")
                else:
                    print("No valid selection to save.")
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                selection_rect = None
                start_pos = None
                selecting = False
                print("Selection canceled.")

    screen.blit(source_image, (0, 0))
    if selection_rect:
        pygame.draw.rect(screen, (255, 0, 0), selection_rect, 2)
    pygame.display.flip()
    clock.tick(FPS)
