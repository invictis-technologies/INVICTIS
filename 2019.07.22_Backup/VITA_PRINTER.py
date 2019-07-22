from time import sleep # Allows use of sleep command
from irCamera import irCamera # Manipulates camera object
from pi2uno_v2 import ARDUINO # Controls the sensor array
from exceptions import OutofBoundsError # Custom-defined exceptions module
from exceptions import InvalidResponseError # Custom-defined exceptions module
from multiprocessing import Process # used to move the printer down
import raspiGPIO as gpio
import serial


# TODO: figure out the bounds for the move function

class VITA():
    def __init__(self, serialConnection, baud, sensorConnection):
        # creates a camera object optimized for IR
        self.camera = irCamera() 
        # initializes a serial connection along the path specified
        self.ser = serial.Serial(serialConnection) 
        # sets the communication rate for the serial port with the device.
        self.ser.baudrate = baud
        # creates a communication link with the arduino
        self.sensor = ARDUINO(sensorConnection)
        # Used for error handling
        self.serialConnection = serialConnection
        # Private attribute to maintain height
        self.__initialHeight = -1

    # Wrapper method to write data to the serial port
    # Data must be of the form "G28 X Y\r\n" where the gcode 
    # and the x, y values may be changed. Returns nothing.
    def write(self, data):
        command = bytes(data, encoding = "ascii")
        self.ser.write(command)

    # Send move command (G1 X Y 0 F) code to printer. Send default 0 for inputs
    # X Y Z are distances in mm to move and F is a speed in mm/min. If the printer
    # cannot move that distance a kill command is sent and a message is printed to
    # stdout. Returns nothing. Z is handled outside the printer's control board so the 
    # distances will not exactly match the inputted distances. 
    def move(self, x, y, z, f):
        #to change in future
        XBOUND = 100
        YBOUND = 100
        FBOUND = 2500

        # if it's in the bounds and not a Z cmd use gcode
        if abs(x) <= XBOUND and abs(y) <= YBOUND and  f <= FBOUND :
            cmdRelative = "G91 \r\n"
            cmdMove = "G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(f) + "\r\n"
            self.write(cmdRelative)
            
            # await printer feedback
            try: 
                self.isOk()
            except: 
                raise
            
            sleep(0.2)
            self.write(cmdMove)
            
            # await printer feedback
            try: 
                self.isOk()
            except: 
                raise
            
            # wait for the motors to move
            sleep((max([abs(x), abs(y), abs(z)])*60*1/f*1.2))
        else:
            raise OutofBoundsError("The attempted movement was out of bounds.")
        
        # if it's a Z cmd control it directly
        if z > 0:
            self.ascend(f)
        else: 
            if z < 0:
                self.descend(f)
                

    # Checks the printer status. Should be run after each printer write command.
    # Takes in nothing and returns nothing. Prints messages to stdOut if errors 
    # are found.
    def isOk(self):
        if self.ser.is_open():
            response = self.ser.readline()
            if response == b"ok\n":
                return
            raise InvalidResponseError("Unexpected response from device. Received: " + response)
        else:
            raise ConnectionError("Serial port is not available. Tried to connect to: " + self.serialConnection)

    # Ends the program and cleans up utilized resources.
    # Takes nothing and returns nothing
    def terminate(self):
        self.camera.stop_preview()
        self.camera.close()
        self.ser.close()
        
        R = 255; G = 0; B = 0 # Red
        self.sensor.statusLED(R,G,B)

    # Wrapper class that takes photos using an attached camera
    # and saves them to the a filename at string filename. Returns nothing
    def capture(self, filename):
        self.camera.capture(filename)

    # Physically center the device bed of the printer for use.
    # Takes nothing and returns nothing
    def initialize(self):
        # reset x and y with a homing command
        self.write("G28 X Y\r\n")
        sleep(5)
        try:
            self.isOk()
        except:
            raise
        else:
            # platform to center
            self.move(110, 60, 0, 2500)


    # Takes in a string sensorConnection and a Vita object 
    # and initializes the device to begin imaging. The system 
    # will raise an IOError and terminate the program if 
    # the connection can not be made.
    def awaitVeins(self):
        R = 0; G = 255; B = 0 # Green
        try:
            self.statusLED(R,G,B)
            
            self.initialize()
            self.waitForButtonPress() # Will loop infinitely until button is pressed

            R = 255; G = 255; B = 0 # Yellow
            self.statusLED(R,G,B)
        except:
            raise 
    
    
    # Removes the needle back to the home position.
    # Returns nothing. 
    def retractNeedle(self):
        SPEED = 2500 #DO NOT CHANGE
        try:
            self.ascend(SPEED)
        except: # non-recoverable error goes into infinite emergency state
            print("Catastrophic Failure: Device in unknown state. PROGRAMMATIC RETRACTION IS IMPOSSIBLE.")
            while True:
                R = 255; G = 255; B = 0 # Yellow
                self.statusLED(R,G,B)
                sleep(0.5)
                R = 255; G = 0; B = 0 # Red
                self.statusLED(R,G,B)
                sleep(0.5)

    # Moves the sensor array and needle housing down at a constant speed
    # Takes in a numerical value speed and returns a Process object movedown.
    # The user is responsible for cleaning up the Process object with the stopZ
    # command. In the current iteration, speed does not affect performance
    def descend(self, speed):
        if self.__initialHeight == -1:
            self.__initialHeight = self.getDistance()

        try:
            # spawns the movement as a new process
            moveDown = multiprocessing.Process(target=gpio.moveDown, args=(speed))
            moveDown.start()
            return moveDown
        except:
            self.stopZ(moveDown)
            raise

    # Moves the sensor array and needle housing up at a constant speed
    # Takes in a numerical value speed and returns nothing.
    # In the current iteration, speed does not affect performance
    def ascend(self, speed):
        if self.__initialHeight == -1:
            return

        try:
            # spawns the movement as a new process
            moveUp = multiprocessing.Process(target=gpio.moveUp, args=(speed))
            moveUp.start()
        except:
            self.stopZ(moveUp)
            raise
        else:
            # is the device at the original height yet?
            currentHeight = self.getDistance()
            while currentHeight < self.__initialHeight:
                currentHeight = self.getDistance()
            self.stopZ(moveUp)

    # Takes in a process object and kills it then cleans up 
    # the attributed resources. Returns nothing. In the event of an emergency 
    # due to unresponsiveness, this function can result in a SystemExit 
    # with exit code 1 which will not return.
    def stopZ(self, moveCommand):
        try:
            moveCommand.terminate()
        except: 
            moveCommand.kill()
        finally:
            gpio.enableMotor(False)
            gpio.closeGPIO()
            if(moveCommand.is_alive()):
                self.terminate()
                SystemExit(1)
            moveCommand.join()

    # Sets the status LED where R,G, and B are values 
    # between 0 and 255. Returns nothing
    def statusLED(self, R,G,B):
        self.sensor.statusLED(R,G,B)

    # Waits to recieve a button press before advancing to the next cmd.
    # Takes in nothing and returns nothing
    def waitForButtonPress(self):
        self.sensor.waitForButtonPress() # Will loop infinitely until button is pressed

    # Queries the attached distance sensor to get the height above the arm
    # takes in nothing and returns a numerical value height if possible
    def getDistance(self):
        try:
            height = self.sensor.getDistance()
            return height
        except:
            raise
    
    # Queries the attached force sensor to get the force feedback from the arm
    # takes in nothing and returns a numerical value force which will be a ratio
    # between 5V and the force measured.
    def getForce(self):
        force = self.getForce()
        return force
