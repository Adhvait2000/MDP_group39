import socket

#Settings for PyGAME

FRAMES = 10
WINDOW_SIZE = 1920, 1080
SCALING_FACTOR = 5

# Connection to RPi
RPI_HOST: str = "192.168.39.1"
RPI_PORT: int = 1234


# Connection to PC
PC_HOST: str = socket.gethostbyname(socket.gethostname())
PC_PORT: int = 4161