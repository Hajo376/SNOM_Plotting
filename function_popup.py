import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import*

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions, Tag_Type, File_Type
Plot_Definitions.show_plot = False # mandatory for gui usage
from SNOM_AFM_analysis.lib.snom_colormaps import *
from mpl_point_clicker import clicker# used for getting coordinates from images



class HelpPopup():
    def __init__(self, parent, help_title:str, help_message:str) -> None:
        self.help_title = help_title
        self.help_message = help_message

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Savefile Dialog')
        self.window.geometry('500x400')

        self._create_help_message()
        
        self.window.mainloop()

    def _create_help_message(self):
        self.frame = ttkb.Labelframe(self.window, text=self.help_title, padding=10)
        self.frame.pack(pady=20)

        # self.help_label = ttkb.Label(self.frame, text=self.help_message, padding=20)
        self.help_label = ttkb.Text(self.frame, wrap=WORD)
        self.help_label.pack()

        self.help_label.insert(END, self.help_message)


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
        
        help_message = """The filetype sets the type of the files. gsf is the standard filetype which can also be opened by Gwyddion an this plotting programm.
You also have to select the channels of which the data should be saved. Select none and all channels will be saved."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How to Save Data to gsf or txt:', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
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

        self.label_zone_width = ttkb.Label(self.frame, text='Pixel integration width:')
        self.label_zone_width.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        self.entry_zone_width = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_zone_width.insert(0, 5)
        self.entry_zone_width.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_height_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._start_leveling)
        self.button_redo_leveling.grid(column=0, row=4, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save_leveling.grid(column=0, row=5, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """For the simple 3 point leveling you need to click on 3 points in the dispayed height data. These points are then assumed to be on one plain.
The plain will then be substracted from the data. If you are satisfied with the result hit \'Save Leveling\' or \'Redo Leveling\' to repeat the procedure.
The leveling will then automatically be applied to all height channels, which are currently in memory.
The pixel integration width is a parameter for the width of the area around the clicked pixel that will be used to calculate a mean height value for that coordinate.
Default is 1, so only the pixel you clicked on. Increase for noisy data, but not so much that features are included!"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How does the 3 Point Heigth Leveling Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

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

        self.label_zone_width = ttkb.Label(self.frame, text='Pixel integration width:')
        self.label_zone_width.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        self.entry_zone_width = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_zone_width.insert(0, 5)
        self.entry_zone_width.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_phase_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._start_leveling)
        self.button_redo_leveling.grid(column=0, row=4, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save_leveling.grid(column=0, row=5, sticky='nsew', padx=button_padx, pady=button_pady)
        

        help_message = """The phase drift compensation is ment to compensate for a linear phase drift along the slow scan axis. 
Select two point along the y-axis which are assumed to have the same phase value and are only different due to the drift.
The program will then substract a linear gradient from the data.
If you are satisfied hit \'Save Leveling\' or \'Redo Leveling\' to repeat the procedure.
The leveling will then automatically be applied to all phase channels, which are currently in memory.
The pixel integration width is a parameter for the width of the area around the clicked pixel that will be used to calculate a mean phase value for that coordinate.
Default is 1, so only the pixel you clicked on. Increase for noisy data, but not so much that features are included!"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How does the Phase Drift Compensation Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

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

        self.button_start_overlay = ttkb.Button(self.frame, text='Start Overlay', bootstyle=SUCCESS, command=self._return_inputs)
        # button_start_overlay.config(state=DISABLED)
        self.button_start_overlay.grid(column=0, row=7, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        help_message = """The overlay channels method is ment to overlay forward and backwards channels.
This works by shifting the x-coordinates relative to each other. For optimal results leveled height channels should be used.
The overlay itself is then applied to the specified channels. So far it usually only makes sense for amplitude and height data.
The overlaying will then automatically be applied, but currently the channels in memory will be overwritten!"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How does the Overlay Method Work?', help_message))
        self.button_help.grid(column=0, row=8, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        self.window.update()
        
    def _return_inputs(self):
        self.forward_channel = str(self.select_forward_channel.get())
        self.backward_channel = str(self.select_backward_channel.get())
        self.overlay_channels = self.select_overlay_channel.get()
        self.window.quit()
        self.window.destroy()

class SyncCorrectionPopup():
    def __init__(self, parent, folder_path, channels, default_dict) -> None:
        # self.measurement = measurement
        self.channels = channels
        self.default_dict = default_dict
        self.folder_path = folder_path

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Synccorrection')
        self.window.geometry('800x600')

        self._create_canvas()
        self._create_menu()
        # self._start_leveling()

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

    def _Synccorrection_Preview(self):
        if self.synccorrection_wavelength.get() != '':
            wavelength = float(self.synccorrection_wavelength.get())
            measurement = Open_Measurement(self.folder_path, channels=self.channels, autoscale=False)
            Plot_Definitions.show_plot = False
            # scanangle = measurement.measurement_tag_dict[Tag_Type.rotation]*np.pi/180
            measurement._Create_Synccorr_Preview(measurement.preview_phasechannel, wavelength, nouserinput=True)
            self._Fill_Canvas()

    def _Synccorrection(self):
        if self.synccorrection_wavelength.get() != '' and self.synccorrection_phasedir.get() != '':
            wavelength = float(self.synccorrection_wavelength.get())
            phasedir = str(self.synccorrection_phasedir.get())
            if phasedir == 'n':
                phasedir = -1
            elif phasedir == 'p':
                phasedir = 1
            else:
                print('Phasedir must be either \'n\' or \'p\'')
            channels = self.channels
            measurement = Open_Measurement(self.folder_path, channels=channels, autoscale=False)
            measurement.Synccorrection(wavelength, phasedir)
            print('finished synccorrection')
            self.default_dict['synccorr_lambda'] = float(self.synccorrection_wavelength.get())
            self.default_dict['synccorr_phasedir'] = str(self.synccorrection_phasedir.get())
            self.window.quit()
            self.window.destroy()
        else:
            print('Either the wavelength or the phasedirection was not specified!')

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Synccorrection', padding=10)
        self.frame.grid(column=1, row=0, padx=button_padx, pady=button_pady)
        # self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        # self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.label_synccorrection_wavelength = ttkb.Label(self.frame, text='Wavelength in µm:')
        self.label_synccorrection_wavelength.grid(column=0, row=0)
        self.synccorrection_wavelength = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.synccorrection_wavelength.insert(0, self.default_dict['synccorr_lambda'])
        self.synccorrection_wavelength.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # first generate preview
        self.button_synccorrection_preview = ttkb.Button(self.frame, text='Generate preview', command=self._Synccorrection_Preview)
        self.button_synccorrection_preview.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # then enter phasedir from preview
        self.label_synccorrection_phasedir = ttkb.Label(self.frame, text='Phasedir (n or p):')
        self.label_synccorrection_phasedir.grid(column=0, row=2)
        self.synccorrection_phasedir = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])
        self.synccorrection_phasedir.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # if phasedir and wavelength are known start synccorrection
        self.button_synccorrection = ttkb.Button(self.frame, text='Synccorrection', bootstyle=PRIMARY, command=self._Synccorrection)
        self.button_synccorrection.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """The synccorrection is ment to correct for the linear phasegradient which is caused by measuring in transmission mode with syncronization.
In this mode the lower parabola used for illumination moves with the tip. This causes a phasedirft on the y-axis of the mirror movement. Due to the parabolic shape only the y-axis is affected.
The programm will automatically read in the rotation parameter of the scan. You need to specify the vacuum wavelength of the used laser though, as this translates to the phase slope.
The programm also needs a phase direction, as this can vary when setting up the interferometer. Therfore hit the \'Generate Preview\' button and chose the correct direction.
Plug the direction into the \'Phasedir\' entry field (only \'n\' for negative and \'p\' for positive are supported.)
When you are done you will be able to press the \'Synccorrection\' button and start the correction. The correction will automatically be applied to all phase channels.
The channels will get the appendix\'_corrected\' and are exported as \'.gsf\' files."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How does the Synccorrection Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


class GaussBlurrPopup():
    def __init__(self, parent, measurement,  folder_path, channels, default_dict) -> None:
        self.measurement = measurement
        self.channels = channels
        self.default_dict = default_dict
        self.folder_path = folder_path

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Gauss Blurr')
        self.window.geometry('800x600')

        self._create_canvas()
        self._create_menu()
        # self._start_leveling()

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

    def _Gaussblurr_Preview(self):
        # new measurement:
        channels = self.select_gaussblurr_channel.get().split(',')
        scaling = int(self.entry_scaling.get())
        sigma = int(self.gaussblurr_sigma.get())
        if channels == '':
            channels = None
            number_of_plots = len(self.channels.split(','))
        else:
            number_of_plots = len(channels)
        preview_measurement = Open_Measurement(self.folder_path, channels, autoscale=self.default_dict['autoscale'])
        # Plot_Definitions.show_plot = False
        preview_measurement.Scale_Channels(channels, scaling)
        preview_measurement.Gauss_Filter_Channels_complex(channels, sigma)
        preview_measurement.Display_Channels()
        preview_measurement.Remove_Last_Subplots(number_of_plots)
        self._Fill_Canvas()

    def _Gaussblurr(self):
        self.scaling = int(self.entry_scaling.get())
        self.sigma = int(self.gaussblurr_sigma.get())
        self.channels = self.select_gaussblurr_channel.get().split(',')
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Gauss Blurr', padding=10)
        self.frame.grid(column=1, row=0, padx=button_padx, pady=button_pady)
        # self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        # self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        # scaling factor 4 means every pixel will be scaled to scaling**2 subpixels
        self.label_scaling = ttkb.Label(self.frame, text='Scaling:')
        self.label_scaling.grid(column=0, row=0)
        self.entry_scaling = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_scaling.insert(0, 4)
        self.entry_scaling.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # sigma for gauss blurr
        self.label_Gaussblurr_sigma = ttkb.Label(self.frame, text='Sigma:')
        self.label_Gaussblurr_sigma.grid(column=0, row=1)
        self.gaussblurr_sigma = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.gaussblurr_sigma.insert(0, 2)
        self.gaussblurr_sigma.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')
        # which channels to blurr?
        self.label_select_gaussblurr_channel = ttkb.Label(self.frame, text='Select Channels to Blurr:')
        self.label_select_gaussblurr_channel.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_gaussblurr_channel = ttkb.Entry(self.frame, justify='center')
        self.select_gaussblurr_channel.insert(0, self.channels)
        self.select_gaussblurr_channel.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # first generate preview
        self.button_gaussblurr_preview = ttkb.Button(self.frame, text='Generate preview', command=self._Gaussblurr_Preview)
        self.button_gaussblurr_preview.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # start Gaussblurr
        self.button_gaussblurr = ttkb.Button(self.frame, text='Gaussblurr', bootstyle=PRIMARY, command=self._Gaussblurr)
        self.button_gaussblurr.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """The synccorrection is ment to correct for the linear phasegradient which is caused by measuring in transmission mode with syncronization.
In this mode the lower parabola used for illumination moves with the tip. This causes a phasedirft on the y-axis of the mirror movement. Due to the parabolic shape only the y-axis is affected.
The programm will automatically read in the rotation parameter of the scan. You need to specify the vacuum wavelength of the used laser though, as this translates to the phase slope.
The programm also needs a phase direction, as this can vary when setting up the interferometer. Therfore hit the \'Generate Preview\' button and chose the correct direction.
Plug the direction into the \'Phasedir\' entry field (only \'n\' for negative and \'p\' for positive are supported.)
When you are done you will be able to press the \'Synccorrection\' button and start the correction. The correction will automatically be applied to all phase channels.
The channels will get the appendix\'_corrected\' and are exported as \'.gsf\' files."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.window, 'How does the Synccorrection Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)



def main():
    root = ttkb.Window(themename='darkly')
    help_message = """The filetype sets the type of the files. gsf is the standard filetype which can also be opened by Gwyddion an this plotting programm.
You also have to select the channels of which the data should be saved. Select none and all channels will be saved."""
    popup = HelpPopup(root, 'help', help_message)
    root.mainloop()

if __name__ == '__main__':
    main()

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