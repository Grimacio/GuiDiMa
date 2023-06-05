import os
import pandas as pd
from tkinter.filedialog import askdirectory
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

folder_path = askdirectory(title = "Select Folder")  # Replace with the path to your folder

# Get a list of all files in the folder
file_list = os.listdir(folder_path)
print(file_list)
# Filter the list to only include Excel files
excel_files = [file for file in file_list if file.endswith('.csv')]

Tensor = {}
Features = {}
blocks = ["A","B","D","N","P","PP","K","L"]
for a in blocks:
    Tensor[a] = []
    Features[a] = []
print(Tensor)
# Iterate over each Excel file
for file in excel_files:
    file_path = os.path.join(folder_path, file)  # Create the full file path
    df = pd.read_csv(file_path)  # Read the Excel file into a DataFrame

    temp_block=np.empty((0,5))
    current_class = ""
    for i in range(len(df)):
        if i == 0:
            current_class = str(df.loc[i, 'Class'])
           # print(str(df.loc[i, 'Class']))
        if str(df.loc[i, 'Class']) == current_class:
            temp_block = np.append(temp_block, [df.iloc[i]], axis=0)
            
            if i == len(df):
                Tensor[current_class] += [temp_block]
                temp_block=np.empty((0,5))
        else:
            mean = np.mean(temp_block[:,3])
            hiv = np.std(temp_block[:,3])
            rms = np.sqrt(np.mean(temp_block[:,3]**2))
            
            fft_result = np.abs(np.fft.fft(temp_block[:,3]))
            freq = np.fft.fftfreq(len(temp_block[:,3]),1/1000)

            Features[current_class] += [[mean,hiv,rms,freq,fft_result]]

            if current_class not in Tensor:
                Tensor[current_class] = [temp_block]
            else:
                Tensor[current_class] += [temp_block]
            
            temp_block=np.empty((0,5))
            current_class = str(df.loc[i, 'Class'])
            
print(Features["K"][0][4])
print(Features["K"][0][3])
smoothed_data = savgol_filter(Features["K"][0][4][:round(len(Features["K"][0][3])/2)], 20, 2)
plt.plot(Features["K"][0][3][:round(len(Features["K"][0][3])/2)],smoothed_data)
plt.show()        
        
        
