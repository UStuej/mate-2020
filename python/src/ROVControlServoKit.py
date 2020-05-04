from adafruit_servokit import ServoKit
import socket
from time import sleep
from threading import Thread
from pygame.time import Clock

ADDRESS = ("169.254.38.172", 12347)
#ADDRESS = ("10.0.0.54", 12347)

MOTOR_TOP_LEFT = 0 # Channel numbers
MOTOR_TOP_RIGHT = 1
MOTOR_BOTTOM_LEFT = 2
MOTOR_BOTTOM_RIGHT = 3
MOTOR_UP_LEFT = 4
MOTOR_UP_RIGHT = 5

SECONDS_TO_FULL = 0.5
FRAMERATE = 240
INCREMENTS_PER_SECOND = 1/SECONDS_TO_FULL # TODO: Check this
INCREMENTS_PER_FRAME = INCREMENTS_PER_SECOND/FRAMERATE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(ADDRESS)

kit = ServoKit(channels=16)

i = 0
new_value = 0

last_values = {"top_left":0,
               "top_right":0,
               "bottom_left":0,
               "bottom_right":0,
               "vertical_left":0,
               "vertical_right":0}

pi_mapping = {"top_left":MOTOR_TOP_LEFT,
              "top_right":MOTOR_TOP_RIGHT,
              "bottom_left":MOTOR_BOTTOM_LEFT,
              "bottom_right":MOTOR_BOTTOM_RIGHT,
              "vertical_left":MOTOR_UP_LEFT,
              "vertical_right":MOTOR_UP_RIGHT}

controls_dict = {}

def apply_controls(controls_dict):
    global i
    global new_value
    global accessing
    global last_values
    
    if controls_dict is None or controls_dict == {}:
        return
    
    controls_dict = controls_dict.copy()
    
    for control in controls_dict.keys():
        power = controls_dict[control]
        new_value = power

        i = last_values[control]
        
        if i != new_value:
            if i < new_value:
                i = min(i+INCREMENTS_PER_FRAME, new_value) # If we're adding power, clip the result to the new value
            elif i > new_value:
                i = max(i-INCREMENTS_PER_FRAME, new_value) # If we're taking away power, clip the result to the new value

            print(str(i)+"\r", end=" ")
                
            kit.continuous_servo[pi_mapping[control]].throttle = i
            last_values[control] = i

clock = Clock()

def apply_continue():
    global controls_dict
    while True:
        apply_controls(controls_dict)
        clock.tick(FRAMERATE)

motor_thread = Thread(target=apply_continue)
motor_thread.start()

fps = 0

while True:
    data, from_address = sock.recvfrom(4096)
    controls = data.decode().split(";")[-2]
    
    if len(controls) > 0:
        #print(controls)
        eval(controls) # Get the last command, evaluate it, and apply the controls
        
    fps = clock.get_fps()
