import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data import clean_data
from scipy.signal import butter, lfilter, freqz
from scipy import zeros, signal, random, stats

# turn off matplot lib warning of potential problems in future versions
import warnings
warnings.filterwarnings("ignore")

cdata = clean_data()
cdata.clean("Good.xlsx","Sheet1", None, 0)
exp = pd.DataFrame()
exp = pd.read_excel("dropLocations.xlsx","Sheet1")
exp1 = exp.loc[:,1]
length = cdata.x.shape[1]

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

def update_line(pl, new_data):
	p1.set_xdata(np.append(p1.get_xdata(), new_data))
	p1.set_ydata(np.append(p1.get_ydata(), new_data))
	plt.draw()
	plt.pause(0.1)

# Filter requirements.
order = 2
fs = 10      # sample rate, Hz
cutoff = .8  # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
# b, a = butter_lowpass(cutoff, fs, order)

# number of set of data in dataframe
setNum = 20
# window size(for plot asthetic)
window = 2
# number of iterations
numit = 1
# initial threshold
thresh = -2.85*np.power(10.0,-3)
# stepsize
delta = .0005
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
# create data frame to store potential thresholds
possThreshList = pd.DataFrame(columns=list(range(numit)))
# lag
lag = 20
# bar distance
bars = .03
# slope holder
prevSlope = 0
prevIntc = 0

# for iteration in range(numit):
for iteration in range(numit):
	ydat = cdata.y.loc[:,setNum]
	data = butter_lowpass_filter(ydat, cutoff, fs, order)
	xaxis = cdata.x.loc[:,setNum]

	plt.subplot(3,1,1)
	plt.plot(-xaxis, -ydat)
		# break
	# plt.axvline(x=expected)
	for i in range(data.shape[0]):
		if i < window:
		   pass
		else:
			winDatay = data[i-window:i]
			winDatax = xaxis[i-window:i]
			# forecasting
			if i >= lag:
				lagarry = -data[i-lag:i]
				lagarrx = -xaxis[i-lag:i]
				slope, intc, r_val, pval, stderr = stats.linregress(lagarrx,lagarry)
				if i >= lag+1:
					# check prediction
					diff = -xaxis[i]--xaxis[i-1]
					forecast = -xaxis[i]*prevSlope+prevIntc
					lower = forecast - bars
					upper = forecast + bars
					plt.subplot(3,1,1)
					plt.plot(-xaxis[i],lower,".")
					plt.plot(-xaxis[i],upper,".")
					if -data[i] >= upper or -data[i] <= lower:
						plt.subplot(3,1,1)
						plt.axvline(x=-xaxis[i])
				xchunk = np.linspace(-xaxis[i],-xaxis[i]+.01,10)
				prevSlope = slope
				prevIntc = intc
				# slp = slope*xchunk
				# plt.subplot(3,1,1)
				# plt.plot(xchunk,slp+bars)
				# plt.plot(xchunk,slp-bars)
			# winDatay1 = data[0:i]
			# winDatax1 = xaxis[0:i]
			plt.subplot(3, 1, 2)
			plt.plot(-winDatax, -winDatay)
			plt.subplot(3, 1, 3)
			grad = np.gradient(-winDatay)
			plt.plot(-winDatax, grad)
			if(grad[1] < threshHolder[iteration]):
				# detected x value of drop
				drop = -xaxis[i]
				plt.axvline(x=drop)
				diff = expected - drop
				errorHolder= np.append(errorHolder,np.power(diff,2))
				# choose direction to go
				print("===== Iteration" + str(iteration) + " =====")
				print("The error is: " + str(errorHolder[iteration]))
				print("expected: "+str(expected) + "    got: "+str(drop))
				print("The threshold is: " + str(threshHolder[iteration]))
				if iteration > 1:
					change = errorHolder[iteration] - errorHolder[iteration-1]
					print("The error changed by: "+str(change))
					if change > 0:
						print("Direction Changed")
						direction = - direction
				threshHolder = np.append(threshHolder, threshHolder[iteration]+direction*delta)
				if direction > 0:
					print("Increasing Threshold from "+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
				else:
					print("Decreasing Threshold"+str(threshHolder[iteration])+" to "+str(threshHolder[iteration+1]))
				if iteration == numit - 1:
					# find possible thresholds values
					index_min = np.amin(errorHolder)
					# get location of minimum error values
					minLoc = np.where(errorHolder == index_min)
					possThresh = threshHolder[minLoc]
					print("final iteration")
					print("errors:")
					print(errorHolder)
					print("possible threshold are:  ")
					print(possThresh)
					possThreshList = possThreshList.append([possThresh],ignore_index = True)
				# break
			# plt.axvline(x=expected)
			plt.pause(0.00001)
			plt.draw()
	print(possThreshList)
	
# Filter the data, and plot both the original and filtered signals.
# y = butter_lowpass_filter(data, cutoff, fs, order)

# ========END HONOR CODE VIOLIATION==============


