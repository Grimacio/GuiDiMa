import pandas
from tkinter import filedialog 
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from sklearn.decomposition import FastICA
import biosppy.signals.ecg as ecg
from scipy.signal import hilbert

import numpy as np
from scipy.signal import butter, sosfilt

def extract_ecg_from_emg(emg_ecg_signal):
    # Preprocessing: Bandpass filter the signal to isolate relevant frequencies
    fs = 1000  # Sampling rate of the signal
    f_low = 10.0  # Lower frequency cutoff
    f_high = 100.0  # Higher frequency cutoff
    b, a = signal.butter(4, [f_low, f_high], fs=fs, btype='bandpass')
    filtered_signal = signal.filtfilt(b, a, emg_ecg_signal)
    # Reshape the signal into a 2D array (required by FastICA)
    X = filtered_signal.reshape(-1, 1)
    # Perform ICA
    ica = FastICA(n_components=1)
    ecg_estimate = ica.fit_transform(X)
    # Rescale the estimated ECG component to match the original scale
    ecg_estimate = np.squeeze(ecg_estimate) * np.ptp(emg_ecg_signal)
    return ecg_estimate

def moving_avg(signal, window_size):
    kernel = np.ones(window_size) / window_size
    smoothed_data = np.convolve(signal, kernel, mode='same')
    return smoothed_data

def three_point_peaks_detector(ecg_envelope):
    lev = np.zeros(len(ecg_envelope))
    std_arr = np.zeros(len(ecg_envelope))
    peaks = []
    window_size = 100
    max_bef = 0

    for i in range(len(ecg_envelope)):
    # Adaptive Thresholding
        start_index = max(0, i - window_size//2)
        end_index = min(len(ecg_envelope), i + window_size//2 + 1)
        ecg_window = ecg_envelope[start_index:end_index]
        max_instant = max(ecg_window)
        std_dev = np.std(ecg_window)
        std_arr[i] = std_dev
        # Thresholding
        if std_dev >= 0.2 * max_instant:
            if max_instant < 2 * max_bef:
                lev[i] = 0.6 * max_instant
            else:
                lev[i] = 0.6 * max_bef
        else:
            lev[i] = 1 * std_dev
        max_bef = max_instant

    # Local Standard Deviation

    # QRS Wave's Peak Detector
        if 1 < i < len(ecg_envelope)-2 and ecg_envelope[i-1] > lev[i-1] and ecg_envelope[i-1] > ecg_envelope[i-2] and ecg_envelope[i-1] > ecg_envelope[i] and std_dev >= 3.5:
            peaks = peaks + [i]

    return peaks, lev, std_arr


name = filedialog.askopenfilename()

data = pandas.read_csv(name)

emg_raw = data["EMGraw"].tolist()
emg_filter = data["EMGfilter"].tolist()
timestamp = data["Timestamp"].tolist()

xi=range(len(timestamp))
extracted_ecg = extract_ecg_from_emg(emg_raw)
analytic_signal = hilbert(extracted_ecg)
squared_envelope = np.abs(analytic_signal)
peaks, lev, std_ar = three_point_peaks_detector(squared_envelope)

"""
window_size = 15
# Calcular a variância em relação aos vizinhos para cada ponto
variancia_pontos = np.zeros(len(extracted_ecg))
for i in range(len(extracted_ecg)):
    start_index = max(0, i - window_size//2)
    end_index = min(len(extracted_ecg), i + window_size//2 + 1)
    variancia_pontos[i] = np.var(extracted_ecg[start_index:end_index])
variancia_pontos = np.convolve(variancia_pontos,np.ones(15)/15) """

plt.figure()
plt.rcParams["figure.autolayout"] = True

plt.plot(extracted_ecg, color="orange")
plt.plot(squared_envelope, color="green")
plt.plot(lev, color="black")
plt.plot(std_ar, color="red")

plt.plot(peaks, [squared_envelope[point] for point in peaks], 'ro', label='Peaks')
plt.legend()

plt.show()

