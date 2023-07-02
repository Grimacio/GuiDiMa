from scipy.signal import butter, lfilter
import pandas
from tkinter import filedialog
import csv
import os 
from tkinter.filedialog import askdirectory
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz

def butter_bandpass(lowcut, highcut, fs, order=5):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def notch_filter(data, cutoff, q_factor, fs):
    # Normalize cutoff frequency and compute angular frequency
    norm_cutoff = cutoff / (0.5 * fs) 
    b, a = butter(2, [norm_cutoff - 1/(2*q_factor), norm_cutoff + 1/(2*q_factor)], btype='bandstop')
    filtered_data = lfilter(b, a, data)
    return filtered_data



# Sample rate and desired cutoff frequencies (in Hz).
fs = 1000
lowcut = 10
highcut = 499
cutoff=50

folder_path = askdirectory(title = "Pasta Inicial")
file_list = os.listdir(folder_path)
excel_files = [file for file in file_list if file.endswith('.csv')]

path= askdirectory(title = "Pasta Final")
for file in excel_files:
    # Filter a noisy signal.
    aberto=pandas.read_csv(folder_path+"/"+file)
    x =  aberto["EMGraw"]
    x =  (x-3800/2)*3.3/3800*1000
    nsamples = len(x)
    t = np.arange(0, nsamples) / fs
    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
    y = notch_filter(y, cutoff, 10, fs)
    #path= askdirectory(title= "Select Folder")
    name = file.replace(".csv", "")+"_filt"
    i=1
    while os.path.exists(path+"/"+name+".csv"):
        name=name+str(i)
        i+=1
    name+=".csv"
    file_new  = open(path+"/"+name, "a", newline="")
    csv.writer(file_new).writerow(["Nsample","Timestamp", "EMGraw", "EMGfilter", "Class"])
    writer=csv.writer(file_new)
    classif = aberto["Class"]
    for index in range(len(x)):
        writer.writerow([index+1, (index+1)/fs, x[index], y[index], classif[index]])