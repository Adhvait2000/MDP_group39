import json
from queue import Queue
import re
import threading
import time
import serial
#from Camera import get_image

from rpi_config import *

class STMInterface:
    def __init__(self, RPiMain):
        self.RPiMain = RPiMain
        self.baudrate = STM_BAUDRATE
        self.serial = None
        self.msg_queue = Queue()
        self.obstacle_count = 0 
        self.second_arrow = None
        self.xdist = None # length of obs 2
        self.ydist = None # distance btw obs 1 and 2

    def connect(self):
        try:
            self.serial = serial.Serial("/dev/ttyUSB0", self.baudrate, write_timeout = 0)
            print("[STM] Connected to STM 0 successfully.")
            #self.clean_buffers()
        except:
            try:
                self.serial = serial.Serial("/dev/ttyUSB1", self.baudrate, write_timeout = 0)
                print("[STM] Connected to STM 1 successfully.")
                self.clean_buffers()
            except Exception as e:
                print("[STM] ERROR: Failed to connect to STM -", str(e))

    def reconnect(self):
        if self.serial != None and self.serial.is_open:
            self.serial.close()
        self.connect()

    def clean_buffers(self):
        self.serial.reset_input_buffer() # receiving
        self.serial.reset_output_buffer() # sending
       

    def listen(self):
        message = None
        while True:
          
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

    def send(self):
        self.second_arrow = None
        self.xdist = None
        self.ydist = None
        while True:
            # message = self.msg_queue.get()

            # message_str = message.decode("utf-8")
            # message_json = json.loads(message_str)
            # message_type = message_json["type"]

            if message_type == "NAVIGATION":
                # display path on android
                self.send_path_to_android(message_json)

                # convert/adjust any turn or obstacle routing commands
                # smooth out commands by combining consecutive SF/SB commands
                commands = self.adjust_commands(message_json["data"]["commands"])
                for command in commands: # send and wait for ACK/reset delay
                    self.write_to_stm(command)
                    # if command.startswith("UF"):
                    #     self.write_to_stm("Y" + command[1:])
                    #     print("[STM] DEBUGGING: first movement distance =", self.ydist)
                    #     if self.ydist < 30:
                    #         self.write_to_stm(command) # resend command if US glitch
                    # else:
                    #     self.write_to_stm(command)
                self.obstacle_count += 1

                print("[STM] Checking second arrow:", self.second_arrow)
                if self.second_arrow != None: # after moving around obstacle 2
                    self.return_to_carpark()
                    print("[STM] DONE")
                    return

                # Start a new thread to capture and send the image to PC
                capture_and_send_image_thread = threading.Thread(target=self.send_image_to_pc, daemon=True)
                capture_and_send_image_thread.start()

                if self.obstacle_count % STM_GYRO_RESET_FREQ == 0:
                    print("[STM] Resetting gyroscope after %d obstacles" % self.obstacle_count)
                    self.write_to_stm(STM_GYRO_RESET_COMMAND)
            else:
                print("[STM] WARNING: Rejecting message with unknown type [%s] for STM" % message_type)

    def write_to_stm(self, command):
        self.clean_buffers()
        if self.is_valid_command(command):
            exception = True
            while exception:
                try:
                    print("[STM] Sending command", command)
                    encoded_string = command.encode()
                    byte_array = bytearray(encoded_string)
                    self.serial.write(byte_array)
                except Exception as e:
                    print("[STM] ERROR: Failed to write to STM -", str(e))
                    exception = True
                    self.reconnect() # reconnect and retry

                else:
                    exception = False
                    if command == STM_GYRO_RESET_COMMAND:
                        print("[STM] Waiting %ss for reset" % STM_GYRO_RESET_DELAY)
                        time.sleep(STM_GYRO_RESET_DELAY)
                    elif re.match(STM_XDIST_COMMAND_FORMAT, command):
                        dist = self.wait_for_dist()
                        if dist >= 0:
                            self.xdist = dist
                            print("[STM] updated XDIST =", self.xdist)
                        else:
                            print("[STM] ERROR: failed to update XDIST, received invalid value:", dist)
                    elif re.match(STM_YDIST_COMMAND_FORMAT, command):
                        dist = self.wait_for_dist()
                        if dist >= 0:
                            self.ydist = dist
                            print("[STM] updated YDIST =", self.ydist)
                        else:
                            print("[STM] ERROR: failed to update YDIST, received invalid value:", dist)
                    else: # standard movement/navigation command
                        print("[STM] Waiting for ACK")
                        self.wait_for_ack()
        else:
            print(f"[STM] ERROR: Invalid command to STM [{command}]. Skipping...")

    def wait_for_ack(self):
        message = self.listen()
        if message  == STM_ACK_MSG:
            print("[STM] Received ACK from STM")
        else:
            print("[STM] ERROR: Unexpected message from STM -", message)
            self.reconnect()

    def wait_for_dist(self):
        distance = "0"
        for i in range(3): # expecting 3 digit distance in cm
            message = self.listen()
            if message.isnumeric():
                distance += message
            else:
                print(f"[STM] ERROR: Unexpected message from STM while getting distance - {message}")
                self.reconnect()
        distance = int(distance)
        print(f"[STM] Read final DIST =", distance)
        return distance

    def send_image_to_pc(self):
        print("[STM] Adding image from camera to PC message queue")
        self.RPiMain.PC.msg_queue.put(get_image())

    def send_path_to_android(self, message_json):
        # send path to Android for display
        if "path" not in message_json["data"]:
            print("[STM] No path found in NAVIGATION message")
        try:
            path_message = self.create_path_message(message_json["data"]["path"])
            self.RPiMain.Android.msg_queue.put(path_message)
            print("[STM] Adding NAVIGATION path from PC to Android message queue")
        except:
            print("[STM] ERROR with path found in NAVIGATION message")

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

    def create_path_message(self, path):
        message = {
            "type": "PATH",
            "data": {
                "path": path
            }
        }
        return json.dumps(message).encode("utf-8")

    # functions for task 2 (W9) - fastest car
    def return_to_carpark(self):
        print(f"[STM] Initiating return to carpark: XDIST = {self.xdist}, YDIST = {self.ydist}, ARROW = {self.second_arrow}")
        commands = self.get_commands_to_carpark()
        for command in commands: # send and wait for ACK
            self.write_to_stm(command)

    def get_commands_to_carpark(self):
        print(f"[STM] Calculating path to carpark...") # after {self.second_arrow} arrow for XDIST = {self.xdist} YDIST = {self.ydist}"
        movement_list = []
        x_adjustment = (self.xdist) // 2 -30 # take floor of div 2, subtract turning radius
        y_adjustment = self.ydist + 80 # min dist btw obs + width of obs * 2

        movement_list.append(f"SF{y_adjustment:03d}")
        if self.second_arrow == 'R':
            movement_list.append("LF090")
            # if abs(x_adjustment) > 5:
            if x_adjustment > 0:
                movement_list.append(f"SF{x_adjustment:03d}")
            else:
                movement_list.append(f"SB{abs(x_adjustment):03d}")
            movement_list.append("RF090")
            movement_list.append("VF200") # reduce ultrasonic threshold
        elif self.second_arrow == 'L':
            movement_list.append("RF090")
            # if abs(x_adjustment) > 5:
            if x_adjustment > 0:
                movement_list.append(f"SF{x_adjustment:03d}")
            else:
                movement_list.append(f"SB{abs(x_adjustment):03d}")
            movement_list.append("LF090")
            movement_list.append("VF200") # reduce ultrasonic threshold
        else:
            print("[STM] ERROR getting path to carpark, second arrow invalid -", self.second_arrow)

        print("[STM] Final path to carpark:", movement_list)
        return movement_list

    def convert(self, command):
        return STM_OBS_ROUTING_MAP[command]
