import os
import pandas as pd
from tkinter.filedialog import askdirectory
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter



def sliding_rms(values, window_size):
    num_windows = len(values) - window_size + 1
    shape = (num_windows, window_size)
    strides = (values.itemsize, values.itemsize)
    windows = np.lib.stride_tricks.as_strided(values, shape=shape, strides=strides)
    squared_values = windows**2
    rms_values = np.sqrt(np.mean(squared_values, axis=1))
    return rms_values

#   Recebe um array x e uma dimensao N e aplica um filtro de Root Mean Square numa janela de N amostras
def rolling_rms(x, N):
  return (pd.DataFrame(abs(x)**2).rolling(N).mean())**0.5


folder_path = askdirectory(title = "Select Folder")  # Replace with the path to your folder

# Get a list of all files in the folder
file_list = os.listdir(folder_path)

# Filter the list to only include CSV files
excel_files = [file for file in file_list if file.endswith('.csv')]

Tensor = {}
Features = {}
blocks = ["A","B","D","N","P","PP","K","L"]
for a in blocks:
    Tensor[a] = []
    Features[a] = []

# Iterate over each CSV file
for file in excel_files:
    file_path = os.path.join(folder_path, file)  # Create the full file path
    df = pd.read_csv(file_path)  # Read the Excel file into a DataFrame


    temp_block = np.empty((0,5))
    current_class = ""

    for i in range(len(df)):

        if i == 0:
            current_class = str(df.loc[i, 'Class'])

        if str(df.loc[i, 'Class']) == current_class:
            temp_block = np.append(temp_block, [df.iloc[i]], axis=0)
            
            if i == len(df):
                Tensor[current_class] += [temp_block]
                temp_block=np.empty((0,5))

        else:

            if current_class not in ['L','K','P','PP']:
                EMG_aux = temp_block[:,3]

                if current_class not in ['K','P','PP']:
                    window_size = 50

                else:
                    window_size = 350
                
                EMG_abs = abs(EMG_aux)
                plt.subplot(1,2,1)
                plt.plot(EMG_abs)
                EMG_abs = rolling_rms(abs(EMG_aux), window_size)
                plt.subplot(1,2,2)
                plt.plot(EMG_abs)
                plt.show()  

                fft_result = np.abs(np.fft.fft(EMG_aux))
                #freq = np.fft.fftfreq(len(EMG_aux),1/1000)

                mean = np.mean(EMG_abs)
                stdev = np.std(EMG_abs)
                rms = np.sqrt(np.mean(EMG_abs**2))
                
                

                #Features[current_class] += [[mean,stdev,rms,freq,fft_result]]

            if current_class not in Tensor:
                Tensor[current_class] = [temp_block]

            else:
                Tensor[current_class] += [temp_block]
            
            temp_block=np.empty((0,5))
            current_class = str(df.loc[i, 'Class'])


#Results     
print(Features["K"][0][4])
print(Features["K"][0][3])
smoothed_data = savgol_filter(Features["K"][0][4][:round(len(Features["K"][0][3])/2)], 20, 2)
plt.plot(Features["K"][0][3][:round(len(Features["K"][0][3])/2)],smoothed_data)
plt.show()        
        
        
