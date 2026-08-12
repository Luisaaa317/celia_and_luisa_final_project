import pygame
import sys

#initialize Pygame
pygame.init()

#screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buy Ticket Game")

#colors
WHITE = (255, 255, 255)

#create backgrounds and make them fit the window
background1 = pygame.image.load("background_example.PNG").convert()
background1 = pygame.transform.scale(background1, (WIDTH, HEIGHT))

background2 = pygame.image.load("background.jpeg").convert()
background2 = pygame.transform.scale(background2, (WIDTH, HEIGHT))

# buy ticket button setup
button_width, button_height = 200, 60
button_x = WIDTH // 2 - button_width // 2
button_y = HEIGHT // 2 - button_height // 2
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

#font
font = pygame.font.SysFont(None, 48)

#initial state of the game
current_background = background1
button_visible = True

#clock, debug added by AI
clock = pygame.time.Clock()

#main game loop
running = True
while running:
    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_visible and button_rect.collidepoint(event.pos):
                # Button clicked: hide it and change background
                button_visible = False
                current_background = background2

    screen.blit(current_background, (0, 0))

    # draw buy ticket button
    if button_visible:
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        text = font.render("Buy Ticket", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)


    pygame.display.flip()

    #debug added by AI
    clock.tick(60)

# safely quit pygame
pygame.quit()
sys.exit()
