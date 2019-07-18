import serial
import time
from nanpy import SerialManager
from nanpy import ArduinoApi

# TODO: Actually test code on arduino and fix bugs that arise there
# TODO: Implement reset/go button and tricolor status led

class ARDUINO():
    def __init__(self, serialConnection):
        # string used to specify which serial connection is controlling the arduino
        self.serialConnection = serialConnection 
        self.statusLed(0, 0, 0)

    '''
    Queries pin 7 and 8 on an Arduino for an HC-SR04 ultrasonic distance 
    monitor and returns the distance to an object from that monitor in mm.
    If no arduino is found, the function will pass and return -1. 
    while printing an error message to stdOut. The function
    does not check that the sensor is connected. Pass it the string
    serialConnection (example '/dev/ttyACM0')
    '''
    def getDistance(self):
        # Distance sensor pins (physically labelled on ARDUINO)
        ECHO_PIN = 7
        TRIG_PIN = 8

        connected, a = self.connect(self)
        if(connected):
            # Initialize the arduino pins
            a.pinMode(TRIG_PIN, a.OUTPUT)
            a.pinMode(ECHO_PIN, a.INPUT)
        
            # The sensor is triggered by a HIGH pulse of 10 or more microseconds.
            # Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
            a.digitalWrite(TRIG_PIN, a.LOW)
            a.delayMicroseconds(5)
            a.digitalWrite(TRIG_PIN, a.HIGH)
            a.delayMicroseconds(10)
            a.digitalWrite(TRIG_PIN, a.LOW)

            # Read the signal from the sensor: a HIGH pulse whose
            # duration is the time (in microseconds) from the sending
            # of the ping to the reception of its echo off of an object.
            a.pinMode(ECHO_PIN, a.INPUT)
            duration = a.pulseIn(ECHO_PIN, a.HIGH)

            #Conversion rate brought to you by the speed of sound
            mm = (duration*.343)/2
            return mm
        else:
            return -1

    '''
    Queries pins A2 and A4 and takes the difference to 
    catch the force data being returned by the force sensor shown in the
    link below. Takes in a string serialConnection
    such as '/dev/ttyACM0'. Returns the difference if possible or
    zero if the connection failed. The force is then a ratio of 
    the difference with the inputted voltage.
    '''
    def getForce(self): 
        # properly set arduino pins to known names
        A2 = 16
        A4 = 18

        # https://www.mouser.com/datasheet/2/187/honeywell-sensing-force-sensors-FSG-product-sheet--1132419.pdf
        connected, a = self.connect(self)
        if(connected):
            # Initialize the arduino pins to read
            pos = a.analogRead(A2)
            neg = a.analogRead(A4)

            diff = pos - neg
        else:
            diff = 0

        return diff

    # Runs an infinite loop waiting for a button press  on pin 3 
    # to break the loop.
    # Takes in nothing returns nothing but will raise an IOerror if
    # the connection can not be made
    def buttonPress(self):
        buttonPin = 3

        connected, a = self.connect(self)
        if (connected):
            while(a.digitalRead(buttonPin) == a.HIGH):
                pass
        else:
            print("Hardware not connected to sensor module")
            raise IOError

    # Sets a tricolor status led. 
    # Values must be within 0 and 255
    def statusLed(self, R, G, B):
        redPin= 11
        greenPin = 10
        bluePin = 9

        # Enforce value boundaries
        if R > 255: R = 255
        else: 
            if R < 0: R = 0
        if G > 255: G = 255
        else: 
            if G < 0: R = 0
        if B > 255: B = 255
        else: 
            if B < 0: R = 0

        connected, a = self.connect(self)
        if (connected):
            a.analogWrite(redPin, R)
            a.analogWrite(greenPin, G)
            a.analogWrite(bluePin, B)
        else:
            print("Hardware not connected to sensor module")
            raise IOError    

    '''
     A static method to connect to an Arduino. Pass it a string serialConnection
     with such as '/dev/ttyACM0'. Returns False if connection is 
     not possible and True if it is.
    ''' 
    @staticmethod
    def connect(self):
        try:
            # Set up serial connection
            connection = SerialManager(device = serialConnection)
            a = ArduinoApi(connection = connection)
            return True, a
        except:
            print("The Arduino is currently not connected to port: " + self.serialConnection)
            return False, None
