from VITA_PRINTER import VITA # Controls the device and the camera
import imageProcessor as imgProc # Runs the vein finding
from exceptions import OutofBoundsError # Custom-defined exceptions module
from exceptions import InvalidResponseError # Custom-defined exceptions module
import sys # Used to cmd line arguments
from time import sleep # used to signal catastrophic failure
import pygame # used to run the click demo function
import subprocess


refpt = []
isClick = False

'''
 Takes in a Vita object and 
 finalizes the state of the program for a safe
 shutdown and release of all resources.
''' 
def closeProgram(device):
    imgProc.closeWindows()
    device.terminate()
    raise SystemExit(0)


def boxMove(device, SPEED):
    height = device.getDistance()
    print("The sensor is " + height + "mm above.")
    device.move(0, 100, SPEED)
    height = device.getDistance()
    print("The sensor is " + height + "mm above.")
    device.move(100, 0, SPEED)
    height = device.getDistance()
    print("The sensor is " + height + "mm above.")
    device.move(0, -90, SPEED)
    height = device.getDistance()
    print("The sensor is " + height + "mm above.")
    device.move(-90, 0, SPEED)

def click(device, SPEED):
    global isClick
    global refpt
    device.start_preview()
    counter = 0
    filetype = (".jpeg")
    num_im_limit = 60
    height = device.getDistance()
    pix2mm = -0.1987*height+50.2399 
    while True:
        try:
            if counter > num_im_limit:
                subprocess.run("rm -f temp*", shell = True)
                counter = 0
            filename = "temp" + str(counter) + filetype
            counter = counter + 1
            device.capture(filename)
            try:
                imgProc.isValidImg(filename)
            except ValueError:
                closeProgram(device)
            else:
                blur = imgProc.preprocess(filename)
                imgProc.click_DEBUG(blur, getMouseCoords)
                if isClick:
                    isClick = False
                    (x, y) = refpt[0]
                    print("("+ str(x) + " + " + str(y) + ")")
                    x_dist = (y - 150)/pix2mm
                    y_dist = (x - 200)/pix2mm
                    print("moving " + str(x_dist) + " " + str(y_dist))
                    device.move(x_dist, y_dist, SPEED)
                sleep(0.1)
        except KeyboardInterrupt:
            return

def getMouseCoords(event, x, y, flags, param):
    if event == pygame.MOUSEBUTTONDOWN:
        global isClick
        global refpt
        isClick = True
        refpt = [(x,y)]

def main():
    deviceConnection = '/dev/ttyUSB0'
    sensorConnection = '/dev/ttyUSB1'
    baud = 250000
    SPEED = 2500 # mm/min

    ## setup
    device = VITA(deviceConnection, baud, sensorConnection)

    try:
        device.awaitVeins()
    except:
        closeProgram(device)

    boxMove(device, SPEED)

    click(device, SPEED)

    closeProgram(device)

    ## injection
    R = 0; G = 0; B = 255 # Blue
    device.statusLED(R,G,B)

    initForce = device.getForce()
    if (initForce == -1): # check that the force sensor is functioning
        print("Force sensor not connected. Injection Failed")
        closeProgram(device)
    else:
        try:
            moveCMD = device.descend(SPEED)
        except:
            device.stopZ(moveCMD)
            device.retractNeedle()
            closeProgram(device)

        force = device.getForce()
        height = device.getDistance

        while(initForce > force and height < 60 or pygame.MOUSEBUTTONDOWN):
            force = device.getForce()
            height = device.getDistance
            if (force == -1): # check that the force sensor is functioning
                print("Force sensor not connected. Injection Failed")
                device.stopZ(moveCMD)
                device.retractNeedle()
                closeProgram(device)
        else:
            device.stopZ(moveCMD)
        
        device.waitForButtonPress() # will loop infinitely until button is pressed

        ## retraction
        device.retractNeedle()
        closeProgram(device)
    
if __name__ == "__main__":
    main()