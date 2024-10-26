import pygame
import math
from typing import List
from collections import deque
from Map.obstacle import Obstacle
from Map.position import Position
from Map.node import Node
from Settings.attributes import *
from Settings.colours import *

class Grid:
    def __init__(self, obstacles: List[Obstacle]):
        self.obstacles = obstacles
        self.nodes = self.generate_nodes()
    
    def generate_nodes(self):
        # generating nodes for this grid
        nodes = deque()
        for i in range(GRID_NUMBER):
            row = deque()
            for j in range(GRID_NUMBER):
                x, y = (GRID_CELL_LENGTH //2 + GRID_CELL_LENGTH*j), \
                        (GRID_CELL_LENGTH // 2 + GRID_CELL_LENGTH*i)

                newNode = Node(x, y, not self.check_valid_position(Position(x,y)))
                row.append(newNode)
            nodes.appendleft(row)
        return nodes

    # getting the coordinate of the node
    def get_coordinate(self, x, y):
        colNum = math.floor(x / GRID_CELL_LENGTH)
        rowNum = GRID_NUMBER - math.floor(y / GRID_CELL_LENGTH) - 1
        # ensure that it returns the coordinates
        # if out of boundary --> error
        try:
            return self.nodes[rowNum][colNum]
        except IndexError:
            return None
    
    # Copy of the grid for simulations
    def copyGrid(self):
        nodes = []
        for row in self.nodes:
            newRow = []
            for col in row:
                newRow.append(col.copy())
            nodes.append(newRow)
        newGrid = Grid(self.obstacles)
        newGrid.nodes = nodes
        return newGrid
    
    # check if the position of the car is valid or not
    def check_valid_position(self, pos: Position):
        if any(obstacle.check_within_boundary(*pos.xy()) for obstacle in self.obstacles):
            return False
        
        # checking if position is too close to the border
        if (pos.y < GRID_CELL_LENGTH or
            pos.y > GRID_LENGTH - GRID_CELL_LENGTH) or \
                (pos.x < GRID_CELL_LENGTH or
                 pos.x > GRID_LENGTH - GRID_CELL_LENGTH):
            return False
        return True        

    @classmethod
    def drawBorders(cls, screen):
        #upper border
        # Draw upper border

        # pygame.draw.line(screen, BLACK, (0, 0), (GRID_LENGTH, 0))
        # # Draw lower border
        # pygame.draw.line(screen, BLACK, (0, GRID_LENGTH), (GRID_LENGTH, GRID_LENGTH))
        # # Draw left border
        # pygame.draw.line(screen, BLACK, (0, 0), (0, GRID_LENGTH))
        # # Draw right border
        # pygame.draw.line(screen, BLACK, (GRID_LENGTH, 0), (GRID_LENGTH, GRID_LENGTH))
        # Define the alternating colors
        colors = [RED, WHITE]

        # Draw upper border with alternating colors
        for i in range(0, GRID_LENGTH, GRID_CELL_LENGTH):
            pygame.draw.line(screen, colors[i // GRID_CELL_LENGTH % 2], (i, 0), (i + GRID_CELL_LENGTH, 0))

        # Draw lower border with alternating colors
        for i in range(0, GRID_LENGTH, GRID_CELL_LENGTH):
            pygame.draw.line(screen, colors[i // GRID_CELL_LENGTH % 2], (i, GRID_LENGTH), (i + GRID_CELL_LENGTH, GRID_LENGTH))

        # Draw left border with alternating colors
        for i in range(0, GRID_LENGTH, GRID_CELL_LENGTH):
            pygame.draw.line(screen, colors[i // GRID_CELL_LENGTH % 2], (0, i), (0, i + GRID_CELL_LENGTH))

        # Draw right border with alternating colors
        for i in range(0, GRID_LENGTH, GRID_CELL_LENGTH):
            pygame.draw.line(screen, colors[i // GRID_CELL_LENGTH % 2], (GRID_LENGTH, i), (GRID_LENGTH, i + GRID_CELL_LENGTH))

    def drawObstacles(self, screen):
        for ob in self.obstacles:
            ob.draw(screen)
        
    def drawNodes(self, screen):
        for row in self.nodes:
            for col in row:
                col.draw(screen)

    def draw(self, screen):
        self.drawNodes(screen)
        self.drawBorders(screen)
        self.drawObstacles(screen)


