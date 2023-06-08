import pandas
from tkinter import filedialog 
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from sklearn.decomposition import FastICA

def generate_model_ecg(duration, sampling_rate):
    # Generate time axis
    t = np.arange(0, duration, 1 / sampling_rate)

    # Generate ECG components
    p_wave = signal.gaussian(int(duration * sampling_rate), std=int(duration * sampling_rate / 10))
    qrs_complex = signal.gaussian(int(duration * sampling_rate), std=int(duration * sampling_rate / 20))
    t_wave = signal.gaussian(int(duration * sampling_rate), std=int(duration * sampling_rate / 10))
    
    # Combine the components to create the ECG signal
    ecg_signal = 0.1 * p_wave - 0.4 * qrs_complex + 0.2 * t_wave

    return ecg_signal



def perform_pattern_recognition(signalx):
    sampling_rate = 1000  # Sampling rate in Hz
    duration = len(signalx)/sampling_rate  # Duration of the ECG signal in seconds
    
    model_ecg_signal=generate_model_ecg(duration, sampling_rate)
    # Normalize the model ECG signal
    model_ecg_signal = (model_ecg_signal - np.mean(model_ecg_signal)) / np.std(model_ecg_signal)
    
    # Normalize the input signal
    signalx = (signalx - np.mean(signalx)) / np.std(signalx)
    
    # Perform cross-correlation
    correlation = np.correlate(signalx, model_ecg_signal, mode='same')
    
    # Find peaks in the correlation signal
    peaks, _ = signal.find_peaks(correlation, height=0)
    
    return peaks


def extract_ecg_from_emg(emg_ecg_signal):
    # Preprocessing: Bandpass filter the signal to isolate relevant frequencies
    fs = 1000  # Sampling rate of the signal
    f_low = 10.0  # Lower frequency cutoff
    f_high = 100.0  # Higher frequency cutoff
    b, a = signal.butter(4, [f_low, f_high], fs=fs, btype='bandpass')
    filtered_signal = signal.filtfilt(b, a, emg_ecg_signal)
    
    # Independent Component Analysis (ICA)
    
    
    # Reshape the signal into a 2D array (required by FastICA)
    X = filtered_signal.reshape(-1, 1)

    
    # Perform ICA
    ica = FastICA(n_components=1)
    ecg_estimate = ica.fit_transform(X)
    
    # Rescale the estimated ECG component to match the original scale
    ecg_estimate = np.squeeze(ecg_estimate) * np.ptp(emg_ecg_signal)
    
    return ecg_estimate


name = filedialog.askopenfilename()

data = pandas.read_csv(name)

emg_raw = data["EMGraw"].tolist()
emg_filter = data["EMGfilter"].tolist()
timestamp = data["Timestamp"].tolist()

xi=range(len(timestamp))
extracted_ecg = extract_ecg_from_emg(emg_raw)


plt.rcParams["figure.autolayout"] = True


plt.plot(emg_filter, color="orange")
plt.plot(extracted_ecg, color="black")
plt.show()


"""
# Example usage
signalx = emg_raw  

peaks = perform_pattern_recognition(signalx)
print(peaks)

# Plot the original signal and identified peaks
plt.figure()
plt.plot(signalx, label='Signal')
plt.plot(peaks, [signalx[point] for point in peaks], 'ro', label='Peaks')
plt.legend()
plt.show()"""

