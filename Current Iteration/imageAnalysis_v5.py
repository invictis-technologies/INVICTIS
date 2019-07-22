import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
from skimage.morphology import thin
import lines_v2 as lines
import pandas as pd

# =====================================================================================
# ===============================Temp Readme======================================
# the file can take in arguments of number of search paths, path length,
# minimum contour area, and window length.
# The file can output a boolean followed by coordinates if any locations are found.
# Or it can just output the coordinates and you catch the Nones if no are found. I
# left places in the code to make these.

# the plots take a majority of the run time. comment out to speed up the program
# by >2x. 

# To make this code a callable function, we need the following changes.
# 1. create function declaration/
# 2. write desired return statements ctrl/cmd f and look for "# Write return here"
# 3. the code is analyzing images in the folder. Stick that in the argument.

# There is a lot that can be optimized further such as the adaptive filtering.
# If needed, there are places in the code I can speed up and write out, but it
# works for now (kinda) and will become obsolete when we move to lasers. Also, we can
# reduce image size, but losing information is bad, and I am currently using averaging
# filters that are not great either.

# The image filtering is currently based on images taken with the old acryllic and 
# cardboard tunnel. We will have to adjust parameters and filters to account for
# these changes.

# See the weird ASCII diagram below for information about how stuff works

# from skimage
# following suggestions by:
# https://pdfs.semanticscholar.org/f8d1/076676696cfdc055e68d2b829333dac08105.pdf
# =====================================================================================
# =====================================================================================
# length of search path
samplePathLength = 600
# divide the length of crawlpath by divFactor, take floor to get number of search paths
divFactor = 5
# minimum allowed contour area
minContourArea = 50000
# length of window to average vein widths
windowLength = 10
# read image into cv2 format
img = cv2.imread('CLAHE_ENHANCED_veinImage_62gs6.png')
# ================================================================
# saves the shape of the image so we can create numpy arrays of the same shape for data visualization
img_shape = img.shape
x_len = img_shape[1]
y_len = img_shape[0]
# we will draw contours on these The 3 channel is for display
# the 1 channel for processing
blank_canvas = np.zeros((y_len, x_len,3),np.uint8)
blank_canvas_gray = np.zeros((y_len, x_len,1),np.uint8)
# convert img to grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# add a blur to reduce noise. Second argument is a kernel that is used to average
# the pixel values. (row, column). I found that a rectangle stretched in the x direction
# works well for finding the long parts of the basilic and cephalic vein.
gray_blurred = cv2.blur(gray,(15,51),0)
# threshold the gray image. Veins will be white(foreground)
thresh = cv2.adaptiveThreshold(gray_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 451, 1.1)
# set pixel grayscale boundaries to preserve with mask
# basically removes balck pixels with values under 10 on a scale of 255(white)
lower = np.array([10])
upper = np.array([255])
# create mask using the bounds
mask = cv2.inRange(gray_blurred, lower, upper)
# use the mask we created earlier to get rid of borders
masked_thresh = cv2.bitwise_or(thresh, thresh, mask=mask)
# create a kernel for opening algorithm. See cv2 docs for kernel options.
# this is a simple rectangle ones kernel.
kernel = np.ones((15,25),np.uint8)
# opening the white and closing the dark backgroung arm.
# reduces background noise and enhances foreground.
opening = cv2.morphologyEx(masked_thresh, cv2.MORPH_OPEN, kernel, iterations = 3)
# find contours of all remaining white areas
contours, hierarchy = cv2.findContours(opening,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# holds contours in loop
contourCheck = np.zeros((y_len, x_len,1),np.uint8)
# holds the best midpoint and distance in every contour
dbOfOptimalLocations = pd.DataFrame()
# only show really big contours, none of that puny sh*t
for contour in contours:
	# only process large contours. Feel free to adjust the contour area threshold
	if cv2.contourArea(contour) > minContourArea:
		# create dataframe to store centerpoints of vein((y,x) type = tuple) and width(pixel)
		mdpt_dist = pd.DataFrame()
		# draw white filled contour on color canvas
		cv2.drawContours(blank_canvas,[contour],-1,(255,255,255),cv2.FILLED)
		# draw contour outline in blue with width 3 pixels. color uses (BGR notation) 
		cv2.drawContours(blank_canvas, [contour], -1, (255, 0, 0), 3)
		# draw filled white contour on gray canvas
		cv2.drawContours(blank_canvas_gray,[contour],-1,(255),cv2.FILLED)
		# draw the outline of contours on the original image
		cv2.drawContours(img, [contour], -1, (255, 0, 0), 1)
		# returns slope and point of contour
		[vx,vy,x,y] = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)

		# vectors for line in direction of vein
		# vein direction vector from linear fit
		veinx = vx
		veiny = -vy
		slope = vy/vx
		# take cross product simplification to get perpendicular vector. see explanation in line below
		perp = tuple([-vy, vx])
		''' 
		the slope vector only points in the positive x direction. For images, the top
		left corner is the origin (0,0). The problem the simplified cross solves is finding
		the vector in the image plane that is perpendicular to the contour vector and points 
		downwards (positive y direction in image space). This perp vector will be used to direct
		linear search paths through the contour to find the width of the vein and the midpoint.
		The program sends a bunch of perpendicular vectors out and then takes a window over 
		vein widths to find the optimal insertion spot.
		Image of what is happening
		-------------/+++++///:::-----------------------------------------++----------------------------------
-------------------::::///++++/////:::----VEIN CONTOUR VECTOR------------++PERP VECTOR---------------------------------------------
-------------------------------::::///++++++////:::----------------------++--------------------------
--------------------------------------------:::////+++++//::::-----------++--------------------------
-------------------------------------------------------:::///+++++++///::o--------->>---------------
---------------------------------------------------------------------::/+o++++++////>>+-------------
------------------------------------------------------------------------/:----------yy/>>>>>------------
------------------------------------------------------------------------++--------:>>>--------------
---------------:///++++++++++//:----------------------------------------++---------------------------
---------:++++//::------------:/+++:-----------------------------------:/---------------------------
--------//-------------------------/++/:-------------------:::::-------/+----------------------------
------000-----------------------------:/++++/::::::/+++++///////++++/--+-::-------------------------
------000-----------------------------------://////:----------------/+oy/:--------------------------
----000--------------------------------------------------------------:++++:-------------------------
---000--:/++++++++++++++++:------------VEIN--CONTOUR--------------+---+o+-----------------------
-----+++/:----------------/+++/--------------------------------------:o------+++------------------
------------------------------:+o+/:---------------:/++++++++++++:---//---------:/++++--------------
-----------------------------------/++ooo++++++o+o+/:-----------:+o+:+-:-----------++-----------------
-------------------------------------------------------------------:sys+:-----------+++----------------
--------------------------------------------------------------------++--:/+++/:-----0000-----------------
--------------------------------------------------------------------++-------:/+++o------------------
-------------------------------------------------------------------+/--------------------------------
-------------------------------------------------------------------++--------------------------------
------------------------------------------------------------------/:--------------------------------
-----------------------------------------------------------------/+:--------------------------------
-----------------------------------------------------------------/:VECTOR ARROW------------------------------
-----------------------------------------------------------------+----------------------------------
		'''
		# legacy cross product code just in case
		# veinVec = np.array([np.rint(veiny * 1000), np.rint(veinx * 1000),0])
		# veinVec = veinVec.astype(np.int64)
		# print(veinVec)
		# zaxis = [0, 0, 1]
		# perp = np.cross(veinVec,zaxis)
		# x,y,w,h = cv2.boundingRect(contour)

		# returns center(x,y), (width, height), angle of rotation for minimum bounding box
		# of the contour. We will take the top line of the rectangle for the starting
		# point of the search paths
		rect = cv2.minAreaRect(contour)
		# find top box corners which we will iterate along and drop search paths
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		x0 = np.power(box[:,0],2)
		x1 = np.power(box[:,1],2)
		dist = np.sqrt(x0+x1)
		topBoxCornerIndex = np.argmin(box[:,1])
		tBoxCoords = tuple(box[topBoxCornerIndex])
		cv2.drawContours(blank_canvas, [box],0,(0,255,255),2)
		# sometimes the algorithm decides to rotate the box 90 degrees for no
		# raisins, but the order of the points are still preserved.

		# weird way of finding the top box edge. determined experimentally
		# print(slope)
		if slope > -0:
			if topBoxCornerIndex >= 3:
				rightBoxCornerIndex = 0
			else:
				rightBoxCornerIndex = topBoxCornerIndex + 1
		else:
			if topBoxCornerIndex <= 0:
				rightBoxCornerIndex = 3
			else:
				rightBoxCornerIndex = topBoxCornerIndex -1
		rBoxCoords = tuple(box[rightBoxCornerIndex])
		cv2.line(blank_canvas, tBoxCoords, rBoxCoords,color = (255,0,255),thickness= 20)
		# find length of top box side, which we will crawl along and drop search paths
		crawlLength = np.sqrt(np.power((tBoxCoords[1]-rBoxCoords[1]),2)+np.power((tBoxCoords[0]-rBoxCoords[0]),2))
		numPaths = np.floor(crawlLength/divFactor).astype(np.int64)
		# Set the start points of the search paths using a linear space
		pointsx =  np.linspace(tBoxCoords[0],rBoxCoords[0],numPaths)
		pointsy = np.linspace(tBoxCoords[1],rBoxCoords[1],numPaths)
		# drop search paths
		for i in range(len(pointsx)):
		# for i in [10,11,12,13]:
			# bresenham algorithm is a simple way to approximates lines with pixels
			# the * is used to unwrap tuples. Takes arguments in a weird order because 
			# cv2 and numpy can't agree on xy or yx notation
			y,x = lines.bresenham_combine(pointsx[i],pointsy[i],*perp, img_shape[0],img_shape[1])
			# limit search lines to 450 pixels(Will need to change if resoltution changes)
			# Feel free to update.
			if x.shape[0] > samplePathLength:
				blank_canvas[y[range(samplePathLength)],x[range(samplePathLength)]] = (0,255,0)
				searchLine = np.array((y[0:samplePathLength],x[0:samplePathLength])).T
				# print(y[0:samplePathLength])
				listCoords = list(zip(x,y))
				intersections = np.empty(0)
				# goes down the search path and checks if the point is on the contour boundary
				for j in range(len(searchLine)):
					# returns 0 if on contour, -1 if outside, and 1 if inside.
					# False flag suppresses distance calculations which speeds up
					# code by 2 or 3x
					# SLOW PART OF ALGORITHM
					dist = cv2.pointPolygonTest(contour,listCoords[j], False)
					if dist == 0:
						cv2.circle(blank_canvas, listCoords[j], 15, (0,0,255), -1)
						intersections = np.append(intersections,listCoords[j], axis = 0)
				# if there are not two intersections, assume the datapoint is bad and disregard neighboring points
				if intersections.shape[0] != 4:
					midpoint = (np.nan,np.nan)
					distance = np.nan
				# calculate the midpoint and vein width(aka distance)
				else:
					x1 = intersections[0]
					x2 = intersections[2]
					y1 = intersections[1]
					y2 = intersections[3]
					midpoint = [np.mean([x1,x2]),np.mean([y1, y2])]
					midpoint = tuple(np.rint(midpoint).astype(np.int64))
					distance = np.sqrt(np.power(y2-y1,2)+np.power(x2-x1,2))
					# print(midpoint)
					# print(distance)
					# cv2.circle(blank_canvas, midpoint, 3, (255,0,255), -1)
				temp = pd.DataFrame([[midpoint, distance]])
				mdpt_dist = mdpt_dist.append(temp, ignore_index=True)
		# exit if no valid paths detected
		if mdpt_dist.shape[0] <= 0:
			print("No midpoints Detected")
			pass
			# Write return here
		else:
			# find the largest windowed distance of the contour and store the points and distance in a larger array
			# print(mdpt_dist.shape)
			windowed = mdpt_dist[1].rolling(windowLength,center = True).mean()
		# print(windowed)
			# print(breaks)
			maxWidthInContourIndex = np.where(windowed == np.amax(windowed))
			optimalLocationInContour = mdpt_dist.iloc[maxWidthInContourIndex]
			dbOfOptimalLocations = dbOfOptimalLocations.append(optimalLocationInContour, ignore_index=True)
print(dbOfOptimalLocations)
optimalLocationIndex = np.where(dbOfOptimalLocations == np.amax(dbOfOptimalLocations.loc[:,1]))[0]
optimalLocation = dbOfOptimalLocations.iloc[optimalLocationIndex][0]
print("who's a good boyo")
if optimalLocation.shape[0] == 0:
	exit("No Locations Detected")
	# Write return here
optimalLocation = optimalLocation.reset_index(drop = True)
print(optimalLocation[0]) 
# Write return here
cv2.circle(blank_canvas, optimalLocation[0], 25, (255,0,255), -1)
# print(dbOfOptimalLocations)
# thin = thin(blank_canvas)
# # plot results
# # original image
plt.subplot(3,2,1)
plt.title('Original'), plt.xticks([]), plt.yticks([])
plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
# thresholded image
plt.subplot(3,2,2)
plt.title('Thresholded'), plt.xticks([]), plt.yticks([])
plt.imshow(masked_thresh, cmap = 'gray', interpolation = 'bicubic')
# thresholded image after opening algorithm
plt.subplot(3,2,3)
plt.title('Thresh + Opened'), plt.xticks([]), plt.yticks([])
plt.imshow(opening, cmap = 'gray', interpolation = 'bicubic')

plt.subplot(3,2,4)
plt.title('Contours Annotated'), plt.xticks([]), plt.yticks([])
plt.imshow(cv2.cvtColor(blank_canvas, cv2.COLOR_BGR2RGB))
cv2.imwrite('annotated.png', blank_canvas)

plt.subplot(3,2,5)
plt.title('Contours Gray'), plt.xticks([]), plt.yticks([])
plt.imshow(cv2.cvtColor(blank_canvas_gray, cv2.COLOR_BGR2RGB))

# to hide tick values on X and Y axis
# plt.xticks([]), plt.yticks([])

plt.show()




