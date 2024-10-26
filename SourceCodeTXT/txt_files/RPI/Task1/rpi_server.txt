
import socket
from rpi_config import *
import pickle
class RPiServer:
    """
    Used as the server in the RPi.
    """
    def __init__(self, host,port):
        self.host = host
        self.socket = socket.socket()
        self.port = port
        #self.msg_queue = Queue()
        self.__data = []
        # conn is a new socket object usable to send and receive data on the connection
        # address is the address bound to the socket on the other end of the connection
        self.conn, self.address = None, None

    def start(self):
        print(f"Creating server at {self.host}:{self.port}")
        self.socket.bind((self.host, self.port))  # Assign IP address and port to socket
        self.socket.listen()  # Listening mode
        print("Listening for connection...")

        self.conn, self.address = self.socket.accept()  # Accept incoming request
        print(f"Connection from {self.address}")

    def receive_data(self):
        assert self.conn is not None and self.address is not None
        with self.conn:
            print(f"Connection from {self.address}")
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                self.__data.append(data)

        # This may allow arbitrary code execution. Only connect to trusted connections!
        return pickle.loads(b''.join(self.__data))  # unpickling

    def close(self):
        print("Closing socket.")
        self.socket.close()


