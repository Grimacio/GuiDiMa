import os
import pandas as pd
from tkinter.filedialog import askdirectory
import numpy as np

folder_path = askdirectory(title = "Select Folder")  # Replace with the path to your folder

# Get a list of all files in the folder
file_list = os.listdir(folder_path)
print(file_list)
# Filter the list to only include Excel files
excel_files = [file for file in file_list if file.endswith('.csv')]


Tensor = {}


# Iterate over each Excel file
for file in excel_files:
    file_path = os.path.join(folder_path, file)  # Create the full file path
    df = pd.read_csv(file_path)  # Read the Excel file into a DataFrame

    temp_block=np.empty((0,5))
    current_class = ""
    for i in range(len(df)):
        if i == 0:
            current_class = str(df.loc[i, 'Class'])
           # print(str(df.loc[i, 'Class']))
        if str(df.loc[i, 'Class']) == current_class:
            temp_block = np.append(temp_block, [df.iloc[i]], axis=0)
            
            if i == len(df):
                Tensor[current_class] += [temp_block]
                temp_block=np.empty((0,5))
        else:
            #print("bloco feito  ", current_class)
            #print(Tensor)
            if current_class not in Tensor:
                Tensor[current_class] = [temp_block]
            else:
                Tensor[current_class] += [temp_block]
            
            temp_block=np.empty((0,5))
            current_class = str(df.loc[i, 'Class'])
            

        
        
        
