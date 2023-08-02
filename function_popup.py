import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import*

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions, Tag_Type, File_Type
from SNOM_AFM_analysis.lib.snom_colormaps import *
from mpl_point_clicker import clicker# used for getting coordinates from images



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
        self.window.destroy()
        #check if all fields are filled meaningful
        # return self.cb_savefiletype.get(), self.select_channels_tosave.get(), self.appendix_tosave.get()
        
class HeightLevellingPopup():
    def __init__(self, parent, measurement, height_channel, autoscale) -> None:
        self.height_channel = height_channel
        self.measurement = measurement
        self.autoscale = autoscale

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('3 Point Height Leveling')
        self.window.geometry('800x600')

        self._create_canvas()
        self._create_menu()
        self._start_leveling()

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
        else:
            self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   

    def _start_leveling(self):
        fig, ax = plt.subplots()
        self.height_data = self.measurement.all_data[self.measurement.channels.index(self.height_channel)]
        ax.pcolormesh(self.height_data, cmap=SNOM_height)
        self.klicker = clicker(ax, ["event"], markers=["x"])
        # ax.legend()
        ax.axis('scaled')
        plt.title('3 Point leveling: please click on three points\nto specify the underground plane.')
        self._Fill_Canvas()


    def _get_klicker_coordinates(self):
        klicker_coords = self.klicker.get_positions()['event'] #klicker returns a dictionary for the events
        klick_coordinates = [[round(element[0]), round(element[1])] for element in klicker_coords]
        return klick_coordinates

    def _level_height_channel(self):
        self.klick_coordinates = self._get_klicker_coordinates()
        if len(self.klick_coordinates) != 3:
            print('You need to klick on 3 points!\Height data was not leveled!')

        self.leveled_height_data = self.measurement._level_height_data(self.height_data, self.klick_coordinates, zone=int(self.entry_zone_width.get()))
        self._show_leveled_data()

    def _show_leveled_data(self): # just for testing
        fig, ax = plt.subplots()
        ax.pcolormesh(self.leveled_height_data, cmap=SNOM_height)
        # ax.legend()
        ax.axis('scaled')
        plt.title('Leveled Height Data')
        self._Fill_Canvas()

    def _save_leveled_data(self):
        self.measurement._Write_to_Logfile('height_leveling_coordinates', self.klick_coordinates)
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Level Heigth data', padding=10)
        self.frame.grid(column=1, row=0)
        self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_height_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=1, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._start_leveling)
        self.button_redo_leveling.grid(column=0, row=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save_leveling.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)

        self.label_zone_width = ttkb.Label(self.frame, text='Pixel integration width:')
        self.label_zone_width.grid(column=0, row=4, padx=button_padx, pady=button_pady, sticky='nsew')
        self.entry_zone_width = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_zone_width.insert(0, 5)
        self.entry_zone_width.grid(column=0, row=5, padx=button_padx, pady=button_pady, sticky='nsew')

class PhaseDriftCompensation():
    def __init__(self, parent, measurement, phase_channel, autoscale) -> None:
        self.phase_channel = phase_channel
        self.measurement = measurement
        self.autoscale = autoscale

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Phase Drift Compensation')
        self.window.geometry('800x600')

        self._create_canvas()
        self._create_menu()
        self._start_leveling()

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
        else:
            self.canvas_fig.get_tk_widget().destroy()
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   

    def _start_leveling(self):
        fig, ax = plt.subplots()
        self.phase_data = self.measurement.all_data[self.measurement.channels.index(self.phase_channel)]
        ax.pcolormesh(self.phase_data, cmap=SNOM_phase)
        self.klicker = clicker(ax, ["event"], markers=["x"])
        # ax.legend()
        ax.axis('scaled')
        plt.title('Please Select 2 Points to Specify the Phasedrift on the y-Axis!')
        self._Fill_Canvas()


    def _get_klicker_coordinates(self):
        klicker_coords = self.klicker.get_positions()['event'] #klicker returns a dictionary for the events
        klick_coordinates = [[round(element[0]), round(element[1])] for element in klicker_coords]
        return klick_coordinates

    def _level_phase_channel(self):
        self.klick_coordinates = self._get_klicker_coordinates()
        mean_values = [self.measurement._Get_Mean_Value(self.phase_data, self.klick_coordinates[i][0], self.klick_coordinates[i][1], zone=int(self.entry_zone_width.get())) for i in range(len(self.klick_coordinates))]
        if len(self.klick_coordinates) != 2:
            print('You have to select only two points!\nPhase data was not corrected!')

        #order points from top to bottom
        if self.klick_coordinates[0][1] > self.klick_coordinates[1][1]:
            second_corrd = self.klick_coordinates[0]
            second_mean = mean_values[0]
            self.klick_coordinates[0] = self.klick_coordinates[1]
            self.klick_coordinates[1] = second_corrd
            mean_values[0] = mean_values[1]
            mean_values[1] = second_mean
        self.phase_slope = (mean_values[1] - mean_values[0])/(self.klick_coordinates[1][1] - self.klick_coordinates[0][1])
        self.leveled_phase_data = self.measurement._Level_Phase_Slope(self.phase_data, self.phase_slope)
        # self.leveled_phase_data = self.measurement._level_phase_data(self.phase_data, self.klick_coordinates, zone=1)
        self._show_leveled_data()

    def _show_leveled_data(self): # just for testing
        fig, ax = plt.subplots()
        ax.pcolormesh(self.leveled_phase_data, cmap=SNOM_phase)
        # ax.legend()
        ax.axis('scaled')
        plt.title('Corrected Phase Data')
        self._Fill_Canvas()

    def _save_leveled_data(self):
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Level Phase data', padding=10)
        self.frame.grid(column=1, row=0)
        self.label_howto = ttkb.Label(self.frame, text='Please Select 2 Points to Specify\nthe Phasedrift on the y-Axis!')
        self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_phase_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=1, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._start_leveling)
        self.button_redo_leveling.grid(column=0, row=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save_leveling.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        
        self.label_zone_width = ttkb.Label(self.frame, text='Pixel integration width:')
        self.label_zone_width.grid(column=0, row=4, padx=button_padx, pady=button_pady, sticky='nsew')
        self.entry_zone_width = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_zone_width.insert(0, 5)
        self.entry_zone_width.grid(column=0, row=5, padx=button_padx, pady=button_pady, sticky='nsew')

class OverlayChannels():
    def __init__(self, parent, default_height_channel_forward, default_height_channel_backward) -> None:
        self.default_height_channel_forward = default_height_channel_forward
        self.default_height_channel_backward = default_height_channel_backward

        # self.window = tk.Tk()
        # self.window = ttkb.Window(alpha=0.9, position=[600,300]) #themename='darkly', 
        # self.window = ttkb.Window(themename='darkly', position=[600,300])
        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Overlay Channels')
        self.window.geometry('500x400')
        # self.window.title('Scrolling')
        
        self._create_input()

        self.window.mainloop()

    def _create_input(self):
        self.frame = ttkb.Labelframe(self.window, text='Overlay Channels', padding=10)
        # self.frame.pack()
        self.frame.pack(pady=20)

        # select forward channel
        self.label_select_forward_channel = ttkb.Label(self.frame, text='Select Forward Height Channel:')
        self.label_select_forward_channel.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_forward_channel = ttkb.Entry(self.frame, justify='center')
        self.select_forward_channel.insert(0, self.default_height_channel_forward)
        self.select_forward_channel.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # select backward channel
        self.label_select_backward_channel = ttkb.Label(self.frame, text='Select backward Height Channel:')
        self.label_select_backward_channel.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_backward_channel = ttkb.Entry(self.frame, justify='center')
        self.select_backward_channel.insert(0, self.default_height_channel_backward)
        self.select_backward_channel.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # which channels to overlay?
        self.label_select_overlay_channel = ttkb.Label(self.frame, text='Select Channels to Overlay:')
        self.label_select_overlay_channel.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_overlay_channel = ttkb.Entry(self.frame, justify='center')
        self.select_overlay_channel.insert(0, 'all')
        self.select_overlay_channel.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # self.change_savefiletype_label = ttkb.Label(self.frame, text='Change Savefile Type:', padding=10)
        # self.change_savefiletype_label.grid(column=0, row=0, sticky='e')
        # self.current_savefiletype = tk.StringVar()
        # self.cb_savefiletype = ttkb.Combobox(self.frame, textvariable=self.current_savefiletype, width=3, justify=CENTER)
        # self.cb_savefiletype['values'] = ['gsf', 'txt']
        # self.cb_savefiletype.current(0)
        # # prevent typing a value
        # self.cb_savefiletype['state'] = 'readonly'
        # self.cb_savefiletype.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        # select channels to save
        # self.label_select_channels_tosave = ttkb.Label(self.frame, text='Select Channels:')
        # self.label_select_channels_tosave.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.select_channels_tosave = ttkb.Entry(self.frame, justify='center')
        # root.update_idletasks()
        # self.select_channels_tosave.insert(0, self.default_channels)
        # self.select_channels_tosave.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # select appendix
        # self.label_appendix_tosave = ttkb.Label(self.frame, text='Select Savefile Appendix:')
        # self.label_appendix_tosave.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.appendix_tosave = ttkb.Entry(self.frame, justify='center')
        # self.appendix_tosave.insert(0, self.default_appendix)
        # self.appendix_tosave.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # save button, only enable if plot was generated previously
        self.button_start_overlay = ttkb.Button(self.frame, text='Start Overlay', bootstyle=SUCCESS, command=self._return_inputs)
        # button_start_overlay.config(state=DISABLED)
        self.button_start_overlay.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.window.update()
        
    def _return_inputs(self):
        self.forward_channel = str(self.select_forward_channel.get())
        self.backward_channel = str(self.select_backward_channel.get())
        self.overlay_channels = self.select_overlay_channel.get()
        self.window.quit()
        self.window.destroy()







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