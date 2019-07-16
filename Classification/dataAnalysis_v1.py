import os
import numpy as np
from matplotlib import pyplot as pp
import pandas as pd

# get current working directory
path = os.getcwd()
# get all files in cwd
files = os.listdir(path)
# serach filenames and get all xlsx extensions
files_xlsx = [f for f in files if f[-4:] == 'xlsx']
#output order of files to txt file
j = 0
with open('fileOrder.txt','a') as out:
	for f in files_xlsx:
		out.write(str(j)+":  "+f+"\r\n")
		j = j + 1
# construct array for dataframes
data = {}
i = 0
# loop through files and add to df
for f in files_xlsx:
	# construct pd dataframe
	data[i] = pd.DataFrame()
	sheetName = f[0:-5:]
	if len(sheetName) >= 31:
		sheetName = sheetName[0:31]
	print(sheetName)
	data[i] = pd.read_excel(f, sheetName)
	i = i + 1
