import numpy as np
import cv2
from matplotlib import pyplot as plt

def bresenham_simple(startx,starty,vecx, vecy, maxy, maxx):
	# print(maxx)
	# print(maxy)
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
	# x = x[x>0]
	# x = x[x<maxx]
	# y = y[y>0]
	# y = y[y<maxy]
	xind_nonzero = np.argwhere(x >= 0)
	xind_lessMaxx = np.argwhere(x < maxx)
	xind = np.intersect1d(xind_nonzero, xind_lessMaxx)
	yind_nonzero = np.argwhere(y >= 0)
	yind_lessMaxy = np.argwhere(y < maxy)
	yind = np.intersect1d(yind_nonzero, yind_lessMaxy)
	# print(np.max(y[yind]))
	# print('=maxes=')
	# print(maxx)
	# print(np.max(x))
	# print(maxy)
	# print(np.max(y))
	ind = np.intersect1d(xind,yind)
	return(y[ind],x[ind])

def bresenham_combine(startx,starty,vecx, vecy, maxy, maxx):

	y_xdir,x_xdir = bresenham_simple(startx,starty,vecx, vecy, maxy, maxx)
	x_ydir,y_ydir = bresenham_simple(starty,startx,vecy, vecx, maxx, maxy)
	x_unSorted = np.concatenate((x_xdir,x_ydir), axis = None)
	y_unSorted = np.concatenate((y_xdir,y_ydir), axis = None)
	sortInd = np.argsort(y_unSorted, kind='quicksort')
	x_out = x_unSorted[sortInd]
	y_out = y_unSorted[sortInd]
	x_out = x_out.astype(np.int64)
	y_out = y_out.astype(np.int64)
	# print('===maxes===')
	# print(np.max(x_out))
	# print(np.max(y_out))
	return(y_out, x_out)