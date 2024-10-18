import pygame
from Settings.attributes import *
from Settings.configuration import *
from Settings.direction import *
from Map.position import *
from Settings.colours import *


class Obstacle:
    def __init__(self, x, y, direction, index):
        # Check if the coordinates are multiples of 10 with offset 5. If they are not, then they are invalid
        # obstacle coordinates.
        # This is from the assumption that all obstacles are placed centered in each grid.
        if (x)  % 10 != 0 or (y) % 10 != 0:
            raise AssertionError("Obstacle center coordinates must be multiples of 10!")

        # Translate given coordinates to be in PyGame coordinates.
        self.pos = Position((x+5) * SCALING_FACTOR, (y+5) * SCALING_FACTOR, direction)
        # Arrow to draw at the target coordinate.
        self.target_image = pygame.transform.scale(pygame.image.load("Assets/target-arrow.png"),
                                                   (50, 50))

        self.index = index

    def __str__(self):
        return f"Obstacle({self.pos})"

    __repr__ = __str__

    def check_within_boundary(self, x, y):

        # Checks whether a given x-y coordinate is within the safety boundary of this obstacle.

        if self.pos.x - OBSTACLE_SAFETY < x < self.pos.x + OBSTACLE_SAFETY and \
                self.pos.y - OBSTACLE_SAFETY < y < self.pos.y + OBSTACLE_SAFETY:
            return True
        return False

    def get_boundary_points(self):

        upper = self.pos.y + OBSTACLE_SAFETY
        lower = self.pos.y - OBSTACLE_SAFETY
        left = self.pos.x - OBSTACLE_SAFETY
        right = self.pos.x + OBSTACLE_SAFETY

        return [
            # Note that in this case, the direction does not matter.
            Position(left, lower),  # Bottom left.
            Position(right, lower),  # Bottom right.
            Position(left, upper),  # Upper left.
            Position(right, upper)  # Upper right.
        ]

    def get_robot_target_pos(self):
        # Returns the point that the robot should target for, including the target orientation.

        if self.pos.direction == Direction.TOP:
            return RobotPosition(self.pos.x, self.pos.y + OBSTACLE_SAFETY + OBSTACLE_LENGTH, Direction.BOTTOM)
        elif self.pos.direction == Direction.BOTTOM:
            return RobotPosition(self.pos.x, self.pos.y - OBSTACLE_SAFETY - OBSTACLE_LENGTH, Direction.TOP)
        elif self.pos.direction == Direction.LEFT:
            return RobotPosition(self.pos.x - OBSTACLE_SAFETY - OBSTACLE_LENGTH, self.pos.y, Direction.RIGHT)
        else:
            return RobotPosition(self.pos.x + OBSTACLE_SAFETY + OBSTACLE_LENGTH, self.pos.y, Direction.LEFT)

    def draw_self(self, screen):
        # Draw the obstacle onto the grid.
        # We need to translate the obstacle's center into that with respect to PyGame
        # Get the coordinates of the grid's bottom left-hand corner.
        rect = pygame.Rect(0, 0, OBSTACLE_LENGTH, OBSTACLE_LENGTH)
        rect.center = self.pos.xy_pygame()
        pygame.draw.rect(screen, BLACK, rect)

        # Draw the direction of the picture
        rect.width = OBSTACLE_LENGTH / 2
        rect.height = OBSTACLE_LENGTH / 2
        rect.center = self.pos.xy_pygame()

        if self.pos.direction == Direction.TOP:
            rect.centery -= OBSTACLE_LENGTH / 4
        elif self.pos.direction == Direction.BOTTOM:
            rect.centery += OBSTACLE_LENGTH / 4
        elif self.pos.direction == Direction.LEFT:
            rect.centerx -= OBSTACLE_LENGTH / 4
        else:
            rect.centerx += OBSTACLE_LENGTH / 4

        # Draw the picture place
        pygame.draw.rect(screen, RED, rect)

    def draw_virtual_boundary(self, screen):
        # Get the boundary points
        points = self.get_boundary_points()

        # Draw left border
        pygame.draw.line(screen, RED, points[0].xy_pygame(), points[2].xy_pygame())
        # Draw right border
        pygame.draw.line(screen, RED, points[1].xy_pygame(), points[3].xy_pygame())
        # Draw upper border
        pygame.draw.line(screen, RED, points[2].xy_pygame(), points[3].xy_pygame())
        # Draw lower border
        pygame.draw.line(screen, RED, points[0].xy_pygame(), points[1].xy_pygame())

    def draw_robot_target(self, screen):
        target = self.get_robot_target_pos()

        rot_image = self.target_image
        angle = 0
        if target.direction == Direction.BOTTOM:
            angle = 180
        elif target.direction == Direction.LEFT:
            angle = 90
        elif target.direction == Direction.RIGHT:
            angle = -90

        rot_image = pygame.transform.rotate(rot_image, angle)
        rect = rot_image.get_rect()
        rect.center = target.xy_pygame()
        screen.blit(rot_image, rect)

    def draw(self, screen):
        # Draw the obstacle itself.
        self.draw_self(screen)
        # Draw the obstacle's boundary.
        self.draw_virtual_boundary(screen)
        # Draw the target for this obstacle.
        self.draw_robot_target(screen)