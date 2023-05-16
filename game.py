# Import the necessary libraries
import pygame
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

# Initialize pygame and pymunk
pygame.init()
pymunk.pygame_util.positive_y_is_up = True

# Define the screen size
WIDTH, HEIGHT = 800, 600

# Create a pygame screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create a pymunk space
space = pymunk.Space()
space.gravity = (0, -900)



# Define game constants
FPS = 60  # Frames per second
BALL_RADIUS = 10  # Radius of the ball
BALL_MASS = 1  # Mass of the ball
PLAYER_FORCE = 100  # Force with which a player hits the ball
GRAVITY = -900  # Gravity (negative because the y-axis is inverted)

# Initialize game variables
mouse_pressed = False  # Is the mouse button pressed?
mouse_position = (0, 0)  # Current position of the mouse
start_position = (0, 0)  # Position of the mouse when the button was pressed
end_position = (0, 0)  # Position of the mouse when the button was released

# Initialize score and timer variables
score = 0
shot_timer = 0
start_time = None

# Function to display the start screen
def display_start_screen():
    screen.fill((255, 255, 255))  # Fill the screen with white

    # Draw the title
    font = pygame.font.Font(None, 64)  # Create a font object
    text = font.render("Putt Putt Game", True, (0, 0, 0))  # Create a text surface
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))  # Blit the text

    # Draw the play button
    pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 50))  # Draw a green rectangle
    font = pygame.font.Font(None, 32)  # Create a font object
    text = font.render("Play", True, (0, 0, 0))  # Create a text surface
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 25 - text.get_height() // 2))  # Blit the text

    pygame.display.flip()  # Update the display

# Function to display the game over screen
def display_game_over_screen():
    screen.fill((255, 255, 255))  # Fill the screen with white

    # Draw the title
    font = pygame.font.Font(None, 64)  # Create a font object
    text = font.render("Game Over", True, (0, 0, 0))  # Create a text surface
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4))  # Blit the text

    # Draw the restart button
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 50))  # Draw a red rectangle
    font = pygame.font.Font(None, 32)  # Create a font object
    text = font.render("Restart", True, (0, 0, 0))  # Create a text surface
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 25 - text.get_height() // 2))  # Blit the text

    pygame.display.flip()  # Update the display

def to_pymunk_coords(pos):
    return pos[0], HEIGHT - pos[1]
# Functions for score, timer and player control
def update_score():
    global score
    score += 1

def start_timer():
    global start_time
    start_time = pygame.time.get_ticks()

def stop_timer():
    global start_time
    elapsed_time = pygame.time.get_ticks() - start_time
    start_time = None
    return elapsed_time

def next_player():
    global current_player
    current_player = (current_player + 1) % len(players)

# Define the Course class
class Course:
    def __init__(self, space):
        self.space = space
        self.static_lines = [
            pymunk.Segment(space.static_body, (50, 50), (750, 50), 5),
            pymunk.Segment(space.static_body, (50, 550), (750, 550), 5),
            pymunk.Segment(space.static_body, (50, 50), (50, 550), 5),
            pymunk.Segment(space.static_body, (750, 50), (750, 550), 5),
            pymunk.Segment(space.static_body, (400, 50), (400, 250), 5),
            pymunk.Segment(space.static_body, (400, 350), (400, 550), 5)
        ]
        
        for line in self.static_lines:
            line.elasticity = 0.95
            line.friction = 0.9
            self.space.add(line)


    def draw(self, screen):
        for line in self.static_lines:
            body = line.body
            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            p1 = pymunk.pygame_util.to_pygame(pv1, screen)
            p2 = pymunk.pygame_util.to_pygame(pv2, screen)
            pygame.draw.lines(screen, pygame.Color("black"), False, [p1, p2])


# Define the Player class
class Player:
    def __init__(self, space, position):
        self.space = space
        self.ball = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        self.ball.position = position
        self.ball_shape = pymunk.Circle(self.ball, 10)
        self.ball_shape.elasticity = 0.95
        self.ball_shape.friction = 0.9
        self.space.add(self.ball, self.ball_shape)
        self.shot_vector = pymunk.Vec2d(0, 0)

    def start_shot(self, mouse_position):
        self.shot_vector = pymunk.Vec2d(*mouse_position) - self.ball.position

    def end_shot(self, mouse_position):
        self.shot_vector -= pymunk.Vec2d(*mouse_position) - self.ball.position
        self.ball.apply_impulse_at_local_point(-self.shot_vector)


    def ball_at_rest(self):
        return self.ball.velocity.length < 1

    def draw(self, screen):
        p = pymunk.pygame_util.to_pygame(self.ball.position, screen)
        pygame.draw.circle(screen, pygame.Color("red"), p, 10)

class Ball:
    def __init__(self, space, start_position):
        # Initialize the ball
        self.space = space
        self.body = pymunk.Body(BALL_MASS, pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS))  # Dynamic body
        self.body.position = start_position
        self.shape = pymunk.Circle(self.body, BALL_RADIUS)
        self.space.add(self.body, self.shape)


# Initialize score and timer variables
score = 0
start_time = pygame.time.get_ticks()

# Initialize player variables
players = [Player(space, (WIDTH // 2, HEIGHT // 2)), Player(space, (WIDTH // 2, HEIGHT // 3))]
current_player = 0

# Create course
course = Course(space)

# Main game loop
running = True
while running:
    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_timer()
            players[current_player].start_shot(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            stop_timer()
            players[current_player].end_shot(pygame.mouse.get_pos())
            update_score()

    # Check if the current player's ball has come to a rest
    if players[current_player].ball_at_rest():
        next_player()

    # Update the physics
    space.step(1/60)

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the course
    course.draw(screen)

    # Draw the players
    for player in players:
        player.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.delay(1000//60)

# Quit pygame
pygame.quit()