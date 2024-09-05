import pygame
import time
from abc import ABC, abstractmethod
from typing import List
from Map.obstacle import Obstacle
from Map.grid import Grid
from Settings.configuration import *
from Settings.colours import *
from Robot.robot import Robot
from GUI.button import Button

# Load button images
start_img = pygame.image.load("Assets/start_btn.png").convert_alpha()
exit_img = pygame.image.load("Assets/exit_btn.png").convert_alpha()
reset_img = pygame.image.load("Assets/reset_btn.png").convert_alpha()

class AlgoApp(ABC):
    def __init__(self, obstacles: List[Obstacle]):
        self.grid = Grid(obstacles)
        self.robot = Robot(self.grid)
        
        self.start_button = Button(1000, 425, start_img, 1)
        self.exit_button = Button(1000, 920, exit_img, 1)
        self.reset_button = Button(1000, 551, reset_img, 0.8)

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class AlgoSimulator(AlgoApp):
    # run the algo using the GUI simulator
    def __init__(self, obstacles: List[Obstacle]):
        super().__init__(obstacles)

        self.running = False
        self.size = self.width, self.height = WINDOW_SIZE
        self.screen = self.clock = None

    def init(self):
        """
        Set initial values for the app.
        """
        pygame.init()
        self.running = True

        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)  # pygame.HWSURFACE | pygame.DOUBLEBUF pygame.RESIZABLE
        self.clock = pygame.time.Clock()

        # Inform user that it is finding path...
        pygame.display.set_caption("Calculating path...")
        font = pygame.font.SysFont("arial", 35)
        text = font.render("Calculating path...", True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def settle_events(self):
        # to process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def do_updates(self):
        self.robot.update()
    
    def render(self):
        # rendering the screen
        rect_outer= pygame.Rect(0, 0, 1300, 1200)
        self.screen.fill(DARK_BLACK, rect=rect_outer)

        rect_grid = pygame.Rect(0, 0, 1000, 1000)
        self.screen.fill(WHITE, rect=rect_grid)

        #Title
        font1 = pygame.font.SysFont("arial", 26)
        text1 = font1.render("MDP Algorithm Simulator", True, WHITE)
        text_rect1 = text1.get_rect()
        text_rect1 = 1000, 10
        self.screen.blit(text1, text_rect1)

        self.grid.draw(self.screen)
        self.robot.draw(self.screen)

        # Draw start and exit buttons
        if self.start_button.draw():
            # Calculate the path.
            start = time.time()
            self.robot.brain.plan_path()
            print(time.time() - start)

        if self.exit_button.draw():
            self.running = False

        if self.reset_button.draw():
            pass

        # Really render now.
        pygame.display.flip()

    def execute(self):
       # initialize the app and start the game loop
        while self.running:
            # Check for Pygame events.
            self.settle_events()
            # Do required updates.
            self.do_updates()

            # Render the new frame.
            self.render()

            self.clock.tick(FRAMES)
    
class AlgoMinimal(AlgoApp):
    """
    Minimal app to just calculate a path and then send the commands over.
    """
    def __init__(self, obstacles):
        # We run it as a server.
        super().__init__(obstacles)

    def init(self):
        pass

    def execute(self):
        # Calculate path
        print("Calculating path...")
        self.robot.brain.plan_path()
        print("Done!")
   
