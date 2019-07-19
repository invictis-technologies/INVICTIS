import numpy as np
import cv2
from matplotlib import pyplot as plt

def bresenham_simple(startx,starty,vecx, vecy, maxx, maxy):
	# if x is 0, then set vecy to a direction
	if vecx == 0:
		if vecy == 0:
			print("skip")
			return([],[])
	if vecx == 0 and vecy != 0:
		vecx = 0
		vecy = vecy/abs(vecy)
	else:
		vecx = vecx/abs(vecx)
		vecy = vecy / vecx
	# extend x in direction of x movement and find all y in line
	if vecx > 0:
		x = np.arange(startx, maxx, 1)
		y = x*vecy
	elif vecx < 0:
		x = np.arange(startx, -1, -1)
		y = x*vecy
	# if x is stationary
	else:
		# y = np.arange(starty,maxy,1)
		# x = np.ones(len(y))*
		return([],[])
	y = np.rint(y)
	xind = np.argwhere(x >= 0)
	xind = np.argwhere(x < maxx)
	yind = np.argwhere(y >= 0)
	yind = np.argwhere(y < maxy)
	ind = np.intersect1d(xind,yind)
	return(y[ind], x[ind])

def bresenham_combine(startx,starty,vecx, vecy, maxx, maxy):
	y_xdir,x_xdir = bresenham_simple(startx,starty,vecx, vecy, maxx, maxy)
	x_ydir,y_ydir = bresenham_simple(starty,startx,vecy, vecx, maxy, maxx)
	x_out = np.concatenate((x_xdir,x_ydir), axis = None)
	y_out = np.concatenate((y_xdir,y_ydir), axis = None)
	x_out = x_out.astype(np.int64)
	y_out = y_out.astype(np.int64)
	return(y_out, x_out)

shape = (200,200)
blank_canvas = np.zeros(shape,np.uint8)
start = (100,100)
vec=(1,0)
blank_canvas[start]= 255
x , y = bresenham_combine(*start,*vec,*shape)
blank_canvas[x,y] = 255
plt.imshow(blank_canvas)
plt.show()
# plt.title('Memes'), plt.xticks([]), plt.yticks([])
# plt.show()