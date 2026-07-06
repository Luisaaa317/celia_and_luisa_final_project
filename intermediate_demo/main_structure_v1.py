import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("game v1")

# Load background from my image
background_image = pygame.image.load("background_example.PNG")  #to be changed later
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load bumblebee image
bee_image = pygame.image.load("bumblebee.PNG")
bee_image = pygame.transform.scale(bee_image, (100, 100))

# Bumblebee class
class Bumblebee:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = bee_image
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create bumblebees
bumblebees = [
    Bumblebee(150, 200),
    Bumblebee(400, 300),
    Bumblebee(650, 150),
]

# Popup spaceholder --> will be mini games later, just for the sake of the demo
popup_active = False
popup_timer = 0

# Main game loop
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for Bumblebee in bumblebees:
                if Bumblebee.is_clicked(mouse_pos):
                    popup_active = True
                    popup_timer = 0
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                popup_active = False  # Close popup with ESC

    if popup_active:
        popup_timer += 1


    screen.blit(background_image, (0, 0))

    for Bumblebee in bumblebees:
        Bumblebee.draw(screen)


    if popup_active:
        popup_width, popup_height = 400, 200
        popup_x = (WIDTH - popup_width) // 2
        popup_y = (HEIGHT - popup_height) // 2

        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.fill((255, 255, 255))  

        font = pygame.font.SysFont("Arial", 20, bold=True)
        text = font.render("spaceholder, minigame coming soon", True, (0, 0, 0))
        text_rect = text.get_rect(center=(popup_width // 2, popup_height // 2))

        popup_surface.blit(text, text_rect)


        screen.blit(popup_surface, (popup_x, popup_y))


        small_font = pygame.font.SysFont("Arial", 20)
        close_text = small_font.render("Press ESC to close", True, (200, 200, 200))
        close_rect = close_text.get_rect(center=(popup_x + popup_width // 2, popup_y + popup_height - 20))
        screen.blit(close_text, close_rect)


    pygame.display.flip()

# Quit
pygame.quit()
sys.exit()
