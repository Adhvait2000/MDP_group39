import math
from queue import PriorityQueue
from typing import List, Tuple
from Settings.attributes import *
from Settings.configuration import *
from Map.position import RobotPosition
from Map.grid import Grid
from Map.node import Node
from Robot.command import *


class ModifiedAStar:
    def __init__(self, grid, brain, start: RobotPosition, end: RobotPosition):
        # We use a copy of the grid rather than use a reference
        # to the exact grid.
        self.grid: Grid = grid.copyGrid()
        self.brain = brain

        self.start = start
        self.end = end


    def getNeighbours(self, pos: RobotPosition) -> List[Tuple[Node, RobotPosition, int, Command]]:
        # get movement neighbours from this position
        # assume that the robot will always make a full 90-degree turn to the next neighbour,
        # and that it will travel a fix distance of 10 travelling straight
        neighbours = []

        # Check travel straights.
        straight_dist = 10 * SCALING_FACTOR
        straight_commands = [
            StraightCommand(straight_dist),
            StraightCommand(-straight_dist)
        ]
        for c in straight_commands:
            # Check if doing this command does not bring us to any invalid position.
            after, p = self.check_valid_command(c, pos)
            if after:
                neighbours.append((after, p, straight_dist, c))

        # Check turns
        turn_penalty = PATH_TURN_COST
        turn_commands = [
            TurnCommand(90, False),  # Forward right turn
            TurnCommand(-90, False),  # Forward left turn
            TurnCommand(90, True),  # Reverse with wheels to right.
            TurnCommand(-90, True),  # Reverse with wheels to left.
        ]

        for c in turn_commands:
            # check if doing this command does not bring us to any invalid positions
            after, p = self.check_valid_command(c, pos)
            if after:
                neighbours.append((after, p, turn_penalty, c))
        return neighbours
    
    def check_valid_command(self, command:Command, p: RobotPosition):
        # check if a command will bring a point to an invalid position
        # if invalid, return None for both the resulting grid location
        # check specifically for validity of turn command
        p = p.copy()
        if isinstance(command, TurnCommand):
            p_c = p.copy()
            for tick in range(command.ticks // PATH_TURN_CHECK_GRANULARITY):
                tick_command = TurnCommand(command.angle / (command.ticks // PATH_TURN_CHECK_GRANULARITY),
                                           command.rev)
                tick_command.applyPos(p_c)
                if not (self.grid.check_valid_position(p_c) and self.grid.get_coordinate(*p_c.xy())):
                    return None, None
        command.applyPos(p)
        if self.grid.check_valid_position(p) and (after := self.grid.get_coordinate(*p.xy())):
            after.pos.direction = p.direction
            return after.copy(), p
        return None, None
    
    def heuristic(self, currPos: Position):
        # measure the difference in distance between the provided position and the end position
        dx = abs(currPos.x - self.end.x)
        dy = abs(currPos.y - self.end.y)
        return math.sqrt(dx * 2 + dy ** 2)

    def start_Astar(self):
        # store frontier nodes to travel to
        frontier = PriorityQueue()
        # store the sequence of nodes being travelled to
        backtrack = dict()
        # store the cost to travel from start to a node
        cost = dict()

        # check what the goal node is
        goalNode = self.grid.get_coordinate(*self.end.xy()).copy() # take note of the copy
        goalNode.pos.direction = self.end.direction # set the required direction

        # add starting node set into the frontier
        start_node: Node = self.grid.get_coordinate(*self.start.xy()).copy() # take note of the copy
        start_node.direction = self.start.direction # make the node know which direction the robot is facing

        offset = 0
        frontier.put((0, offset, (start_node, self.start)))  # Extra time parameter to tie-break same priority.
        cost[start_node] = 0
        # Having None as the parent means this key is the starting node.
        backtrack[start_node] = (None, None)  # Parent, Command

        while not frontier.empty():  # While there are still nodes to process.
            # Get the highest priority node.
            priority, _, (current_node, current_position) = frontier.get()
            # If the current node is our goal.
            if current_node == goalNode:
                # Get the commands needed to get to destination.
                self.extract_commands(backtrack, goalNode)
                return current_position

            # Otherwise, we check through all possible locations that we can
            # travel to from this node.
            for new_node, new_pos, weight, c in self.getNeighbours(current_position):
                new_cost = cost.get(current_node) + weight

                if new_node not in backtrack or new_cost < cost[new_node]:
                    offset += 1
                    priority = new_cost + self.heuristic(new_pos)

                    frontier.put((priority, offset, (new_node, new_pos)))
                    backtrack[new_node] = (current_node, c)
                    cost[new_node] = new_cost
        # If we are here, means that there was no path that we could find.
        # We return None to show that we cannot find a path.
        return None    


    def extract_commands(self, backtrack, goalNode):
        """
        Extract required commands to get to destination.
        """
        commands = []
        curr = goalNode
        while curr:
            curr, c = backtrack.get(curr, (None, None))
            if c:
                commands.append(c)
        commands.reverse()
        self.brain.commands.extend(commands)