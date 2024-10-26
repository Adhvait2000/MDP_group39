# Test USB connection to STM
from queue import Queue
from rpi_config import *
import serial
import re
from time import sleep
import time
import requests
import json
from picamera import PiCamera

class STMInterface:
    url = 'http://192.168.39.21:5000/image'
    def __init__(self, RPiMain):
        self.msg_queue = Queue()
        self.baudrate = 115200
        self.serial = 0
        self.connected = False
        self.RPiMain = RPiMain
        self.obstacle_count = 0


    def is_valid_command(self, command):
        if re.match(STM_NAV_COMMAND_FORMAT, command) or command == STM_GYRO_RESET_COMMAND:
            return True
        else:
            return False

    def adjust_commands(self, commands):
            def is_turn_command(command):
                return self.is_valid_command(command) and re.match("^[LR]", command)

            def adjust_turn_command(turn_command):
                return STM_COMMAND_ADJUSTMENT_MAP.get(turn_command, turn_command)

            def is_obstacle_routing_command(command):
                return (command in STM_OBS_ROUTING_MAP.keys())

            def adjust_obstacle_routing_command(obs_routing_command):
                if obs_routing_command.startswith("SECOND"):
                    self.second_arrow = obs_routing_command[len("SECOND")]
                    print("[STM] Saving second arrow as", self.second_arrow)
                return STM_OBS_ROUTING_MAP[obs_routing_command]

            def is_straight_command(command):
                return self.is_valid_command(command) and command.startswith("S")

            def combine_straight_commands(straight_commands):
                dir_dict = {"SF": 1, "SB": -1} # let forward direction be positive
                total = 0
                for c in straight_commands:
                    dir = c[:2]
                    val = int(c[2:])
                    total += dir_dict.get(dir, 0) * val

                if total > 0:
                    return "SF%03d" % abs(total)
                elif total < 0:
                    return "SB%03d" % abs(total)
                else:
                    return None

            def add_command(final, new):
                # check new and preceding are straight commands
                if is_straight_command(new) and \
                        (len(final) > 0 and is_straight_command(final[-1])):
                    prev = final.pop(-1) # remove prev
                    combined = combine_straight_commands([prev, new])
                    if combined != None:
                        final.append(combined)
                    else: # failed to combine commands
                        final.append(prev)
                        final.append(new)
                else:
                    final.append(new)

                return final

            final_commands = []
            for i in range(len(commands)):
                command = commands[i].upper()
                if is_straight_command(command):
                    final_commands = add_command(final_commands, command)
                else:
                    adj_commands = []
                    if is_turn_command(command):
                        adj_commands = adjust_turn_command(command)
                    elif is_obstacle_routing_command(command):
                        adj_commands = adjust_obstacle_routing_command(command)
                    else:
                        final_commands = add_command(final_commands, command)
                    for c in adj_commands:
                        final_commands = add_command(final_commands, c)
            return final_commands

    def post(self, path):
        try:
            # Open the image file
            image_file = open(path, 'rb')
            files = {'file': image_file}
            response = requests.post(self.url, files=files)
            json_data = response.json()
            print(json_data["image_id"])
            #RettoAndroid = "TARGET,"+json_data["obstacle_id"]+","
            print("Response Text:", response.text)
            return json_data["obstacle_id"],json_data["image_id"]
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return e


    def get_image(self,id):
        # capture img to img_pth
        timestamp = round(time.time())
        img_pth = f"img_{timestamp}_{id}.jpg"
        camera = PiCamera()
        camera.start_preview()
        sleep(2)
        camera.capture(img_pth)
        camera.stop_preview()
        camera.close()
        return img_pth

    def connect(self):
        try:
            #Serial COM Configuration
            self.serial = serial.Serial("/dev/ttyUSB0", self.baudrate, write_timeout = 0)
            self.connected = True
            print("Connected to STM 0 successfully.")
        except:
            try:
                self.serial = serial.Serial("/dev/ttyUSB1", self.baudrate, write_timeout = 0)
                self.connected = True
                print("Connected to STM 1 successfully.")
            except Exception as e:
                print("Failed to connect to STM: %s" %str(e))

    def wait_for_ACK(self):
        message = self.listen()
        if message == 'A':
            print("[STM] Received ACK from STM")
        else:
            print("[STM] ERROR: Unexpected message from STM -",message)
            self.reconnect()
    def listen(self):
        message = None
        while True:
            # print("[STM] In listening loop...")
            try:
                message = self.serial.read().decode("utf-8")
                print("[STM] Read from STM:", message[:MSG_LOG_MAX_SIZE])

                if len(message) < 1:
                    # print("[STM] Ignoring message with length <1 from STM")
                    continue
                else:
                    break

            except Exception as e:
                message = str(e)
                break
        return message


    def send(self, encoded_msg):
        try:
            print(encoded_msg)
            self.serial.write(encoded_msg)
            self.wait_for_ACK()
#            print("Write to STM: " + encoded_msg)
        except Exception as e:
            print("Failed to write to STM: %s" %str(e))

    def run(self):
        while True:
            if not self.msg_queue.empty() and self.RPiMain.Android.start:
                self.connect()
                message = self.msg_queue.get()
                for command in message:
                        if command.startswith('s'):
                            obstacle_id = 1 
                            image_id = 11
                            try:
                                path = self.get_image(command[-1])
                                obstacle_id , image_id =  self.post(path)
                            except Exception as e:
                                print(e)
                            RettoAndroid =  "TARGET," + str(obstacle_id) + "," + str(image_id)
                            self.RPiMain.Android.msg_queue.put(RettoAndroid)
                            self.RPiMain.Android.image_id = True
                            self.obstacle_count+=1
                            print(self.obstacle_count)
                            if self.obstacle_count % STM_GYRO_RESET_FREQ == 0:
                                print("[STM] Resetting gyroscope after %d obstacles" % self.obstacle_count)
                                self.send(STM_GYRO_RESET_COMMAND)
                            #android.send(RettoAndroid)
                            sleep(1.5)
                        elif re.match('^[SLR][FB][0-9]{3}$', command):
                            for c in self.adjust_commands([command]):
                                print("Sending command:", c)
                                self.send(bytearray(c.encode()))
                                #sleep(3)
                print("All command executed.")
                try:
                    print("Stitching images")
                    response = requests.get("http://192.168.39.21:5000/stitch")
                    print("Done stitching images")
                    print("Task 1 done")
                except Exception as e:
                    print(e)


      
