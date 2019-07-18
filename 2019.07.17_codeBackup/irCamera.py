from picamera import PiCamera
import pathlib # used to find deprecated image files
import os # used to delete deprecated image files

class irCamera():
    # Construct an ircamera object which is optimized for vein finding
    def __init__(self):
        self.ircamera = PiCamera(
            #resolution = (3280, 2464),
            resolution = (1280, 960),
            #resolution = (400,300),
            sensor_mode = 4
            )
        self.ircamera.iso = 100
        self.ircamera.raw_format = 'rgb'
        #default = 50
        self.ircamera.brightness = 55
        self.ircamera.shutter_speed = 500000
        #see modes
        #off, auto, night, nightpreview, backlight
        #spotlight, sports, snow, beach, verylong, fixedfps
        #antishake, fireworks
        self.ircamera.exposure_mode = 'off'
        self.ircamera.annotate_text_size = 160
        self.ircamera.awb_gains = 0
        self.ircamera.awb_mode = 'off'
        #between -100 and 100 default = 0
        self.ircamera.contrast = 100
        #camera.color_effects = (120, 120)
        #denoise = true
        self.ircamera.image_denoise = False
        #see metering modes 'average', 'spot', backlit', 'matrix'
        self.ircamera.meter_mode = 'average'
        #-100 to 100 default = 0
        self.ircamera.saturation = 60
        #-100 to 100 default = 0
        self.ircamera.sharpness = 100
        # Preview is used to detect and handle calling errors
        self.preview = False
    
    # Begins a live onscreen camera feed in a windowed 
    # environment. Nothing is returned.
    def start_preview(self):
        if self.preview == True:
            return

        self.preview = True
        self.ircamera.start_preview(fullscreen = False, window = (10, 100, 400, 300))
    
    # Ends the live onscreen camera feed. Nothing is returned
    def stop_preview(self):
        if self.preview == False:
            return

        self.preview = False
        self.ircamera.stop_preview()

    # Takes a still image of the camera frame and saves it to the working directory
    # as a png file named filename where filename is some string. Nothing is returned.
    def capture(self, filename):
        filepath = filename + '.png'
        path = pathlib.Path(filepath)

        # Delete the old vein data
        if path.exists():
            os.remove(filename + filepath)
        
        self.ircamera.capture(filename, format = 'png', use_video_port = False, resize = (400,300))

    # Finalizes the state of the camera to prevent GPU memory leaks
    # Takes in nothing and returns nothing
    def close(self):
        self.close()