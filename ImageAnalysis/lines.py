import numpy as np
import cv2
from matplotlib import pyplot as plt

def bresenham_simple(startx,starty,vecx, vecy, maxy, maxx):
	# print(startx)
	# print(starty)
	# print(vecx)
	# print(vecy)
	startx.astype(np.int64)
	starty.astype(np.int64)
	# if x is 0, then set vecy to a direction
	if vecx == 0:
		print("skip")
		return([],[])
	else:
		vecy = vecy / vecx
	# extend x in direction of x movement and find all y in line
	if vecx > 0:
		# print(startx)
		# print(maxx)
		x = np.arange(startx, maxx, 1)
	elif vecx < 0:
		x = np.arange(startx, -1, -1)

	x_relative = x - startx

	if vecy == 0:
		y = x_relative*vecy + starty
	else:
		y = x_relative*vecy + starty

	y = np.rint(y)
	xind = np.argwhere(x >= 0)
	xind = np.argwhere(x[xind] < maxx)
	yind = np.argwhere(y >= 0)
	yind = np.argwhere(y[yind] < maxy)
	ind = np.intersect1d(xind,yind)
	return(y[ind],x[ind])

def bresenham_combine(startx,starty,vecx, vecy, maxy, maxx):

	y_xdir,x_xdir = bresenham_simple(startx,starty,vecx, vecy, maxy, maxx)
	x_ydir,y_ydir = bresenham_simple(starty,startx,vecy, vecx, maxx, maxy)
	x_out = np.concatenate((x_xdir,x_ydir), axis = None)
	y_out = np.concatenate((y_xdir,y_ydir), axis = None)
	x_out = x_out.astype(np.int64)
	y_out = y_out.astype(np.int64)
	return(y_out, x_out)