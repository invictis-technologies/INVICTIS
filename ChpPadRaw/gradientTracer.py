import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data_chpPadRaw import clean_data
from scipy.signal import butter, lfilter, freqz
from scipy import zeros, signal, random

class gradientTracer:
	def __init__(self,possThreshList, distance,thresh, window, skip, delta, numit, plotGrad, debugOut):
		self.plotGrad = plotGrad
		self.debugOut = debugOut
		# knows number of iterations
		self.numit = numit
		# window size of tracking gradient
		self.window = window
		# stepsize
		self.delta = delta
		# skip first n datapoints due to lowpass noise
		self.skip = skip
		# create data frame to store potential thresholds
		self.possThreshList = possThreshList
		#create a data frame to store error from expected
		self.distance = distance
		# threshold tracker
		self.threshHolder = np.empty(0)
		# error holder
		self.errorHolder = np.empty(0)
		# direction(+/- 1)
		self.direction = 1
		# put in first threshold value
		self.threshHolder = np.append(self.threshHolder, thresh)
		# set up data arrays

	# takes a smoothed curve and calculates the entire fradient
	# used mainly for plotting asthetic
	def calculateFullGrad(self, xaxis, data):
		temp1 = xaxis[0:len(xaxis) - 1]
		temp2 = xaxis[1:len(xaxis)]
		xaxisDiff = (np.array(temp1) + np.array(temp2)) / 2
		fullGrad = np.diff(data)/np.diff(xaxis)
		return xaxisDiff, fullGrad
	# takes windows of a smoothed curve and processes the data
	# as it reads.
	def calculatePartialGrad(self, i, iteration, xaxis, data, xaxisDiff, fullGrad):
		winDatay = data[i-self.window:i]
		winDatax = xaxis[i-self.window:i]
		grad = np.diff(winDatay)/np.diff(winDatax)
		xdif = np.mean(winDatax)
		return xdif, grad
	# updates threshold
	def updateThreshold(self, iteration):
		self.threshHolder = np.append(self.threshHolder, self.threshHolder[iteration]+self.direction*self.delta)
	# updates lists to be output in excel file
	def updateLists(self):
		# print("the iteration is" + str(iteration))
		# find possible thresholds values
		index_min = np.amin(self.errorHolder)
		# get location of minimum error values
		minLoc = np.where(self.errorHolder == index_min)
		# the entire array of possible values
		possThresh = self.threshHolder[minLoc]
		# removed duplicates
		possThresh = np.unique(possThresh)
		distFromTarget = index_min
		distFromTarget = np.unique(distFromTarget)
		if(distFromTarget.size):
			self.distance = self.distance.append([[distFromTarget]],ignore_index = True)
		else:
			distFromTarget = None
			self.distance = self.distance.append([[0]],ignore_index = True)
		if(possThresh.size):
			self.possThreshList = self.possThreshList.append([possThresh],ignore_index = True)
		else:
			self.possThreshList = self.possThreshList.append([[0]],ignore_index = True)	
	# Finds where the data crosses the deriviative threshold
	def detectDrops(self, i, iteration, xaxisDiff,fullGrad, grad, expected):
		# #============================
		# if no drops detected, set the point to the last one
		#Otherwise we would lower the threshold infinitely
		if i >= len(fullGrad)-1:
			drop = len(fullGrad) - 1
			self.direction = -self.direction
			self.updateThreshold(iteration)
			self.errorHolder= np.append(self.errorHolder,9001)
			if self.debugOut:
				print("===== Iteration" + str(iteration) + " =====")
				print("The error is: " + str(self.errorHolder[iteration]))
				print("expected: "+str(expected) + "    got: "+str(drop))
				print("The threshold is: " + str(self.threshHolder[iteration]))
		# If we find a threshold save to dataframe
		if(grad < self.threshHolder[iteration]):
			# detected x value of drop
			drop = xaxisDiff[i]
			if self.plotGrad == True:
				plt.subplot(3,1,1)
				plt.axvline(x=drop,color='r')
				plt.subplot(3,1,2)
				plt.axvline(x=drop,color='r')
				plt.pause(.01)
			if drop == xaxisDiff[self.skip-self.window]:
				self.direction = -self.direction
			diff = expected - drop
			self.errorHolder= np.append(self.errorHolder,np.power(diff,2))

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
					self.direction = -self.direction
				else:
					self.direction = self.direction
			self.updateThreshold(iteration)
			if self.debugOut:	
				if self.direction > 0:
					print("Increasing Threshold from "+str(self.threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
				else:
					print("Decreasing Threshold from "+str(self.threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
			if (iteration >= self.numit - 1):
				self.updateLists()
			return True, self.possThreshList, self.distance
		return False, self.possThreshList, self.distance
	def xlsxOut(self, dataFolder):
		# Finish up and Send data to excel files
		# Be sure to change the path on your computer
		# The following will overwrite files
		# be sure to rename any important previous runs
		print("Finished. Moving to Excel File")
		outputname = "thresholds.xlsx"
		filepath = '/Users/<<Insert path here>>/INVICTIS/ChpPadRaw/DataOutput/' + dataFolder+'_' + outputname
		self.possThreshList.to_excel(filepath, sheet_name = 'Sheet1')

		outputname = "distance.xlsx"
		filepath = '/Users/<<Insert Path here>>/INVICTIS/ChpPadRaw/DataOutput/' + dataFolder +'_'+ outputname
		self.distance.to_excel(filepath, sheet_name = 'Sheet1')
