from scipy.signal import butter, lfilter
import pandas
from tkinter import filedialog
import csv
import os 
from tkinter.filedialog import askdirectory
import numpy as np
from sklearn.decomposition import FastICA

def butter_bandpass(lowcut, highcut, fs, order=5):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def remove_ecg_using_ica(emg_signal):
    # Apply ICA to separate independent components
    ica = FastICA(n_components=2)  # Assuming ECG is one of the two components
    components = ica.fit_transform(emg_signal.reshape(-1, 1))

    # Identify ECG component based on correlation with the original signal
    correlations = np.corrcoef(emg_signal, components[:, 0])
    ecg_component = components[:, np.argmax(correlations[0, :])]

    # Remove ECG component from the original signal
    filtered_emg = emg_signal - ecg_component

    return filtered_emg


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 1000
    lowcut = 10
    highcut = 499

    while True:
        # Filter a noisy signal.
        x =  pandas.read_csv(filedialog.askopenfilename())["EMGraw"]
        nsamples = len(x)
        t = np.arange(0, nsamples) / fs
        y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
        filtered_emg = remove_ecg_using_ica(y)


        path= askdirectory(title= "Select Folder")
        name=input("File name?: \n")
        i=1
        while os.path.exists(path+"/"+name+".csv"):
            name=name+str(i)
            i+=1
        name+=".csv"
        file    = open(path+"/"+name, "a", newline="")
        csv.writer(file).writerow(["Nsample","Timestamp", "EMGraw", "EMGfilter"])
        writer=csv.writer(file)

        for index in range(len(x)):
            writer.writerow([index, index/fs, x[index], filtered_emg[index]])


