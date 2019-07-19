import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
from skimage.morphology import thin
import lines
# from skimage
# following suggestions by:
# https://pdfs.semanticscholar.org/f8d1/076676696cfdc055e68d2b829333dac08105.pdf
def findInjectionSite():
	pass
# read image into cv2 format
img = cv2.imread('CLAHE_ENHANCED_veinImage_6_cl2_gs8.png')
img_shape = img.shape
x_len = img_shape[1]
y_len = img_shape[0]
# we will draw contours on these The 3 channel is for display
# the 1 channel for processing
blank_canvas = np.zeros((y_len, x_len,3),np.uint8)
blank_canvas_gray = np.zeros((y_len, x_len,1),np.uint8)
# set pixel boundaries to preserve with mask
# basically removes black borders
# list used r g b indexing
lower = np.array([10])
upper = np.array([255])
# convert img to grayscale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# another blur for funsies
gray_blurred = cv2.blur(gray,(15,25),0)
# # blur with kernel as stretched rect in x direction
# blur = cv2.blur(img, (21, 21),0)
# create mask
mask = cv2.inRange(gray_blurred, lower, upper)
# threshold the gray image. Veins will be white(foreground)
thresh = cv2.adaptiveThreshold(gray_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 401, 1.1)
# use the mask we created earlier to get rid of borders
masked_thresh = cv2.bitwise_or(thresh, thresh, mask=mask)
# create a kernel for opening algorithm
kernel = np.ones((15,25),np.uint8)
# opening the white and closing the backgroung arm
opening = cv2.morphologyEx(masked_thresh, cv2.MORPH_OPEN, kernel, iterations = 3)

# find contours of all remaining white areas
contours, hierarchy = cv2.findContours(opening,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
# holds contour
contourCheck = np.zeros((y_len, x_len,1),np.uint8)
# only show really big contours, none of that puny sh*t
for contour in contours:
	if cv2.contourArea(contour) > 70000:
		print(contour.shape)
		cv2.drawContours(blank_canvas,[contour],-1,(255,255,255),cv2.FILLED)
		cv2.drawContours(blank_canvas, [contour], -1, (255, 0, 0), 3)
		cv2.drawContours(blank_canvas_gray,[contour],-1,(255),cv2.FILLED)
		cv2.drawContours(img, [contour], -1, (255, 0, 0), 3)
		# returns slope and point
		[vx,vy,x,y] = cv2.fitLine(contour, cv2.DIST_L2,0,0.01,0.01)
		# vectors for line in direction of vein
		# vein direction vector from linear fit
		veinx = vx
		veiny = -vy
		# take cross product simplification to get perpendicular vector
		perp = tuple([-vy, vx])
		# legacy cross product code just in case
		# veinVec = np.array([np.rint(veiny * 1000), np.rint(veinx * 1000),0])
		# veinVec = veinVec.astype(np.int64)
		# print(veinVec)
		# zaxis = [0, 0, 1]
		# perp = np.cross(veinVec,zaxis)
		# x,y,w,h = cv2.boundingRect(contour)

		# returns center(x,y), (width, height), angle of rotation
		rect = cv2.minAreaRect(contour)

		# find top box corners which we will iterate along and drop
		# search paths
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		x0 = np.power(box[:,0],2)
		x1 = np.power(box[:,1],2)
		dist = np.sqrt(x0+x1)
		leftBoxCornerIndex = np.argmin(dist)
		lBoxCoords = tuple(box[leftBoxCornerIndex])
		# sometimes the algorithm decides to rotate the box 90 degrees for no
		# raisins, but the order of the points are still preserved
		if leftBoxCornerIndex >= 3:
			rightBoxCornerIndex = 0
		else:
			rightBoxCornerIndex = leftBoxCornerIndex + 1
		rBoxCoords = tuple(box[rightBoxCornerIndex])
		pointsx =  np.linspace(lBoxCoords[0],rBoxCoords[0],200)
		pointsy = np.linspace(lBoxCoords[1],rBoxCoords[1],200)
		for i in range(len(pointsx)):
		# for i in [10]:
			y,x = lines.bresenham_combine(pointsx[i],pointsy[i],*perp, img_shape[0],img_shape[1])
			searchLine = np.array((y[0:450],x[0:450])).T
			listCoords = list(zip(x,y))
			intersections = np.empty(0)
			for j in range(len(searchLine)):
				dist = cv2.pointPolygonTest(contour,listCoords[j], False)
				print(dist)
				if dist == 0:
					cv2.circle(blank_canvas, listCoords[j], 15, (0,0,255), -1)
					intersections = np.append(intersections,listCoords[j])
			print(intersections)
			print(intersections.shape)
			# pixVals = np.array(blank_canvas_gray[y,x])
			# pixVals = np.reshape(pixVals, (1, len(pixVals)))
			# np.savetxt("pixVals.txt", pixVals)
			# # for j in range(len(pixVals)):
			# # 	print(pixVals[j])
			# breaks = np.where(np.diff(pixVals) > 0)
			blank_canvas[y[0:400],x[0:400]] = (0,255,0)
			# print(breaks)
		cv2.line(blank_canvas, lBoxCoords, rBoxCoords,color = (0,0,255),thickness= 1)
		# cv2.drawContours(blank_canvas,[box],-1,(255),3)
		# check width at these yvalues
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




