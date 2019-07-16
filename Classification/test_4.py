import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data import clean_data
from scipy.signal import butter, lfilter, freqz
from scipy import zeros, signal, random
from time import sleep
from forecast import Forecast

print("Beginning...")
calcForecast = False
# plots either forecast or gradient or no plots
plotFig = True
plotForecast = False
debugOut = False
# ==========PLOT CONTROLLER========
plotGrad = not plotForecast
if plotFig == False:
	plotForecast = False
	plotGrad = False
if calcForecast == False:
	plotForecast = False

# =================================
# turn off matplot lib warning of potential problems in future versions
import warnings
warnings.filterwarnings("ignore");

# clean the data using clean_data.py
cdata = clean_data()
# arguments of filename.xlsx string, sheet name string, 
# cleanOutputFilename(.xlsx) string, and boolean for whether 
# or not you want to output to file: 0 = false, 1 = true
cdata.clean("Good.xlsx","Sheet1", None, 0)
exp = pd.DataFrame()
exp = pd.read_excel("dropLocations.xlsx","Sheet1")
exp1 = exp.loc[:,1]
length = cdata.x.shape[1]

# begin low pass filter 
# =========FROM===========
# https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
def butter_lowpass(cutoff, fs, order=5):
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = butter(order, normal_cutoff, btype='low', analog=False)
	return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
	b, a = butter_lowpass(cutoff, fs, order=order)
	y = lfilter(b, a, data)
	return y
# Filter the data, and plot both the original and filtered signals.
# y = butter_lowpass_filter(data, cutoff, fs, order)

# ========END HONOR CODE VIOLIATION==============
# def dataPointIterator():

# Filter requirements. (Butterworth filter)
order = 3
fs = 10      # sample rate, Hz
cutoff = 1.1  # desired cutoff frequency of the filter, Hz

# =====Start Analysis=====

# number of set of data in dataframe
setNum = 0
#skip a number of datapoints before windowing
skip = 30
# window size(for plot asthetic)
window = 2
# number of iterations
# numit = 500
numit = 100
# stepsize
# delta = .00001
delta = 0.01
# lag
lag = 20
# bar distance
bars = .02
# create data frame to store potential thresholds
possThreshList = pd.DataFrame(columns=list(range(numit)))
#create a data frame to store error from expected
distance = pd.DataFrame(columns=list(range(1)))
# for setNum in range(length):
for setNum in [65]:
	print("Data Set: " + str(setNum))
	# initial threshold
	thresh = -2.85*np.power(10.0,-3)
	#expected value
	expected = exp1[setNum]
	# threshold tracker
	threshHolder = np.empty(0)
	# error holder
	errorHolder = np.empty(0)
	# direction(+/- 1)
	direction = 1
	# put in first threshold value
	threshHolder = np.append(threshHolder, thresh)
	# set up data arrays
	ydat = -cdata.y.loc[:,setNum]
	data = butter_lowpass_filter(ydat, cutoff, fs, order)
	xaxis = -cdata.x.loc[:,setNum]
	xaxis = xaxis[~np.isnan(xaxis)]
	ydat = ydat[~np.isnan(ydat)]
	data = data[~np.isnan(data)]
	temp1 = xaxis[0:len(xaxis) - 1]
	temp2 = xaxis[1:len(xaxis)]
	xaxisDiff = (np.array(temp1) + np.array(temp2)) / 2
	fullGrad = np.diff(data)/np.diff(xaxis)
	# loops through the data stream numit times
	for iteration in range(numit):
		plt.close()
		if calcForecast == True:
			# instantiate forecast class
			forecast = Forecast(lag, bars, xaxis, data)
				# #====Plot Change in Threshold vs Iteration
			if plotForecast == True:
				plt.subplot(2,1,1)
		if plotGrad == True:
			plt.subplot(3,1,1)
		plt.axvline(x=expected)
		plt.axvline(x=xaxisDiff[skip-window],c='g')
				# plt.scatter(iteration, threshHolder[iteration])
		plt.plot(xaxis, ydat)
		# if debugOut == True:
		# 	print(iteration)

		currentGrad = None
		currentThresh = None
		pointTrack = None

		if plotGrad == True:
			plt.subplot(3,1,2)
			plt.plot(xaxisDiff,fullGrad)
		# #=========================================
		# loops through the data stream
		for i in range(skip-window,len(fullGrad)):
			if i < window:
			   pass
			else:
				winDatay = data[i-window:i]
				winDatax = xaxis[i-window:i]
				grad = np.diff(winDatay)/np.diff(winDatax)
				xdif = np.mean(winDatax)

				if calcForecast == True:
					# winDatay1 = data[0:i]
					# winDatax1 = xaxis[0:i]
					# forecasting data
					forecast.forecast(i)
					if plotForecast:
						if i > lag + 1:
							plt.subplot(2, 1, 1)
							plt.plot(xaxis[i],forecast.low,".")
							plt.plot(xaxis[i],forecast.up,".")
					if forecast.hit == True:
						if plotForecast == True:
							plt.axvline(x=xaxis[i])
						# plt.show()
						# print(forecast.hit)
				if plotGrad == True:
					# #=====Plot Error vs Iteration
					# plt.subplot(2,1,2)
					# plt.plot(xaxis, data)
					plt.subplot(3,1,2)
					plt.axvline(x=expected)
					plt.axvline(x=xaxisDiff[skip-window],c='g')
					if not currentThresh == None:
						currentThresh.remove()
					currentThresh = plt.axhline(y=threshHolder[iteration])
					# plt.plot(winDatax, grad)
					# plt.subplot(3, 1, 2)
					# plt.plot(winDatax, winDatay)
					# plt.subplot(3, 1, 3)
					if not pointTrack == None:
						pointTrack.remove()
					pointTrack = plt.scatter(xaxisDiff[i], fullGrad[i],c='g',s=16)
					plt.subplot(3,1,3)
					if not currentGrad == None:
						currentGrad.remove()
					currentGrad = plt.axhline(y=grad,color='r')
					plt.axhline(y=threshHolder[iteration])


				# #============================
				# if no drops detected, set the point to the last one
				#Otherwise we would lower the threshold infinitely
				if i >= len(fullGrad)-1:
					drop = len(fullGrad) - 1
					direction = -direction
					threshHolder = np.append(threshHolder, threshHolder[iteration]+direction*delta)
					errorHolder= np.append(errorHolder,9001)

				# If we find a threshold save to dataframe
				if(grad < threshHolder[iteration]):
					# detected x value of drop
					drop = xaxisDiff[i]
					if plotGrad == True:
						plt.subplot(3,1,1)
						plt.axvline(x=drop,color='r')
						plt.subplot(3,1,2)
						plt.axvline(x=drop,color='r')
						plt.pause(.01)
					if drop == xaxisDiff[skip-window]:
						direction = -direction
					diff = expected - drop
					errorHolder= np.append(errorHolder,np.power(diff,2))
					# #=====DEBUG OUTPUT======
					if debugOut:
						print("===== Iteration" + str(iteration) + " =====")
						print("The error is: " + str(errorHolder[iteration]))
						print("expected: "+str(expected) + "    got: "+str(drop))
						print("The threshold is: " + str(threshHolder[iteration]))
					# #=======================

					# attempt to correct course after first iteration
					# had issues where first threshold is below the threshold
					# or giving large error, so the threshold would move
					#in the wrong direction since the following
					# code that changes direction only looks at the current
					# and previous error values.
					if iteration == 1:
						# if the difference is large, chances are we 
						# are hitting early, so lower the threshold
						if diff > 5:
							direction = -1 
						else:
							direction = 1
					# # change direction of threshold if L2 error is large
					# if iteration > 1:
					# 	change = errorHolder[iteration] - errorHolder[iteration-1]
					# 	# print("The error changed by: "+str(change))
					# 	if change > 0:
					# 		# print("Changing Direction")
					# 		direction = - direction
					threshHolder = np.append(threshHolder, threshHolder[iteration]+direction*delta)
					# #===DEBUG OUTPUT===
					if debugOut:
						if direction > 0:
							print("Increasing Threshold from "+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
						else:
							print("Decreasing Threshold from "+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
					# #==================
					if (iteration >= numit - 1):
						# print("the iteration is" + str(iteration))
						# find possible thresholds values
						index_min = np.amin(errorHolder)
						# get location of minimum error values
						minLoc = np.where(errorHolder == index_min)
						# the entire array of possible values
						possThresh = threshHolder[minLoc]
						# removed duplicates
						possThresh = np.unique(possThresh)
						distFromTarget = index_min
						distFromTarget = np.unique(distFromTarget)
						if(distFromTarget.size):
							distance = distance.append([[distFromTarget]],ignore_index = True)
						else:
							distFromTarget = None
							distance = distance.append([[0]],ignore_index = True)
						# #====ENDING DEBUG====
						if debugOut:
							print("final iteration")
							print("errors:")
							print(errorHolder)
							print("possible threshold are:  ")
							print(possThresh)
						# #====================
						if(possThresh.size):
							possThreshList = possThreshList.append([possThresh],ignore_index = True)
						else:
							possThreshList = possThreshList.append([[0]],ignore_index = True)
					if plotFig == True:
						plt.draw()
						plt.pause(0.0001)
					break
				if plotFig == True:
					# plt.draw()
					plt.pause(0.0001)
					#To keep processors from spazzing out and giving crap values
					# sleep(.00001)
if plotFig == True:
	plt.show()
# Finish up and Send data to excel files
# Be sure to change the path on your computer
# The following will overwrite files
# be sure to rename any important previous runs
print("Finished. Moving to Excel File")
outputname = "thresholds.xlsx"
filepath = '/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/Classification/DataOutput/' + outputname
possThreshList.to_excel(filepath, sheet_name = 'Sheet1')

outputname = "distance.xlsx"
filepath = '/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/Classification/DataOutput/' + outputname
distance.to_excel(filepath, sheet_name = 'Sheet1')

