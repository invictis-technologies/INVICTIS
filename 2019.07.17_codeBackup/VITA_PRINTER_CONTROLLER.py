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
    def mainLoop1(self, camera, ser):
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
            except KeyboardInterrupt:
                terminate(camera, ser)
        
    def terminate(self):
        self.camera.stop_preview()
        cv2.destroyAllWindows()
        subprocess.run("rm -f temp*", shell = True)
        self.ser.close()
        exit()