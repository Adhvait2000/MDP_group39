from Android import AndroidInterface
from ImageRec import ImageRecInterface
from STM import STMInterface
from threading import Thread
import requests
class RPiMain:
    def __init__(self):
        self.Android = AndroidInterface(self)
        self.STM = STMInterface(self)
        self.ImageRec = ImageRecInterface()
        self.start = False

    def connect_components(self):
        self.Android.connect()
        self.STM.connect()

    def cleanup(self):
        self.Android.disconnect()
        self.STM.disconnect()

    def task2(self):
        while True:
            if(self.start):
                print("connecting to STM")
                self.STM.connect()
                self.STM.write_to_stm("YF200")
                print("Caputuring picure 1")
                direction = self.ImageRec.post(self.ImageRec.get_image())
                if(direction == 'L'):
                    for c in self.STM.convert("FIRSTLEFT"):
                        print("> Sending command:", c)
                        self.STM.write_to_stm(c)
                else:
                    for c in self.STM.convert("FIRSTRIGHT"):
                        print("> Sending command:", c)
                        self.STM.write_to_stm(c)

                print("Caputuring picure 2")
                direction = self.ImageRec.post(self.ImageRec.get_image())
                if(direction == 'L'):
                    self.STM.second_arrow = 'L'
                    for c in self.STM.convert("SECONDLEFT"):
                        print("> Sending command:", c)
                        self.STM.write_to_stm(c)
                else:
                    self.STM.second_arrow = 'R'
                    for c in self.STM.convert("SECONDRIGHT"):
                        print("> Sending command:", c)
                        self.STM.write_to_stm(c)
                print("Returning to carpark")
                self.STM.return_to_carpark()
                try:
                    print("Stitching images")
                    response = requests.get("http://192.168.39.21:5000/stitch")
                    print("Done stitching images")
                except Exception as e:
                    print(e)
                print("Task 2 ends")
                break

    def run(self):
        self.Android.connect()
        Android_listen = Thread(target= self.Android.listen, name= "Android_listen_thread")
        STM_run = Thread(target= self.task2, name= "STM_start")

        Android_listen.start()
        STM_run.start()

rpi = RPiMain()
rpi.run()

