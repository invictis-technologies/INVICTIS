from VITA_PRINTER import VITA # Controls the device and the camera
import imageProcessor as imgProc # Runs the vein finding
from exceptions import OutofBoundsError # Custom-defined exceptions module
from exceptions import InvalidResponseError # Custom-defined exceptions module
import sys # Used to cmd line arguments
from time import sleep # used to signal catastrophic failure
    
# TODO: Make the currently unrecoverable errors that terminate the program recoverable
# TODO: implement DEMO mode with live viewing
# TODO: implement inVeins() force sensing

'''
 Finds veins and presents their location.
 It takes in a string filename and a VITA object device,
 and returns x and y as distances.
'''
def veinImaging(filename, device):
    # Is the sensor connected?
    try:
        height = device.getDistance()
    except IOError:
        closeProgram(device)
    else:
        device.capture(filename)
        # is the image readable?
        try:
            imgProc.isValidImg(filename)
        except ValueError:
            closeProgram(device)
        else:
            img = imgProc.preprocess(filename)

            x,y = imgProc.getVeins(img, height)

            return x, y

def inVeins(force, distanceDown):
        return None

'''
 Takes in a Vita object and 
 finalizes the state of the program for a safe
 shutdown and release of all resources. 
'''
def closeProgram(device):
    imgProc.closeWindows()
    device.terminate()
    raise SystemExit(0)

'''
 Parses the command line options to set a string filename and activate
 demo mode with th '-D' option which shows the images. By default, if no 
 options are given demo mode is off and the images are saved to veins.png 
 in the current directory. Returns the string filename and boolean DEMO
'''
def getOptions():
    DEMO = False
    filename = 'veins'
    if sys.argv[1] == '-D':
        DEMO = True
    if len(sys.argv) >= 3:
        filename = sys.argv[2]
    return filename, DEMO



def main():
    deviceConnection = '/dev/ttyUSB0'
    sensorConnection = '/dev/ttyUSB1'
    filename, DEMO = getOptions() # need to implement demo mode
    baud = 250000

    ## setup
    device = VITA(deviceConnection, baud, sensorConnection)

    try:
        device.awaitVeins()
    except:
        closeProgram(device)

    ## vein finding
    x, y = veinImaging(filename, device)
    SPEED = 2500 # mm/min
    while (x != 0 and y != 0):
        x, y = veinImaging(filename, device)
        try:
            device.move(x, y, SPEED)
        except:
            closeProgram(device)

    ## injection
    R = 0; G = 0; B = 255 # Blue
    device.statusLED(R,G,B)

    force = device.getForce()
    if (force == -1): # check that the force sensor is functioning
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
        distanceDown = device.getDistance

        while(not inVeins(force, distanceDown)):
            force = device.getForce()
            distanceDown = device.getDistance
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