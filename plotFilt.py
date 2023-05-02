import pandas
from tkinter import filedialog 
from matplotlib import pyplot as plt

name = filedialog.askopenfilename()

data = pandas.read_csv(name)

emg_raw = data["EMGraw"].tolist()
emg_filter = data["EMGfilter"].tolist()
timestamp = data["Timestamp"].tolist()

xi=range(len(timestamp))

plt.rcParams["figure.autolayout"] = True
plt.subplot(211)
plt.plot(timestamp,emg_raw)
plt.subplot(212)
plt.plot(timestamp,emg_filter)
plt.show()
