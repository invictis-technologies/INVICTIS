import numpy as np
import cv2
import subprocess
from VITA_PRINTER import VITA_PRINTER
import serial

from picamera import PiCamera
from time import sleep
from fractions import Fraction

class VITA_PRINTER_CONTROLLER():
    def __init__(self, camera, ser):
        self.camera = camera
        self.ser = ser
        
    def mainLoop(self, printer):
        self.ser.write(b"G28 X Y\r\n")
        sleep(3)
        printer.printerCheckOk(self)
        printer.printerMove(self, 0, 100, 0, 2500)
        printer.printerMove(self, 100, 0, 0, 2500)
        printer.printerMove(self, 0, -90, 0, 2500)
        printer.printerMove(self, -90, 0, 0, 2500)
        self.terminate()
    
    #body of program. Takes in camera and serial port
    #still need to adapt
    def mainLoop1(camera, ser):
        camera.start_preview(fullscreen = False, window = (10, 100, 400, 300))
        PictureTaken = True
        counter = 0
        filetype = (".jpeg")
        num_im_limit = 60
        while PictureTaken:
            try:
                if counter > num_im_limit:
                    subprocess.run("rm -f temp*", shell = True)
                    counter = 0
                filename = "temp" + str(counter) + filetype;
                counter = counter + 1
                #camera.capture("temp.png", use_video_port = True, resize = (400,300))
                camera.capture(filename, use_video_port = False, resize = (400,300))
                img = cv2.imread(filename,0)
                clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8,8))
                cl1 = clahe.apply(img)
                edges = cv2.Canny(cl1, 30,150)
                blur = cv2.GaussianBlur(cl1, (3,5),0)
                ret, th1 = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
                cv2.imshow("image", edges)
                cv2.waitKey(100)
            except KeyboardInterrupt as e:
                terminate(camera, ser)
        
    def terminate(self):
        self.camera.stop_preview()
        cv2.destroyAllWindows()
        subprocess.run("rm -f temp*", shell = True)
        self.ser.close()
        exit()
        
#sets up serial connection with Velleman k8200 3d printer
def setupSerial():
    #set up serial connection
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 250000
    return ser


#sets up camera settings
def setupCamera():
    camera = PiCamera(
        #resolution = (3280, 2464),
        resolution = (1280, 960),
        #resolution = (400,300),
        sensor_mode = 4
        )
    camera.iso = 100
    camera.raw_format = 'rgb'
    #default = 50
    camera.brightness = 55
    camera.shutter_speed = 500000
    #see modes
    #off, auto, night, nightpreview, backlight
    #spotlight, sports, snow, beach, verylong, fixedfps
    #antishake, fireworks
    camera.exposure_mode = 'off'
    camera.annotate_text_size = 160
    camera.awb_gains = 0
    camera.awb_mode = 'off'
    #between -100 and 100 default = 0
    camera.contrast = 100
    #camera.color_effects = (120, 120)
    #denoise = true
    camera.image_denoise = False
    #see metering modes 'average', 'spot', backlit', 'matrix'
    camera.meter_mode = 'average'
    #-100 to 100 default = 0
    camera.saturation = 60
    #-100 to 100 default = 0
    camera.sharpness = 100
    return camera

        
def main():
    ser = setupSerial()
    camera = setupCamera()
    printer = VITA_PRINTER()
    controller = VITA_PRINTER_CONTROLLER(camera, ser)
    controller.mainLoop(printer)
    #if main loop terminates, exit program
    controller.terminate()
    
if __name__ == "__main__":
    main()