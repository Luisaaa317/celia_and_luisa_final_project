#import libraries
import pygame
import sys

#initialize Pygame
pygame.init()

#set up window for game
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ART MUSEUM")

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
RED = (200, 0, 0)
GRAY = (230, 230, 230)

#create backgrounds and make them fit the window
background1 = pygame.image.load("ticket_booth.PNG").convert()
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
info_font = pygame.font.SysFont(None, 25)
title_font = pygame.font.SysFont(None, 35)
small_font = pygame.font.SysFont(None, 37)

#initial state of the game
current_background = background1
button_visible = True # becomes false after 2nd background becomes visible
visitor_visible = False #becomes true when 2nd background is visible
exhibition_finished = False   # becomes true once exit button is clicked
exhibition_intro_visible = False  # becomes true when background2 appears

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

# info window that explains game
def draw_exhibition_intro_popup():

    window_width, window_height = 620, 320
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

    #title
    title_surface = title_font.render("Welcome to the Exhibition Hall!", True, BLACK)
    screen.blit(title_surface, (window_x + 20, window_y + 20))

    #instructions
    instructions = [
        "Use the arrow keys to move around the hall.",
        "Walk up to a painting, align the magnifying glass ",
        "and press ENTER to",
        "read information about it.",
        "You must view all 6 paintings before you",
        "can exit the museum and take the quiz.",
    ]

    for i, line in enumerate(instructions):
        line_surface = info_font.render(line, True, BLACK)
        screen.blit(line_surface, (window_x + 20, window_y + 70 + i * 33))

    #close hint
    hint_surface = info_font.render("Press enter or esc to start exploring!", True, (100, 100, 100))
    screen.blit(hint_surface, (window_x + 20, window_y + window_height - 35))


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
        screen.blit(title_surface, (window_x + 20, window_y + 15))

        #description text
        lines = wrap_text(self.description, info_font, window_width - 40)
        for i, line in enumerate(lines):
            line_surface = info_font.render(line, True, BLACK)
            screen.blit(line_surface, (window_x + 20, window_y + 55 + i * 30))

        #how to close info popup
        hint_surface = info_font.render("press enter or esc to close", True, (100, 100, 100))
        screen.blit(hint_surface, (window_x + 20, window_y + window_height - 30))


#create the 6 paintings (x, y, width, height)
paintings = [
    Painting("the_starry_night.png", (174, 165, 102 , 123), "The starry night (1889)",
             "Van Gogh painted The Starry Night while staying at the Saint-Paul-de-Mausole asylum in southern France. It shows a village under a dramatic, swirling sky, with stars that seem to vibrate and move. The view was inspired by what Van Gogh could see from his window, but it was not painted exactly as reality. Instead, the intense blues, yellows, and energetic brushstrokes turn the night sky into something emotional and almost alive."),
    Painting("mona_lisa.jpeg", (187, 328, 67, 145), "Mona Lisa (1519)",
             "Probably the most famous portrait in the world, the Mona Lisa is known for its small, almost unreadable smile. Leonardo used extremely soft layers of paint to blur the outlines of her face, creating the impression that her expression changes when you look away and back again. The distant landscape behind her is also strange: it does not quite follow normal perspective, which gives the painting its dreamlike atmosphere."),
    Painting("the_great_wave.png", (335, 173, 143, 80), "The Great Wave off Kanagawa (1831)",
             "Despite often being called a painting, this image is actually a Japanese woodblock print. It shows a huge wave rising above small fishing boats, while Mount Fuji appears quietly in the distance. The contrast is part of what makes it so memorable: the wave looks enormous and dangerous, while the mountain seems calm and almost fragile. Hokusai's print became influential far beyond Japan and inspired many European artists in the nineteenth century."),
    Painting("the_garden.png", (342, 303, 80, 85), "The Garden of Earthly Delights (1505)",
             "Bosch's triptych is filled with strange animals, oversized fruit, unusual buildings, and figures doing things that are difficult to explain. The left panel shows paradise, the centre is crowded with human pleasures and temptations, and the right side becomes a dark anddisturbing vision of hell. It feels almost like an early fantasy world: every section contains small details that invite the viewer to stop, look closer, and invent their own interpretation."),
    Painting("slaying_holofernes.png", (522, 355, 90, 90), "Judith Slaying Holofernes (1620)",
             "This painting tells a violent story from the Bible: Judith kills the enemy general Holofernes in order to save her city. Artemisia Gentileschi presents the scene without trying to make it elegant or heroic. Judith and her servant are shown working together with determination, while Holofernes struggles beneath them. The painting is famous for its intensity and for the unusually powerful way it portrays its female characters."),
    Painting("the_son_of_man.png", (525, 210, 92, 103), "The Son of Man (1964)",
             "At first glance, this image seems simple: a man in a dark suit and bowler hat stands in front of a wall and the sea. But his face is hidden behind a floating green apple, making the portrait oddly unsettling. Magritte often used ordinary objects in impossible situations to challenge the viewer's expectations. The painting suggests that even familiar things can remain mysterious when something small is placed in the way."),
]

#which info popup is currently open
active_painting = None


# create quiz for ending game

#multiple choice question class
class QuizQuestion:
    def __init__(self, question, options, correct_index):
        self.question = question
        self.options = options
        self.correct_index = correct_index
        self.option_rects = []

    def draw(self, surface):
        window_width, window_height = 640, 400
        window_x = WIDTH // 2 - window_width // 2
        window_y = HEIGHT // 2 - window_height // 2

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(surface, WHITE, popup_rect)
        pygame.draw.rect(surface, BLACK, popup_rect, 3)

        #question text
        lines = wrap_text(self.question, title_font, window_width - 40)
        for i, line in enumerate(lines):
            line_surface = title_font.render(line, True, BLACK)
            surface.blit(line_surface, (window_x + 20, window_y + 20 + i * 32))

        #answer options as clickable buttons
        self.option_rects = []
        y_start = window_y + 20 + len(lines) * 32 + 20
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(window_x + 30, y_start + i * 55, window_width - 60, 45)
            pygame.draw.rect(surface, GRAY, option_rect)
            pygame.draw.rect(surface, BLACK, option_rect, 2)

            option_text = info_font.render(option, True, BLACK)
            text_rect = option_text.get_rect(midleft=(option_rect.x + 15, option_rect.centery))
            surface.blit(option_text, text_rect)

            self.option_rects.append(option_rect)

    def check_click(self, pos):
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                return i
        return None


#free text question class
class TextQuestion:
    def __init__(self, question):
        self.question = question
        self.input_box_rect = None

    def draw(self, surface, current_text):
        window_width, window_height = 640, 300
        window_x = WIDTH // 2 - window_width // 2
        window_y = HEIGHT // 2 - window_height // 2

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        pygame.draw.rect(surface, WHITE, popup_rect)
        pygame.draw.rect(surface, BLACK, popup_rect, 3)

        #question text
        lines = wrap_text(self.question, title_font, window_width - 40)
        for i, line in enumerate(lines):
            line_surface = title_font.render(line, True, BLACK)
            surface.blit(line_surface, (window_x + 20, window_y + 20 + i * 32))

        #text input box
        box_y = window_y + 20 + len(lines) * 32 + 30
        self.input_box_rect = pygame.Rect(window_x + 30, box_y, window_width - 60, 45)
        pygame.draw.rect(surface, GRAY, self.input_box_rect)
        pygame.draw.rect(surface, BLACK, self.input_box_rect, 2)

        #blinking cursor
        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        typed_surface = info_font.render(current_text + cursor, True, BLACK)
        surface.blit(typed_surface, (self.input_box_rect.x + 10, self.input_box_rect.y + 10))

        #hint
        hint_surface = info_font.render("Type your answer and press ENTER", True, (100, 100, 100))
        surface.blit(hint_surface, (window_x + 20, box_y + 60))


#the 10 quiz questions
quiz_questions = [
    QuizQuestion(
        "Which of the following statements is true?",
        ["1. Da Vinci used strong, striking colors and big outlines.",
         "2. The look of the Mona Lisa points up to the sky.",
         "3. The atmosphere makes it the most famous painting.",
         "4. Da Vinci painted together with Monet."],
        2
    ),
    QuizQuestion(
        "Where did Vincent van Gogh paint The Starry Night?",
        ["1. Southern France", "2. Northern Italy", "3. Bretagne", "4. Paris"],
        0
    ),
    QuizQuestion(
        "What is special about Katsushika Hokusai's artwork?",
        ["1. It is sketched with pencil.", "2. It only contains 3 colors.",
         "3. It is a woodblock print.", "4. The painting process took years."],
        2
    ),
    QuizQuestion(
        "What is the painting Judith Slaying Holofernes inspired by?",
        ["1. A novel by Jane Austen.", "2. The Bible.",
         "3. The Quran.", "4. Feminism."],
        1
    ),
    QuizQuestion(
        "When was The Garden of Earthly Delights painted?",
        ["1. 1980", "2. 1245", "3. 300 b.c.", "4. 1510"],
        3
    ),
    QuizQuestion(
        "Which color does the apple in Magritte's painting have?",
        ["1. Green", "2. Red", "3. Yellow", "4. All three."],
        0
    ),
    QuizQuestion(
        "What is the correct name of the artwork?",
        ["1. The Father's Son.", "2. The Son of Man.",
         "3. An Apple and a Man.", "4. Mankind."],
        1
    ),
    QuizQuestion(
        "In the background of The Great Wave off Kanagawa, you can see...",
        ["1. ...Mount Everest", "2. ...The Rocky Mountains",
         "3. ...Mount Fuji", "4. ...Mount Fajoo"],
        2
    ),
    QuizQuestion(
        "In this museum you looked at...",
        ["1. Imaginary paintings.", "2. 6 real-life artworks.",
         "3. Unknown art.", "4. Popular photography."],
        1
    ),
    TextQuestion("Which artwork is your favorite?")
]

#quiz state variables
quiz_active = False
quiz_result_active = False
quiz_passed = False
current_question_index = 0
score = 0
user_text_input = ""

#result screen "continue" button
result_button_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 120, 220, 55)


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
                exhibition_intro_visible = True  # show the intro popup

            #check if the exit museum button was clicked --> now starts the quiz
            all_viewed = all(p.viewed for p in paintings)
            if all_viewed and not exhibition_finished and not quiz_active and not quiz_result_active \
                    and exit_button_rect.collidepoint(event.pos):
                quiz_active = True
                current_question_index = 0
                score = 0
                user_text_input = ""

            #clicking an answer during the quiz --> for multiple choice questions
            if quiz_active:
                current_q = quiz_questions[current_question_index]
                if isinstance(current_q, QuizQuestion):
                    clicked_index = current_q.check_click(event.pos)
                    if clicked_index is not None:
                        if clicked_index == current_q.correct_index:
                            score += 1
                        current_question_index += 1
                        if current_question_index >= len(quiz_questions):
                            quiz_active = False
                            quiz_result_active = True
                            quiz_passed = score >= 7

            #clicking the "continue/retry" button on the result screen
            if quiz_result_active and result_button_rect.collidepoint(event.pos):
                if quiz_passed:
                    quiz_result_active = False
                    exhibition_finished = True
                    current_background = background3
                    visitor_visible = False
                else:
                    #retry the quiz from the beginning
                    quiz_result_active = False
                    quiz_active = True
                    current_question_index = 0
                    score = 0
                    user_text_input = ""

#if the visitor moves
        if event.type == pygame.KEYDOWN:

            # close the exhibition intro popup when enter or esc is pressed
            if exhibition_intro_visible:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    exhibition_intro_visible = False
                continue  # block all other key actions while intro popup is open

            #typing for the free-text quiz question
            if quiz_active:
                current_q = quiz_questions[current_question_index]
                if isinstance(current_q, TextQuestion):
                    if event.key == pygame.K_RETURN:
                        #text question always counts as correct
                        score += 1
                        current_question_index += 1
                        user_text_input = ""
                        if current_question_index >= len(quiz_questions):
                            quiz_active = False
                            quiz_result_active = True
                            quiz_passed = score >= 7
                    elif event.key == pygame.K_BACKSPACE:
                        user_text_input = user_text_input[:-1]
                    else:
                        user_text_input += event.unicode
                    continue  # skip movement keys while typing

            if event.key == pygame.K_LEFT:
                left_pressed = True
            if event.key == pygame.K_RIGHT:
                right_pressed = True
            if event.key == pygame.K_UP:
                up_pressed = True
            if event.key == pygame.K_DOWN:
                down_pressed = True

            #pressing enter --> visitor interacts with a painting thats being touched
            if event.key == pygame.K_RETURN and not exhibition_finished and not quiz_active:
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

    #visitor moves only if no info window is open, no quiz active, and exhibition isn't finished
    if visitor_visible and active_painting is None and not exhibition_finished and not quiz_active \
            and not quiz_result_active and not exhibition_intro_visible:
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
        pygame.draw.rect(screen, GREEN, button_rect)
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
    if all_viewed and active_painting is None and not exhibition_finished and not quiz_active \
            and not quiz_result_active and not exhibition_intro_visible:
        pygame.draw.rect(screen, RED, exit_button_rect)
        exit_text = small_font.render("Exit Museum", True, WHITE)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_text, exit_text_rect)

    #draw the info window if a painting is active
    if active_painting is not None:
        active_painting.draw_info_window()

    #draw the exhibition intro popup 
    if exhibition_intro_visible:
        draw_exhibition_intro_popup()

    #draw the current quiz question
    if quiz_active:
        current_q = quiz_questions[current_question_index]
        if isinstance(current_q, QuizQuestion):
            current_q.draw(screen)
        else:
            current_q.draw(screen, user_text_input)

    #draw the result screen
    if quiz_result_active:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        result_box = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 150, 500, 300)
        pygame.draw.rect(screen, WHITE, result_box)
        pygame.draw.rect(screen, BLACK, result_box, 3)

        score_text = font.render(f"Score: {score} / 10", True, BLACK)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        screen.blit(score_text, score_rect)

        if quiz_passed:
            message = "Congratulations! You passed!"
            msg_color = GREEN
        else:
            message = "Not quite! Try again."
            msg_color = RED

        msg_text = title_font.render(message, True, msg_color)
        msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(msg_text, msg_rect)

        button_color = GREEN if quiz_passed else RED
        pygame.draw.rect(screen, button_color, result_button_rect)
        button_label = "Enter Cafe" if quiz_passed else "Try Again"
        button_text = small_font.render(button_label, True, WHITE)
        button_text_rect = button_text.get_rect(center=result_button_rect.center)
        screen.blit(button_text, button_text_rect)

    pygame.display.flip()

    #debug added by AI
    clock.tick(60)

#quit pygame
pygame.quit()
sys.exit()
