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
blocks = ["A","B","D","N","P","PP","K", "L"]
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

            if current_class != "L":
                EMG_aux = temp_block[:,3]

                if current_class not in ['K','P','PP']:
                    window_size = 50

                else:
                    window_size = 350
                
                EMG_abs = abs(EMG_aux)
                dimension= len(EMG_abs)
                EMG_abs = rolling_rms(abs(EMG_aux), window_size)

                mean = np.mean(EMG_abs)
                #stdev = (str(np.std(EMG_abs)).split(" ")[4]).split('/')[0]
                stdev = np.std(EMG_aux)
                rms = np.sqrt(np.mean(EMG_abs**2))

                power_spectrum = (np.abs(np.fft.fft(EMG_aux))**2 / len(EMG_aux))
                freq = np.fft.fftfreq(len(EMG_aux),1/1000)
                freq_cut=freq[:round(len(freq)/2)]
                power_spectrum = abs(savgol_filter(power_spectrum[:round(len(freq)/2)], 20, 2))

                power_integral = sum(power_spectrum*(freq[1]-freq[0]))

                power_spectrum = power_spectrum/np.sum(power_spectrum)
                cumulative_sum = np.cumsum(power_spectrum)

                mean_frequency = np.average(freq_cut, weights=power_spectrum)
                median_index = np.searchsorted(cumulative_sum, 0.5)
                peak = freq_cut[np.argmax(power_spectrum)]

                percent = 0.30
                lower_bound= np.searchsorted(cumulative_sum,0.5-percent/2)
                higher_bound= np.searchsorted(cumulative_sum,0.5+percent/2)
                interval=[freq_cut[lower_bound], freq_cut[higher_bound]]
                print(float(stdev))
                Features[current_class] += [[dimension, mean, float(stdev) ,rms, power_integral, interval, peak, mean_frequency, freq_cut[median_index]]]

            if current_class not in Tensor:
                Tensor[current_class] = [temp_block]

            else:
                Tensor[current_class] += [temp_block]
            
            temp_block=np.empty((0,5))
            current_class = str(df.loc[i, 'Class'])


data=[[]]
for key, value in Features.items(): 
    
    if len(value)!=0:

        for j in value:
            data += [[str(key)]+j]

dataframe = pd.DataFrame(data, columns=["Class", "Dimension", "mean",  "stdev", "rms", "integralP", "Fint", "Fmax", "Fmean", "Fmedian"])
dataframe.to_excel("Doente.xlsx", index=False)


