import math
from abc import ABC, abstractmethod
from Settings.configuration import *
from Settings.attributes import *
from Settings.direction import *
from Map.position import *

class Command(XYZ):
    def _init__(self, time):
        self.time = time # time in seconds in which this command is carried out
        self.ticks = math.ceil(time * FRAMES) # number of frame ticks 
        self.totalTicks = self.ticks # keep track of original total ticks
        
    def tick(self):
        self.ticks -= 1

    @abstractmethod
    def processOneTick(self, robot):
        pass

    @abstractmethod
    # apply command to a position
    # attributes will reflect current position
    def applyPos(self, currPos):
        pass

    @abstractmethod
    def convertMessage(self):
        # convert message to send to RPi
        pass

    
class ScanCommand(Command):
    def __init__(self, time, objIndex):
        super().__init__(time)
        self.objIndex = objIndex
    
    def __str__(self):
        return f"ScanCommand(time={self.time, self.objIndex})"
    
    __repr__ = __str__

    def processOneTick(self, robot):
        if self.totalTicks == 0:
            return
        
        self.tick()
    
    def applyPos(self, currPos):
        pass

    def convertMessage(self):
        # just return a string of s
        return f"s{self.objIndex:04}"
    

class StraightCommand(Command):
    def __init__(self, dist):
        # calculate the time needed to travel the required distance
        time = abs(dist / ROBOT_SPEED)
        super().__init__(time)

        self.dist = dist

    def __str__(self):
        return f"StraightCommand(dist={self.dist / SCALING_FACTOR}, {self.total_ticks} ticks)"

    # By assigning __repr__ = __str__, 
    # you're telling Python that whenever __repr__ is called, \
    # it should behave just like __str__
    
    __repr__ = __str__

    def processOneTick(self, robot):
        if self.totalTicks == 0:
            return
        
        self.tick()
        distance = self.dist / self.totalTicks
        robot.straight(distance)
    
    def applyPos(self, currPos: Position):
        # applied on the current Position object

        if currPos.direction == Direction.RIGHT:
            currPos.x += self.dist
        elif currPos.direction == Direction.TOP:
            currPos.y += self.dist
        elif currPos.direction == Direction.BOTTOM:
            currPos.y -= self.dist
        else:
            currPos.x -= self.dist
        return self


    def convertMessage(self):
        #Message will be: fXXXX for forward, bXXXX for backward
        #XXXX will be the distance in decimal in centimeters

        descaled_distance = int(self.dist // SCALING_FACTOR)
        if descaled_distance < 0:
            # backward command
            return f"b{abs(descaled_distance):04}"
        
        # else return forward command
        return f"f{abs(descaled_distance):04}"

class TurnCommand(Command):
    def __init__(self, angle, rev):
        # angle to turn and whether it is in reverse or not
        time = abs((math.radians(angle) * ROBOT_LENGTH) / 
                    ROBOT_SPEED * ROBOT_S_FACTOR)
        super().__init__(time)

        self.angle = angle
        self.rev = rev

    def __str__(self):
        return f"TurnCommand({self.angle:.2f}degrees, {self.total_ticks} ticks, rev={self.rev})"
    

    __repr__ = __str__

    def processOneTick(self, robot):
        if self.totalTicks == 0:
            return
        
        self.tick()
        angle = self.angle / self.totalTicks
        robot.turn(angle, self.rev)

    def applyPos(self, currPos: Position):
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
        assert isinstance(currPos, RobotPosition), print("Cannot apply turn command on non-robot positions!")

        # get change in x,y coord
        xChange = ROBOT_TURNING * (math.sin(math.radians(currPos.angle + self.angle)) - math.sin(math.radians(currPos.angle)))
        yChange = ROBOT_TURNING * (math.cos(math.radians(currPos.angle + self.angle)) - math.cos(math.radians(currPos.angle)))
       
        # wheels turn right moving forward
        if self.angle < 0 and not self.rev:
            currPos.x -= xChange
            currPos.y += yChange
        elif (self.angle < 0 and self.rev) or (self.angle >= 0 and not self.rev):
            # wheels turn left moving backwards or wheels turn left moving forwards
            currPos.x += xChange
            currPos.y -= yChange
        else: # wheels turn right moving backwards
            currPos.x -= xChange
            currPos.y += yChange
        currPos.angle += self.angle

        if currPos.angle < -180:
            currPos.angle += 2*180
        elif currPos.angle >= 180:
            currPos.angle -= 2*180
        

        # Update the Position's directions

        if 45 <= currPos.angle < 3*45:
            currPos.direction = Direction.TOP
        elif -45 < currPos.angle < 45:
            currPos.direction = Direction.RIGHT
        elif -45*3 <= currPos.angle <= -45:
            currPos.direction = Direction.BOTTOM
        else:
            currPos.direction = Direction.LEFT
        return self

    def convert_to_message(self):
        if self.angle > 0 and not self.rev:
            # This is going forward left.
            return "l0090"  # Note the smaller case L.
        elif self.angle > 0 and self.rev:
            # This is going backward and with the wheels to the right.
            return "R0090"
        elif self.angle < 0 and not self.rev:
            # This is going forward right.
            return "r0090"
        else:
            # This is going backward and with the wheels to the left.
            return "L0090"
        