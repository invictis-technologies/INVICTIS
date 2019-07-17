from clean_data_chpPadRaw import clean_data
import numpy as np
from matplotlib import pyplot as plt
# c = clean_data()
# c.clean("/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/ChpPadRaw/1mms","1mmsout.xlsx",False)
xaxis = [1, 2, 3 , 4, 5, 6, 7, 8,  9,10]
data = [2,4,5,16,32,16,5,4,2,1]
temp1 = xaxis[0:len(xaxis) - 1]
temp2 = xaxis[1:len(xaxis)]
xaxisDiff = (np.array(temp1) + np.array(temp2)) / 2
fullGrad = np.diff(data)/np.diff(xaxis)

print(temp1)
print(temp2)
print(xaxisDiff)
print(fullGrad)
print(np.diff(data))
print(np.diff(xaxis))
plt.plot(xaxisDiff, fullGrad)
plt.show()