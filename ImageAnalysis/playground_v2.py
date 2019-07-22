import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd

# def bresenham_simple(startx,starty,vecx, vecy, maxy, maxx):
# 	# if x is 0, then set vecy to a direction
# 	if vecx == 0:
# 		print("skip")
# 		return([],[])
# 	else:
# 		vecy = vecy / vecx
# 	# extend x in direction of x movement and find all y in line
# 	if vecx > 0:
# 		x = np.arange(startx, maxx, 1)
# 	elif vecx < 0:
# 		x = np.arange(startx, -1, -1)

# 	x_relative = x - startx

# 	if vecy == 0:
# 		y = x_relative*vecy + starty
# 	else:
# 		y = x_relative*vecy + starty

# 	y = np.rint(y)
# 	xind = np.argwhere(x >= 0)
# 	xind = np.argwhere(x < maxx)
# 	yind = np.argwhere(y >= 0)
# 	yind = np.argwhere(y < maxy)
# 	ind = np.intersect1d(xind,yind)
# 	return(y[ind],x[ind])

# def bresenham_combine(startx,starty,vecx, vecy, maxy, maxx):

# 	y_xdir,x_xdir = bresenham_simple(startx,starty,vecx, vecy, maxy, maxx)
# 	x_ydir,y_ydir = bresenham_simple(starty,startx,vecy, vecx, maxx, maxy)
# 	x_out = np.concatenate((x_xdir,x_ydir), axis = None)
# 	y_out = np.concatenate((y_xdir,y_ydir), axis = None)
# 	x_out = x_out.astype(np.int64)
# 	y_out = y_out.astype(np.int64)
# 	return(y_out, x_out)

# shape = (200,100)
# blank_canvas = np.zeros(shape,np.uint8)
# start = (100,99)
# vec=(-1,1)
# blank_canvas[start]= 255
# y,x = bresenham_combine(*start,*vec,*shape)
# print(shape)
# print(x)
# print(y)
# blank_canvas[y,x] = 255
# plt.imshow(blank_canvas)
# plt.show()
# exit()
# # plt.title('Memes'), plt.xticks([]), plt.yticks([])
# # plt.show()



# a = [1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,1,1,1,0,0,0,0,0,0,0]
# c = np.where(np.diff(a) != 0)
# print(c)


# a = np.arange(1,10,1)
# b = [1, 7, 34, 23,234]
# print(np.argwhere(np.isin(b,a)))

# df = pd.DataFrame({'B': [0, 1, 2,3,5, None, 4]})
# y = df.rolling(3,center = True).mean()
# print(y)
# print(np.where(y == np.amax(y)))
# print([1:5])
# a = np.array([1,2,3,4,5,6])
# print(a[1:5])
# print(np.argwhere(a[1:5] > 3))

a = np.array([1,-1,2,-2,3,-3,4,5,6])
a = a[a>0]
print(a)