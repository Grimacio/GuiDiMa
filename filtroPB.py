from scipy.signal import butter, lfilter
import pandas
from tkinter import filedialog
import csv
import os 
from tkinter.filedialog import askdirectory

def butter_bandpass(lowcut, highcut, fs, order=5):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 1000
    lowcut = 80.0
    highcut = 499

    # Filter a noisy signal.
    x =  pandas.read_csv(filedialog.askopenfilename())["ACCraw"]
    nsamples = len(x)
    t = np.arange(0, nsamples) / fs
    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)

    path= askdirectory(title= "Select Folder")
    name=input("File name?: \n")
    i=1
    while os.path.exists(path+"/"+name+".csv"):
        name=name+str(i)
        i+=1
    name+=".csv"
    file    = open(path+"/"+name, "a", newline="")
    csv.writer(file).writerow(["Nsample","Timestamp", "ACCraw", "EMGfilter"])
    writer=csv.writer(file)

    for index in range(len(x)):
        writer.writerow([index, index/fs, x[index], y[index]])