import pygame
from time import sleep

pygame.init()
display = pygame.display.set_mode((100, 100))
joystick = pygame.joystick.Joystick(0)
joystick.init()
i = joystick.get_name()

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


while True:
    debugJoystick()
    sleep(1)
