from time import sleep
from irCamera import irCamera
import serial
import imageProcessor as imgProc

# TODO: figure out the bounds for the move function

class VITA():
    def __init__(self, serialConnection, baud):
        # creates a camera object optimized for IR
        self.camera = irCamera() 
        # initializes a serial connection along the path specified
        self.ser = serial.Serial(serialConnection) 
        # sets the communication rate for the serial port with the device.
        self.ser.baudrate = baud

    # Wrapper method to write data to the serial port
    # Data must be of the form "G28 X Y\r\n" where the gcode 
    # and the x, y values may be changed. Returns nothing.
    def write(self, data):
        command = bytes(data, encoding = "ascii")
        self.ser.write(command)

    # Send move command (G1 X Y Z F) code to printer. Send default 0 for inputs
    # X Y Z are distances in mm to move and F is a speed in mm/min. If the printer
    # cannot move that distance a kill command is sent and a message is printed to
    # stdout. Returns nothing
    def move(self, x, y, z, f):
        #to change in future
        xBound = 100
        yBound = 100
        zBound = 10

        if abs(x) <= xBound or abs(y) <= yBound or abs(z) <= zBound:
            cmdRelative = "G91 \r\n"
            cmdMove = "G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(f) + "\r\n"
            self.write(cmdRelative)
            self.isOk()
            sleep(0.2)
            self.write(cmdMove)
            self.isOk()
            sleep((max([abs(x), abs(y), abs(z)])*60*1/f*1.2))
        else:
            print("The attempted movement was out of bounds.")
            self.terminate()

    # Checks the printer status. Should be run after each printer write command.
    # Takes in nothing and returns nothing. Prints messages to stdOut if errors 
    # are found.
    def isOk(self):
        if self.ser.is_open():
            response = self.ser.readline()
            print(response)
            if response == b"ok\n":
                return True
            print("printer error. things not okay! t('_'t)")
        else:
            print("serial port /dev/ttyUSB0 not open")
        self.terminate()

    # Ends the program and cleans up utilized resources.
    # Takes nothing and returns nothing
    def terminate(self):
        self.camera.stop_preview()
        self.camera.close()
        imgProc.closeWindows()
        self.ser.close()
        exit()

    # Wrapper class that takes photos using an attached camera
    # and saves them to the a filename at string filename. Returns nothing
    def capture(self, filename):
        try:
            self.camera.capture(filename)
        except:
            print("The image capture failed.")
            self.terminate()

    # Physically device bed the printer for use.
    # Takes nothing and returns nothing
    def initialize(self):
        # reset x and y with a homing command
        self.write("G28 X Y\r\n")
        sleep(5)
        self.isOk()

        # center platform
        self.move(110, 60, 0, 2500)

        
