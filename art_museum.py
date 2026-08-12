#import libraries
import pygame
import sys

#initialize Pygame
pygame.init()

#set up window for game
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buy Ticket Game")

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#create backgrounds and make them fit the window
background1 = pygame.image.load("background_example.PNG").convert()
background1 = pygame.transform.scale(background1, (WIDTH, HEIGHT))

background2 = pygame.image.load("exhibition_hall_final.JPG").convert()
background2 = pygame.transform.scale(background2, (WIDTH, HEIGHT))

background3 = pygame.image.load("background_example.PNG").convert()
background3 = pygame.transform.scale(background3, (WIDTH, HEIGHT))

#buy ticket button setup
button_width, button_height = 200, 60
button_x = WIDTH // 2 - button_width // 2
button_y = HEIGHT // 2 - button_height // 2
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

#exit museum button setup
exit_button_width, exit_button_height = 220, 60
exit_button_x = WIDTH // 2 - exit_button_width // 2
exit_button_y = 20
exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, exit_button_width, exit_button_height)

#font
font = pygame.font.SysFont(None, 48)
info_font = pygame.font.SysFont(None, 28)
title_font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 32)

#initial state of the game
current_background = background1
button_visible = True # becomes false after 2nd background becomes visible
visitor_visible = False #becomes true when 2nd background is visible
exhibition_finished = False   # becomes true once exit button is clicked

#states of keys pressed
left_pressed = False
right_pressed = False
up_pressed = False
down_pressed = False

#constants for the visitor class
SCREEN_WIDTH = WIDTH
SCREEN_HEIGHT = HEIGHT

#create visitor class using own image
class Visitor:
    def __init__(self, pos_x: int, pos_y: int):
        try:
            img = pygame.image.load("character_final.PNG").convert_alpha()
        except pygame.error as e:
            print(f"Error loading character image: {e}")
        else:
            self.img = pygame.transform.scale(img, (100, 100))

        self.pos_x = pos_x
        self.pos_y = pos_y

#make visitor move by using arrow keys
    def animate(self, dr: str):
        direction = 1
        if dr == "left":
            direction = -1

        if dr == "left":
            self.pos_x += direction * 5
        elif dr == "right":
            self.pos_x += direction * 5

        if up_pressed:
            self.pos_y -= 5
        if down_pressed:
            self.pos_y += 5

#make sure visitor cannot leave window
        if self.pos_x < 0:
            self.pos_x = 0
        if self.pos_x > SCREEN_WIDTH - 100:
            self.pos_x = SCREEN_WIDTH - 100

        if self.pos_y < 0:
            self.pos_y = 0
        if self.pos_y > SCREEN_HEIGHT - 100:
            self.pos_y = SCREEN_HEIGHT - 100

    def draw(self):
        screen.blit(self.img, (self.pos_x, self.pos_y))

    #get the visitor's current spot, used for when painting is being clicked
    def get_rect(self):
        return pygame.Rect(self.pos_x, self.pos_y, 100, 100)


#create visitor
visitor = Visitor(100, 200)


#helper function to wrap long text so it fits inside the info window
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "

    lines.append(current_line)
    return lines


#create painting class
class Painting:
    def __init__(self, image_path, rect, title="", description=""):

        self.rect = pygame.Rect(rect)
        self.title = title
        self.description = description
        self.viewed = False   # has the painting been opened yet?
# debug by AI
        try:
            img = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading painting image {image_path}: {e}")
            #fallback: plain gray rectangle so the game doesn't crash
            img = pygame.Surface((self.rect.width, self.rect.height))
            img.fill((180, 180, 180))

        #scale the picture to exactly fit the frame's rectangle
        self.img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

    def draw(self):
        screen.blit(self.img, self.rect.topleft)

    #draws the text window with this painting's title and description
    def draw_info_window(self):
        window_width, window_height = 600, 300
        window_x = WIDTH // 2 - window_width // 2
        window_y = HEIGHT // 2 - window_height // 2

        #semi-transparent dark overlay behind the popup
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        #popup box
        popup_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(screen, WHITE, popup_rect)
        pygame.draw.rect(screen, BLACK, popup_rect, 3)

        #title text
        title_surface = title_font.render(self.title, True, BLACK)
        screen.blit(title_surface, (window_x + 20, window_y + 20))

        #description text
        lines = wrap_text(self.description, info_font, window_width - 40)
        for i, line in enumerate(lines):
            line_surface = info_font.render(line, True, BLACK)
            screen.blit(line_surface, (window_x + 20, window_y + 70 + i * 30))

        #how to close info popup
        hint_surface = info_font.render("press enter or esc to close", True, (100, 100, 100))
        screen.blit(hint_surface, (window_x + 20, window_y + window_height - 35))


#create the 6 paintings (x, y, width, height)
paintings = [
    Painting("background_example.PNG", (174, 165, 102 , 123), "Painting One",
             "This is a description of the first painting. Replace this with your own text about the artwork."),
    Painting("background_example.PNG", (186, 327, 67, 145), "Painting Two",
             "This is a description of the second painting. Replace this with your own text."),
    Painting("background_example.PNG", (335, 173, 143, 80), "Painting Three",
             "This is a description of the third painting. Replace this with your own text."),
    Painting("background_example.PNG", (342, 303, 80, 85), "Painting Four",
             "This is a description of the fourth painting. Replace this with your own text."),
    Painting("background_example.PNG", (522, 355, 90, 90), "Painting Five",
             "This is a description of the fifth painting. Replace this with your own text."),
    Painting("background_example.PNG", (525, 210, 92, 103), "Painting Six",
             "This is a description of the sixth painting. Replace this with your own text."),
]

#which info popup is currently open
active_painting = None

#clock for controlling frame rate --> debug by AI
clock = pygame.time.Clock()

#main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

#if the buy ticket button is clicked the background changes and the visitor becomes visible
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_visible and button_rect.collidepoint(event.pos):
                button_visible = False
                current_background = background2
                visitor_visible = True

            #check if the exit museum button was clicked
            all_viewed = all(p.viewed for p in paintings)
            if all_viewed and not exhibition_finished and exit_button_rect.collidepoint(event.pos):
                exhibition_finished = True
                current_background = background3
                visitor_visible = False

#if the visitor moves
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left_pressed = True
            if event.key == pygame.K_RIGHT:
                right_pressed = True
            if event.key == pygame.K_UP:
                up_pressed = True
            if event.key == pygame.K_DOWN:
                down_pressed = True

            #pressing enter --> visitor intercats with a painting thats being touched
            if event.key == pygame.K_RETURN and not exhibition_finished:
                if active_painting is None:
                    #check if the visitor overlaps any painting
                    visitor_rect = visitor.get_rect()
                    for painting in paintings:
                        if visitor_rect.colliderect(painting.rect):
                            active_painting = painting
                            active_painting.viewed = True   # mark as viewed
                            break
                else:
                    #if a window is already open, enter closes it
                    active_painting = None

            #esc also closes the info window
            if event.key == pygame.K_ESCAPE:
                active_painting = None

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_pressed = False
            if event.key == pygame.K_RIGHT:
                right_pressed = False
            if event.key == pygame.K_UP:
                up_pressed = False
            if event.key == pygame.K_DOWN:
                down_pressed = False

    #visitor moves only if no info window is open and the exhibition isn't finished
    if visitor_visible and active_painting is None and not exhibition_finished:
        if left_pressed:
            visitor.animate("left")
        if right_pressed:
            visitor.animate("right")
        if up_pressed:
            visitor.animate("up")
        if down_pressed:
            visitor.animate("down")

    screen.blit(current_background, (0, 0))

    #draw buy ticket button
    if button_visible:
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        text = font.render("Buy Ticket", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

    #draw paintings only when background 2 is visible
    if current_background is background2 and not exhibition_finished:
        for painting in paintings:
            painting.draw()

    #draw visitor
    if visitor_visible:
        visitor.draw()

    #once all paintings have been viewed the exit button appears
    all_viewed = all(p.viewed for p in paintings)
    if all_viewed and active_painting is None and not exhibition_finished:
        pygame.draw.rect(screen, (200, 0, 0), exit_button_rect)
        exit_text = small_font.render("Exit Museum", True, WHITE)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_text, exit_text_rect)

    #draw the info window if a painting is active
    if active_painting is not None:
        active_painting.draw_info_window()

    pygame.display.flip()

    #debug added by AI
    clock.tick(60)

#quit pygame
pygame.quit()
sys.exit()
