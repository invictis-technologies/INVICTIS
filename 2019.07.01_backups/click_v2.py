import numpy as np
import cv2
import subprocess
from VITA_PRINTER import VITA_PRINTER
from camera_v4 import VITA_PRINTER_CONTROLLER
import serial
import pygame

from picamera import PiCamera
from time import sleep
from fractions import Fraction
refpt = []
isClick = False
pix2mm = 2.7
def mainLoop(controller, printer):
    global isClick
    global refpt
    global pix2mm
    camera = controller.camera
    camera.start_preview(fullscreen = False, window = (10, 100, 400, 300))
    counter = 0
    filetype = (".jpeg")
    num_im_limit = 60
    while True:
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
            #edges = cv2.Canny(cl1, 30,150)
            blur = cv2.GaussianBlur(cl1, (3,5),0)
            cv2.circle(blur, (200, 150), 2, (255, 0, 0))
            #ret, th1 = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
            cv2.imshow("image", blur)
            cv2.setMouseCallback("image", getMouseCoords)
            if isClick:
                isClick = False
                (x, y) = refpt[0]
                print("("+ str(x) + " + " + str(y) + ")")
                x_dist = (y - 150)/pix2mm
                y_dist = (x - 200)/pix2mm
                print("moving " + str(x_dist) + " " + str(y_dist))
                printer.printerMove(controller, x_dist, y_dist, 0, 2500)
            cv2.waitKey(100)
        except KeyboardInterrupt as e:
            controller.terminate()
            exit()

def getMouseCoords(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global isClick
        global refpt
        isClick = True
        refpt = [(x,y)]
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
    printer = VITA_PRINTER()
    camera = setupCamera()
    controller = VITA_PRINTER_CONTROLLER(camera, ser)
    ser.write(b"G28 X Y\r\n")
    sleep(5)
    printer.printerCheckOk(controller)
    printer.printerMove(controller, 110, 60, 0, 2500)
    mainLoop(controller, printer)
    #if main loop terminates, exit program
    controller.terminate()
    exit()
    
if __name__ == "__main__":
    main()
