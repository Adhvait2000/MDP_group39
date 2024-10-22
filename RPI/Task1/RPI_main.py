
from threading import Thread
from queue import Queue
from Android import AndroidInterface
from PC import PCInterface
from STM import STMInterface
import requests


class RPiMain:
    def __init__(self):
        self.Android = AndroidInterface(self)
        self.PC = PCInterface(self)
        self.STM = STMInterface(self)
      

    def connect_components(self):
        self.Android.connect()
        self.STM.connect()

    def cleanup(self):
        self.Android.disconnect()
        self.STM.disconnect()

    def run(self):
        print("[RPiMain] Starting RPiMain...")

        self.connect_components()
        print("[RPiMain] Components connected successfully")


        Android_listen = Thread(target= self.Android.listen, name= "Android_listen_thread") #get obstacles
        PC= Thread(target= self.PC.getPathToSTM, name= "PC_send_thread") #send obstacle to algo, get path, send to stm
        Android_send = Thread(target= self.Android.send, name= "Android_send_thread") #send obstacle id
        STM_run = Thread(target= self.STM.run, name= "STM_run_thread")

        # start threads
        Android_listen.start()
        print("Android_listen works")
        PC.start()
        print("PC start works")
        Android_send.start()
        print("Android_send works")
        STM_run.start()
        print("stm_run works")

        
        Android_send.join()

        print("[RPiMain] All threads concluded, cleaning up...")
        self.cleanup()

        print("[RPiMain] Exiting RPiMain...")


rpi = RPiMain()
rpi.run()

