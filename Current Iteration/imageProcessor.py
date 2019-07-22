import numpy as np # OpenCv uses Numpy arrays to store things
import cv2 # Performs the image analysis
import imghdr # Checks that an image is valid

# TODO: Add in computer vision algorithm as findVeins() method

'''
 Takes in a valid image (it is up to the client to validate the image)
 and properly processes it in preparation for computer vision. The image
 is given by string filename. Returns a cv2 object
'''
def preprocess(filename):
    img = cv2.imread(filename,0)
    
    # see contrast limited adaptive histogram equalization for details
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img)

    # despeckle the newly formatted image
    blur = cv2.GaussianBlur(cl1, (3,5),0)
    cv2.circle(blur, (200, 150), 2, (255, 0, 0))

    return blur

'''
 Takes in a valid image (it is up to the client to validate the image)
 and identifies likely regions of large veins. The image
 is by the cv2 object img and a height from the arm in mm.
 An x and y distance to the veins are returned in mm.
'''
def getVeins(img, height):
    pixX, pixY = findVeins()

    # formula determined experimentally
    pix2mm = -0.1987*height+50.2399 
    
    # Determined experimentally to be the center of the frame
    xDist = (pixY - 150)/pix2mm
    yDist = (pixX - 200)/pix2mm

    return xDist, yDist

def findVeins():
        return None,None

'''
 Takes in a filename and checks whether or not the filename is a
 valid image. Returns True if it is or false if it is not and prints to 
 stdOut. It is advised that the client always call this when working with 
 new images.
'''
def isValidImg(filename):
    fileExtension = imghdr.what(filename)
    if fileExtension is None:
        print(filename + " is not a readable image.") 
        closeWindows()
        raise ValueError('File is not a readable image')

'''
 Wrapper function to close openCV outside of this scope in case of errors.
 It takes nothing and returns nothing
'''
def closeWindows():
    cv2.destroyAllWindows()

# Debug function added to allow for clickable interactions with cv2 objects
def click_DEBUG(img, getMouseCoords):
        cv2.imshow("image", img)
        cv2.setMouseCallback("image", getMouseCoords)