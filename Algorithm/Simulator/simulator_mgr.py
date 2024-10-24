import sys
from typing import List
from Settings.direction import Direction
from Settings.configuration import RPI_HOST, RPI_PORT, PC_HOST, PC_PORT
from Map.obstacle import Obstacle
from Simulator.simulator import AlgoMinimal
from Simulator.simulator import AlgoSimulator
from Connection.rpi_client import RPiClient
from Connection.rpi_server import RPiServer

def parse_obstacle_data(data) -> List[Obstacle]:
    obstacles = []
    for obstacle_params in data:
        obstacles.append(Obstacle(obstacle_params[0], obstacle_params[1], Direction(obstacle_params[2]), obstacle_params[3]))
    # [[x, y, orient, index], [x, y, orient, index]]
    return obstacles

def run_simulator():
    # Fill in obstacle positions with respect to lower bottom left corner.
    # (x-coordinate, y-coordinate, Direction)
    obstacles = [[105, 75, 180, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3], [75, 125, 90, 4], [15, 185, -90, 5]]
    obs = parse_obstacle_data(obstacles)
    app = AlgoSimulator(obs)
    app.init()
    app.execute()

    # Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    print(commands)

def run_minimal(also_run_simulator):
    # Create a client to connect to the RPi.
    print(f"Attempting to connect to {RPI_HOST}:{RPI_PORT}")
    client = RPiClient(RPI_HOST, RPI_PORT)
    # Wait to connect to RPi.
    while True:
        try:
            client.connect()
            break
        except OSError:
            pass
        except KeyboardInterrupt:
            client.close()
            sys.exit(1)
    print("Connected to RPi!\n")

    print("Waiting to receive obstacle data from RPi...")
    # Create a server to receive information from the RPi.
    server = RPiServer(PC_HOST, PC_PORT)
    # Wait for the RPi to connect to the PC.
    try:
        server.start()
    except OSError or KeyboardInterrupt as e:
        print(e)
        server.close()
        client.close()
        sys.exit(1)

    # At this point, both the RPi and the PC are connected to each other.
    # Create a synchronous call to wait for RPi data.
    obstacle_data: list = server.receive_data()
    server.close()
    print("Got data from RPi:")
    print(obstacle_data)

    obstacles = parse_obstacle_data(obstacle_data)
    if also_run_simulator:
        app = AlgoSimulator(obstacles)
        app.init()
        app.execute()
    app = AlgoMinimal(obstacles)
    app.init()
    app.execute()

    # Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    client.send_message(commands)
    client.close()


def wk_simulator_w_obstacles(obstacle_data_from_rpi):
    parsed_obstacles = parse_obstacle_data(obstacle_data_from_rpi)
    # app = AlgoMinimal(parsed_obstacles)
    app = AlgoSimulator(parsed_obstacles)
    app.init()
    app.execute()

    # Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    print(commands)


def wk_real_run(run_pygame):
    # 1. Create a client to connect to the RPi.
    print(f"Attempting to connect to {RPI_HOST}:{RPI_PORT}")
    client = RPiClient(RPI_HOST, RPI_PORT)
    # Wait to connect to RPi.
    while True:
        try:
            client.connect()
            break
        except OSError:
            pass
        except KeyboardInterrupt:
            client.close()
            sys.exit(1)
    print("Connected to RPi!\n")

    print("Waiting to receive obstacle data from RPi...")
    # 2. Create a server to receive information from the RPi.
    server = RPiServer(PC_HOST, PC_PORT)
    # Wait for the RPi to connect to the PC.
    try:
        server.start()
    except OSError or KeyboardInterrupt as e:
        print(e)
        server.close()
        client.close()
        sys.exit(1)

    # 3. At this point, both the RPi and the PC are connected to each other.
    # Create a synchronous call to wait for RPi data.
    obstacle_data: list = server.receive_data()
    server.close()
    print("Got data from RPi:")
    print(obstacle_data)

    # 4.
    obstacles = parse_obstacle_data(obstacle_data)
    if run_pygame:
        app = AlgoSimulator(obstacles)
        app.init()
        app.execute()
    else:
        app = AlgoMinimal(obstacles)
        app.init()
        app.execute()

    # 5. Send the list of commands over.
    print("Sending list of commands to RPi...")
    commands = app.robot.convert_all_commands()
    client.send_message(commands)
    client.close()

