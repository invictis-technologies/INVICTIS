from VITA_PRINTER import VITA # Controls the device and the camera
import imageProcessor as imgProc # Runs the vein finding
from pi2uno_v2 import ARDUINO # Controls the sensor array
from exceptions import OutofBoundsError # Custom-defined exceptions module
from exceptions import InvalidResponseError # Custom-defined exceptions module
import sys # Used to activate demo mode
from time import sleep # used to signal catastrophic failure
    
# TODO: Make the currently unrecoverable errors that terminate the program recoverable
# TODO: implement DEMO mode with live viewing
# TODO: implement inVeins() force sensing

# Removes the needle back to the home position.
# takes in a VITA object device, an ARDUINO object sensor,
# and a numerical distanceDown and returns nothing. 
def retractNeedle(device, sensor, distanceDown):
    EMERGENCY_REMOVAL = 1
    SPEED = 2500 #DO NOT CHANGE
    z = 0

    try:
        device.move(0, 0, distanceDown, SPEED)
    except OutofBoundsError: # Recoverable error
        print("Extraction Failed. Beginning emergency removal.")
        while z < distanceDown:
            try:
                device.move(0,0,EMERGENCY_REMOVAL, SPEED)
                z += 1
            except: # non-recoverable error goes into infinite emergency state
                while True:
                    print("Catastrophic Failure: Device in unknown state. PROGRAMMATIC RETRACTION IS IMPOSSIBLE.")
                    R = 255; G = 255; B = 0 # Yellow
                    sensor.statusLED(R,G,B)
                    sleep(0.5)
                    R = 255; G = 0; B = 0 # Red
                    sensor.statusLED(R,G,B)
                    sleep(0.5)

    except: # non-recoverable error goes into infinite emergency state
        while True:
            print("Catastrophic Failure: Device in unknown state. PROGRAMMATIC RETRACTION IS IMPOSSIBLE.")
            R = 255; G = 255; B = 0 # Yellow
            sensor.statusLED(R,G,B)
            sleep(0.5)
            R = 255; G = 0; B = 0 # Red
            sensor.statusLED(R,G,B)
            sleep(0.5)
    finally:
        closeProgram(device, sensor)


# Finds veins and presents their location.
# It takes in a string filename, a VITA object device,
# and a ARDUINO object sensor and returns x and y as distances.
def veinImaging(filename, device, sensor):
    # Is the sensor connected?
    try:
        height = sensor.getDistance()
    except IOError:
        closeProgram(device, sensor)
    else:
        device.capture(filename)
        # is the image readable?
        try:
            imgProc.isValidImg(filename)
        except ValueError:
            closeProgram(device, sensor)
        else:
            imgProc.preprocess(filename)

            x,y = imgProc.getVeins(filename, height)

            return x, y

# Takes in a string sensorConnection and a Vita object 
# and initializes the device to begin imaging. The system 
# will raise an IOError and terminate the program if 
# the connection can not be made.
def awaitVeins(sensorConnection, device):
    R = 0; G = 255; B = 0 # Green

    sensor = ARDUINO(sensorConnection)

    try:
        sensor.statusLED(R,G,B)
        
        device.initialize()
        sensor.waitForButtonPress() # Will loop infinitely until button is pressed

        R = 255; G = 255; B = 0 # Yellow
        sensor.statusLED(R,G,B)
        return sensor
    except:
        closeProgram(device, sensor)

# Takes in a Vita object and an arduino object and 
# finalizes the state of the program for a safe
# shutdown and release of all resources. 
def closeProgram(device, sensor):
    R = 255; G = 0; B = 0 # Red
    sensor.statusLED(R,G,B)
    imgProc.closeWindows()
    device.terminate()
    raise SystemExit(0)

# Parses the command line options to set a string filename and activate
# demo mode with th '-D' option which shows the images. By default, if no 
# options are given demo mode is off and the images are saved to veins.png 
# in the current directory. Returns the string filename and boolean DEMO
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
    device = VITA(deviceConnection, baud)
    sensor = awaitVeins(sensorConnection, device)

    ## vein finding
    x, y = veinImaging(filename, device, sensor)
    SPEED = 2500 # mm/min
    while (x != 0 and y != 0):
        x, y = veinImaging(filename, device, sensor)
        try:
            device.move(x, y, 0, SPEED)
        except:
            closeProgram(device, sensor)

    ## injection
    R = 0; G = 0; B = 255 # Blue
    sensor.statusLED(R,G,B)

    distanceDown = 0 #mm
    z = -1 # mm

    force = sensor.getForce()
    if (force == -1): # check that the force sensor is functioning
        print("Force sensor not connected. Injection Failed")
        closeProgram(device, sensor)
    else:
        while(not inVeins(force, distanceDown)):
            try:
                device.move(0,0,z,SPEED)
            except:
                retractNeedle(device, sensor, distanceDown)
                closeProgram(device, sensor)
            distanceDown += abs(z)

            force = sensor.getForce()
            if (force == -1): # check that the force sensor is functioning
                print("Force sensor not connected. Injection Failed")
                retractNeedle(device, sensor, distanceDown)
        
        sensor.waitForButtonPress() # will loop infinitely until button is pressed

        ## retraction
        retractNeedle(device, sensor, distanceDown)
    
if __name__ == "__main__":
    main()