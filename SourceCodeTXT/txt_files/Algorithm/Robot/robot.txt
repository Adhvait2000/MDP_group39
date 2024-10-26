import pygame
import datetime
from Map.position import RobotPosition
from Settings.direction import *
from Settings.attributes import *
from Settings.colours import *
from Robot.command import *
from Robot.algo_mgr import Brain

class Robot:
    def __init__(self, grid):
        # Note that we assume the robot starts always facing the top.
        # This value will never change, but it will not affect us as the robot uses a more fine-tuned internal
        # angle tracker.
        self.pos = RobotPosition(ROBOT_SAFETY_DISTANCE,
                                 ROBOT_SAFETY_DISTANCE,
                                 Direction.TOP,
                                 90)
        self._start_copy = self.pos.copy()

        self.brain = Brain(self, grid)

        self.__image = pygame.transform.scale(pygame.image.load("Assets/robot.jpg"),
                                              (ROBOT_LENGTH / 2, ROBOT_LENGTH / 2))

        self.path_hist = []  # Stores the history of the path taken by the robot.

        self.__current_command = 0  # Index of the current command being executed.
        self.printed = False  # Never printed total time before.
    
    def get_current_post(self):
        return self.pos
    
    def convert_all_commands(self):
        # convert the list of commands to corresponding list of messages
        print("Converting commands to string...", end="")
        string_commands = [command.convert_to_message() for command in self.brain.commands]
        print("Done!")
        return string_commands

    def turn(self, d_angle, rev):
        # turn the robot in a specific angle, and whether to do it in reverse or not
        # angle in radians
        # negative angle will cause the robot to be rotated in a clockwise manner
        """
        x_new = x + R(sin(∆θ + θ) − sin θ)
        y_new = y − R(cos(∆θ + θ) − cos θ)
        θ_new = θ + ∆θ
        R is the turning radius.

        Take note that:
            - +ve ∆θ -> rotate counter-clockwise
            - -ve ∆θ -> rotate clockwise

        Note that ∆θ is in radians.
        """
        TurnCommand(d_angle, rev).applyPos(self.pos)
    
    def straight(self, dist):
        # make the robot go straight
        StraightCommand(dist).applyPos(self.pos)
    
    def draw_hamilton_path(self, screen):
        prev = self._start_copy.xy_pygame()
        for obs in self.brain.simple_hamiltonian:
            target = obs.get_robot_target_pos().xy_pygame()
            pygame.draw.line(screen, BLUE, prev, target)
            prev = target
    
    def draw_self(self, screen):
        # arrow to represent the direction of the robot
        rot_image = pygame.transform.rotate(self.__image, -(90 - self.pos.angle))
        rect = rot_image.get_rect()
        rect.center = self.pos.xy_pygame()
        screen.blit(rot_image, rect)
    
    def draw_historic_path(self, screen):
        for dot in self.path_hist:
            pygame.draw.circle(screen, BLACK, dot, 3)
    
    def draw(self, screen):
        # draw the robot
        self.draw_self(screen)
        # draw the hamiltonian path found by the robot
        self.draw_hamilton_path(screen)
        # draw the historic path sketched by the robot
        self.draw_historic_path(screen)
    
    def update(self):
        # storing the historic path
        if len(self.path_hist) == 0 or self.pos.xy_pygame() != self.path_hist[-1]:
            # only add a new point history if there is none
            self.path_hist.append(self.pos.xy_pygame())
        
        # if no more commands to execute, then return
        if self.__current_command >= len(self.brain.commands):
            return
        
        # check current command has non-null ticks
        # needed to check commands that have 0 tick execution time
        if self.brain.commands[self.__current_command].totalTicks == 0:
            self.__current_command += 1
            if self.__current_command >= len(self.brain.commands):
                return
        
        # if not, the first command in the list is always the command to execute
        command: Command = self.brain.commands[self.__current_command]
        command.processOneTick(self)
        # if there are no more ticks to do, we can assume that the command is complete, so can remove it
        if command.ticks <= 0:
            print(f"Finished processing {command}, {self.pos}")
            self.__current_command += 1
            if self.__current_command == len(self.brain.commands) and not self.printed:
                total_time = 0
                for command in self.brain.commands:
                    total_time += command.time
                    total_time = round(total_time)
                    # calculate the time for all commands
                    print (f"All commands took {datetime.timedelta(seconds = total_time)}")
                    self.printed = True