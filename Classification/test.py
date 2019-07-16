import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from clean_data import clean_data
from scipy.signal import butter, lfilter, freqz


cdata = clean_data()
cdata.clean("Good.xlsx","Sheet1", None, 0)
exp = pd.DataFrame()
exp = pd.read_excel("dropLocations.xlsx","Sheet1")
exp1 = exp.loc[:,1]
length = cdata.x.shape[1]
print(cdata.x.shape)

# #for visual classification
# for i in range(1,length):
# 	plt.title("figure" + str(i))
# 	plt.plot(-cdata.x.loc[:,i], -cdata.y.loc[:,i], 'b-', label='data')
# 	plt.grid()
# 	print(exp1[i-1])
# 	plt.show()


# #plotting histogram to pad/truncate data.
# plt.plot(-a.x,-a.y)
# plt.show()
# len_sequences = []
# length = a.x.shape[1]
# for i in range(1,length):
# 	g = a.x.loc[:,i]
# 	len_sequences.append(len(g.dropna()))
# print(pd.Series(len_sequences).describe())
# hist= np.histogram(len_sequences, bins = 'auto')
# plt.hist(hist)  # arguments are passed to np.histogram
# plt.show()

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

# Filter requirements.
order = 2
fs = 10      # sample rate, Hz
cutoff = .8  # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Lowpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()

data = cdata.y.loc[:,65]
t = cdata.x.loc[:,65]
# Filter the data, and plot both the original and filtered signals.
y = butter_lowpass_filter(data, cutoff, fs, order)

# show plot
plt.subplot(2, 1, 2)
plt.plot(-t, -data, 'b-', label='data')
plt.plot(exp1[1],1,linewidth=10, label='stop')
plt.plot(-t, -y, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
print(exp1[0])
plt.grid()
plt.legend()
plt.subplots_adjust(hspace=0.35)
plt.show()
# ========END HONOR CODE VIOLIATION==============


