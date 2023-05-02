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


    plt.figure(1)
    plt.clf()
    for order in [3, 6, 9]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, fs=fs, worN=2000)
        plt.plot(w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')


    # Filter a noisy signal.
    T = 91
    nsamples = T * fs
    t = np.arange(0, nsamples) / fs
    a = 0.02
    f0 = 600.0
    x =  pandas.read_csv(filedialog.askopenfilename())["EMGraw"]

    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)



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
        writer.writerow([index, index/fs, x[index], y[index]])


    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')


    plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)
    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

    plt.show()