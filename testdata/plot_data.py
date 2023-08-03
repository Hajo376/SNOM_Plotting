

from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions, Tag_Type, File_Type
from tkinter import filedialog

folder_path = filedialog.askdirectory()

channels = ['O2A_overlain', 'O2A_overlain_manipulated']
measurement = Open_Measurement(folder_path, channels=channels, autoscale=True)
measurement.Display_Channels()