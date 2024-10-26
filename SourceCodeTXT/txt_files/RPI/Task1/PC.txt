import sys
from queue import Queue
from rpi_client import RPiClient
from rpi_server import RPiServer

class PCInterface:
    def __init__(self, RPiMain):
        self.msg_queue = Queue()
        self.RPiMain = RPiMain
        
    def getPathToSTM(self):
    # Create a server for the PC to connect to
        server = RPiServer("192.168.39.1", 1234)
        # Wait for the PC to connect to the RPi.
        print("Waiting for connection from PC...")
        try:
            server.start()
        except Exception as e:
            print(e)
            server.close()
            sys.exit(1)
        print("Connection from PC established!\n")

        # Then, we use this to connect to the PC's server.
        host = server.address[0]  # IP address
        # Create a client to connect to the PC's server.
        try:
            client = RPiClient(host, 4161)
        except OSError as e:
            print(e)
            server.close()
            sys.exit(1)

        # Wait to connect to RPi.
        print(f"Attempting connection to PC at {host}:{4161}")
        while True:
            try:
                client.connect()
                break
            except OSError:
                pass
            except Exception as e:
                print(e)
                server.close()
                client.close()
                sys.exit(1)
        print("Connected to PC!\n")

        while not self.msg_queue.empty(): 
            
            # Send over the obstacle data to the PC.
            print("Sending obstacle data to PC...")
          
            obstacle_data = self.msg_queue.get()
            client.send_message(obstacle_data)  
            client.close()
            print("Done!\n")

            # Receive commands from the PC.
            print("Receiving robot commands from PC...")
            try:
                commands = server.receive_data()
                print("Commands received!\n")
                print(commands)
            except Exception as e:
                print(e)
            finally:
                server.close()
                self.RPiMain.STM.msg_queue.put(commands) #put the path from algo into stm queue
        
