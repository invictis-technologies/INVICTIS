import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data_chpPadRaw import clean_data
from scipy.signal import butter, lfilter, freqz
from scipy import zeros, signal, random
from time import sleep
from forecast import Forecast
from gradientTracer import gradientTracer

print("Beginning...")
calcForecast = True
calcGradient = False
plotFig = True
debugOut = False
# plots either forecast or gradient or no plots
# ==========PLOT CONTROLLER========
if calcForecast == True and plotFig == True:
	plotForecast = True
	plotGrad = False
if calcGradient == True and plotFig == True:
	plotForecast = False
	plotGrad = True
elif plotFig == False:
	plotForecast = False
	plotGrad = False
# =================================
# turn off matplot lib warning of potential problems in future versions
import warnings
warnings.filterwarnings("ignore");
dataFolder = "1mms"
# clean the data using clean_data.py
cdata = clean_data()
# arguments of filename.xlsx string, sheet name string, 
# cleanOutputFilename(.xlsx) string, and boolean for whether 
# or not you want to output to file: 0 = false, 1 = true
cdata.clean("/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/ChpPadRaw/" + dataFolder,None, 0)
# exp = pd.DataFrame()
# exp = pd.read_excel("dropLocations.xlsx","Sheet1")
# exp1 = exp.loc[:,1]
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

def processData(setNum, expected):
		ydat = -np.array(cdata.y.iloc[:,setNum])
		xaxis = -np.array(cdata.x.iloc[:,setNum])
		pd.to_numeric(xaxis, errors='coerce')
		xaxis = pd.to_numeric(xaxis, downcast='float')
		xaxis = xaxis[~np.isnan(xaxis)]
		ydat = pd.to_numeric(ydat, downcast='float')
		ydat = ydat[~np.isnan(ydat)]
		data = butter_lowpass_filter(ydat, cutoff, fs, order)
		data = data[~np.isnan(data)]
		return xaxis, ydat, data, 

# Filter requirements. (Butterworth filter)
order = 1
fs = 10      # sample rate, Hz
cutoff = 1.5  # desired cutoff frequency of the filter, Hz
# lag
lag = 20
# bar distance
bars = .02
#skip a number of datapoints before windowing
skip = 20
# window size(for plot asthetic)
window = 2
# initial threshold
thresh = -2.85*np.power(10.0,-3)
# number of iterations
if plotGrad:
	numit = 100
elif plotForecast:
	numit = 1
# stepsize
delta = 0.005

# create data frame to store potential thresholds
possThreshList = pd.DataFrame(columns=list(range(numit)))
#create a data frame to store error from expected
distance = pd.DataFrame(columns=list(range(1)))

# =====Start Analysis=====
# number of set of data in dataframe
# for setNum in [23]:
for setNum in range(length):
	g = gradientTracer(possThreshList, distance, thresh, window, skip, delta, numit, plotGrad, debugOut)
	print("Data Set: " + str(setNum))
	#expected value
	expected = np.array(cdata.expected.iloc[:,setNum])
	if not 'bad' in expected:
		# threshold tracker
		g.threshHolder = np.empty(0)
		# error holder
		g.errorHolder = np.empty(0)
		# direction(+/- 1)
		g.direction = 1
		# put in first threshold value
		g.threshHolder = np.append(g.threshHolder, thresh)
		pd.to_numeric(expected, errors='coerce')
		expected = expected[~np.isnan(expected)]
		expected = expected[0]
		xaxis, ydat, data = processData(setNum, expected)
		xaxisDiff, fullGrad = g.calculateFullGrad(xaxis,data)
		# loops through the data stream numit times
		for iteration in range(numit):
			plt.close()
			if calcForecast == True:
				# instantiate forecast class
				forecast = Forecast(lag, bars, xaxis, data)
					# #====Plot Change in Threshold vs Iteration
				if plotForecast == True:
					plt.subplot(2,1,1)
			if calcGradient == True:
				currentGrad = None
				currentThresh = None
				pointTrack = None
			# #=========================================
			# loops through the data stream
			for i in range(skip-window,len(fullGrad)):
				if i < window:
				   pass
				else:
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
					if calcGradient == True:
						xdif, grad = g.calculatePartialGrad(i, iteration, xaxis, data, xaxisDiff, fullGrad)
						dropDetected, possThreshList, distance = g.detectDrops(i, iteration, xaxisDiff, fullGrad, grad, expected)	
						if dropDetected:
							break
						# #====DEBUG====
						if plotGrad == True:
							plt.subplot(3,1,1)
							plt.axvline(x=expected)
							plt.axvline(x=xaxisDiff[skip-window],c='g')
							plt.plot(xaxis, ydat, c='c')
							# plt.plot(xaxis, data,'-', color = 'm')
							plt.subplot(3,1,2)
							plt.plot(xaxisDiff,fullGrad,c='c')
							plt.subplot(3,1,2)
							plt.axvline(x=expected)
							plt.axvline(x=xaxisDiff[skip-window],c='g')
							if not currentThresh == None:
								currentThresh.remove()
							currentThresh = plt.axhline(y=g.threshHolder[iteration])
							if not pointTrack == None:
								pointTrack.remove()
							pointTrack = plt.scatter(xaxisDiff[i], fullGrad[i],c='g',s=16)
							plt.subplot(3,1,3)
							if not currentGrad == None:
								currentGrad.remove()
							currentGrad = plt.axhline(y=grad,color='r')
							plt.axhline(y=g.threshHolder[iteration])
						if debugOut == True:
							print("final iteration")
							print("errors:")
							print(errorHolder)
							print("possible threshold are:  ")
							print(possThresh)
							# #====================	
					if plotFig == True:
						plt.pause(0.0001)
						# plt.draw()
						plt.pause(0.0001)
						#To keep processors from spazzing out and giving crap values
						# sleep(.00001)
	else:
		if calcGradient == True:
			print("has been yeeted")
			distance = distance.append([['skipped']],ignore_index = True)
			possThreshList = possThreshList.append(["skipped"],ignore_index = True)

if plotFig == True:
	plt.show()
if calcGradient == True:	
	g.xlsxOut(dataFolder)