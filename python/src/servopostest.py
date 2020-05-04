from gpiozero import Servo
from time import sleep
import math

correction=0.5
maxPW=(2.0+correction)/1000
minPW=(1.0-correction)/1000

servo = Servo(23, min_pulse_width=minPW, max_pulse_width=maxPW)

angleNum = 0
servoPos = 0

while True:

    angle = input ('Angle Num:')
    angleNum = (float(angle))

    if (angleNum > 90):
        print("Please input a number below 90 degrees.")
    if (angleNum < -90):
        print("Please input a number above -90 degrees.")
    if (angleNum >= -90 and angleNum <= 90):
        servoPos = angleNum/90
        print("Setting servo to ", angleNum, " degrees...")
        servo.value = servoPos    
