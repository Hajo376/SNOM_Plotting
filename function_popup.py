import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import*

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions, Tag_Type, File_Type



class SavedataPopup():
    def __init__(self, parent, default_channels, default_appendix) -> None:
        self.default_channels = default_channels
        self.default_appendix = default_appendix

        # self.window = tk.Tk()
        # self.window = ttkb.Window(alpha=0.9, position=[600,300]) #themename='darkly', 
        # self.window = ttkb.Window(themename='darkly', position=[600,300])
        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Savefile Dialog')
        self.window.geometry('500x400')
        # self.window.title('Scrolling')
        
        self._create_input()

        self.window.mainloop()

    def _create_input(self):
        self.frame = ttkb.Labelframe(self.window, text='Save Data to gsf or txt', padding=10)
        # self.frame.pack()
        self.frame.pack(pady=20)

        self.change_savefiletype_label = ttkb.Label(self.frame, text='Change Savefile Type:', padding=10)
        self.change_savefiletype_label.grid(column=0, row=0, sticky='e')
        self.current_savefiletype = tk.StringVar()
        self.cb_savefiletype = ttkb.Combobox(self.frame, textvariable=self.current_savefiletype, width=3, justify=CENTER)
        self.cb_savefiletype['values'] = ['gsf', 'txt']
        self.cb_savefiletype.current(0)
        # prevent typing a value
        self.cb_savefiletype['state'] = 'readonly'
        self.cb_savefiletype.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        # select channels to save
        self.label_select_channels_tosave = ttkb.Label(self.frame, text='Select Channels:')
        self.label_select_channels_tosave.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_channels_tosave = ttkb.Entry(self.frame, justify='center')
        # root.update_idletasks()
        self.select_channels_tosave.insert(0, self.default_channels)
        self.select_channels_tosave.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # select appendix
        self.label_appendix_tosave = ttkb.Label(self.frame, text='Select Savefile Appendix:')
        self.label_appendix_tosave.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.appendix_tosave = ttkb.Entry(self.frame, justify='center')
        self.appendix_tosave.insert(0, self.default_appendix)
        self.appendix_tosave.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # save button, only enable if plot was generated previously
        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Save Channels', bootstyle=SUCCESS, command=self._return_inputs)
        # button_save_to_gsftxt.config(state=DISABLED)
        self.button_save_to_gsftxt.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.window.update()
        
    def _return_inputs(self):
        self.filetype = self.cb_savefiletype.get()
        self.channels = self.select_channels_tosave.get()
        self.appendix = self.appendix_tosave.get()
        self.window.quit()
        #check if all fields are filled meaningful
        # return self.cb_savefiletype.get(), self.select_channels_tosave.get(), self.appendix_tosave.get()
        

class HeightLevellingPopup():
    def __init__(self, parent, height_channel, measurement_folder, autoscale) -> None:
        self.height_channel = height_channel
        self.measurement_folder = measurement_folder
        self.autoscale = autoscale

        # self.window = tk.Tk()
        # self.window = ttkb.Window(alpha=0.9, position=[600,300]) #themename='darkly', 
        # self.window = ttkb.Window(themename='darkly', position=[600,300])
        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Savefile Dialog')
        self.window.geometry('800x600')
        # self.window.title('Scrolling')
        
        # self._create_input()
        self._create_canvas()
        self._create_menu()
        self._create_fig()

        # all the space for canvas
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.mainloop()

    def _create_canvas(self):
        # canvas area
        self.canvas_area = ttkb.Frame(self.window, width=600, height=600)
        self.canvas_area.grid(column=0, row=0, sticky='nsew')

    def _Fill_Canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   

    def _create_fig(self):
        Plot_Definitions.show_plot = False
        self.measurement = Open_Measurement(self.measurement_folder, channels=[self.height_channel], autoscale=self.autoscale)
        # self.measurement.Display_Channels() #show_plot=False
        self.measurement.Level_Height_Channels([self.height_channel])
        self._Fill_Canvas()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Save Data to gsf or txt', padding=10)
        # self.frame.pack()
        # self.frame.pack(pady=20)
        self.frame.grid(column=1, row=0)

        self.change_savefiletype_label = ttkb.Label(self.frame, text='Change Savefile Type:', padding=10)
        self.change_savefiletype_label.grid(column=0, row=0, sticky='e')
        self.current_savefiletype = tk.StringVar()
        self.cb_savefiletype = ttkb.Combobox(self.frame, textvariable=self.current_savefiletype, width=3, justify=CENTER)
        self.cb_savefiletype['values'] = ['gsf', 'txt']
        self.cb_savefiletype.current(0)
        # prevent typing a value
        self.cb_savefiletype['state'] = 'readonly'
        self.cb_savefiletype.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        '''
        # select channels to save
        self.label_select_channels_tosave = ttkb.Label(self.frame, text='Select Channels:')
        self.label_select_channels_tosave.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_channels_tosave = ttkb.Entry(self.frame, justify='center')
        # root.update_idletasks()
        self.select_channels_tosave.insert(0, self.default_channels)
        self.select_channels_tosave.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # select appendix
        self.label_appendix_tosave = ttkb.Label(self.frame, text='Select Savefile Appendix:')
        self.label_appendix_tosave.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.appendix_tosave = ttkb.Entry(self.frame, justify='center')
        self.appendix_tosave.insert(0, self.default_appendix)
        self.appendix_tosave.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # save button, only enable if plot was generated previously
        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Save Channels', bootstyle=SUCCESS, command=self._return_inputs)
        # button_save_to_gsftxt.config(state=DISABLED)
        self.button_save_to_gsftxt.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.window.update()'''


# popup = SavedataPopup('O2A,O3A,Z C', '_manipulated')
# filetype = popup.filetype
# channels = popup.channels
# appendix = popup.appendix
# print(filetype, channels, appendix)








'''
class FunctionPopup(ttk.Frame):
    def __init__(self, text_list) -> None:
        self.text_data = text_list
        self.item_number = len(text_list)

        self.window = tk.Tk()
        self.window.geometry('500x400')
        self.window.title('Scrolling')
        
        self._create_input()


        self.window.mainloop()

    def _create_input(self):
        self.frame = ttkb.Labelframe(self.window, text='Function name')
        self.frame.pack()
        for index, item in enumerate(self.text_data):
            self._create_item(index, item).pack(expand=True, fill='both', padx=10, pady=4)

    def _create_item(self, index, item):
        frame = ttkb.Frame(self.frame)

        # grid layout
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure((0,1,2,3,4), weight=1, uniform='a')

        # widgets
        ttk.Label(frame, text=f'#{index}').grid(row=0, column=0)
        # get widget type
        widget_text = item[0]
        widget_type = item[1]
        if widget_type == 'button':
            ttk.Label(frame, text=f'{item[0]}').grid(row=0, column=1)
            ttk.Button(frame, text=f'{item[1]}').grid(row=0, column=2, columnspan=3, sticky='nsew', padx=(0,15))
        elif widget_type == 'entry':
            ttk.Label(frame, text=f'{item[0]}').grid(row=0, column=1)
            entry = ttk.Entry(frame)
            entry.insert(0, 'test')
            entry.grid(row=0, column=2, columnspan=3, sticky='nsew', padx=(0,15))
        elif widget_type == 'checkbox':
            ttk.Label(frame, text=f'{item[0]}').grid(row=0, column=1)
            checkbox_val = ttkb.IntVar()
            checkbox_val.set(1)
            checkbox = ttkb.Checkbutton(frame, text='Autoscale data', variable=checkbox_val, onvalue=1, offvalue=0)
            checkbox.grid(row=0, column=2, columnspan=3, sticky='nsew', padx=(0,15))

        else:
            ttk.Label(frame, text=f'#{index}').grid(row=0, column=0)
            ttk.Label(frame, text=f'{item[0]}').grid(row=0, column=1)
            ttk.Button(frame, text=f'{item[1]}').grid(row=0, column=2, columnspan=3, sticky='nsew', padx=(0,15))

        return frame


text_list_v2 = [('label', 'button'), ('thing', 'entry'), ('third', 'checkbox'), ('label1', 'button'), ('label2', 'buton'), ('label3', 'button'), ('label4', 'button')]
element_1_dict = {'type':'label', }
element_list = []
popup = FunctionPopup(text_list_v2)

'''