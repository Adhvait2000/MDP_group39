import pygame
from Map.position import Position
from Settings.attributes import *
from Settings.colours import *

class Node:
    def __init__(self, x, y, occupied, direction = None):
        # position of object
        self.pos = Position(x,y, direction)
        # indicates if node is occupied or not 
        self.occupied = occupied

    def __str__(self):
        return f"Node({self.pos})"
    
    __repr__ = __str__

    def __eq__(self, other):
        # compares position and direction
        # to check equality with another node based on position and direction
        return self.pos.xy_dir() == other.pos.xy_dir()
    
    def __hash__(self):
        return hash(self.pos.xy_dir())

    def copy(self):
        
        return Node(self.pos.x, self.pos.y, self.occupied, self.pos.direction)

    def draw_self(self, screen):
        # draw node on the pygame screen
        if self.occupied:  # If current node is not permissible to the robot
            rect = pygame.Rect(0, 0, GRID_CELL_LENGTH, GRID_CELL_LENGTH)
            rect.center = self.pos.xy_pygame() # set center of rectangle to the node's position
            pygame.draw.rect(screen, DARK_GREY , rect) # draw the rectangle on screen

    def draw_boundary(self, screen):
        x_pygame, y_pygame = self.pos.xy_pygame()

        # calculates the positions for the boundaries of the node
        left = x_pygame - GRID_CELL_LENGTH // 2
        right = x_pygame + GRID_CELL_LENGTH // 2
        top = y_pygame - GRID_CELL_LENGTH // 2
        bottom = y_pygame + GRID_CELL_LENGTH // 2

        # Draw the boundary lines for the node
        pygame.draw.line(screen, GREY, (left, top), (left, bottom))  # Left border
        pygame.draw.line(screen, GREY, (left, top), (right, top))  # Top border
        pygame.draw.line(screen, GREY, (right, top), (right, bottom))  # Right border
        pygame.draw.line(screen, GREY, (left, bottom), (right, bottom))  # Bottom border


    def draw(self, screen):
        # Draw self
        self.draw_self(screen)
        # Draw node border
        self.draw_boundary(screen)