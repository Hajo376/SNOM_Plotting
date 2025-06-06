##############################################################################
# Copyright (C) 2023-2025 Hans-Joachim Schill

# This file is part of snom_plotting.

# snom_plotting is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# snom_plotting is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with snom_plotting.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from lib.gui_parameters import*

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from snom_analysis.main import SnomMeasurement, PlotDefinitions, MeasurementTags
PlotDefinitions.show_plot = False # mandatory for gui usage
from snom_analysis.lib.snom_colormaps import *
from mpl_point_clicker import clicker# used for getting coordinates from images
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import gc
import time
from PIL import Image, ImageTk

from copy import deepcopy # to copy the measurement instance

# variables: 
pi = 3.14


class HelpPopup():
    def __init__(self, parent, help_title:str, help_message:str) -> None:
        self.help_title = help_title
        self.help_message = help_message

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Savefile Dialog')
        self.window.geometry('500x400')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')
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
    def __init__(self, parent, measurement, height_channel, default_dict) -> None:
        self.parent = parent
        self.height_channel = height_channel
        self.measurement = measurement
        self.autoscale = default_dict['autoscale']
        self.default_dict = default_dict
        self.window_width = 1000
        self.window_height = 600


        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('3 Point Height Leveling')
        # self.window.geometry(f'800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

        self._create_menu()
        self._create_canvas()
        self._change_popup_size()

        self._start_leveling()

        # all the space for canvas
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.mainloop()

    def _change_popup_size(self):
        self.window.update()
        # self.window.update_idletasks()
        canvas_width = self.canvas_area.winfo_width()
        # print('canvasframe width: ', self.canvas_area.winfo_width())
        # print('canvasfig width: ', self.canvas_fig.winfo_width())
        # self.canvas_fig
        # print('menu width: ', self.frame.winfo_width())
        menu_width = self.frame.winfo_width()
        self.window.geometry(f'{self.window_width}x{self.window_height}')

    def _create_canvas(self):
        # canvas area
        self.window.update()

        self.canvas_area = ttkb.Frame(self.window, width=self.window_width-self.frame.winfo_width(), height=self.window_height)
        self.canvas_area.grid(column=0, row=0, sticky='nsew')
        # self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.window_width-self.frame.winfo_width(), height=self.window_height)
        # self.canvas_frame.grid(column=0, row=0, sticky='nsew')

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        '''# extra frame because canvas is buggy, but only for initialization
        try: self.canvas_frame.winfo_exists()
        except:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)  
            self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
            self.canvas_frame.pack()

            # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            # self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   
            self.canvas_fig.draw()
        else:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_frame)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)'''

    def _update_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   
        # extra frame because canvas is buggy
        # self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
        # self.canvas_frame.pack()

        # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        # self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   
        # self.canvas_fig.draw()


    def _start_leveling(self):
        # plt.clf()
        fig, ax = plt.subplots()
        # print('height channel:', self.height_channel)
        # print('all channels: ', self.measurement.channels)
        self.height_data = self.measurement.all_data[self.measurement.channels.index(self.height_channel)]
        ax.pcolormesh(self.height_data, cmap=SNOM_height)
        self.klicker = clicker(ax, ["event"], markers=["x"])
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()

        plt.title('3 Point leveling: please click on three points\nto specify the underground plane.')
        self._fill_canvas()

    def _redo_leveling(self):
        fig, ax = plt.subplots()
        # print('height channel:', self.height_channel)
        # print('all channels: ', self.measurement.channels)
        self.height_data = self.measurement.all_data[self.measurement.channels.index(self.height_channel)]
        ax.pcolormesh(self.height_data, cmap=SNOM_height)
        self.klicker = clicker(ax, ["event"], markers=["x"])
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()
        plt.title('3 Point leveling: please click on three points\nto specify the underground plane.')
        # self._update_canvas()
        self._fill_canvas()


    def _get_klicker_coordinates(self):
        klicker_coords = self.klicker.get_positions()['event'] #klicker returns a dictionary for the events
        klick_coordinates = [[round(element[0]), round(element[1])] for element in klicker_coords]
        # print('klick corrdinates: ', klick_coordinates)
        return klick_coordinates

    def _level_height_channel(self):
        self.klick_coordinates = self._get_klicker_coordinates()
        if len(self.klick_coordinates) != 3:
            print('You need to klick on 3 points!\Height data was not leveled!')

        self.leveled_height_data = self.measurement._level_height_data(self.height_data, self.klick_coordinates, zone=int(self.entry_zone_width.get()))
        self._show_leveled_data()

    def _show_leveled_data(self): # just for testing
        # plt.clf()
        fig, ax = plt.subplots()
        ax.pcolormesh(self.leveled_height_data, cmap=SNOM_height)
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()
        plt.title('Leveled Height Data')
        self._fill_canvas()
        # self._update_canvas()


    def _save_leveled_data(self):
        self.measurement._write_to_logfile('height_leveling_coordinates', self.klick_coordinates)
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
        self.entry_zone_width.insert(0, self.default_dict['pixel_integration_width'])
        self.entry_zone_width.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_height_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._redo_leveling)
        self.button_redo_leveling.grid(column=0, row=4, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save_leveling.grid(column=0, row=5, sticky='nsew', padx=button_padx, pady=button_pady)

        #todo change definition of pixel integration zone in all following messages
        help_message = """For the simple 3 point leveling you need to click on 3 points in the dispayed height data. These points are then assumed to be on one plain.
The plain will then be substracted from the data. If you are satisfied with the result hit \'Save Leveling\' or \'Redo Leveling\' to repeat the procedure.
The leveling will then automatically be applied to all height channels, which are currently in memory.
The pixel integration width is a parameter for the width of the area around the clicked pixel that will be used to calculate a mean height value for that coordinate.
Default is 1, so only the pixel you clicked on. Increase for noisy data, but not so much that features are included!"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the 3 Point Heigth Leveling Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class PhaseDriftCompensation():
    def __init__(self, parent, measurement, phase_channel, autoscale, default_dict) -> None:
        self.parent = parent
        self.phase_channel = phase_channel
        self.measurement = deepcopy(measurement)
        self.autoscale = autoscale
        self.default_dict = default_dict
        self.original_phase_data = self.measurement.all_data[self.measurement.channels.index(self.phase_channel)].copy()

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Phase Drift Compensation')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        
        '''# extra frame because canvas is buggy, but only for initialization
        try: self.canvas_frame.winfo_exists()
        except:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)  
            self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
            self.canvas_frame.pack()

            # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            # self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   
            self.canvas_fig.draw()
        else:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_frame)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        '''
        '''
        try: self.canvas_frame.winfo_exists()
        except:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 
            # extra frame because canvas is buggy
            self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
            self.canvas_frame.pack()

            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.canvas_fig.draw()  
        else:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_frame)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)''' 

    def _start_leveling(self):
        # plt.clf()
        fig, ax = plt.subplots()
        self.phase_data = self.measurement.all_data[self.measurement.channels.index(self.phase_channel)]
        ax.pcolormesh(self.phase_data, cmap=SNOM_phase)
        self.klicker = clicker(ax, ["event"], markers=["x"])
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()
        plt.title('Please Select 2 Points to Specify the Phasedrift on the y-Axis!')
        self._fill_canvas()

    def _redo_leveling(self):
        # undo leveling
        self.measurement.all_data[self.measurement.channels.index(self.phase_channel)] = self.original_phase_data
        self._start_leveling()


    def _get_klicker_coordinates(self):
        klicker_coords = self.klicker.get_positions()['event'] #klicker returns a dictionary for the events
        klick_coordinates = [[round(element[0]), round(element[1])] for element in klicker_coords]
        return klick_coordinates

    def _level_phase_channel(self):
        self.klick_coordinates = self._get_klicker_coordinates()
        mean_values = [self.measurement._get_mean_value(self.phase_data, self.klick_coordinates[i][0], self.klick_coordinates[i][1], zone=int(self.entry_zone_width.get())) for i in range(len(self.klick_coordinates))]
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
        self.leveled_phase_data = self.measurement._level_phase_slope(self.phase_data, self.phase_slope)
        # self.leveled_phase_data = self.measurement._level_phase_data(self.phase_data, self.klick_coordinates, zone=1)
        self._show_leveled_data()

    def _show_leveled_data(self): # just for testing
        fig, ax = plt.subplots()
        ax.pcolormesh(self.leveled_phase_data, cmap=SNOM_phase)
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()
        plt.title('Corrected Phase Data')
        self._fill_canvas()

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
        self.entry_zone_width.insert(0, self.default_dict['pixel_integration_width'])
        self.entry_zone_width.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_phase_channel)
        # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        self.button_save_to_gsftxt.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._redo_leveling)
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
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Phase Drift Compensation Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class OverlayChannels():
    def __init__(self, parent, default_height_channel_forward, default_height_channel_backward, measurement) -> None:
        self.parent = parent
        self.default_height_channel_forward = default_height_channel_forward
        self.default_height_channel_backward = default_height_channel_backward
        self.measurement = measurement

        # self.window = tk.Tk()
        # self.window = ttkb.Window(alpha=0.9, position=[600,300]) #themename='darkly', 
        # self.window = ttkb.Window(themename='darkly', position=[600,300])
        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Overlay Channels')
        self.window.geometry('500x400')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')
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
The overlaying will then automatically be applied, but currently the channels in memory will be overwritten!
You only need to specify the forward amplitude channels. The channels also don't need to be in memory.
If you want to overlay all channels, just type 'all'."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Overlay Method Work?', help_message))
        self.button_help.grid(column=0, row=8, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        self.window.update()
        
    def _return_inputs(self):
        self.forward_channel = str(self.select_forward_channel.get())
        self.backward_channel = str(self.select_backward_channel.get())
        self.overlay_channels = self.select_overlay_channel.get()

        if self.overlay_channels == 'all':
            self.overlay_channels = None
        else:
            self.overlay_channels = [channel for channel in self.overlay_channels.split(',')]
        self.measurement.overlay_forward_and_backward_channels_v2(self.forward_channel, self.backward_channel, self.overlay_channels)
        self.window.quit()
        self.window.destroy()

class SyncCorrectionPopup():
    def __init__(self, parent, folder_path, channels, default_dict) -> None:
        # self.measurement = measurement
        self.parent = parent
        self.channels = channels
        self.default_dict = default_dict
        self.folder_path = folder_path

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Synccorrection')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 
        # extra frame because canvas is buggy
        # self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
        # self.canvas_frame.pack()

        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()  

    def _synccorrection_preview(self):
        if self.synccorrection_wavelength.get() != '':
            wavelength = float(self.synccorrection_wavelength.get())
            measurement = SnomMeasurement(self.folder_path, channels=self.channels, autoscale=False)
            PlotDefinitions.show_plot = False
            # scanangle = measurement.measurement_tag_dict[MeasurementTags.rotation]*np.pi/180
            measurement._create_synccorr_preview(measurement.preview_phasechannel, wavelength, nouserinput=True)
            self._fill_canvas()

    def _synccorrection(self):
        if self.synccorrection_wavelength.get() != '' and self.synccorrection_phasedir.get() != '':
            self.wavelength = float(self.synccorrection_wavelength.get())
            self.phasedir = str(self.synccorrection_phasedir.get())
            if self.phasedir == 'n':
                self.phasedir = -1
            elif self.phasedir == 'p':
                self.phasedir = 1
            else:
                print('self.phasedir must be either \'n\' or \'p\'')
            channels = self.channels
            measurement = SnomMeasurement(self.folder_path, channels=channels, autoscale=False)
            measurement.synccorrection(self.wavelength, self.phasedir)
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
        self.button_synccorrection_preview = ttkb.Button(self.frame, text='Generate preview', command=self._synccorrection_preview)
        self.button_synccorrection_preview.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # then enter phasedir from preview
        self.label_synccorrection_phasedir = ttkb.Label(self.frame, text='Phasedir (n or p):')
        self.label_synccorrection_phasedir.grid(column=0, row=2)
        self.synccorrection_phasedir = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])
        self.synccorrection_phasedir.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # if phasedir and wavelength are known start synccorrection
        self.button_synccorrection = ttkb.Button(self.frame, text='Synccorrection', bootstyle=PRIMARY, command=self._synccorrection)
        self.button_synccorrection.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """The synccorrection is ment to correct for the linear phasegradient which is caused by measuring in transmission mode with syncronization.
In this mode the lower parabola used for illumination moves with the tip. This causes a phasedirft on the y-axis of the mirror movement. Due to the parabolic shape only the y-axis is affected.
The programm will automatically read in the rotation parameter of the scan. You need to specify the vacuum wavelength of the used laser though, as this translates to the phase slope.
The programm also needs a phase direction, as this can vary when setting up the interferometer. Therfore hit the \'Generate Preview\' button and chose the correct direction.
Plug the direction into the \'Phasedir\' entry field (only \'n\' for negative and \'p\' for positive are supported.)
When you are done you will be able to press the \'Synccorrection\' button and start the correction. The correction will automatically be applied to all phase channels.
The channels will get the appendix\'_corrected\' and are exported as \'.gsf\' files."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Synccorrection Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class GaussBlurrPopup():
    def __init__(self, parent, measurement,  folder_path, channels, default_dict) -> None:
        self.parent = parent
        self.measurement = measurement
        self.channels = channels
        self.default_dict = default_dict
        self.folder_path = folder_path

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Gauss Blurr')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 
        # extra frame because canvas is buggy
        # self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
        # self.canvas_frame.pack()

        # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        # self.canvas_fig.draw()  

    def _gaussblurr_preview(self):
        # new measurement:
        channels = self.select_gaussblurr_channel.get().split(',')
        scaling = int(self.entry_scaling.get())
        sigma = int(self.gaussblurr_sigma.get())
        if channels == '':
            channels = None
            number_of_plots = len(self.channels.split(','))
        else:
            number_of_plots = len(channels)
        # preview_measurement = SnomMeasurement(self.folder_path, channels, autoscale=self.default_dict['autoscale'])
        # preview_measurement = self.measurement
        preview_measurement = deepcopy(self.measurement)
        # PlotDefinitions.show_plot = False
        # make shure that no channel is blurred twice! eg. for repeated previewing
        for channel in channels:
            if preview_measurement.filter_gauss_indicator in preview_measurement.channels_label[preview_measurement.channels.index(channel)]:
                channels.remove(channel) # remove channel if its label already has the appendix indicating that it was blurred
        preview_measurement.scale_channels(channels, scaling)
        preview_measurement.gauss_filter_channels_complex(channels, sigma)
        preview_measurement.display_channels()
        preview_measurement.remove_last_subplots(number_of_plots)
        print('Done blurring! Blurred channels: ', channels)
        self._fill_canvas()

    def _gaussblurr(self):
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
        self.label_gaussblurr_sigma = ttkb.Label(self.frame, text='Sigma:')
        self.label_gaussblurr_sigma.grid(column=0, row=1)
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
        self.button_gaussblurr_preview = ttkb.Button(self.frame, text='Generate preview', command=self._gaussblurr_preview)
        self.button_gaussblurr_preview.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # start Gaussblurr
        self.button_gaussblurr = ttkb.Button(self.frame, text='Gaussblurr', bootstyle=PRIMARY, command=self._gaussblurr)
        self.button_gaussblurr.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """The synccorrection is ment to correct for the linear phasegradient which is caused by measuring in transmission mode with syncronization.
In this mode the lower parabola used for illumination moves with the tip. This causes a phasedirft on the y-axis of the mirror movement. Due to the parabolic shape only the y-axis is affected.
The programm will automatically read in the rotation parameter of the scan. You need to specify the vacuum wavelength of the used laser though, as this translates to the phase slope.
The programm also needs a phase direction, as this can vary when setting up the interferometer. Therfore hit the \'Generate Preview\' button and chose the correct direction.
Plug the direction into the \'Phasedir\' entry field (only \'n\' for negative and \'p\' for positive are supported.)
When you are done you will be able to press the \'Synccorrection\' button and start the correction. The correction will automatically be applied to all phase channels.
The channels will get the appendix\'_corrected\' and are exported as \'.gsf\' files."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Synccorrection Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class PhaseOffsetPopup_using_package_library():
    def __init__(self, parent, measurement, phase_channel):
        phase_data = measurement.all_data[measurement.channels.index(phase_channel)]
        from snom_analysis.lib.phase_slider import get_phase_offset
        self.phase_offset = get_phase_offset(phase_data)

class PhaseOffsetPopup():
    def __init__(self, parent, measurement, phase_channel, autoscale) -> None:
        self.parent = parent
        self.phase_channel = phase_channel
        self.measurement = measurement
        self.autoscale = autoscale
        self.window_width = 1000
        self.window_height = 600
        self.cmap = SNOM_phase

        self.phase_data = self.measurement.all_data[measurement.channels.index(self.phase_channel)]
        # print('original xres, yres: ', len(self.phase_data[0]), len(self.phase_data))
        self.shifted_phase_data = np.copy(self.phase_data)# temporary copy
        # resize phase data to make preview more efficient
        self.phase_data_resized = self.resize_data(self.phase_data, [self.window_width-100,self.window_height])
        # print('resized xres, yres: ', len(self.phase_data_resized[0]), len(self.phase_data_resized))
        self.phase_shift = 0

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Shift Phase')
        # self.window.geometry(f'800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

        self._create_menu()
        self._create_canvas()
        self._change_popup_size()

        # self._start_leveling()
        self.window.bind('<Return>', self._on_change_entry)
        self.canvas_area.bind("<Configure>", self._windowsize_changed)
        # all the space for canvas
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.mainloop()

    def _change_popup_size(self):
        self.window.update_idletasks()
        # self.window.update()
        # get current size:
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        # get image size:
        xres = len(self.phase_data_resized[0])
        yres = len(self.phase_data_resized)
        # get menu width:
        menu_width = self.frame.winfo_width()
        menu_height = self.frame.winfo_height()
        # total needed size:
        x_total = xres + menu_width + 0 # somehow there is some unknown padding or so...
        y_total = yres + menu_height + 0 # somehow there is some unknown padding or so...
        # adjust winwo size:
        # get the screen width and height of the display used
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - x_total/2)
        center_y = int(screen_height/2 - y_total/2)
        self.window.geometry(f"{x_total}x{y_total}+{center_x}+{center_y}")
        # print('changed window geometry to: ', x_total, y_total)

    def _windowsize_changed(self, event):
        self.window.update_idletasks()
        # get current size:
        width = self.canvas_area.winfo_width()
        height = self.canvas_area.winfo_height()
        # resize image
        # the bounds have to be reduced by the padding and text height of the labelframe containing the canvas
        text_height = 12
        self.phase_data_resized = self.resize_data(self.phase_data, [width-4*button_padx, height-4*button_pady-text_height], min_dev=0, max_scaling=5)
        # update image
        self._update_image(self.phase_shift)

    def _create_canvas(self):
        # canvas area
        self.window.update_idletasks()
        # self.canvas_area = ttkb.Frame(self.window)
        self.canvas_area = ttkb.LabelFrame(self.window, text='Phase Shift Preview', padding=button_padx)
        self.canvas_area.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)
        self.canvas = ttkb.Canvas(self.canvas_area, width=self.window_width-self.frame.winfo_width(), height=self.window_height)
        self.canvas.pack(expand=True, fill='both')
        # Initial plot
        # create image
        phase_data_scaled = ((self.phase_data_resized - np.min(self.phase_data_resized)) / (np.max(self.phase_data_resized) - np.min(self.phase_data_resized)) * 255).astype(np.uint8)
        self.image = Image.fromarray(np.uint8(self.cmap(phase_data_scaled)*255))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def resize_data(self, data, bounds:list=[500,500], min_dev=0.3, max_scaling:int=5):
        # bounds = [x,y] in px
        # min dev means if data is more than min_dev (in percent) smaller that the respective bound it should be upscaled
        x_bound, y_bound = bounds
        # print('x_bound, y_bound:', x_bound, y_bound)
        xres = len(data[0])
        yres = len(data)
        x_scaling, y_scaling = 1, 1
        # print('xres:', xres, 'yres:', yres)
        
        # print('canvas size:', self.canvas_frame.winfo_width(), self.canvas_frame.winfo_height())
        # if resolutionis larger than the canvas size, resize the data
        if xres > x_bound:
            xres = x_bound
            x_scaling = (xres / len(data[0]))
            y_scaling = x_scaling
            yres = int(yres * x_scaling)
        elif yres > y_bound:
            yres = y_bound
            y_scaling = (yres / len(data))
            x_scaling = y_scaling
            xres = int(xres * y_scaling)
        elif xres < x_bound and yres < y_bound:
            x_scaling = x_bound / xres
            y_scaling = y_bound / yres
            if x_scaling < y_scaling:
                xres = x_bound
                yres = int(yres * x_scaling)
            else:
                yres = y_bound
                xres = int(xres * y_scaling)
        # print('x_scaling:', x_scaling, 'y_scaling:', y_scaling)
        if (xres != len(data[0]) or yres != len(data)) and ((x_scaling > (1 + min_dev) and y_scaling > (1 + min_dev)) or (x_scaling < (1 - min_dev) and y_scaling < (1 - min_dev))):
            # print('Resizing data')
            # print('xres:', xres, 'yres:', yres)
            # print('x_scaling:', x_scaling, 'y_scaling:', y_scaling)
            if x_scaling > max_scaling and y_scaling > max_scaling: 
                xres = len(data[0])*max_scaling
                yres = len(data)*max_scaling
                # instead of upscaling the data which would make the phase shift calculation slower we implement the zoom method for the photoimage
                # self.zoom_factor = min([x_scaling, y_scaling])
                # print('zoom factor: ', self.zoom_factor)
                # return data
            # else:
                # return np.resize(data, (yres, xres))
            img = Image.fromarray(data)
            img = img.resize((xres, yres), Image.Resampling.NEAREST)
            return np.array(img)
        # print('Data not resized')
        return data

    def _shift_phase(self, data, shift):
        def apply_shift(x):
            return (x + shift) % (2*pi)
        return np.vectorize(apply_shift)(data)   

    def _save_leveled_data(self):
        # self.measurement._write_to_logfile('height_leveling_coordinates', self.klick_coordinates)
        self.phase_offset = float(self.entry_slider.get())
        self.window.quit()
        self.window.destroy()

    def _update_image(self, val):
        try:
            self.phase_shift = float(val)
            shifted_phase_data = self._shift_phase(self.phase_data_resized, float(val))
            # print('xres, yres: ', len(shifted_phase_data[0]), len(shifted_phase_data))
            phase_data_scaled = ((shifted_phase_data - np.min(shifted_phase_data)) / (np.max(shifted_phase_data) - np.min(shifted_phase_data)) * 255).astype(np.uint8)
            image = Image.fromarray(np.uint8(self.cmap(phase_data_scaled)*255))
            tk_image = ImageTk.PhotoImage(image)
            self.canvas.imgref = tk_image
            self.canvas.itemconfig(self.image_on_canvas, image=tk_image)
        except: pass

    def _on_change_slider(self, event):
        phase = 2*pi/100*float(event)
        # self.slider_var.set(f"{phase:.2f}")
        self.entry_slider.delete(0, END)
        self.entry_slider.insert(0, str(round(float(phase),2)))
        self._update_image(phase)  

    def _on_change_entry(self, event):
        # print('entry changed: event: ', event)
        # print('event type: ', type(event))
        # print('entry value: ', self.entry_slider.get())
        # print('entry value type: ', type(self.entry_slider.get()))
        # self.slider.set(self.entry_slider.get())
        value = float(self.entry_slider.get())
        slider_val = value/(2*pi)*100
        self.slider.set(slider_val)
        self._on_change_slider(str(slider_val))

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Shift Phase Data', padding=10)
        self.frame.grid(column=1, row=0)

        self.entry_slider = ttkb.Entry(self.frame, width=10, justify='center')
        self.entry_slider.insert(0, 0)
        self.entry_slider.grid(column=0, row=1, sticky='nsew', padx=button_padx, pady=button_pady)

        self.slider = ttkb.Scale(self.frame, from_=0, to=100, orient=HORIZONTAL, command=self._on_change_slider) # bootstrap slider has a self recursive bug, not good for big data
        self.slider.set(0)
        self.slider.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.button_save = ttkb.Button(self.frame, text='Save', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save.grid(column=0, row=2, sticky='nsew', padx=button_padx, pady=button_pady)

        help_message = """This simple phase offset correction will apply a phase correction to all phase channels in memory.
Currently the first phase channel is used as a preview channel.
To change the phase offset simply change the slider or type the value in the entry field and hit enter.
You can use the left mouse button to drag and drop the slider. If you click the left mouse button on the slider the slider will move in that direction by a small amount (1%), good for finetuning.
If you right click on the slider the slider will move to the position of the mouse pointer.
You can also change the size of the popup and thus the image by dragging the window borders.
However be aware that the data will be scaled accordingly so larger image means slower preview.
There is also a maximum scaling factor of 5 to limit the size of the data. If the data becomes too large and the slider feedback too slow, bugs might appear..."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the 3 Point Heigth Leveling Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)


class PhaseOffsetPopup_old():
    def __init__(self, parent, measurement, phase_channel, autoscale) -> None:
        self.parent = parent
        self.phase_channel = phase_channel
        self.measurement = measurement
        self.autoscale = autoscale
        self.window_width = 1000
        self.window_height = 600

        self.phase_data = self.measurement.all_data[measurement.channels.index(self.phase_channel)]
        self.shifted_phase_data = np.copy(self.phase_data)# temporary copy
        self.previous_shift = 0


        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Shift Phase')
        # self.window.geometry(f'800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

        self._create_menu()
        self._create_canvas()
        self._change_popup_size()

        self._fill_canvas()

        # self._start_leveling()
        self.window.bind('<Return>', self._on_change_entry)
        # all the space for canvas
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.mainloop()

    def _change_popup_size(self):
        self.window.update()
        # self.window.update_idletasks()
        canvas_width = self.canvas_area.winfo_width()
        # print('canvasframe width: ', self.canvas_area.winfo_width())
        # print('canvasfig width: ', self.canvas_fig.winfo_width())
        # self.canvas_fig
        # print('menu width: ', self.frame.winfo_width())
        menu_width = self.frame.winfo_width()
        self.window.geometry(f'{self.window_width}x{self.window_height}')

    def _create_canvas(self):
        # canvas area
        self.window.update()

        self.canvas_area = ttkb.Frame(self.window, width=self.window_width-self.frame.winfo_width(), height=self.window_height)
        self.canvas_area.grid(column=0, row=0, sticky='nsew')
        # self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.window_width-self.frame.winfo_width(), height=self.window_height)
        # self.canvas_frame.grid(column=0, row=0, sticky='nsew')

    def _create_fig(self):

        self.fig, axis = plt.subplots()
        self.plot = plt.pcolormesh(self.shifted_phase_data, cmap=SNOM_phase, vmin=0, vmax=pi*2)
        axis.invert_yaxis()
        divider = make_axes_locatable(axis)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = plt.colorbar(self.plot, cax=cax)
        cbar.ax.get_yaxis().labelpad = 15
        label = 'Phase'
        title = 'Shift the phase'
        cbar.ax.set_ylabel(label, rotation=270)
        axis.set_title(title)
        axis.axis('scaled')

    def _create_fig_v2(self):

        self.fig = Figure()
        axis = self.fig.add_subplot()
        self.plot = axis.pcolormesh(self.shifted_phase_data, cmap=SNOM_phase, vmin=0, vmax=pi*2)
        axis.invert_yaxis()
        divider = make_axes_locatable(axis)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = plt.colorbar(self.plot, cax=cax)
        cbar.ax.get_yaxis().labelpad = 15
        label = 'Phase'
        title = 'Shift the phase'
        cbar.ax.set_ylabel(label, rotation=270)
        axis.set_title(title)
        axis.axis('scaled')

    def _fill_canvas(self):
        self._create_fig()
        # self._create_fig_v2()
        # self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
         
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        # self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.window.update_idletasks()
        self.canvas_fig.draw()
        # extra frame because canvas is buggy, but only for initialization
        '''
        try: self.canvas_frame.winfo_exists()
        except:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)  
            self.canvas_frame = ttkb.Frame(self.canvas_area, width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
            self.canvas_frame.pack()

            # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            # self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)   
            self.canvas_fig.draw()
        else:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_frame)
            self.canvas_fig.draw()
            # self._Change_Mainwindow_Size()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)'''

    def _shift_phase(self):
        yres = len(self.shifted_phase_data)
        xres = len(self.shifted_phase_data[0])
        for y in range(yres):
            for x in range(xres):
                # self.shifted_phase_data[y][x] = (self.shifted_phase_data[y][x] + (float(self.rounded_val) - self.previous_shift)) % (2*np.pi)
                self.shifted_phase_data[y][x] = (self.phase_data[y][x] + float(self.rounded_val)) % (2*pi)
        # self.previous_shift = float(self.rounded_val)   

    def _save_leveled_data(self):
        # self.measurement._write_to_logfile('height_leveling_coordinates', self.klick_coordinates)
        self.phase_offset = float(self.rounded_val)
        self.window.quit()
        self.window.destroy()

    def _on_change_slider(self, event):
        print('slider changed: event: ', event)
        print('event type: ', type(event))
        print('old value: ', self.rounded_val)
        # print('slider value: ', str(self.slider.get()))
        # new_val = str(round(float(self.slider.get()), 3))
        # new_val = round(self.slider.get(), 3)
        new_val = event
        if new_val != self.rounded_val:
            # self.rounded_val = str(round(float(self.slider.get()), 3))
            # self.rounded_val = round(float(self.slider.get()), 3)
            self.rounded_val = new_val
            self.entry_slider.delete(0, END)
            # self.entry_slider.insert(0, float(self.rounded_val))
            self.entry_slider.insert(0, str(round(float(event),2)))
            # self.shifted_phase_data = self.measurement._Shift_Phase_Data(self.phase_data, float(self.rounded_val))
            self._shift_phase()
            print('shifted phase data')
            self._fill_canvas()
            gc.collect()
        print('changed slider')

    def _on_slider_click(self, event):
        """Handle clicking on the slider to set the value directly."""
        slider_length = self.slider.winfo_width()
        slider_start = self.slider.winfo_rootx()
        click_position = event.x_root - slider_start
        value = self.slider.cget("from") + (click_position / slider_length) * (self.slider.cget("to") - self.slider.cget("from"))
        self.slider.set(value)
        

    def _on_change_entry(self, event):
        print('entry changed: event: ', event)
        print('entry value: ', self.entry_slider.get())
        self.slider.set(self.entry_slider.get())
        self._on_change_slider(event)

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Shift Phase Data', padding=10)
        self.frame.grid(column=1, row=0)

        self.slider = ttkb.Scale(self.frame, from_=0, to=2*pi, orient=HORIZONTAL, command=self._on_change_slider) # bootstrap slider has a self recursive bug, not good for big data
        # self.slider = ttk.Scale(self.frame, from_=0, to=2*pi, orient=HORIZONTAL, command=self._on_change_slider)
        # self.slider =  tk.Scale(self.frame, from_=0, to=2*pi, orient=HORIZONTAL, command=self._on_change_slider, resolution=0.1)
        self.slider.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.slider.set('1.3')
        self.rounded_val = '0'

        self.entry_slider = ttkb.Entry(self.frame, width=10, justify='center')
        self.entry_slider.insert(0, 0)
        self.entry_slider.grid(column=0, row=1, sticky='nsew', padx=button_padx, pady=button_pady)

        self.button_save = ttkb.Button(self.frame, text='Save', bootstyle=SUCCESS, command=self._save_leveled_data)
        self.button_save.grid(column=0, row=2, sticky='nsew', padx=button_padx, pady=button_pady)


        # self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        # self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        # self.label_zone_width = ttkb.Label(self.frame, text='Pixel integration width:')
        # self.label_zone_width.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.entry_zone_width = ttkb.Entry(self.frame, width=input_width, justify='center')
        # self.entry_zone_width.insert(0, 5)
        # self.entry_zone_width.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')

        # self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Start Leveling', bootstyle=PRIMARY, command=self._level_height_channel)
        # # button_save_to_gsftxt.config(state=DISABLED) # todo disable unless clicker was clicked exactly 3 times
        # self.button_save_to_gsftxt.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.button_redo_leveling = ttkb.Button(self.frame, text='Redo Leveling', bootstyle=WARNING, command=self._redo_leveling)
        # self.button_redo_leveling.grid(column=0, row=4, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.button_save_leveling = ttkb.Button(self.frame, text='Save Leveling', bootstyle=SUCCESS, command=self._save_leveled_data)
        # self.button_save_leveling.grid(column=0, row=5, sticky='nsew', padx=button_padx, pady=button_pady)


        help_message = """This simple phase offset correction will apply a phase correction to all phase channels in memory.
Currently the first phase channel is used as a preview channel.
To change the phase offset simply change the slider or type the value in the entry field and hit enter."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the 3 Point Heigth Leveling Work?', help_message))
        self.button_help.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class CreateRealpartPopup():
    def __init__(self, parent, preview_ampchannel, preview_phasechannel) -> None:
        self.parent = parent

        # self.window = tk.Tk()
        # self.window = ttkb.Window(alpha=0.9, position=[600,300]) #themename='darkly', 
        # self.window = ttkb.Window(themename='darkly', position=[600,300])
        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Create Real or Imaginary Data')
        self.window.geometry('500x400')
        self.preview_ampchannel = preview_ampchannel
        self.preview_phasechannel = preview_phasechannel
        # self.window.title('Scrolling')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')
        
        self._create_input()

        self.window.mainloop()

    def _create_input(self):
        self.frame = ttkb.Labelframe(self.window, text='Create Complex Data', padding=10)
        # self.frame.pack()
        self.frame.pack(pady=20)

        self.change_complextype_label = ttkb.Label(self.frame, text='Change Complex Type:', padding=10)
        self.change_complextype_label.grid(column=0, row=0, sticky='e')
        self.current_complextype = tk.StringVar()
        self.cb_complextype = ttkb.Combobox(self.frame, textvariable=self.current_complextype, width=4, justify=CENTER)
        self.cb_complextype['values'] = ['real', 'imag']
        self.cb_complextype.current(0)
        # prevent typing a value
        self.cb_complextype['state'] = 'readonly'
        self.cb_complextype.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        
        self.entry_label_amp_channel = ttkb.Label(self.frame, text='Select the amp channel:')
        self.entry_label_amp_channel.grid(column=0, row=1, padx=input_padx, pady=input_pady, sticky='nsew')
        self.entry_amp_channel = ttkb.Entry(self.frame, justify=CENTER)
        self.entry_amp_channel.insert(0, self.preview_ampchannel)
        self.entry_amp_channel.grid(column=1, row=1, padx=input_padx, pady=input_pady, sticky='nsew')

        self.entry_label_phase_channel = ttkb.Label(self.frame, text='Select the phase channel:')
        self.entry_label_phase_channel.grid(column=0, row=2, padx=input_padx, pady=input_pady, sticky='nsew')
        self.entry_phase_channel = ttkb.Entry(self.frame, justify=CENTER)
        self.entry_phase_channel.insert(0, self.preview_phasechannel)
        self.entry_phase_channel.grid(column=1, row=2, padx=input_padx, pady=input_pady, sticky='nsew')





        # save button, only enable if plot was generated previously
        self.button_save_to_gsftxt = ttkb.Button(self.frame, text='Create Data', bootstyle=SUCCESS, command=self._return_inputs)
        # button_save_to_gsftxt.config(state=DISABLED)
        self.button_save_to_gsftxt.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        
        help_message = """This method creates real or imaginary data.
Select the complex type you want to create and also the amplitude and phase channel to use.
The channels do not have to be in memory, if they aren't only the new real or imag channel will be added.
"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How Does This Method Work?', help_message))
        self.button_help.grid(column=0, row=8, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        self.window.update()
        
    def _return_inputs(self):
        self.complex_type = self.cb_complextype.get()
        self.amp_channel = self.entry_amp_channel.get()
        self.phase_channel = self.entry_phase_channel.get()
        self.window.quit()
        self.window.destroy()

class HeightMaskingPopup():
    def __init__(self, parent, channels, measurement, default_dict) -> None:
        self.parent = parent
        self.channels = channels
        self.measurement = measurement
        self.default_dict = default_dict
        
        self.preview_channel = self.measurement.height_channel
        # if height channel not in measurement load it extra
        if self.preview_channel not in self.measurement.channels:
            self.measurement.add_channels([self.preview_channel])

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Height Masking')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 

    def _heightmask_preview(self):#todo
        height_data = self.measurement.all_data[self.measurement.channels.index(self.preview_channel)]
        self.threshold = float(self.entry_threshold.get())
        self.mask_array = self.measurement._create_mask_array(height_data, self.threshold)
        

        self.fig, ax = plt.subplots()
        masked_height_data = np.multiply(height_data, self.mask_array)
        ax.pcolormesh(masked_height_data, cmap=SNOM_height)
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()

        plt.title('Height Mask Preview')

        self._fill_canvas()
        self.button_heightmask.config(state=ON)

    def _heightmask(self):
        self.mask_channels = self.select_heightmask_channel.get().split(',')
        
        
        for channel in self.measurement.channels:
            if channel in self.mask_channels:
                channel_index = self.measurement.channels.index(channel)
                self.measurement.all_data[channel_index] = np.multiply(self.measurement.all_data[channel_index], self.mask_array)
                self.measurement.channels_label[channel_index] = self.measurement.channels_label[channel_index] + '_masked'

        print('The following channels have been masked!\n', self.mask_channels)
        self.measurement._write_to_logfile('height_masking_threshold', self.threshold)
        # also make shure to transferr the mask array to the measurement, 
        # because it needs to know it for autocut and to plot a white border around masked areas
        self.measurement.mask_array = self.mask_array
        if self.autocut.get() == 1:
            # self.measurement._Auto_cut_channels(self.mask_channels)
            self.measurement.cut_channels(self.mask_channels, autocut=True)
        
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Height Masking', padding=10)
        self.frame.grid(column=1, row=0, padx=button_padx, pady=button_pady)
        # self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        # self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        # scaling factor 4 means every pixel will be scaled to scaling**2 subpixels
        self.label_threshold = ttkb.Label(self.frame, text='Threshold:')
        self.label_threshold.grid(column=0, row=0)
        self.entry_threshold = ttkb.Entry(self.frame, width=input_width, justify='center')
        self.entry_threshold.insert(0, self.default_dict['height_threshold'])
        self.entry_threshold.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # sigma for gauss blurr
        # self.label_gaussblurr_sigma = ttkb.Label(self.frame, text='Sigma:')
        # self.label_gaussblurr_sigma.grid(column=0, row=1)
        # self.gaussblurr_sigma = ttkb.Entry(self.frame, width=input_width, justify='center')
        # self.gaussblurr_sigma.insert(0, 2)
        # self.gaussblurr_sigma.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')
        # which channels to blurr?
        self.label_select_heightmask_channel = ttkb.Label(self.frame, text='Select Channels to Mask:')
        self.label_select_heightmask_channel.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_heightmask_channel = ttkb.Entry(self.frame, justify='center')
        self.select_heightmask_channel.insert(0, self.channels)
        self.select_heightmask_channel.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # first generate preview
        self.button_heightmask_preview = ttkb.Button(self.frame, text='Generate Preview', command=self._heightmask_preview)
        self.button_heightmask_preview.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        self.autocut = ttkb.IntVar()
        self.autocut.set(0)
        self.checkbox_autocut = ttkb.Checkbutton(self.frame, text='Autocut Channels', variable=self.autocut, onvalue=1, offvalue=0)
        self.checkbox_autocut.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # start Masking
        self.button_heightmask = ttkb.Button(self.frame, text='Heightmask Channels', bootstyle=PRIMARY, command=self._heightmask)
        self.button_heightmask.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.button_heightmask.config(state=DISABLED)

        #todo
        help_message = """The height masking method creates a mask array based on a threshold value of the standard height channel.
If the height channel is not part of the channels in memory it will be loaded automatically.
The masking procedure sets all pixels with a height value above the treshold to 1 and below the threshold to 0.
Please make shure to use leveled data or make use of the 3 point height leveling fuction.
The mask can then be applied to all channels in memory or just specific ones.
If you want to get rid of zero value pixels on the autside check the autocut checkbox."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Height Masking Work?', help_message))
        self.button_help.grid(column=0, row=7, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class RotationPopup():
    def __init__(self, parent, channels, measurement, default_dict) -> None:
        self.parent = parent
        self.channels = channels
        self.measurement = measurement
        self.default_dict = default_dict

        self.rotation_orientation = (1,0)# oder anders herum? wie rum definieren? geg. Uhrzeigersinn?

        self.preview_channel = self.channels.split(',')[0] # just use the first channel in memory for now
        #find out colormap
        if self.measurement.height_indicator in self.preview_channel:
            self.preview_cmap = SNOM_height
        elif self.measurement.phase_indicator in self.preview_channel:
            self.preview_cmap = SNOM_phase
        elif self.measurement.amp_indicator in self.preview_channel:
            self.preview_cmap = SNOM_amplitude

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Rotation')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

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

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 

    def _rotation_preview(self):#todo
        self.rotation = float(self.cb_rotation.get())
        preview_data = self.measurement.all_data[self.measurement.channels.index(self.preview_channel)]
        # preview_measurement = self.measurement.copy().all_data[self.measurement.channels.index(self.preview_channel)]
        
        #start the rotation:
        rotations = int(self.rotation / 90)
        for i in range(rotations):
            preview_data = np.rot90(preview_data, axes=self.rotation_orientation)
        
        

        self.fig, ax = plt.subplots()
        ax.pcolormesh(preview_data, cmap=self.preview_cmap)
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()

        plt.title('Rotation Preview')

        self._fill_canvas()

    def _rotate(self):
        self.rotation = float(self.cb_rotation.get())
        self.rotation_channels = self.select_heightmask_channel.get().split(',')
        rotations = int(self.rotation / 90)        
        
        '''for channel in self.measurement.channels:
            if channel in self.rotation_channels:
                channel_index = self.measurement.channels.index(channel)
                
                for i in range(rotations):
                    self.measurement.all_data[channel_index] = np.rot90(self.measurement.all_data[channel_index], axes=self.rotation_orientation) # todo, rotations larger than 90 lead to issues with gif
                self.measurement.channels_label[channel_index] = self.measurement.channels_label[channel_index] + '_rotated' # eigentlich ueberfluessig

                XReal, YReal = self.measurement.channel_tag_dict[self.measurement.channels.index(channel)][MeasurementTags.scan_area]
                self.measurement.channel_tag_dict[self.measurement.channels.index(channel)][MeasurementTags.scan_area] = [YReal, XReal]
                XRes, YRes = self.measurement.channel_tag_dict[self.measurement.channels.index(channel)][MeasurementTags.pixel_area]
                self.measurement.channel_tag_dict[self.measurement.channels.index(channel)][MeasurementTags.pixel_area] = [YRes, XRes]
                self.measurement.channel_tag_dict[self.measurement.channels.index(channel)][MeasurementTags.rotation] += rotations*90 # careful, i dont know the definition from the snom

        # print('The following channels have been masked!\n', self.rotation_channels)
        # self.measurement._write_to_logfile('height_masking_threshold', self.threshold)
        self.measurement._write_to_logfile('rotation', self.rotation)
        # also make shure to transferr the mask array to the measurement, 
        # because it needs to know it for autocut and to plot a white border around masked areas'''
        for i in range(rotations):
            self.measurement.rotate_90_deg()

        
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Rotation', padding=10)
        self.frame.grid(column=1, row=0, padx=button_padx, pady=button_pady)
        # self.label_howto = ttkb.Label(self.frame, text='Please select 3 Points to Specify the Background Plane!')
        # self.label_howto.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.change_rotation_label = ttkb.Label(self.frame, text='Rotation:', padding=10)
        self.change_rotation_label.grid(column=0, row=0, sticky='e')
        self.current_rotation = tk.StringVar()
        self.cb_rotation = ttkb.Combobox(self.frame, textvariable=self.current_rotation, width=3, justify=CENTER)
        self.cb_rotation['values'] = ['0', '90', '180', '270']
        self.cb_rotation.current(0)
        # prevent typing a value
        self.cb_rotation['state'] = 'readonly'
        self.cb_rotation.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        # sigma for gauss blurr
        # self.label_gaussblurr_sigma = ttkb.Label(self.frame, text='Sigma:')
        # self.label_gaussblurr_sigma.grid(column=0, row=1)
        # self.gaussblurr_sigma = ttkb.Entry(self.frame, width=input_width, justify='center')
        # self.gaussblurr_sigma.insert(0, 2)
        # self.gaussblurr_sigma.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')
        # which channels to blurr?
        self.label_select_heightmask_channel = ttkb.Label(self.frame, text='Select Channels to Rotate:')
        self.label_select_heightmask_channel.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_heightmask_channel = ttkb.Entry(self.frame, justify='center')
        self.select_heightmask_channel.insert(0, self.channels)
        self.select_heightmask_channel.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # first generate preview
        self.button_heightmask_preview = ttkb.Button(self.frame, text='Generate Preview', command=self._rotation_preview)
        self.button_heightmask_preview.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # start Masking
        self.button_heightmask = ttkb.Button(self.frame, text='Rotate Channels', bootstyle=PRIMARY, command=self._rotate)
        self.button_heightmask.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.button_heightmask.config(state=DISABLED)

        #todo
        help_message = """
In order to rotate you data, select one of the predefined rotation values, for now only steps of 90 deg are possible. 
You can simply preview the rotation and repeat as often as necessary.
Then make shure all the channels you want to rotate are selected and start the rotation.
"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Rotation Work?', help_message))
        self.button_help.grid(column=0, row=7, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class LogarithmPopup():
    def __init__(self, parent, channels, measurement, default_dict) -> None:
        self.parent = parent
        self.channels = channels
        self.measurement = measurement
        self.default_dict = default_dict

        # only select the amp channels as default
        self.amp_channels = []
        for channel in self.channels.split(','):
            if self.measurement.amp_indicator in channel:
                self.amp_channels.append(channel)

        # try to select an amp channel for preview, this will take the last found
        self.preview_channel = None
        for i in range(len(self.channels.split(','))):
            if self.measurement.amp_indicator in self.channels.split(',')[i]:
                self.preview_channel = self.channels.split(',')[i]
        if self.preview_channel is None:
            self.preview_channel = self.channels.split(',')[0] # just use the first channel in memory for now

        #find out colormap
        if self.measurement.height_indicator in self.preview_channel:
            self.preview_cmap = SNOM_height
        elif self.measurement.phase_indicator in self.preview_channel:
            self.preview_cmap = SNOM_phase
        elif self.measurement.amp_indicator in self.preview_channel:
            self.preview_cmap = SNOM_amplitude

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Logarithm')
        self.window.geometry('800x600')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')

        self._create_canvas()
        self._create_menu()

        # all the space for canvas
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.mainloop()

    def _create_canvas(self):
        # canvas area
        self.canvas_area = ttkb.Frame(self.window, width=600, height=600)
        self.canvas_area.grid(column=0, row=0, sticky='nsew')

    def _fill_canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 

    def _logarithm_preview(self):#todo
        preview_data = self.measurement.all_data[self.measurement.channels.index(self.preview_channel)]
        preview_data = np.log(preview_data)

        self.fig, ax = plt.subplots()
        ax.pcolormesh(preview_data, cmap=self.preview_cmap)
        # ax.legend()
        ax.axis('scaled')
        ax.invert_yaxis()

        plt.title('Logarithm Preview')

        self._fill_canvas()

    def _apply_log(self):
        self.logarithm_channels = self.select_logarithm_channel.get().split(',')
        
        for channel in self.measurement.channels:
            if channel in self.logarithm_channels:
                channel_index = self.measurement.channels.index(channel)
                
                self.measurement.all_data[channel_index] = np.log(self.measurement.all_data[channel_index])
                self.measurement.channels_label[channel_index] = self.measurement.channels_label[channel_index] + '_log' # eigentlich ueberfluessig

        self.measurement._write_to_logfile('logarithm', self.logarithm_channels)
        
        self.window.quit()
        self.window.destroy()

    def _create_menu(self):
        self.frame = ttkb.Labelframe(self.window, text='Logarithm', padding=10)
        self.frame.grid(column=1, row=0, padx=button_padx, pady=button_pady)
        self.label_select_logarithm_channel = ttkb.Label(self.frame, text='Select Channels to apply the log to:')
        self.label_select_logarithm_channel.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_logarithm_channel = ttkb.Entry(self.frame, justify='center')
        self.select_logarithm_channel.insert(0, self.amp_channels)
        self.select_logarithm_channel.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # first generate preview
        self.button_heightmask_preview = ttkb.Button(self.frame, text='Generate Preview', command=self._logarithm_preview)
        self.button_heightmask_preview.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # start Masking
        self.button_heightmask = ttkb.Button(self.frame, text='Apply log to Channels', bootstyle=PRIMARY, command=self._apply_log)
        self.button_heightmask.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        #todo
        help_message = """
This function simply applies a log to the data, should usually only be used for amplitude data.
"""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Logarithm Work?', help_message))
        self.button_help.grid(column=0, row=7, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

class GifCreationPopup():
    def __init__(self, parent, measurement) -> None:
        self.parent = parent
        self.measurement = measurement

        self.window = ttkb.Toplevel(parent)
        self.window.grab_set()
        self.window.title('Overlay Channels')
        self.window.geometry('500x400')
        parent.eval(f'tk::PlaceWindow {str(self.window)} center')
        
        self._create_input()

        self.window.mainloop()

    def _create_input(self):
        self.frame = ttkb.Labelframe(self.window, text='Create Realpart Gif', padding=10)
        self.frame.pack(pady=20)

        # which channels to overlay?
        self.label_select_gif_channels = ttkb.Label(self.frame, text='Select Channels to make the gif out of:')
        self.label_select_gif_channels.grid(column=0, row=0, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_gif_channels = ttkb.Entry(self.frame, justify='center')
        # try to find out which channels should be used for gif:
        channels = self.measurement.channels
        initial_channels = []
        for channel in channels:
            demodulation_order = self.measurement._get_demodulation_num(channel)
            if self.measurement.amp_indicator in channel:
                # check if phase channel of same demodulation is present, either normal or e.g. corrected 
                phase_channel = channel.replace(self.measurement.amp_indicator, self.measurement.phase_indicator)
                for chan in channels:
                    if phase_channel in chan:
                        initial_channels.append(channel)
                        initial_channels.append(chan)
                        break
                if len(initial_channels) == 0: break
        if len(initial_channels) == 0:
            print('No suitable channels found for gif creation!')
            initial_channels = ['O2A','O2P']
        self.select_gif_channels.insert(0, ','.join(initial_channels))
        self.select_gif_channels.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)

        # add label plus entry for number of frames
        self.label_frames = ttkb.Label(self.frame, text='Number of Frames:')
        self.label_frames.grid(column=0, row=2, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)
        self.frames_entry = ttkb.Entry(self.frame, justify='center')
        self.frames_entry.insert(0, '20')
        self.frames_entry.grid(column=1, row=2, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)

        # add label plus entry for fps value
        self.label_fps = ttkb.Label(self.frame, text='Frames per second:')
        self.label_fps.grid(column=0, row=4, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)
        self.fps = ttkb.Entry(self.frame, justify='center')
        self.fps.insert(0, '10')
        self.fps.grid(column=1, row=4, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)

        # add label plus entry for dpi of the saved gif
        self.label_dpi = ttkb.Label(self.frame, text='DPI of the GIF:')
        self.label_dpi.grid(column=0, row=6, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)
        self.dpi = ttkb.Entry(self.frame, justify='center')
        self.dpi.insert(0, '100')
        self.dpi.grid(column=1, row=6, columnspan=1, sticky='nsew', padx=button_padx, pady=button_pady)


        self.button_start_overlay = ttkb.Button(self.frame, text='Start Gif Creation', bootstyle=SUCCESS, command=self._return_inputs)
        self.button_start_overlay.grid(column=0, row=8, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        help_message = """The Gif creation method is ment to animate the realpart of an interferometric snom measurement.
You need to select an amplitude channel and a phase channel to create the gif. They do not need to be of the same demodulation order. 
Also make shure to select the corrected phase channel if you are working with the synchronized mode."""
        # You also have to select the channels of which the data should be saved. Select none and all channels will be saved.'''
        self.button_help = ttkb.Button(self.frame, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.parent, 'How does the Gif Creation Method Work?', help_message))
        self.button_help.grid(column=0, row=9, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        
        self.window.update()
        
    def _return_inputs(self):
        # destroy previous plot
        # plt.close()
        
        self.gif_channels = self.select_gif_channels.get()

        
        self.gif_channels = [channel for channel in self.gif_channels.split(',')]
        # check if amp and phase channel have been provided and separeted by correct order
        if len(self.gif_channels) != 2:
            print('You need to provide exactly 2 channels!')
            return
        phase_indicator = self.measurement.phase_indicator
        amp_indicator = self.measurement.amp_indicator
        if phase_indicator not in self.gif_channels[0] and phase_indicator not in self.gif_channels[1]:
            print('You need to provide at least one phase channel!')
            return
        if amp_indicator not in self.gif_channels[0] and amp_indicator not in self.gif_channels[1]:
            print('You need to provide at least one amplitude channel!')
            return
        if phase_indicator in self.gif_channels[0] and amp_indicator in self.gif_channels[1]:
            self.gif_channels = [self.gif_channels[1], self.gif_channels[0]]
        else:
            self.gif_channels = [self.gif_channels[0], self.gif_channels[1]]
        # get all the other values from the entry fields
        self.frames = int(self.frames_entry.get())
        self.fps = int(self.fps.get())
        self.dpi = int(self.dpi.get())
        self.gif_path = self.measurement.create_gif(self.gif_channels[0], self.gif_channels[1], self.frames, self.fps, self.dpi)

        self.window.quit()
        self.window.destroy()        

class CutDataPopup_using_package_library():
    def __init__(self, parent, measurement):
        self.measurement = measurement
        self._cut_data()
        # from snom_analysis.lib.rectangle_selector import select_rectangle
        # self.coordinates = select_rectangle(data, channel)
    
    def _cut_data(self):
        self.measurement.cut_channels()
        

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