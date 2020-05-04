# This is a version of the program that works with an
# an Xbox One controller and without a physical
# Raspberry Pi (uses a dummy ServoKit module).

import pygame
import time
import math
# from adafruit_servokit import ServoKit

class DummyContinousServoPowerable(object):
    def __init__(self, pin):
        self.pin = pin
    def __setattr__(self, key, value):
        if key == "throttle":
            print("[DummyContinousServo] Set motor power on pin %s to %s" % (self.pin, value))
        elif key == "pin":
            object.__setattr__(self, key, value)
        else:
            print("[DummyContinousServo] WARNING: Invalid attribute accessed: %s" % key)
            object.__setattr__(self, key, value)

class DummyContinuousServo(object):
    def __getitem__(self, item):
        return DummyContinousServoPowerable(item)

class DummyServoKit(object):
    continuous_servo = DummyContinuousServo()

RGB_GREEN = (0, 255 ,0)
RGB_BLUE = (0, 0, 255)
RGB_RED = (255, 0, 0)
RGB_PURPLE = (130, 0, 130)
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
RESOLUTION = (SCREEN_WIDTH, SCREEN_HEIGHT)
JOY_X = SCREEN_WIDTH/2
JOY_Y = SCREEN_HEIGHT/2
POWER_MULTIPLIER = 0.6 # Multiplier to be applied to all target motor powers

SECONDS_TO_FULL = 0.5
FRAMERATE = 240
INCREMENTS_PER_SECOND = 1/SECONDS_TO_FULL
INCREMENTS_PER_FRAME = INCREMENTS_PER_SECOND/FRAMERATE

MOTOR_TOP_LEFT = 0 # Channel numbers
MOTOR_TOP_RIGHT = 1
MOTOR_BOTTOM_LEFT = 2
MOTOR_BOTTOM_RIGHT = 3
MOTOR_UP_LEFT = 4
MOTOR_UP_RIGHT = 5

MX1_X = JOY_X - SCREEN_HEIGHT/4   #MX1 = motor X1
MX1_Y = JOY_Y - SCREEN_HEIGHT/4

MX2_X = JOY_X + SCREEN_HEIGHT/4   #MX2 = motor X2
MX2_Y = JOY_Y + SCREEN_HEIGHT/4

MY1_X = JOY_X + SCREEN_HEIGHT/4   #MY1 = motor Y1 
MY1_Y = JOY_Y - SCREEN_HEIGHT/4

MY2_X = JOY_X - SCREEN_HEIGHT/4   #MY1 = motor Y2
MY2_Y = JOY_Y + SCREEN_HEIGHT/4

vmotorpower = 0.01
DEADZONE = 0.1

pygame.init()

screen = pygame.display.set_mode(RESOLUTION)
font = pygame.font.SysFont("ROV_control_font", 25)

rightJoyYAxisIndex = 3
rightJoyXAxisIndex = 4
leftJoyYAxisIndex = 1
leftJoyXAxisIndex = 0
upJoyButton = 3
downJoyButton = 0
verticalaxis_left = 1
verticalaxis_right = 3

kit = DummyServoKit()
# kit = ServoKit(channels=16)

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

def translateRange(value, old_min, old_max, new_min, new_max):
    old_range = (old_max-old_min)
    if old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)  
        new_value = (((value-old_min)*new_range)/old_range)+new_min
    return new_value

def connectJoystick():
    global joystick

    pygame.joystick.quit()
    pygame.joystick.init() # Refresh joystick list

    while pygame.joystick.get_count() == 0:
        print("No joysticks detected. Retrying...")
        time.sleep(1.0)
        pygame.joystick.quit()
        pygame.joystick.init() # Refresh joystick list
    
    if pygame.joystick.get_count() < 1:
        print("Multiple joysticks found.")
        possible_joysticks = []
        for joystick_id in range(pygame.joystick.get_count()):
            possible_joystick = pygame.joystick.Joystick(joystick_id)
            print("Joystick %i: '%s'" % (joystick_id, possible_joystick.get_name()))
        id_entered = False
        while not id_entered:
            joystick_id = input("Enter the id of the joystick you want to use: ")
            try:
                joystick = possible_joysticks[int(joystick_id)]
                id_entered = True
            except:
                print("Invalid joystick id. Id must be in the range %i to %i." % (0, pygame.joystick.get_count()-1))
        print("Joystick chosen.")
    else:
        print("Joystick found.")
        joystick = pygame.joystick.Joystick(0)
    
    joystick.init()

    print("Initialized Joystick '%s' with id %i." % (joystick.get_name(), joystick.get_id()))

def debugJoystick():
    pygame.event.pump()
    
    try:
        print("Data of joystick '%s':\n    Joystick id: %i" % (joystick.get_name(), joystick.get_id()))
        for axis in range(joystick.get_numaxes()):
            print("    Axis %i: %f" % (axis,
                                       joystick.get_axis(axis)))
        for button in range(joystick.get_numbuttons()):
            print("    Button %i: %f" % (button, joystick.get_button(button)))
    except BaseException as error:
        print("Error while debugging joystick: %s" % error)

def useControls(controls_dict):
    global i
    global new_value
    global accessing
    global last_values
    
    if controls_dict is None or controls_dict == {}:
        return
    
    controls_dict = controls_dict.copy()
    
    for control in controls_dict.keys():
        power = controls_dict[control]*POWER_MULTIPLIER
        
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

def getControls():
    #time.sleep(.02)
    try:
        message = ""
        for axis in joymap.keys(): # Get and adjust value
            
            value = joystick.get_axis(axis)
            print(round(axis,2), round(value,2))
            message = "value: %2.2f " % value
            if abs(value) < DEADZONE:
                value = 0
            control, inverted = joymap[axis]
            if inverted:
                value *= -1

                
        ### We have read the joystick positions, now we convert them to motor power

        ### Calculate the magnitude of the joystick position

        ### Calculate the angle of the joystick position

        ### Calculate the motor power vector angle (rotate 45 degrees)

        ### Calculate the raw X and Y motor power values

        ### Calculate the scaling factor

        ### Apply the scaling factor       
            
    except ConnectionRefusedError as error:
        print("Error while getting controls: %s" % error)
    return output.copy()

def getControls():
    #time.sleep(.02)
    try:
        message = ""
        for button in joymap.keys(): # Get and adjust value
            
            value = joystick.get_button(button)
            print(round(button,2), round(value,2))
            message = "value: %2.2f " % value
            if abs(value) < DEADZONE:
                value = 0
            control, inverted = joymap[button]
            if inverted:
                value *= -1
            
    except ConnectionRefusedError as error:
        print("Error while getting controls: %s" % error)
    return output.copy()

####################  PROGRAM STARTS  ####################

connectJoystick()

rect_width = 70
extent = int(screen.get_height()/2) # Extent from the middle that the bars can go (negative and positive)
max_height = screen.get_height()-extent # The height of the middle of the joystick visualization bars. Set to screen.get_height()-extent to align with the bottom of the window

running = True

clock = pygame.time.Clock()

# DEBUG
#while True:
#    debugJoystick()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    if not running: # Quit immediately after given the signal
        break

    screen.fill((0, 0, 0))
    rightJoyYPos = -joystick.get_axis(rightJoyYAxisIndex)
    rightJoyXPos = joystick.get_axis(rightJoyXAxisIndex)
    
    if (rightJoyYPos == 0):
        if (rightJoyXPos >= 0):
            rightjoystickAngle = 0
        if (rightJoyXPos < 0):
            rightjoystickAngle = 180*math.pi/180.0
    else:
        rightjoystickAngle = math.atan(rightJoyXPos/rightJoyYPos)

    rightmotorAngle = rightjoystickAngle + (45.0*math.pi/180.0)

    # If the joystick does not properly recentered, we set it to 0
    if (abs(rightJoyXPos) < DEADZONE) and (abs(rightJoyYPos) < DEADZONE):
           rightrawmotorX = 0
           rightrawmotorY = 0
    else:
        rightrawmotorX = math.sin(rightmotorAngle)
        rightrawmotorY = math.cos(rightmotorAngle)
        
    if (rightJoyYPos < 0.0):
        rightrawmotorY = rightrawmotorY*-1
        rightrawmotorX = rightrawmotorX*-1
       
    try:
        rightscale = max(abs(rightJoyXPos),abs(rightJoyYPos))/max(abs(rightrawmotorX),abs(rightrawmotorY))
    except ZeroDivisionError:
        rightscale = 0

    scaledrightmotorX = rightscale*rightrawmotorX
    if scaledrightmotorX > 1.0:
       scaledrightmotorX = 1.0
    elif scaledrightmotorX < -1.0:
       scaledrightmotorX = -1.0

    if (scaledrightmotorX >0) and (scaledrightmotorX < 0.40):
       scaledrightmotorX = scaledrightmotorX/2
    elif (scaledrightmotorX >= 0.40) and (scaledrightmotorX < 0.70):
       scaledrightmotorX = scaledrightmotorX-0.20 
    elif (scaledrightmotorX >= 0.70) and (scaledrightmotorX ==1):
       scaledrightmotorX = (5/3)*scaledrightmotorX-2/3
       
    if (scaledrightmotorX > -0.40) and (scaledrightmotorX < 0):
       scaledrightmotorX = scaledrightmotorX/2
    elif (scaledrightmotorX <= -0.40 and scaledrightmotorX > -0.70):
       scaledrightmotorX = scaledrightmotorX+0.20 
    elif (scaledrightmotorX <= 0.70 and scaledrightmotorX == -1):
       scaledrightmotorX = (5/3)*scaledrightmotorX+2/3

    scaledrightmotorY = rightscale*rightrawmotorY
    if scaledrightmotorY > 1.0:
       scaledrightmotorY = 1.0
    elif scaledrightmotorY < -1.0:
       scaledrightmotorY = -1.0


    if (scaledrightmotorY >0) and (scaledrightmotorY < 0.40):
       scaledrightmotorY = scaledrightmotorY/2
    elif (scaledrightmotorY >= 0.40) and (scaledrightmotorY < 0.70):
       scaledrightmotorY = scaledrightmotorY-0.20 
    elif (scaledrightmotorY >= 0.70) and (scaledrightmotorY ==1):
       scaledrightmotorY = (5/3)*scaledrightmotorY-2/3

    if (scaledrightmotorY > -0.40) and (scaledrightmotorY < 0):
       scaledrightmotorY = scaledrightmotorY/2
    elif (scaledrightmotorY <= -0.40 and scaledrightmotorY > -0.70):
       scaledrightmotorY = scaledrightmotorY+0.20 
    elif (scaledrightmotorY <= 0.70 and scaledrightmotorY == -1):
       scaledrightmotorY = (5/3)*scaledrightmotorY+2/3

    leftJoyYPos = -joystick.get_axis(leftJoyYAxisIndex)
    leftJoyXPos = joystick.get_axis(leftJoyXAxisIndex)
    
    if (leftJoyYPos == 0):
       if (leftJoyXPos >= 0):
          leftjoystickAngle = 0
          if (leftJoyXPos < 0):
             leftjoystickAngle = 180*math.pi/180.0
    else:
        leftjoystickAngle = math.atan(leftJoyXPos/leftJoyYPos)

    leftmotorAngle = leftjoystickAngle + (45.0*math.pi/180.0)
       ##    print("joystick angle DEG = ", joystickAngle*180.0/math.pi)

    if (abs(leftJoyXPos) < DEADZONE) and (abs(leftJoyYPos) < DEADZONE):
           leftrawmotorX = 0
           leftrawmotorY = 0
    else:
        leftrawmotorX = math.sin(leftmotorAngle)
        leftrawmotorY = math.cos(leftmotorAngle)

        
    if (leftJoyYPos < 0.0):
        leftrawmotorY = leftrawmotorY*-1
        leftrawmotorX = leftrawmotorX*-1
    try:
        leftscale = max(abs(leftJoyXPos),abs(leftJoyYPos))/max(abs(leftrawmotorX),abs(leftrawmotorY))
    except ZeroDivisionError:
        leftscale = 0
    scaledleftmotorX = leftscale*leftrawmotorX
    #LIMITING THE POWER TO 1 FOR LEFT X 
    if scaledleftmotorX > 1.0:
       scaledleftmotorX = 1.0
    elif scaledleftmotorX < -1.0:
       scaledleftmotorX = -1.0

    #SCALING LEFT X MOTOR (UPER LEFT ONE) WHEN POSITIVE 
    if (scaledleftmotorX >0) and (scaledleftmotorX < 0.40):
       scaledleftmotorX = scaledleftmotorX/2
    elif (scaledleftmotorX >= 0.40) and (scaledleftmotorX < 0.70):
       scaledleftmotorX = scaledleftmotorX-0.20 
    elif (scaledleftmotorX >= 0.70) and (scaledleftmotorX ==1):
       scaledleftmotorX = (5/3)*scaledleftmotorX-2/3
    #SCALING LEFT X MOTOR WHEN NEGATIVE
    if (scaledleftmotorX > -0.40) and (scaledleftmotorX < 0):
       scaledleftmotorX = scaledleftmotorX/2
    elif (scaledleftmotorX <= -0.40 and scaledleftmotorX > -0.70):
       scaledleftmotorX = scaledleftmotorX+0.20 
    elif (scaledleftmotorX <= 0.70 and scaledleftmotorX == -1):
       scaledleftmotorX = (5/3)*scaledleftmotorX+2/3
       
    #LIMITNG THE POWER TO 1 FOR LEFT Y
    scaledleftmotorY = leftscale*leftrawmotorY
    if scaledleftmotorY > 1.0:
       scaledleftmotorY = 1.0
    elif scaledleftmotorY < -1.0:
       scaledleftmotorY = -1.0

    #SCALING LEFT Y WHEN POSITIVE
    if (scaledleftmotorY >0) and (scaledleftmotorY < 0.40):
       scaledleftmotorY = scaledleftmotorY/2
    elif (scaledleftmotorY >= 0.40) and (scaledleftmotorY < 0.70):
       scaledleftmotorY = scaledleftmotorY-0.20 
    elif (scaledleftmotorY >= 0.70) and (scaledleftmotorY ==1):
       scaledleftmotorY = (5/3)*scaledleftmotorY-2/3
    #SCALING LEFT Y WHEN NEGATIVE 
    if (scaledleftmotorY > -0.40) and (scaledleftmotorY < 0):
       scaledleftmotorY = scaledleftmotorY/2
    elif (scaledleftmotorY <= -0.40 and scaledleftmotorY > -0.70):
       scaledleftmotorY = scaledleftmotorY+0.20 
    elif (scaledleftmotorY <= 0.70 and scaledleftmotorY == -1):
       scaledleftmotorY = (5/3)*scaledleftmotorY+2/3

    upJoyPos = joystick.get_button(upJoyButton)
    downJoyPos = joystick.get_button(downJoyButton)
    verticalpos = -1*(joystick.get_axis(verticalaxis_left)/2) + (joystick.get_axis(verticalaxis_right)/2) # New code
    
    vmotorpower = vmotorpower + upJoyPos * 0.01 + downJoyPos * -0.01 + verticalpos/4

    #print(vmotorpower, upJoyPos, downJoyPos)

    if (vmotorpower > 1.0) :
        vmotorpower = 1.0
    if (vmotorpower < -1.0) :
        vmotorpower = -1.0
        
    #print("leftX, leftY, rightX, rightY, vmotor = ", round(scaledleftmotorX,2), round(scaledleftmotorY,2), round(scaledrightmotorX,2), round(scaledrightmotorY,2), round(vmotorpower,2)) 

    pygame.draw.lines(screen, RGB_PURPLE, False, [(75,240), (75,240+vmotorpower*-100)],2)   
    pygame.draw.lines(screen, RGB_GREEN, False, [(400,240), (400+rightJoyXPos*100,240+rightJoyYPos*100*-1)], 2)
    pygame.draw.lines(screen, RGB_GREEN, False, [(240,240), (240+leftJoyXPos*100,240+leftJoyYPos*100*-1)], 2)

    pygame.draw.lines(screen, RGB_BLUE, False, [(MY2_X,MY2_Y), (MY2_X-scaledleftmotorY*50,MY2_Y-scaledleftmotorY*50)], 2)
    pygame.draw.lines(screen, RGB_BLUE, False, [(MY1_X,MY1_Y), (MY1_X-scaledrightmotorY*50,MY1_Y-scaledrightmotorY*50)], 2)

    pygame.draw.lines(screen, RGB_RED, False, [(MX1_X,MX1_Y), (MX1_X+scaledleftmotorX*50,MX1_Y-scaledleftmotorX*50)], 2)

    pygame.draw.lines(screen, RGB_RED, False, [(MX2_X,MX2_Y), (MX2_X+scaledrightmotorX*50,MX2_Y-scaledrightmotorX*50)], 2)

    useControls({"top_left":scaledleftmotorX, "top_right":scaledrightmotorY, "bottom_left":scaledleftmotorY, "bottom_right":scaledrightmotorX, "vertical_left":vmotorpower, "vertical_right":vmotorpower})   

    pygame.display.flip()
    clock.tick(FRAMERATE)
