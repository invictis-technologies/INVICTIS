import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
#Strings
#arg 1 = filename with extension. 
#arg 2 = sheetname
#arg 3 = filename with extension
#Boolean
#arg 4 = Write data to excel file, True or false.

#make sure the first row of the file is numbered in ascending order

#returns two pandas dataframes one with x columns and one with y columns,
class clean_data:
	def __init__(self):
		self.x = pd.DataFrame()
		self.y = pd.DataFrame()

	def clean(self,filename, sheetName, outputname, outputBool):
		f = filename
		# get current working directory
		path = os.getcwd()
		# get all files in cwd
		files = os.listdir(path)
		# construct array for dataframes
		data = {}
		# add data to df
		# construct pd dataframe
		data = pd.DataFrame()
		data = pd.read_excel(f, sheetName)

		#removes the first 3 zeroed values all blank columns
		a = np.arange(1,data.shape[1]+1,1)
		b = np.arange(2,data.shape[1],3)
		index = np.delete(a,b)

		#save the data to a new xlsx file
		cleanData = data.loc[3::, index]
		x = cleanData.shape[0]
		xlabel = np.arange(x)
		# cleanData = cleanData.set_index(xlabel)
		# cleanDate = cleanData.reindex(columns=ylabel)
		cleanData = cleanData.reset_index(drop = True)
		y = cleanData.shape[1]
		ylabel = np.arange(y)
		cleanData.columns = ylabel
		# print(cleanData)
		if outputBool == True:
			filepath = '/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/Classification/' + outputname
			cleanData.to_excel(filepath, sheet_name = 'Sheet1')
		c = np.arange(0,cleanData.shape[1],2)
		x = cleanData.loc[:,c]
		x.columns = np.arange(x.shape[1])
		y = cleanData.loc[:,c+1]
		y.columns = np.arange(y.shape[1])
		self.x = x
		self.y = y



