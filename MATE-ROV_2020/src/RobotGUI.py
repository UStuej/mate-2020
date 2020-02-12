from math import floor, ceil, sqrt, atan, sin, cos, pi
from imutils.video import VideoStream, FPS
from ast import literal_eval
import numpy as np
import pytweening
import netifaces
import imutils
import socket
import time
import cv2

USE_GUI = True # Whether or not to use the graphical user interface to control the motors. Should be off if used as a library (like on the Pi)

def GPIO_BACKEND_PIN_SET_POWER(pin, power, output_type=0):
    """Stand in function for any supported backend with a function to set a GPIO pin to a certain power (or do the equivelent as is required for the program). This function expects a valid pin number and a power ranging from -1.0 to 1.0, as well as an output type specifying the type of device to be powered. Actual function should be written separately, then the constant name assigned to it"""
    print(str(pin)+", "+str(power))
    #raise NotImplementedError

def normalize_angle(angle):
    """Utility function to normalize an angle in degrees within the range 0-360"""
    return angle-360*(angle//360)

def translate(value, old_min, old_max, new_min, new_max):
    """Utility function to translate a number from one range to another, preserving the ratio"""
    old_range = (old_max-old_min)
    
    if old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)  
        new_value = (((value-old_min)*new_range)/old_range)+new_min
    return new_value

def auto_canny(image, sigma=0.33): # auto_canny function from pyimagesearch.com
    v = np.median(image)
    lower = int(max(0, (1.0-sigma)*v))
    upper = int(min(255, (1.0+sigma)*v))
    edged = cv2.Canny(image, lower, upper)
    return edged

def canny(image): # Wrapper for more pyimagesearch.com code
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    return auto_canny(blurred)

def detect_lines(image): # Wrapper for previous 2 functions and actual line detection code
    """Returns detected lines in image"""
    return cv2.HoughLinesP(canny(image), rho=1, theta=np.pi/180, threshold=100, minLineLength=100, maxLineGap=50)

class AbstractMotor(object):
    """Abstract motor class to represent motors with variable speed and direction that can be controlled by a floating point value from -1.0 to 1.0"""
    def __init__(self, initial_speed=0.0):
        self.speed = initial_speed
    def update(self):
        pass # Some call to actual motor control code here
    def __setattr__(self, name, value):
        if name in self.__dict__:
            old_value = self.__dict__[name]
        else:
            old_value = None
        self.__dict__[name] = value
        
        if name == "speed" and value != old_value: # Avoid redundant motor commands for slow backends
            self.update()
    def __repr__(self):
        return type(self).__name__+"(initial_speed=%s)" % self.speed

class GPIOMotor(AbstractMotor):
    """GPIO motor class to represent a single PWM motor connected to this computer. update() directly applies changes to the motor speed"""
    def __init__(self, pin, initial_speed=0.0):
        self.pin = pin
        self.speed = initial_speed
    def update(self):
        GPIO_BACKEND_PIN_SET_POWER(self.pin, self.speed) # Actual range of PWM control output must be from 1000-2000. Use translate in backend function to accomodate this
    def __repr__(self):
        return type(self).__name__+"(%s, initial_speed=%s)" % (self.pin, self.speed)

class GPIOMotorArray(object):
    """GPIO motor class to represent an array of PWM motors connected to this computer. update() calls update() on each motor. This class is somewhat useless, as there is no real benefit of using it instead of a list of motors besides minor convenience, and only exists for completeness and compatibilitiy reasons"""
    def __init__(self, motors=[]):
        self.motors = list(motors)
    def add_motor(self, pin, initial_speed=0.0):
        self.motors.append(GPIOMotor(pin, initial_speed))
    def update(self):
        for motor in self.motors:
            motor.update()
    def __repr__(self):
        return type(self).__name__+"(motors=%s)" % self.motors

class RemoteGPIOMotor(object):
    """GPIO motor class to represent a single PWM motor connected to another computer. update() saves changes to the motor speed, but doesn't apply it. This class MUST be used in conjunction with RemoteGPIOMotorArray to be functional"""
    def __init__(self, pin, owner, initial_speed=0.0):
        self.owner = owner
        self.owner.motors.append(self)
        self.pin = pin
        self.speed = initial_speed
    def update(self):
        self.owner.unapplied_commands[self.pin] = round(self.speed, 3)
    def __repr__(self):
        return type(self).__name__+"(%s, %s, initial_speed=%s)" % (self.pin, self.owner, self.speed)

class RemoteGPIOMotorArray(object):
    """GPIO motor class to represent an array of PWM motors connected to another computer. apply() sends the motor's commands in a batch"""
    def __init__(self, other, motors=[]):
        self.other = other
        self.motors = list(motors)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controls = {}
    def add_motor(self, pin, initial_speed=0.0):
        self.motors.append(RemoteGPIOMotor(pin, initial_speed))
    def apply(self):
        data = (str(self.controls)+";").encode()
        self.socket.sendto(data, self.other)
    def __repr__(self):
        return type(self).__name__+"(%s, motors=%s)" % (self.other, self.motors)

class BaseLocalGPIOMotorArray(RemoteGPIOMotorArray):
    """Base GPIO motor class to represent an array of PWM motors connected to this computer, but operated by a remote one"""
    def __init__(self, this, motors=[]):
        self.other = other
        self.motors = list(motors)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controls = {}
        self.socket.bind(this)
    def apply(self):
        self.controls = literal_eval(self.socket.recvfrom(1024).decode().split(";")[-1])
        
        for pin in controls:
            GPIO_BACKEND_PIN_SET_POWER(pin, controls[pin])
    def __repr__(self):
        return type(self).__name__+"(%s, motors=%s)" % (self.this, self.motors)

class AbstractServo(object):
    """Abstract servo class to represent servos that can be set to specific angles"""
    def __init__(self, initial_angle=0, min_angle=0, max_angle=360):
        self.angle = initial_angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.update()
    def update(self):
        pass # Some call to actual servo control code here
    def __setattr__(self, name, value):
        self.__dict__[name] = value
        
        if name == "angle":
            self.update()
    def __repr__(self):
        return type(self).__name__+"(initial_angle=%s, min_angle=%s, max_angle=%s)" % (self.initial_angle, self.min_angle, self.max_angle)

class TargetMotorController(AbstractMotor):
    """Controls a motor that inherits from AbstractMotor, setting its speed to a target value within some number of ticks given an acceleration value from 0.0 to 1.0. Can be used in place of an AbstractMotor"""
    def __init__(self, motor, initial_target=0.0):
        self.motor = motor
        self.target = initial_target
    def update(self, new_target=None, acceleration=1.0):
        if new_target:
            self.target = new_target
        if self.motor.speed < self.target: # Clip speed to target speed
            self.motor.speed = min(1.0, self.motor.speed+acceleration)
        if self.motor.speed > self.target:
            self.motor.speed = max(-1.0, self.motor.speed-acceleration)
    def __repr__(self):
        return type(self).__name__+"(initial_target=%s)" % (self.motor, self.initial_target)
    def apply(self):
        self.motor.owner.apply()

class TargetServoController(AbstractServo):
    """Controls a servo that inherits from AbstractServo, setting its angle to a target value within some number of ticks given an acceleration value from 0 to 360. Can be used in place of an AbstractServo"""
    def __init__(self, servo, initial_target=0.0):
        self.servo = servo
        self.target = initial_target
    def update(self, new_target=None, acceleration=360):
        if new_target:
            self.target = normalize_angle(new_target)
        if self.motor.speed < self.target: # Clip speed to target speed
            self.motor.speed = min(360, self.motor.speed+acceleration)
        if self.motor.speed > self.target:
            self.motor.speed = max(0, self.motor.speed-acceleration)
    def __repr__(self):
        return type(self).__name__+"(%s, initial_target=%s)" % (self.servo, self.initial_target)

class TankSteeringController(object):
    """Controls four motors (inheriting from AbstractMotor) with a two tuple input representing left and right tank steering inputs, each ranging from -1.0 to 1.0"""
    def __init__(self, front_left, front_right, back_left, back_right):
        self.front_left = front_left
        self.front_right = front_right
        self.back_left = back_left
        self.back_right = back_right
    def update(self, control):
        left, right = control
        
        self.front_left.speed = left
        self.back_right.speed = left
        
        self.front_right.speed = right
        self.back_left.speed = right
    def __repr__(self):
        return type(self).__name__+"(%s, %s, %s, %s)" % (self.front_left, self.front_right, self.back_left, self.back_right)
    def apply(self):
        for motor in [self.front_left, self.front_right, self.back_left, self.back_right]:
            if "owner" in dir(motor):
                self.front_left.owner.apply()
        
class HexROVController():
    """Controlls four motors (inheriting from AbstractMotor) on each corner of an ROV tilted at 45 degree angles inwards and outwards of the ROV body with a two-tuple input representing a direction in x and y coordinates for the ROV to travel"""
    def __init__(self, front_left, front_right, back_left, back_right, deadzone=0): # TODO: Copy Elis' code from twoJoystickController program to implement proper tank steering with the ROV
        self.front_left = front_left
        self.front_right = front_right
        self.back_left = back_left
        self.back_right = back_right
        self.deadzone = deadzone
    def update(self, control):
        rightJoyXPos = control[0]
        rightJoyYPos = -control[1]
        if (rightJoyYPos == 0):
            if (rightJoyXPos >= 0):
                joystickAngle = 0
            if (rightJoyXPos < 0):
                joystickAngle = 180*pi/180.0
        else:
            joystickAngle = atan(rightJoyXPos/rightJoyYPos)
        motorAngle = joystickAngle + (45.0*pi/180.0)
        if (abs(rightJoyXPos) < self.deadzone) and (abs(rightJoyYPos) < self.deadzone):
            rawmotorX = 0
            rawmotorY = 0
        else:
            rawmotorX = sin(motorAngle)
            rawmotorY = cos(motorAngle)
        if (rightJoyYPos < 0.0):
            rawmotorY = rawmotorY*-1
            rawmotorX = rawmotorX*-1
        try:
            scale = max(abs(rightJoyXPos), abs(rightJoyYPos))/max(abs(rawmotorX), abs(rawmotorY))
        except ZeroDivisionError:
            scale = 0
        scaledmotorX = scale*rawmotorX
        if scaledmotorX > 1.0:
           scaledmotorX = 1.0
        elif scaledmotorX < -1.0:
           scaledmotorX = -1.0
        if (scaledmotorX > 0) and (scaledmotorX < 0.40):
           scaledmotorX = scaledmotorX/2
        elif (scaledmotorX >= 0.40) and (scaledmotorX < 0.70):
           scaledmotorX = scaledmotorX-0.20 
        elif (scaledmotorX >= 0.70) and (scaledmotorX == 1):
           scaledmotorX = (5/3)*scaledmotorX-2/3 
        if (scaledmotorX > -0.40) and (scaledmotorX < 0):
           scaledmotorX = scaledmotorX/2
        elif (scaledmotorX <= -0.40 and scaledmotorX > -0.70):
           scaledmotorX = scaledmotorX+0.20 
        elif (scaledmotorX <= 0.70 and scaledmotorX == -1):
           scaledmotorX = (5/3)*scaledmotorX+2/3
        scaledmotorY = scale*rawmotorY
        if scaledmotorY > 1.0:
           scaledmotorY = 1.0
        elif scaledmotorY < -1.0:
           scaledmotorY = -1.0
        if (scaledmotorY > 0) and (scaledmotorY < 0.40):
           scaledmotorY = scaledmotorY/2
        elif (scaledmotorY >= 0.40) and (scaledmotorY < 0.70):
           scaledmotorY = scaledmotorY-0.20 
        elif (scaledmotorY >= 0.70) and (scaledmotorY == 1):
           scaledmotorY = (5/3)*scaledmotorY-2/3
        if (scaledmotorY > -0.40) and (scaledmotorY < 0):
           scaledmotorY = scaledmotorY/2
        elif (scaledmotorY <= -0.40 and scaledmotorY > -0.70):
           scaledmotorY = scaledmotorY+0.20 
        elif (scaledmotorY <= 0.70 and scaledmotorY == -1):
           scaledmotorY = (5/3)*scaledmotorY+2/3
        self.front_left.speed = scaledmotorX
        self.back_right.speed = scaledmotorX
        self.front_right.speed = scaledmotorY
        self.back_left.speed = scaledmotorY
    def __repr__(self):
        return type(self).__name__+"(%s, %s, %s, %s, deadzone=%s)" % (self.front_left, self.front_right, self.back_left, self.back_right, self.deadzone)
    def apply(self):
        for motor in [self.front_left, self.front_right, self.back_left, self.back_right]:
            if "owner" in dir(motor):
                self.front_left.owner.apply()

class TargetNavigator(object):
    """Manages a HexROVController (or a similar class with the same update arguments) to follow a position on screen, keeping it at a set location on the screen"""
    def __init__(self, controller, screen_size, target=None, power_function=pytweening.linear):
        if not target:
            target = (screen_size[0]//2, screen_size[1]//2)
            
        self.controller = controller
        self.power_function = power_function
        self.target = target
        self.screen_size = max(screen_size)/2
    def update(self, position):
        x_distance = self.target[0]-position[0]
        y_distance = self.target[1]-position[1]
        x_sign = -1 if x_distance < 0 else 1
        y_sign = -1 if y_distance < 0 else 1
        
        if abs(x_distance) >= abs(y_distance):
            x_factor = 1*x_sign
            y_factor = abs(y_distance/x_distance)*y_sign
        else:
            x_factor = abs(x_distance/y_distance)*x_sign
            y_factor = 1*y_sign
        distance = sqrt((self.target[0]-position[0])**2+(self.target[1]-position[1])**2)
        power_factor = self.power_function(translate(distance, 0, self.screen_size, 0, 1))
        power = (x_factor*power_factor, y_factor*power_factor)
        self.controller.update(power)
    def __repr__(self):
        return type(self).__name__+"(%s, %s, target=%s, power_function=%s)" % (self.controller, self.screen_size, self.target, self.power_function)
    def apply(self):
        self.controller.apply()

class ObjectTracker(object):
    """Uses OpenCV to track an object within the bounding box and initial frame given. Each update() call takes a new image from a video capture and returns the bounding box of the object. Currently only useful in ObjectNavigator"""
    def __init__(self, initial_frame, bounding_box, accuracy):
        if accuracy == 0:
            self.tracker = cv2.TrackerMOSSE_create()
        elif accuracy == 1:
            self.tracker = cv2.TrackerKCF_create()
        elif accuracy == 2:
            self.tracker = cv2.TrackerCSRT_create()
        else:
            raise ValueError("Accuracy must be 0, 1, or 2.")
        
        self.accuracy = accuracy
        self.bounding_box = bounding_box
        
        assert self.tracker.create(initial_frame, bounding_box)
    def update(self, frame):
        frame = imutils.resize(frame, width=500)
        success, bounding_box = self.tracker.update(frame)
        
        if success:
            return tuple(int(vertex) for vertex in bounding_box)
        else:
            return (0, 0, 0, 0)
    def __repr__(self):
        return type(self).__name__+"(%s, %s, %s)" % (self.frame, self.bounding_box, self.accuracy)

class ObjectNavigator(object):
    """Manages a TargetNavigator and ObjectTracker, combining both functions to follow the center of an object, keeping it at a set position on the screen"""
    def __init__(self, navigator, tracker, video_capture):
        self.navigator = navigator
        self.tracker = tracker
        self.capture = video_capture
    def update(self):
        x, y, w, h = self.tracker.update(self.capture.read())
        center = x+(w/2), y+(h/2)
        self.navigator.update(center)
    def __repr__(self):
        return type(self).__name__+"(%s, %s)" % (self.navigator, self.tracker)
    def apply(self):
        self.navigator.controller.apply()

class RemoteVideoCapture(object):
    """Class to emulate the *basic* behavior of cv2.VideoCapture (the read() method), with a remote video stream from a set ip, port, and encoding (via cv2.imencode/cv2.imdecode)"""
    def __init__(self, other, image_shape):
        height, width, channels = image_shape
        self.max_bytes = height*width*channels
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(other)
    def read(self):
        try:
            return imdecode(self.socket.recvfrom(self.max_bytes), cv2.CV_LOAD_IMAGE_COLOR)
        except:
            return (False, None)
    def __repr__(self):
        return type(self).__name__+"(%s, %s, %s, %s)" % (self.ip_address, self.port, self.image_shape)

class RemoteVideoSender(object):
    """Class to emulate basic behavior of cv2.VideoWriter (the write() method), with a local video stream to send to given an ip, port, and encoding (via cv2.imencode/cv2.imdecode)"""
    def __init__(self, other, encoding=".jpg"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.other = other
        self.encoding = encoding
    def write(self, image):
        data = imencode(image, self.encoding)
        remaining_length = len(data)
        
        while remaining_length > 0:
            remaining_length -= self.socket.sendto(data[len(data)-remaining_length:], self.other)

class LineNavigator(object):
    """Manages a TargetNavigator, combining its functionality with detect_lines to keep a line in the middle of the screen""" # TODO: Remove redundant and unnecessary code and make sure this works properly
    def __init__(self, navigator, tracker, screen_size, video_capture, direction="up"):
        assert direction in ["up", "down", "left", "right"]
        self.navigator = navigator
        self.tracker = tracker
        self.screen_size = screen_size
        self.direction = direction
        self.capture = video_capture
    def update(self):
        lines = detect_lines(self.capture.read())
        max_distance = 0
        m = None
        b = None
        line_parameters = {"x1":0, "y1":0, "x2":0, "y2":0}
        for line in lines:
            x1 = line[0][0]
            y1 = line[0][1]
            x2 = line[0][2]
            y2 = line[0][3]
            distance = sqrt((x2-x1)**2, (y2-y1)**2)
            if distance > max_distance:
                line_parameters["x1"] = x1
                line_parameters["x2"] = x2
                line_parameters["y1"] = y1
                line_parameters["y2"] = y2
        max_distance = distance
        x1, x2, y1, y2 = line_parameters["x1"], line_parameters["x2"], line_parameters["y1"], line_parameters["y2"]
        x_distance = abs(x2-x1)
        y_distance = abs(y2-y1)
        x_sign = -1 if x_distance < 0 else 1
        y_sign = -1 if y_distance < 0 else 1
        if abs(x_distance) >= abs(y_distance):
            x_factor = 1*x_sign
            y_factor = abs(y_distance/x_distance)*y_sign
        else:
            x_factor = abs(x_distance/y_distance)*x_sign
            y_factor = 1*y_sign
        m = y_factor/x_factor
        b = y1-m*x1
        if self.direction == "up":
            target = (screen_size[1]-b)/m, screen_size[1] # The top of the visible line
        elif self.direction == "down":
            target = (screen_size[1]-b)/m, 0 # The bottom of the visible line
        elif self.direction == "left":
            target = 0, m*screen_size[0]+b # The leftmost visible part of the line
        elif self.direction == "right":
            target = screen_size[0], m*screen_size[0]+b # The rightmost visible part of the line
        else:
            raise ValueError("Invalid direction!")
        self.navigator.update(target)
    def __repr__(self):
        return type(self).__name__+"(%s, %s, %s, direction=%s)" % (self.navigator, self.tracker, self.screen_size, self.direction)
    def apply(self):
        self.navigator.controller.apply()

def assemble_motor_objects():
    """Convenience function for creating motor array objects. This is required for save states due to parsing via newlines"""
    global motors, motor_array
    
    if local_motors:
        motors = {pin:GPIOMotor(pin[1], pin_values[pin]) for pin in available_pins}
        
        if local_input:
            motor_array = GPIOMotorArray(motors)
        else:
            motor_array = BaseLocalGPIOMotorArray(other, motors)
    else:
        motor_array = RemoteGPIOMotorArray(other)
        motors = {pin:RemoteGPIOMotor(pin[1], motor_array, pin_values[pin]) for pin in available_pins}

def assemble_controller():
    """Convenience function for creating controller objects. This is required for save states due to parsing via newlines"""
    global controller, camera

    if controller_name in ["Object Navigator", "Line Navigator"]:
        if local_camera:
            camera = cv2.VideoCapture(camera_id)
        else:
            camera = RemoteVideoCapture(other_camera, (640, 480, 3)) # TODO: User input initial camera frame size

    if controller_name == "Hex ROV Controller":
        controller = HexROVController(*[motors.get(pin, AbstractMotor()) for pin in hex_rov_pins.values()], deadzone=deadzone)
    elif controller_name == "Tank Steering Controller":
        controller = TankSteeringController(*[motors.get(pin, AbstractMotor()) for pin in tank_rov_pins.values()], deadzone=deadzone)
    elif controller_name == "Object Navigator":
        if type(controller) == HexROVController:
            controller = ObjectNavigator(TargetNavigator(controller, size), ObjectTracker(camera.read(), (0, 0, 0, 0), 1), camera) # TODO: User input initial bounding box and accuracy
        else:
            controller = ObjectNavigator(TargetNavigator(controller.navigator.controller), ObjectTracker(camera.read(), (0, 0, 0, 0), 1), camera)
    elif controller_name == "Line Navigator":
        controller = LineNavigator() # TODO: Implement
    else:
        raise NotImplementedError("Controller type '%s' not implemented!" % controller_name)

if __name__ == "__main__" and USE_GUI:
    import pygame
    import OpenGL.GL as gl
    from imgui.integrations.pygame import PygameRenderer
    import imgui
    import sys

    def print(*strings):
        global console_text
        console_text += "\n"+" ".join(strings)

    pygame.init()
    size = 1200, 720

    pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.OPENGL|pygame.RESIZABLE)

    pygame.display.set_caption("ROV Testbed")

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size

    local_motors = False
    local_camera = False
    local_input = True

    camera_id = 0

    other = ("localhost", 12345)
    other_camera = ("localhost", 12346)

    available_pins = [(7, 4, False), (11, 17, False), (12, 18, True), (13, 27, False),
                      (15, 22, False), (16, 23, False), (18, 24, False), (22, 25, False),
                      (33, 13, True), (36, 16, False), (37, 26, False)]

    pin_values = {pin:0 for pin in available_pins}

    assemble_motor_objects()

    hex_rov_pins = {"Front Left Motor":None, "Front Right Motor":None, "Back Left Motor":None, "Back Right Motor":None}
    tank_rov_pins = hex_rov_pins.copy()

    controller_input_names = {"Hex ROV Controller":["X", "Y"], "Tank Steering Controller":["Left", "Right"], "Target Navigator":[], "Object Navigator":[], "Line Navigator":[]}
    controller_inputs = {"X":None, "Y":None, "Left":None, "Right":None}
    
    try:
        pygame.joystick.quit()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    except:
        joystick = None
        
    deadzone = 0.2
    rov_type = "Hex ROV"
    controller_name = "Hex ROV Controller"
    assemble_controller()
    
    command = ""
    console_text = sys.version+"\nType \"help\", \"copyright\", \"credits\" or \"license()\" for more information."

    while True:
        joystick_changed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                io.display_size = event.size
            elif event.type in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION]:
                joystick_changed = True
                
            impl.process_event(event)

        outputs = {}
            
        for input_name in controller_input_names[controller_name]:
            if controller_inputs[input_name]:
                if controller_inputs[input_name].startswith("Axis"):
                    outputs[input_name] = float(joystick.get_axis(int(controller_inputs[input_name][5:])))
                elif controller_inputs[input_name].startswith("Button"):
                    outputs[input_name] = int(joystick.get_button(int(controller_inputs[input_name][7:])))
                else:
                    raise NotImplementedError("Unimplemented input type used in '%s'" % controller_inputs[input_name])
            else:
                outputs[input_name] = 0

        if controller_name == "Hex ROV Controller":
            controller.update((outputs["X"], outputs["Y"]))
        elif controller_name == "Tank Steering Controller":
            controller.update((outputs["Left"], outputs["Right"]))
        elif controller_name in ["Object Navigator", "Line Navigator"]:
            raise BaseException(controller_name+str(controller))
            controller.update()
        else:
            raise NotImplementedError("Unimplemented controller type '%s'" % controller_name)

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                clicked, selected = imgui.menu_item("Exit", "Ctrl+Q", False, True)

                if clicked:
                    pygame.quit()
                    sys.exit()

                clicked, selected = imgui.menu_item("Load Local State File", "", False, True)

                if clicked:
                    try:
                        config_file = open("rov_testbed_state.txt", mode="r")
                        for line in config_file.read().split("\n"):
                            exec(line)
                            print(line)
                        config_file.close()
                    except FileNotFoundError:
                        pass

                clicked, selected = imgui.menu_item("Save Local State File", "", False, True)

                if clicked:
                    try:
                        config_file = open("rov_testbed_state.txt", mode="w")
                        output_string = ""
                        
                        for item in ["local_motors", "other", "available_pins", "hex_rov_pins", "tank_rov_pins", "deadzone", "rov_type", "pin_values", "controller_inputs", "controller_name", "local_input", "local_camera"]:
                            output_string += item+" = "+repr(globals()[item])+"\n"

                        output_string += "assemble_motor_objects()\nassemble_controller()"

                        config_file.write(output_string)
                        config_file.close()
                    except FileNotFoundError:
                        pass

                clicked, selected = imgui.menu_item("Reset Current State", "", False, True)

                if clicked:
                    local_motors = False

                    other = ("localhost", 12345)

                    available_pins = [(7, 4, False), (11, 17, False), (12, 18, True), (13, 27, False),
                                      (15, 22, False), (16, 23, False), (18, 24, False), (22, 25, False),
                                      (33, 13, True), (36, 16, False), (37, 26, False)]

                    pin_values = {pin:0 for pin in available_pins}

                    assemble_motor_objects()

                    hex_rov_pins = {"Front Left Motor":None, "Front Right Motor":None, "Back Left Motor":None, "Back Right Motor":None}
                    tank_rov_pins = hex_rov_pins.copy()

                    controller_inputs = {"X":None, "Y":None, "Left":None, "Right":None}

                    deadzone = 0.2
                    rov_type = "Hex ROV"

                    assemble_controller()

                imgui.end_menu()
            if imgui.begin_menu("Joystick"):
                clicked, selected = imgui.menu_item("Connect Joystick", "", False, True)

                if clicked:
                    try:
                        pygame.joystick.quit()
                        pygame.joystick.init()
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                    except:
                        joystick = None

                imgui.end_menu()
            if imgui.begin_menu("ROV Type"):
                for selected_rov_type in ["Hex ROV", "Tank Steering ROV"]:
                    clicked, selected = imgui.menu_item(selected_rov_type, "", rov_type == selected_rov_type)

                    if clicked:
                        rov_type = selected_rov_type
                imgui.end_menu()
            if imgui.begin_menu("Controller Type"):
                for controller_type in ["Hex ROV Controller", "Tank Steering Controller", "Target Navigator", "Object Navigator", "Line Navigator"]:
                    clicked, selected = imgui.menu_item(controller_type, "", controller_name == controller_type)

                    if clicked:
                        controller_name = controller_type
                        assemble_controller()

                imgui.end_menu()
            imgui.end_main_menu_bar()

        #imgui.show_demo_window()

        imgui.begin("Available GPIO Pins")
        
        for pin in available_pins:
            if pin[2]:
                imgui.selectable("GPIO #"+str(pin[0])+", BCM #"+str(pin[1])+" (Hardware PWM)")
            else:
                imgui.selectable("GPIO #"+str(pin[0])+", BCM #"+str(pin[1]))
                
            if imgui.begin_drag_drop_source():
                imgui.set_drag_drop_payload("pin", str(pin).encode())
                if pin[2]:
                    imgui.text("GPIO #"+str(pin[0])+", BCM #"+str(pin[1])+" (Hardware PWM)")
                else:
                    imgui.text("GPIO #"+str(pin[0])+", BCM #"+str(pin[1]))
                imgui.end_drag_drop_source()

        imgui.end()

        imgui.begin("GPIO Pin Values")
        
        for pin in available_pins:
            if pin[2]:
                changed, new_value = imgui.slider_float("GPIO #"+str(pin[0])+", BCM #"+str(pin[1])+" (Hardware PWM)", motors[pin].speed, -1, 1)
            else:
                changed, new_value = imgui.slider_float("GPIO #"+str(pin[0])+", BCM #"+str(pin[1]), motors[pin].speed, -1, 1)
                
            if changed and abs(new_value) > deadzone:
                motors[pin].speed = new_value
                pin_values[pin] = new_value
            elif changed:
                motors[pin].speed = 0
                pin_values[pin] = 0

        imgui.end()

        imgui.begin(rov_type)

        if rov_type == "Hex ROV":
            rov_pins = hex_rov_pins
        elif rov_type == "Tank Steering ROV":
            rov_pins = tank_rov_pins
        else:
            print(rov_type)
            raise ValueError

        changed1, local_input = imgui.checkbox("Local Input", local_input)
        changed2, local_motors = imgui.checkbox("Local Motors", (not local_input) or local_motors)
        changed3, local_camera = imgui.checkbox("Local Camera", local_camera)

        if any([changed1, changed2, changed3]):
            assemble_motor_objects()
            assemble_controller()

        changed = False
        
        for motor in ["Front Left Motor", "Front Right Motor", "Back Left Motor", "Back Right Motor"]:
            if imgui.button("Clear "+motor[0]+motor.split(" ")[1][0]):
                rov_pins[motor] = None
                changed = True

            imgui.same_line()

            if rov_pins[motor]:
                if rov_pins[motor][2]:
                    imgui.text(motor+": GPIO #"+str(rov_pins[motor][0])+", BCM #"+str(rov_pins[motor][1])+" (Hardware PWM)")
                else:
                    imgui.text(motor+": GPIO #"+str(rov_pins[motor][0])+", BCM #"+str(rov_pins[motor][1]))
                    
                if imgui.begin_drag_drop_target():
                    data = imgui.accept_drag_drop_payload("pin")
                    
                    if data:
                        rov_pins[motor] = literal_eval(data.decode())
                        changed = True
                        
                    imgui.end_drag_drop_target()
            else:
                imgui.text(motor+": No assigned pin")
                
                if imgui.begin_drag_drop_target():
                    data = imgui.accept_drag_drop_payload("pin")
                    
                    if data:
                        rov_pins[motor] = literal_eval(data.decode())
                        changed = True
                        
                    imgui.end_drag_drop_target()

        if changed:
            assemble_controller()
                    
        imgui.end()

        imgui.begin(controller_name)

        for controller_input in controller_input_names[controller_name]:
            if imgui.button("Clear "+controller_input[0]):
                controller_inputs[controller_input] = None

            imgui.same_line()

            if controller_inputs[controller_input] is not None:
                imgui.text(controller_input+": "+controller_inputs[controller_input])
                    
                if imgui.begin_drag_drop_target():
                    data = imgui.accept_drag_drop_payload("input")
                    
                    if data:
                        controller_inputs[controller_input] = data.decode()
                        
                    imgui.end_drag_drop_target()
            else:
                imgui.text(controller_input+": No assigned input")
                
                if imgui.begin_drag_drop_target():
                    data = imgui.accept_drag_drop_payload("input")
                    
                    if data:
                        controller_inputs[controller_input] = data.decode()
                        
                    imgui.end_drag_drop_target()

        imgui.end()

        imgui.begin("Joystick Input")
        imgui.text("Joystick connected" if joystick else "Joystick not connected")
        
        if joystick:
            for axis in range(joystick.get_numaxes()):
                value = joystick.get_axis(axis)
                imgui.selectable("Axis %s: %s" % (axis, round(value, 3)))

                if imgui.begin_drag_drop_source():
                    imgui.set_drag_drop_payload("input", ("Axis "+str(axis)).encode())
                    imgui.text("Axis %s: %s " % (axis, round(value, 3)))
                    imgui.end_drag_drop_source()
                    
            for button in range(joystick.get_numbuttons()):
                value = joystick.get_button(button)
                imgui.selectable("Button %s: %s" % (button, value))

                if imgui.begin_drag_drop_source():
                    imgui.set_drag_drop_payload("input", ("Button "+str(button)).encode())
                    imgui.text("Button %s: %s" % (button, value))
                    imgui.end_drag_drop_source()
            
        imgui.end()

        if local_motors:
            imgui.begin("Motor server IP address and port")

            changed, ip_address = imgui.input_text("IP address", other[0], 512)

            if changed:
                other = (ip_address, other[1])
            
            changed, port = imgui.input_int("Port", other[1])

            if changed:
                other = (other[0], port)
        else:
            imgui.begin("Motor client IP address and port")

            changed, ip_address = imgui.input_text("IP address", other[0], 512)

            if changed:
                other = (ip_address, other[1])
            
            changed, port = imgui.input_int("Port", other[1])

            if changed:
                other = (other[0], port)

        if imgui.button("Apply"):
            assemble_motor_objects()
            assemble_controller()

        imgui.end()

        if local_camera:
            imgui.begin("Camera server IP address and port")

            changed, ip_address = imgui.input_text("IP address", other_camera[0], 512)

            if changed:
                other_camera = (ip_address, other[1])
            
            changed, port = imgui.input_int("Port", other_camera[1])

            if changed:
                other_camera = (other_camera[0], port)

            changed, camera_id = imgui.input_int("Camera ID", camera_id)
        else:
            imgui.begin("Camera client IP address and port")

            changed, ip_address = imgui.input_text("IP address", other_camera[0], 512)

            if changed:
                other = (ip_address, other_camera[1])
            
            changed, port = imgui.input_int("Port", other_camera[1])

            if changed:
                other = (other_camera[0], port)

        if imgui.button("Apply"):
            assemble_motor_objects()
            assemble_controller()

        if not (local_motors and local_input):
            controller.apply()

        imgui.end()

        imgui.begin("Console")

        imgui.text(console_text)

        entered, command = imgui.input_text("Command", command, 512, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        
        if entered:
            try:
                output = eval(command)
                if output is not None:
                    console_text += "\n"+str(output)
            except BaseException as error:
                try:
                    exec(command)
                except BaseException as error2:
                    console_text += "\nError while attempting to evaluate expression: %s\nError while attempting to execute input as code: %s" % (error, error2)
                    
            command = ""

        imgui.end()

        gl.glClearColor(0.5, 0.5, 0.5, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()

# TODO: Test remote motor connectivity support
# TODO: Finish implementing servos (gui support and remote control)
# TODO: Add adafruit motor library support on the Pi version
# TODO: Add default constants for some *very* commonly set values (irrespective of config files, would need actual examples of this to implement properly)
# TODO: Finish implementing all ROV Controllers into the gui
# TODO: Somehow change stuff so that .apply isn't an assumed functional property of all controllers
# TODO: Rewrite controller manager handling code so that they're handled like managers and not special controllers
