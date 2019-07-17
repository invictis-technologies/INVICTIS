import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
class Forecast:
	def __init__(self, lag, bars, xaxis, data):
		# slope holder
		self.prevSlope = 0
		# intercept holder
		self.prevIntc = 0
		# lag
		self.lag = lag
		# bars
		self.bars = bars
		# xaxis data
		self.xaxis = xaxis
		# data
		self.data = data
		self.hit = False
		self.up = 0
		self.low = 0
	# check detected datapoint against previous prediction 
	def checkForecast(self,i):
		self.hit = 0
		# check prediction
		diff = self.xaxis[i]-self.xaxis[i-1]
		forecast = self.xaxis[i]*self.prevSlope+self.prevIntc
		lower = forecast - self.bars
		upper = forecast + self.bars
		# plt.plot(self.xaxis[i],lower,".")
		# plt.plot(self.xaxis[i],upper,".")
		self.low = lower
		self.up = upper
		if self.data[i] >= upper or self.data[i] <= lower:
			# plt.subplot(3,1,1)
			# plt.axvline(x=self.xaxis[i])
			self.hit = True
	#takes a window of lag data points and predicts the next
	#uses something to determine boundaries for the projected data point
	def forecast(self, i):
		# forecasting
		if i >= self.lag:
			lagarry = self.data[i-self.lag:i]
			lagarrx = self.xaxis[i-self.lag:i]
			slope, intc, r_val, pval, stderr = stats.linregress(lagarrx,lagarry)
			if i >= self.lag+1:
				# plt.subplot(3, 1, 1)
				# plt.plot(xaxis[i],forecast.low,".")
				# plt.plot(xaxis[i],forecast.up,".")
				# plt.draw()
				# plt.pause(0.0001)
				self.checkForecast(i)
			xchunk = np.linspace(self.xaxis[i],self.xaxis[i]+.01,10)
			self.prevSlope = slope
			self.prevIntc = intc
