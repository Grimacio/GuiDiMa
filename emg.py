import biosppy 
import pandas
from tkinter import filedialog 

name = filedialog.askopenfilename()

data = pandas.read_csv(name)

emg_raw = data["EMGraw"].tolist()

resultado=biosppy.signals.emg.emg(emg_raw)
onsets=resultado[2]

print((onsets[-1]-onsets[0])/(len(onsets)-1))


