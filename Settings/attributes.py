from Settings.configuration import *

# Attributes for the robot
ROBOT_LENGTH = 20 * SCALING_FACTOR
ROBOT_TURNING = 20 * SCALING_FACTOR
ROBOT_SPEED = 100 * SCALING_FACTOR
ROBOT_S_FACTOR = ROBOT_LENGTH/ ROBOT_TURNING
ROBOT_SAFETY_DISTANCE = 15 * SCALING_FACTOR
ROBOT_TIME = 0.25 #time taken in seconds for the robot to detect the image

# Attributes for the Grid
GRID_LENGTH = 200 * SCALING_FACTOR # 200cm by 200cm
GRID_CELL_LENGTH = 10 * SCALING_FACTOR #10cm by 10cm
GRID_START_LENGTH = 30 * SCALING_FACTOR
GRID_NUMBER = GRID_LENGTH // GRID_CELL_LENGTH #number of grids in one row/column

# Obstacle Attributes
OBSTACLE_LENGTH = 10 *  SCALING_FACTOR # 10cm by 10cm
OBSTACLE_SAFETY = ROBOT_SAFETY_DISTANCE // 3 * 4 

# Attributes for path finding
# higher path costs means that car will encourage straight line turns
PATH_TURN_COST = 999 * ROBOT_SPEED * ROBOT_TURNING

# lower granularity means algo checks for turns more often
PATH_TURN_CHECK_GRANULARITY = 1

