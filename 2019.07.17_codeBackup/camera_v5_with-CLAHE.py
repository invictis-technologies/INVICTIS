from VITA_PRINTER import VITA
from irCamera import irCamera
import imageProcessor as imgProc
from pi2uno_v2 import ARDUINO
from time import sleep
    
# TODO: Make the currently unrecoverable errors that terminate the program recoverable
# TODO: implement DEMO mode with live viewing

# Finds veins and presents their location.
# It takes in a string filename, a VITA object device,
# and a ARDUINO object sensor and returns x and y as distances.
def veinImaging(filename, device, sensor):
    height = sensor.getDistance()

    if height == -1:
        device.terminate()
        exit()

    device.capture(filename)
    if imgProc.isValidImg(filename):
        imgProc.preprocess(filename)

        x,y = imgProc.getVeins(filename, height)

        return x, y
    else:
        device.terminate()
        exit()

def main():
    deviceConnection = '/dev/ttyUSB0'
    sensorConnection = '/dev/ttyUSB1'
    filename = 'veins'
    baud = 250000

    device = VITA(deviceConnection, baud)
    sensor = ARDUINO(sensorConnection)

    device.initialize()

    try:
        sensor.buttonPress()
    except IOError:
        device.terminate()

    x, y = veinImaging(filename, device, sensor)
    while (x != 0 and y != 0):
        x, y = veinImaging(filename, device, sensor)
        device.move(x, y, 0, 2500)
    
    ## injection step
    # sensor.getForce

    ## retraction step

    device.terminate()
    exit()
    
if __name__ == "__main__":
    main()