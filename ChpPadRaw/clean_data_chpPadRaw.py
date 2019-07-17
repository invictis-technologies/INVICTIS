import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import glob
from time import sleep
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
		self.expected = None

	def clean(self,folderPath, outputname, outputBool):
		# f = filename
		# get current working directory
		path = os.getcwd()
		# get all files in cwd
		files = os.listdir(path)
		# construct array for dataframes
		data = {}
		regex = folderPath + "/*.xlsx"
		allData = pd.DataFrame()
		for f in glob.glob(regex):
			# construct pd dataframe
			data = pd.DataFrame()
			# add data to df
			data = pd.read_excel(f)
			# remove extraneous columns by index
			colsToRemove = [0,3,4]
			data = data.drop(data.columns[colsToRemove], axis=1)
			# replace units in row 0 and zero vals in row 1:3
			cols = [0,1]
			data.loc[[0,1,2,3],data.columns[cols]] = np.nan
			allData = pd.concat([allData,data],axis=1)
		if outputBool == True:
			filepath = '/Users/robertshi/Desktop/S\'19/Invictis/data_analysis/ChpPadRaw/' + outputname
			allData.to_excel(filepath, sheet_name = 'Sheet1')
		# storing columns of x, y, and expected
		colHeaders = np.array(allData.columns.tolist())
		c = np.arange(0,allData.shape[1]-2,3)
		x = allData.iloc[:,c]
		x.columns = np.arange(x.shape[1])
		y = allData.iloc[:,c+1]
		y.columns = np.arange(y.shape[1])
		expected = allData.iloc[:,c+2]
		expected.columns = np.arange(expected.shape[1])
		self.x = x
		self.y = y
		self.expected = expected


