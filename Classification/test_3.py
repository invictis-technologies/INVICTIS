import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data import clean_data
from scipy.signal import butter, lfilter, freqz
from scipy import zeros, signal, random
from time import sleep

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

# Filter requirements. (Butterworth filter)
order = 5
fs = 10      # sample rate, Hz
cutoff = .8  # desired cutoff frequency of the filter, Hz

# =====Start Analysis=====

# number of set of data in dataframe
setNum = 0
# window size(for plot asthetic)
window = 2
# number of iterations
# numit = 500
numit = 500
# stepsize
# delta = .00001
delta = 0.00001
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
	# loops through the data stream numit times
	for iteration in range(numit):
		# #====Plot Change in Threshold vs Iteration
		plt.subplot(2,1,1)
		plt.scatter(iteration, threshHolder[iteration])
		plt.draw()
		plt.pause(0.0001)
		# #=========================================
		ydat = cdata.y.loc[:,setNum]
		data = butter_lowpass_filter(ydat, cutoff, fs, order)
		xaxis = cdata.x.loc[:,setNum]
		# loops through the data stream
		for i in range(data.shape[0]):
			if i < window:
			   pass
			else:
				winDatay = data[i-window:i]
				winDatax = xaxis[i-window:i]
				# winDatay1 = data[0:i]
				# winDatax1 = xaxis[0:i]
				grad = np.gradient(-winDatay)
				# #=====Plot Error vs Iteration
				# plt.subplot(2,1,2)
				# plt.plot(-winDatax, grad)
				# plt.axvline(x=expected)
				# plt.axhline(y=threshHolder[iteration])
				# #============================

				# if no drops detected, set the point to the last one
				#Otherwise we would lower the threshold infinitely
				if i >= data.shape[0]-1:
					drop = data.shape[0] - 1
					direction = 1
					threshHolder = np.append(threshHolder, threshHolder[iteration]+direction*delta)
					errorHolder= np.append(errorHolder,9001)
				# If we find a threshold save to dataframe
				if(grad[1] < threshHolder[iteration]):
					# detected x value of drop
					drop = -xaxis[i]
					diff = expected - drop
					errorHolder= np.append(errorHolder,np.power(diff,2))
					# #=====DEBUG OUTPUT======
					# print("===== Iteration" + str(iteration) + " =====")
					# print("The error is: " + str(errorHolder[iteration]))
					# print("expected: "+str(expected) + "    got: "+str(drop))
					# print("The threshold is: " + str(threshHolder[iteration]))
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
					# change direction of threshold if L2 error is large
					if iteration > 1:
						change = errorHolder[iteration] - errorHolder[iteration-1]
						# print("The error changed by: "+str(change))
						if change > 0:
							# print("Changing Direction")
							direction = - direction
					threshHolder = np.append(threshHolder, threshHolder[iteration]+direction*delta)
					# #===DEBUG OUTPUT===
					# if direction > 0:
					# 	print("Increasing Threshold from "+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
					# else:
					# 	print("Decreasing Threshold from "+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
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
						# print("final iteration")
						# print("errors:")
						# print(errorHolder)
						# print("possible threshold are:  ")
						# print(possThresh)
						# #====================
						if(possThresh.size):
							possThreshList = possThreshList.append([possThresh],ignore_index = True)
						else:
							possThreshList = possThreshList.append([[0]],ignore_index = True)
					break
				#To keep processors from spazzing out and giving crap values
				sleep(.00001)

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

