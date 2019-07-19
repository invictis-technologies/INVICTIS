import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd
from scipy import zeros, signal, random
from time import sleep
from PIL import Image
# read image into cv2 format
img = cv2.imread('veinImage_963.png')

# set pixel boundaries to preserve with mask
# basically removes black borders
# list used r g b indexing
lower = np.array([0, 20, 0])
upper = np.array([255, 255, 255])
# blur with kernel as stretched rect in x direction
blur = cv2.blur(img, (21, 21),0)
# create mask
mask = cv2.inRange(blur, lower, upper)

# convert img to grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# another blur for funsies
gray_blurred = cv2.blur(gray,(15,15),0)
# threshold the gray image. Veins will be white(foreground)
thresh = cv2.adaptiveThreshold(gray_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 451, 1.1)
# use the mask we created earlier to get rid of borders
masked_thresh = cv2.bitwise_or(thresh, thresh, mask=mask)
# create a kernel for opening algorithm
kernel = np.ones((5,5),np.uint8)
# opening the white and closing the backgroung arm
opening = cv2.morphologyEx(masked_thresh, cv2.MORPH_OPEN, kernel, iterations = 3)

# find contours of all remaining white areas
contours, hierarchy = cv2.findContours(opening,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

imgOut = img
# only show really big contours, none of that puny sh*t
for contour in contours:
	if cv2.contourArea(contour) > 10000:
		cv2.drawContours(imgOut, contour, -1, (255, 0, 0), 3)

# plot results
# original image
plt.subplot(2,2,1)
plt.title('Original'), plt.xticks([]), plt.yticks([])
plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
# thresholded image
plt.subplot(2,2,2)
plt.title('Thresholded'), plt.xticks([]), plt.yticks([])
plt.imshow(masked_thresh, cmap = 'gray', interpolation = 'bicubic')
# thresholded image after opening algorithm
plt.subplot(2,2,3)
plt.title('Thresh + Opened'), plt.xticks([]), plt.yticks([])
plt.xticks([]), plt.yticks([])
plt.imshow(opening, cmap = 'gray', interpolation = 'bicubic')

plt.subplot(2,2,3)
plt.title('Thresh + Opened+ Opened'), plt.xticks([]), plt.yticks([])
plt.xticks([]), plt.yticks([])
plt.imshow(masked_thresh, cmap = 'gray', interpolation = 'bicubic')

# plt.imshow(laplacian, cmap = 'gray', interpolation = 'bicubic')

# to hide tick values on X and Y axis
# plt.xticks([]), plt.yticks([])

plt.show()




