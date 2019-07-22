"""
A module used to control the Pololu A4983 stepper motor controller
programatically from a raspberry pi. See:
https://www.pololu.com/file/0J199/a4983_DMOS_microstepping_driver_with_translator.pdf
for details.

The raspberry pi pinout is as follows in the format gpioNum(pinNum)

PWM Step Pin: 19(35)
enable Pin: 20(38)
direction Pin: 21(40)
"""

import RPi.GPIO as IO # controls the gpio pins on the pi

# TODO: figure out how to implement speed and height controls probably do speed here and height in VITA
# TODO: Comment everything


# Sends a cmd through the IO pins to change
# the vertical position of the arm. In this
# case the arm moves upward. Takes in a speed
# and returns nothing. Though a numerical value
# is brought in for speed, in the current iteration 
# speed control has not been implemented.
def moveUp(speed):
    directionPin = 21

    motorOn()

    IO.setup(directionPin, IO.OUT)
    IO.output(directionPin, IO.LOW) # Low is clockwise

# Sends a cmd through the IO pins to change
# the vertical position of the arm. In this
# case the arm moves downward. Takes in a speed
# and returns nothing. Though a numerical value
# is brought in for speed, in the current iteration 
# speed control has not been implemented.
def moveDown(speed):
    directionPin = 21

    motorOn()

    IO.setup(directionPin, IO.OUT)
    IO.output(directionPin, IO.HIGH) # High is counter clockwise

# Cleans up the resources associated with using the rpi
# gpio pins. Takes in nothing and returns nothing.
# the client is responsible for calling this after use.
def closeGPIO():
    IO.cleanup()

# Turns the motors on or off if the moveup or movedown 
# cmd has already been called. The behvior is undefined 
# otherwise. Takes in a boolean turnOnMotor which enables 
# the motors while true and disables them while false.
def enableMotor(turnOnMotor):
    enablePin = 20

    if(turnOnMotor == True):
        output = IO.LOW # Enable pin must be low to operate
    else:
        output = IO.HIGH

    IO.setup(enablePin, IO.OUT)
    IO.output(enablePin, output)


# Static helper method that controls the step signal sent to the
# motor controller and sets up the pins for use. Takes in nothing
# and returns nothing.
@staticmethod
def motorOn():
    pwmPin  = 19

    frequency = 122 # frequency of PWM signal in hz
    dutyCycle = 50 # duty cycle of pwm

    IO.setwarnings(False) # ignore io warnings
    IO.setmode(IO.BCM)  # set pin numbering system

    IO.setup(pwmPin,IO.OUT) 

    p = IO.PWM(pwmPin, frequency) 

    enableMotor(True)
    p.start(dutyCycle)