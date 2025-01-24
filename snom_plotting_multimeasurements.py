
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import *
# from matplotlib import pyplot as plt

# import matplotlib
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
# plt.rcParams['figure.dpi'] = 300
#import backends explicitly or they wont work in exe format
import matplotlib.backends.backend_pdf
import matplotlib.backends.backend_ps
import matplotlib.backends.backend_svg
# from random import randint
import sys
import os
# import pathlib
# this_files_path = pathlib.Path(__file__).parent.absolute()

import gc # garbage collector to delete unecessary memory 
from enum import Enum, auto
# to work with config files
from configparser import ConfigParser
import ast # for string to list, dict ... conversion

# from SNOM_AFM_analysis.python_classes_snom import *
from snom_analysis.main import PlotDefinitions, MeasurementTags, MeasurementTypes
from snom_analysis.main import SnomMeasurement, FileHandler, ApproachCurve, Scan3D
import numpy as np

# for animations like gif
import imageio
from matplotlib.animation import FuncAnimation

# import scipy
# import pickle # for saving of defaults in a binary dictionary
import json # json is a plain text file, so easy to read and manual changes possible
from pathlib import Path, PurePath
this_files_path = Path(__file__).parent
from lib.function_popup import SavedataPopup, HeightLevellingPopup, PhaseDriftCompensation, HelpPopup, SyncCorrectionPopup, GifCreationPopup
from lib.function_popup import CreateRealpartPopup, OverlayChannels, GaussBlurrPopup, PhaseOffsetPopup, HeightMaskingPopup, RotationPopup, LogarithmPopup
from lib.function_popup import CutDataPopup_using_package_library
#for scrollframe
from lib.scrollframe import ScrollFrame
from lib.channel_textfield import ChannelTextfield
# config file path for the snom_classes conig file
snom_analysis_config_path = Path(os.path.expanduser('~')) / Path('SNOM_Config') / Path('SNOM_Analysis') / Path('config.ini')


# class MeasurementTypes(Enum):
#     SNOM = auto()
#     AFM = auto() # not used yet but could be implemented to simplify the gui for afm users like a mode switch
#     APPROACHCURVE = auto()
#     APPROACH3D = auto()
#     SPECTRUM = auto()
#     NONE = auto() # if no plotting type is defined


class MainGui():
    def __init__(self):
        self.root = ttkb.Window(themename='darkly') # 'journal', 'darkly', 'superhero', 'solar', 'litera' (default) 
        self.root.minsize(width=main_window_minwidth, height=main_window_minheight)
        self.root.title("SNOM Plotter")
        
        
        # self.root.geometry(f"{1100}x{570}+200+200")
        # self.root.update_idletasks()
        # self.root.eval(f'tk::PlaceWindow . center')
        

        
        self.measurement = None # to keep track of the measurement object
        self.initialdir = os.path.expanduser('~') # will be used if no old measurement is found
        # on startup make shure the all_subplots memory gets cleaned
        PlotDefinitions.autodelete_all_subplots = True # set to false once the first measurement is loaded
        # variable to check if user has changed the channels, if so do not change on relod of new measurements
        self.relod_default_channels = True # set initialy to true, this will try to reload the old defaults set by the user
        self.file_type = None # make shure to overwrite the channels with corresponding default channels if filetype changes

        scaling = 1.33
        # scaling = 1.25
        # scaling = 1
        self.root.tk.call('tk', 'scaling', scaling)# if the windows system scaling factor is not 100% FigureCanvasTkAgg will generate a plot also scaled by that factor...
        # currently there is no way around it instead of setting the scaling manually, dont ask why 1.33 instead of 1.25, i have no idea

        # self.root.iconbitmap(os.path.join(this_files_path,'snom_plotting.ico'))
        self.root.iconbitmap(this_files_path / Path('icon.ico'))
        self._generate_savefolder()
        self._load_user_defaults_config()
        # try to load the old defaults from the last measurement
        self._init_old_measurement()
        self._main_app()
        
    def _main_app(self):
        self._left_menu()
        self._canvas_area()
        self._right_menu()
        self._change_mainwindow_size()
        self._update_scrollframes()
        # upadate the buttons
        self._initialize_buttons()
        # self.root.eval('tk::PlaceWindow . center') # does not work...
        
        # configure canvas to scale with window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        

        
        # start mainloop
        self.canvas_area.bind("<Configure>", self._windowsize_changed)
        self.root.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.root.protocol("WM_DELETE_WINDOW", self._exit)# make shure all processes are closed when closing main window

        self.root.mainloop()

    def _left_menu(self):
        self.menu_left = ttkb.Frame(self.root, padding=5)
        self.menu_left.grid(column=0, row=0, rowspan=2)

        self.menu_left_scrollframe = ScrollFrame(self.menu_left, main_window_minheight-2*button_pady) #, 160 make adaptable to fig height
        self.menu_left_scrollframe.pack(expand=True, fill='both')
        self.menu_left_scrollframe.changeCanvasHeight(self.root.winfo_height()) # initialize to stretch to full height

        
        self.menu_left_upper = ttkb.LabelFrame(self.menu_left_scrollframe.viewPort, text='Main controls')
        self.menu_left_upper.grid(column=0, row=0, padx=button_padx, pady=button_pady)

        # add mode switch to change ui and functions for snom plotting, approach curves, maybe spektra and more...
        # todo, for now at the bottom, but best to put it on top
        # for now just use different buttons from which only one can be selected
        self.plotting_mode_switch_frame = ttkb.Frame(self.menu_left_upper)
        self.plotting_mode_switch_frame.grid(column=0, columnspan=2, row=16)
        self.plotting_mode_switch_1 = ttkb.Button(self.plotting_mode_switch_frame, bootstyle=DANGER, text="SNOM", command=lambda: self._change_plotting_mode(MeasurementTypes.SNOM))
        self.plotting_mode_switch_1.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # for AFM users, disable certain functions which only work for snom, maybe adjust colormaps or something like that
        self.plotting_mode_switch_2 = ttkb.Button(self.plotting_mode_switch_frame, bootstyle=DANGER, text="AFM", command=lambda: self._change_plotting_mode(MeasurementTypes.AFM))
        # self.plotting_mode_switch_2.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # for Approach curves
        self.plotting_mode_switch_3 = ttkb.Button(self.plotting_mode_switch_frame, bootstyle=DANGER, text="A. Curve", command=lambda: self._change_plotting_mode(MeasurementTypes.APPROACHCURVE))
        self.plotting_mode_switch_3.grid(column=2, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # for 3D Measurements (multiple Approach curves)
        self.plotting_mode_switch_4 = ttkb.Button(self.plotting_mode_switch_frame, bootstyle=DANGER, text="3D Scan", command=lambda: self._change_plotting_mode(MeasurementTypes.SCAN3D))
        self.plotting_mode_switch_4.grid(column=3, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # for NANO FTIR spectra or so
        self.plotting_mode_switch_5 = ttkb.Button(self.plotting_mode_switch_frame, bootstyle=DANGER, text="Spectra", command=lambda: self._change_plotting_mode(MeasurementTypes.SPECTRUM))
        # self.plotting_mode_switch_5.grid(column=4, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # turn on the mode which is currently active if it was found in user defaults for the old measurement
        self._change_plotting_mode_button_color(self.plotting_mode, 1)

        # top level controls for plot
        self.get_folder_path_button = ttkb.Button(self.menu_left_upper, text="Select Measurement", bootstyle=PRIMARY, command=lambda:self._get_new_folderpath())
        self.get_folder_path_button.grid(column=0, row=0, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.label_select_channels = ttkb.Label(self.menu_left_upper, text='Select Channels:')
        
        # new version based on text field, can extend over multiple lines if many channels are in memory
        self.select_channels_text = ttkb.Text(self.menu_left_upper, width=20, height=1)
        self.select_channels_text.tag_config('center', justify=CENTER) # only works on first line
        self.select_channels_text.tag_add('center', '1.0', END)
        self.select_channels_text.grid(column=0, row=2, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.select_channels_text.insert(END, ','.join(self._get_default_channels()), 'center')

        self.SnomMeasurement_button = ttkb.Button(self.menu_left_upper, text="Load Channels", bootstyle=INFO, command=self._create_measurement)
        self.SnomMeasurement_button.grid(column=0, row=3, columnspan=1, padx=button_padx, pady=button_pady, sticky='nsew')
        if self.file_type == None:
            self.SnomMeasurement_button.config(state=DISABLED)
        self.generate_plot_button = ttkb.Button(self.menu_left_upper, text="Plot Channels", bootstyle=INFO, command=lambda:self._generate_plot())
        self.generate_plot_button.config(state=DISABLED)
        self.generate_plot_button.grid(column=1, row=3, columnspan=1, padx=button_padx, pady=button_pady, sticky='nsew')
        # todo, update plot button
        self.update_plot_button = ttkb.Button(self.menu_left_upper, text='Update Plot', command=self._update_plot)
        self.update_plot_button.config(state=DISABLED)
        self.update_plot_button.grid(column=0, row=4, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # plot all plot in memory:
        self.generate_all_plot_button = ttkb.Button(self.menu_left_upper, text="Show all Plots", bootstyle=PRIMARY, command=self._generate_all_plot)
        self.generate_all_plot_button.config(state=DISABLED)
        self.generate_all_plot_button.grid(column=0, row=5, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # save button, only enable if plot was generated previously
        self.button_save_to_gsftxt = ttkb.Button(self.menu_left_upper, text='Save Data', bootstyle=SUCCESS, command=self._save_to_gsf_or_txt)
        self.button_save_to_gsftxt.config(state=DISABLED)
        self.button_save_to_gsftxt.grid(column=0, row=6, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # set dpi for save method
        self.label_figure_dpi = ttkb.Label(self.menu_left_upper, text='DPI:')
        self.label_figure_dpi.grid(column=0, row=7)
        self.figure_dpi = ttkb.Entry(self.menu_left_upper, width=input_width, justify='center')
        # self.figure_dpi.insert(0, '100')
        self.figure_dpi.insert(0, self.default_dict['dpi'])
        self.figure_dpi.grid(column=1, row=7, padx=button_padx, pady=button_pady, sticky='ew')
        self.save_plot_button = ttkb.Button(self.menu_left_upper, text="Save Plot", bootstyle=SUCCESS, command=lambda:self._save_plot())
        self.save_plot_button.config(state=DISABLED)
        self.save_plot_button.grid(column=0, row=9, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        
        # exit button, closes everything
        self.exit_button = ttkb.Button(self.menu_left_upper, text='Exit', command=self._exit, bootstyle=DANGER)
        self.exit_button.grid(column=0, row=10, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        
        # save all defaults:
        self.save_defaults_button = ttkb.Button(self.menu_left_upper, text='Save User Defaults', bootstyle=SUCCESS, command=self._save_user_defaults)
        self.save_defaults_button.grid(column=0, row=11, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # load all defaults:
        self.load_defaults_button = ttkb.Button(self.menu_left_upper, text='Restore User Defaults', bootstyle=WARNING, command=self._restore_user_defaults)
        self.load_defaults_button.grid(column=0, row=12, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # restore all old defaults:
        self.restore_defaults_button = ttkb.Button(self.menu_left_upper, text='Restore Defaults', bootstyle=WARNING, command=self._restore_old_defaults)
        self.restore_defaults_button.grid(column=0, row=13, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        # help button popup
        help_message = """The main functionality of this GUI is to load and display SNOM or AFM data.
Of course, once the data is loaded it can also be manipulated by functions and then saved.

First you have to select a measurement folder. This folder should contain all the different channels created by your SNOM or AFM.
Then you select the channels you want to display or manipulate. Careful, some functions require specific channels to work! 
E.g. if you want to level your height data this channel must be included in the overal channels entry field. 
Or the gauss blurr requires amplitude and phase data of the same demodulation order, if not available it will only blurr amplitude and height data.

Did you know that the newest version of this program also supports approach curves?! If you want you can also add functionality for Nano-FTIR spectra!

The channels entry might also change depending on which functions you apply. The idea being: each data list has a corresponding channel name. 
If you perform an operation which creates new datalists, like the Overlay function these datalists will be given a new channel name, e.g. if you manipulate
your data the specific channel will get the '_manipulated' appendix to make shure you don't overwrite your original data when you hit \'Save Data\'.
All created channels together with the old ones are then displayed in the Channels entry. However you can also delete them from the entry if you don't want to display them.
They will stay in memory until you hit \'Load Channels\' again.
Everytime you select a new measurement the programm will try to find the standard channels for that filetype. You can save your default channels by typing them in the Channels entry
and pressing 'Save User Defaults'.

When you have selected some channels press the \'Load Channels\' button. This will load the data of the specified channels into the memory.
By the way if you change the channels in the entry you should reload the channels, otherwise they will not be accessible to the program.
Now you can use the \'Plot Channels\' button. This will generate a plot of the specified channels. 
Careful, from now on you should use the \'Update Plot\' button. The reason is, that whenever you press the \'Plot Channels\' button
the generated plots will automatically be appended to the all_subplots memory. This is a file in your home directory. 
These will be displayed when you click on \'Show all Plots\'. If you don't want to add the plots to this memory, e.g. you want to compare two different
measurements and have to visualize steps in between, use the \'Update Plot\' button. This does the same but it deletes the version you are updating in the plot memory before adding the updated version.
The update button will just display the current state of your data. This also includes changes like height leveling or blurring.
To reset the changes you will need to reload the channels, but until you hit save nothing is changed permanently.

The Plot memory will be deleted once you restart the application or if you hit 'Clear All Plots'.

To create the plots that you want play around with the main window by draggin it. This will change the plot dimensions. Also use the matplotlib toolbar.
You can then eigther use the matplotlibs save dialog or the build in \'Save Plot\' function, where you can also set the dpi for your plot.

If simple plotting is not enough for you, you can also play with manipulations in the right menu like adding a gaussian blurr to your data or applying a simple height leveling.
Most functions are found under the \'Advanced\' tab of the right menu. Most functions also supply some more information under the individual help buttons.

Once you setteled into a routine or adjusted everything to your liking you can also hit the \'Save User Defaults\' button. This will save most settings to a json file in your home directory.
These settings will be loaded automatically when you reopen the GUI, together with the last opened measurement folder. So go ahead and just hit 'Load Channels' and 'Plot Channels' again.
But data manipulation functions have to be applied manually.
"""
        self.menu_left_help_button = ttkb.Button(self.menu_left_upper, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.root, 'How does this GUI work?', help_message))
        self.menu_left_help_button.grid(column=0, row=14, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        self.menu_left_clear_plots_button = ttkb.Button(self.menu_left_upper, text='Clear All Plots', bootstyle=DANGER, command=self._clear_all_plots)
        self.menu_left_clear_plots_button.config(state=ON)
        self.menu_left_clear_plots_button.grid(column=0, row=15, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        
        
        '''
        self.menu_left_separator = ttkb.Separator(self.menu_left_scrollframe.viewPort, orient='horizontal')
        self.menu_left_separator.grid(column=0, row=1, columnspan=1, sticky='ew', padx=button_padx, pady=20)

        # plot styles
        self.menu_left_lower = ttkb.LabelFrame(self.menu_left_scrollframe.viewPort, text='Plot controls')
        self.menu_left_lower.grid(column=0, row=2, padx=button_padx, pady=button_pady)

        # change width of colorbar:
        self.label_colorbar_width = ttkb.Label(self.menu_left_lower, text='Colorbar width:')
        self.label_colorbar_width.grid(column=0, row=0)
        self.colorbar_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.colorbar_width.insert(0, '5')
        self.colorbar_width.insert(0, self.default_dict['colorbar_width'])
        self.colorbar_width.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # change figure width:

        self.label_canvas_fig_width = ttkb.Label(self.menu_left_lower, text='Figure width:')
        self.label_canvas_fig_width.grid(column=0, row=1)
        self.canvas_fig_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.canvas_fig_width.insert(0, f'{canvas_width}')
        self.canvas_fig_width.insert(0, self.default_dict['figure_width'])
        self.canvas_fig_width.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')

        # change figure height:
        self.label_canvas_fig_height = ttkb.Label(self.menu_left_lower, text='Figure height:')
        self.label_canvas_fig_height.grid(column=0, row=2)
        self.canvas_fig_height = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.canvas_fig_height.insert(0, self.default_dict['figure_height'])
        self.canvas_fig_height.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # hide_ticks = True
        self.checkbox_hide_ticks = ttkb.IntVar()
        self.checkbox_hide_ticks.set(self.default_dict['hide_ticks'])
        self.hide_ticks = ttkb.Checkbutton(self.menu_left_lower, text='Hide ticks', variable=self.checkbox_hide_ticks, onvalue=1, offvalue=0)
        self.hide_ticks.grid(column=0, row=3, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # show_titles = True
        self.checkbox_show_titles = ttkb.IntVar()
        self.checkbox_show_titles.set(self.default_dict['show_titles'])
        self.show_titles = ttkb.Checkbutton(self.menu_left_lower, text='Show titles', variable=self.checkbox_show_titles, onvalue=1, offvalue=0)
        self.show_titles.grid(column=0, row=4, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # tight_layout = True
        self.checkbox_tight_layout = ttkb.IntVar()
        self.checkbox_tight_layout.set(self.default_dict['tight_layout'])
        self.tight_layout = ttkb.Checkbutton(self.menu_left_lower, text='Tight layout', variable=self.checkbox_tight_layout, onvalue=1, offvalue=0)
        self.tight_layout.grid(column=0, row=5, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # hspace = 0.4 #standard is 0.4
        self.label_h_space = ttkb.Label(self.menu_left_lower, text='Horizontal space:')
        self.label_h_space.grid(column=0, row=6)
        self.h_space = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.h_space.insert(0, self.default_dict['h_space'])
        self.h_space.grid(column=1, row=6, padx=button_padx, pady=button_pady, sticky='ew')
        # add scalebar
        self.label_add_scalebar = ttkb.Label(self.menu_left_lower, text='scalebar channel:')
        self.label_add_scalebar.grid(column=0, row=7)
        self.add_scalebar = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.add_scalebar.insert(0, self.default_dict['scalebar_channel'])
        self.add_scalebar.grid(column=1, row=7, padx=button_padx, pady=button_pady, sticky='ew')
        '''
        
        # reconfigure size of left menu
        self.menu_left.update()
        # width = max(self.menu_left_upper.winfo_width() + 3*button_padx, self.menu_left_lower.winfo_width() + 3*button_padx)
        width = self.menu_left_upper.winfo_width() + 3*button_padx
        self.menu_left_scrollframe.canvas.config(width=width)

        
        # things to add?
        # plot title, colorbar width, colorbar, add scalebar, ...
        # figsizex = 10
        # figsizey = 5
        # colorbar_width = 10 # in percent, standard is 5 or 10
        # # Define Plot font sizes
        # font_size_default = 8
        # font_size_axes_title = 12
        # font_size_axes_label = 10
        # font_size_tick_labels = 8
        # font_size_legend = 8
        # font_size_fig_title = 12
        # #definitions for color bar ranges:
        # vmin_height = 0
        # vmax_height = 0
        # vmin_amp = 1 # to make shure that the values will be initialized with the first plotting command
        # vmax_amp = -1
        # # phase_cbar_range = True
        # # vmin_phase = 0
        # # vmax_phase = 0
        # vmin_real = 0
        # vmax_real = 0

    def _right_menu(self):
        self.menu_right = ttkb.Frame(self.root) #, width=200
        self.menu_right.grid(column=2, row=0, rowspan=2, padx=button_padx, pady=button_pady)

        # organize multiple menues in notebooks -> tabs
        self.menu_right_notebook = ttkb.Notebook(self.menu_right)
        self.menu_right_notebook.pack()

        self.menu_right_1_scrollframe = ScrollFrame(self.menu_right_notebook, main_window_minheight-2*button_pady) # , 170
        self.menu_right_1_scrollframe.pack()

        self.menu_right_2_scrollframe = ScrollFrame(self.menu_right_notebook, main_window_minheight-2*button_pady) # , 170
        self.menu_right_2_scrollframe.pack()

        # first tab:
        self._right_menu_tab1()

        # second tab:
        self._right_menu_tab2()

        # third tab: save channels to gsf or txt
        # self._right_menu_tab3()

        # add tabs to notebook
        self.menu_right_notebook.add(self.menu_right_1_scrollframe, text='Basic')
        # self.menu_right_notebook.add(self.menu_right_2, text='Advanced')
        self.menu_right_notebook.add(self.menu_right_2_scrollframe, text='Advanced')
        # self.menu_right_notebook.add(self.menu_right_3, text='ToDo')


        # self.menu_right_notebook.config(width=self.menu_right_1_scrollframe.winfo_width())
        #reconfigure canvas size 
        self.menu_right_1.update()
        self.menu_right_1_scrollframe.canvas.config(width=self.menu_right_1.winfo_width())
        self.menu_right_2_scrollframe.canvas.config(width=self.menu_right_1.winfo_width())
        # tab = event.widget.nametowidget(event.widget.select())
        # tab = event.widget.nametowidget(event.widget.select())
        # event.widget.configure(height=tab.winfo_reqheight())
        # event.widget.configure(width=tab.winfo_reqwidth())

    def _right_menu_tab1(self):
        self.menu_right_1 = ttkb.Frame(self.menu_right_1_scrollframe.viewPort)
        self.menu_right_1.grid(column=0, row=0)

        ################## menu for plot controls #####################
        # plot styles
        self.menu_left_lower = ttkb.LabelFrame(self.menu_right_1, text='Plot controls')
        self.menu_left_lower.grid(column=0, row=0, padx=button_padx, pady=button_pady)

        # change width of colorbar:
        self.label_colorbar_width = ttkb.Label(self.menu_left_lower, text='Colorbar width:')
        self.label_colorbar_width.grid(column=0, row=0)
        self.colorbar_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.colorbar_width.insert(0, '5')
        self.colorbar_width.insert(0, self.default_dict['colorbar_width'])
        self.colorbar_width.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # change figure width:

        self.label_canvas_fig_width = ttkb.Label(self.menu_left_lower, text='Figure width:')
        self.label_canvas_fig_width.grid(column=0, row=1)
        self.canvas_fig_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.canvas_fig_width.insert(0, f'{canvas_width}')
        self.canvas_fig_width.insert(0, self.default_dict['figure_width'])
        self.canvas_fig_width.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')

        # change figure height:
        self.label_canvas_fig_height = ttkb.Label(self.menu_left_lower, text='Figure height:')
        self.label_canvas_fig_height.grid(column=0, row=2)
        self.canvas_fig_height = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.canvas_fig_height.insert(0, self.default_dict['figure_height'])
        self.canvas_fig_height.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # hide_ticks = True
        self.checkbox_hide_ticks = ttkb.IntVar()
        self.checkbox_hide_ticks.set(self.default_dict['hide_ticks'])
        self.hide_ticks = ttkb.Checkbutton(self.menu_left_lower, text='Hide ticks', variable=self.checkbox_hide_ticks, onvalue=1, offvalue=0)
        self.hide_ticks.grid(column=0, row=3, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # show_titles = True
        self.checkbox_show_titles = ttkb.IntVar()
        self.checkbox_show_titles.set(self.default_dict['show_titles'])
        self.show_titles = ttkb.Checkbutton(self.menu_left_lower, text='Show titles', variable=self.checkbox_show_titles, onvalue=1, offvalue=0)
        self.show_titles.grid(column=0, row=4, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # title prefix like: '{Prefix: }{auto generated title}'
        self.label_measurement_title = ttkb.Label(self.menu_left_lower, text='Prefix Title:')
        self.label_measurement_title.grid(column=0, row=5, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.measurement_title = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.measurement_title.insert(0, '')
        self.measurement_title.grid(column=0, row=6, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')

        # tight_layout = True
        self.checkbox_tight_layout = ttkb.IntVar()
        self.checkbox_tight_layout.set(self.default_dict['tight_layout'])
        self.tight_layout = ttkb.Checkbutton(self.menu_left_lower, text='Tight layout', variable=self.checkbox_tight_layout, onvalue=1, offvalue=0)
        self.tight_layout.grid(column=0, row=7, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # hspace = 0.4 #standard is 0.4
        # self.label_h_space = ttkb.Label(self.menu_left_lower, text='Horizontal space:')
        # self.label_h_space.grid(column=0, row=8)
        # self.h_space = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.h_space.insert(0, self.default_dict['h_space'])
        # self.h_space.grid(column=1, row=8, padx=button_padx, pady=button_pady, sticky='ew')
        # add scalebar
        self.label_add_scalebar = ttkb.Label(self.menu_left_lower, text='scalebar channel:')
        self.label_add_scalebar.grid(column=0, row=9, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.add_scalebar = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.add_scalebar.insert(0, self.default_dict['scalebar_channel'])
        self.add_scalebar.grid(column=0, row=10, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # add sliders for the subplot parameters like hspace, wspace, etc.
        # wspace 0-1
        self.label_change_subplots_wspace = ttkb.Label(self.menu_left_lower, text='wspace:')
        self.label_change_subplots_wspace.grid(column=0, row=11, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_wspace = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_wspace.set(str(float(self.default_dict['subplot_wspace'])*10))	
        # print('wspace:', float(self.default_dict['subplot_wspace'])*10)
        self.slider_change_subplots_wspace.grid(column=0, row=12, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # hspace 0-1
        self.label_change_subplots_hspace = ttkb.Label(self.menu_left_lower, text='hspace:')
        self.label_change_subplots_hspace.grid(column=0, row=13, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_hspace = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_hspace.set(str(float(self.default_dict['subplot_hspace'])*10))
        self.slider_change_subplots_hspace.grid(column=0, row=14, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # left 0-0.5
        self.label_change_subplots_left = ttkb.Label(self.menu_left_lower, text='left:')
        self.label_change_subplots_left.grid(column=0, row=15, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_left = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_left.set(str(float(self.default_dict['subplot_left'])*20))
        self.slider_change_subplots_left.grid(column=0, row=16, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # right 0.5-1
        self.label_change_subplots_right = ttkb.Label(self.menu_left_lower, text='right:')
        self.label_change_subplots_right.grid(column=0, row=17, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_right = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_right.set(str(float(self.default_dict['subplot_right']-0.5)*20))
        self.slider_change_subplots_right.grid(column=0, row=18, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # top 0.5-1
        self.label_change_subplots_top = ttkb.Label(self.menu_left_lower, text='top:')
        self.label_change_subplots_top.grid(column=0, row=19, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_top = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_top.set(str(float(self.default_dict['subplot_top']-0.5)*20))
        self.slider_change_subplots_top.grid(column=0, row=20, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')
        # bottom 0-0.5
        self.label_change_subplots_bottom = ttkb.Label(self.menu_left_lower, text='bottom:')
        self.label_change_subplots_bottom.grid(column=0, row=21, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.slider_change_subplots_bottom = ttkb.Scale(self.menu_left_lower, from_=0, to=10, orient=HORIZONTAL, command=self._update_canvas)
        self.slider_change_subplots_bottom.set(str(float(self.default_dict['subplot_bottom'])*20))
        self.slider_change_subplots_bottom.grid(column=0, row=22, columnspan=2, padx=button_padx, pady=button_pady, sticky='ew')


        ################## separator #####################
        self.menu_right_separator = ttkb.Separator(self.menu_right_1, orient='horizontal')
        self.menu_right_separator.grid(column=0, row=1, sticky='ew', padx=button_padx, pady=20)
        
        ################## menu for data controls #####################
        self.menu_right_upper = ttkb.LabelFrame(self.menu_right_1, text='Manipulate Data') # , width=200
        self.menu_right_upper.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # set min to zero
        self.checkbox_setmintozero_var = ttkb.IntVar()
        self.checkbox_setmintozero_var.set(self.default_dict['set_min_to_zero'])
        self.set_min_to_zero = ttkb.Checkbutton(self.menu_right_upper, text='Set min to zero', variable=self.checkbox_setmintozero_var, onvalue=1, offvalue=0)
        self.set_min_to_zero.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        # autoscale
        self.checkbox_autoscale = ttkb.IntVar()
        self.checkbox_autoscale.set(self.default_dict['autoscale'])
        self.autoscale = ttkb.Checkbutton(self.menu_right_upper, text='Autoscale data', variable=self.checkbox_autoscale, onvalue=1, offvalue=0)
        self.autoscale.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        '''
        # apply gaussian filter
        self.checkbox_gaussian_blurr = ttkb.IntVar()
        self.checkbox_gaussian_blurr.set(self.default_dict['gaussian_blurr'])
        self.gaussian_blurr = ttkb.Checkbutton(self.menu_right_upper, text='Blurr Data', variable=self.checkbox_gaussian_blurr, onvalue=1, offvalue=0)
        self.gaussian_blurr.grid(column=0, row=3, padx=button_padx, pady=button_pady, sticky='nsew')
        '''
        self.checkbox_shared_phase_range = ttkb.IntVar()
        self.checkbox_shared_phase_range.set(self.default_dict['shared_phase'])
        self.shared_phase_range = ttkb.Checkbutton(self.menu_right_upper, text='Shared phase range', variable=self.checkbox_shared_phase_range, onvalue=1, offvalue=0)
        self.shared_phase_range.grid(column=0, row=3, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        # full_phase_range = True # this will overwrite the cbar
        self.checkbox_full_phase_range = ttkb.IntVar()
        self.checkbox_full_phase_range.set(self.default_dict['full_phase'])
        self.full_phase_range = ttkb.Checkbutton(self.menu_right_upper, text='Full phase range', variable=self.checkbox_full_phase_range, onvalue=1, offvalue=0)
        self.full_phase_range.grid(column=0, row=4, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # amp_cbar_range = True
        self.checkbox_amp_cbar_range = ttkb.IntVar()
        self.checkbox_amp_cbar_range.set(self.default_dict['shared_amp'])
        self.amp_cbar_range = ttkb.Checkbutton(self.menu_right_upper, text='Shared amp range', variable=self.checkbox_amp_cbar_range, onvalue=1, offvalue=0)
        self.amp_cbar_range.grid(column=0, row=5, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # real_cbar_range = True
        self.checkbox_real_cbar_range = ttkb.IntVar()
        self.checkbox_real_cbar_range.set(self.default_dict['shared_real'])
        self.real_cbar_range = ttkb.Checkbutton(self.menu_right_upper, text='Shared real range', variable=self.checkbox_real_cbar_range, onvalue=1, offvalue=0)
        self.real_cbar_range.grid(column=0, row=6, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # height_cbar_range = True
        self.checkbox_height_cbar_range = ttkb.IntVar()
        self.checkbox_height_cbar_range.set(self.default_dict['shared_height'])
        self.height_cbar_range = ttkb.Checkbutton(self.menu_right_upper, text='Shared height range', variable=self.checkbox_height_cbar_range, onvalue=1, offvalue=0)
        self.height_cbar_range.grid(column=0, row=7, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')



        help_message = """Under the 'Basic' tab you will find simple changes to the plotting behaviour.
You can change things like the width of the colorbars. This setting is in % and corresponds to the width of the corresponding image.
The figure width and height can be set in pixels to enshure that multiple images have the same dimensions. This setting will change automatically if you change the window size.
You can hide and unhide the ticks which show the pixelnumbers.
So far the titles of the images are generated automatically, this can also be disabled with the 'Show Titles' checkbox.
You can add your own prefix for the automatic titles.
Thight layout is typically used for the matplotlib plots.
You can also add a scalebar to your images. Just insert the channel names of the images which should have a scalebar. Typically i would use the height channel for that.

Next are some simple data manipulations. 
You can set the minimum value of the height channels to zero.
Autoscale data will try to stretch your data to have the correct physical dimensions. This works however only if you have chosen clever values for the resolutions.
E.g. you take a scan 1µm x 1µm and you chose a resolution of 100 on the x-axis. Then you should use 100 or 50 or 25 or 20... for the y-axis.
The programm will simply copy each pixel on the shorter axis by an integer mutliple of the resolution on the finer axis.
This means: 
    If xres=100 and yres=100 nothing happens.
    If xres=100 and yres=50 the pixels on the y-axis are duplicated.
    If xres=100 and yres=80 there is no integer to scale the y-axis accordingly.

You can change the phase range of your data to always span 0 to 2pi.
If you select the Shared ... range checkboxes all created plots will use the same datarange. Good for comparisons of multiple measurements (same channel).


"""
        self.menu_left_help_button = ttkb.Button(self.menu_right_1, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.root, 'Basic Operations', help_message))
        self.menu_left_help_button.grid(column=0, row=3, columnspan=1, padx=button_padx, pady=button_pady, sticky='ew')
        
        ''' # synccorrection is now in the advanced tab
        ################## separator #####################
        self.menu_right_separator = ttkb.Separator(self.menu_right_1, orient='horizontal')
        self.menu_right_separator.grid(column=0, row=3, sticky='ew', padx=button_padx, pady=20)

        ################## menu for synccorrection #####################
        # additional controls
        self.menu_right_synccorrection = ttkb.LabelFrame(self.menu_right_1, text='Synccorrection', width=200)
        self.menu_right_synccorrection.grid(column=0, row=4, padx=button_padx, pady=button_pady, sticky='nsew')
        # synccorrection
        self.label_synccorrection_wavelength = ttkb.Label(self.menu_right_synccorrection, text='Wavelength in µm:')
        self.label_synccorrection_wavelength.grid(column=0, row=0)
        self.synccorrection_wavelength = ttkb.Entry(self.menu_right_synccorrection, width=input_width, justify='center')
        self.synccorrection_wavelength.insert(0, self.default_dict['synccorr_lambda'])
        self.synccorrection_wavelength.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # first generate preview
        self.button_synccorrection_preview = ttkb.Button(self.menu_right_synccorrection, text='Generate preview', command=self._synccorrection_Preview)
        self.button_synccorrection_preview.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # then enter phasedir from preview
        self.label_synccorrection_phasedir = ttkb.Label(self.menu_right_synccorrection, text='Phasedir (n or p):')
        self.label_synccorrection_phasedir.grid(column=0, row=2)
        self.synccorrection_phasedir = ttkb.Entry(self.menu_right_synccorrection, width=input_width, justify='center')
        self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])
        self.synccorrection_phasedir.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # if phasedir and wavelength are known start synccorrection
        self.button_synccorrection = ttkb.Button(self.menu_right_synccorrection, text='Synccorrection', bootstyle=PRIMARY, command=self._synccorrection)
        self.button_synccorrection.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)'''

    def _right_menu_tab2(self):
        # self.menu_right_2_scrollframe = ScrollFrame(self.menu_right_notebook, main_window_minheight-2*button_pady) # , 170
        # self.menu_right_2_scrollframe.pack()
        self.menu_right_2 = ttkb.Frame(self.menu_right_2_scrollframe.viewPort)
        self.menu_right_2.grid(column=0, row=0)
        # self.menu_right_2 = ttkb.Frame(self.menu_right_notebook)
        # self.menu_right_2.pack()

        # height leveling, phase drift compensation, overlay forward and backwards channels, create real and imaginary part, 
        self.menu_right_2_height_leveling = ttkb.Button(self.menu_right_2, text='3 Point Height Leveling', bootstyle=PRIMARY, command=self._3_point_height_leveling)
        self.menu_right_2_height_leveling.config(state=DISABLED)
        self.menu_right_2_height_leveling.grid(column=0, row=0, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_phase_drift_comp = ttkb.Button(self.menu_right_2, text='Phase Drift Comp.', bootstyle=PRIMARY, command=self._phase_drift_compensation)
        self.menu_right_2_phase_drift_comp.config(state=DISABLED)
        self.menu_right_2_phase_drift_comp.grid(column=0, row=1, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_overlay = ttkb.Button(self.menu_right_2, text='Overlay Both Directions', bootstyle=PRIMARY, command=self._overlay_channels)
        self.menu_right_2_overlay.config(state=DISABLED)
        self.menu_right_2_overlay.grid(column=0, row=2, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_create_realpart = ttkb.Button(self.menu_right_2, text='Create Real Part Data', bootstyle=PRIMARY, command=self._create_realpart)
        self.menu_right_2_create_realpart.config(state=DISABLED)
        self.menu_right_2_create_realpart.grid(column=0, row=3, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_shift_phase = ttkb.Button(self.menu_right_2, text='Shift Phase', bootstyle=PRIMARY, command=self._change_phase_offset)
        self.menu_right_2_shift_phase.config(state=DISABLED)
        self.menu_right_2_shift_phase.grid(column=0, row=4, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_synccorrection = ttkb.Button(self.menu_right_2, text='Synccorrection', bootstyle=PRIMARY, command=self._synccorrection)
        self.menu_right_2_synccorrection.grid(column=0, row=5, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_gaussblurr = ttkb.Button(self.menu_right_2, text='Gauss Blurr', bootstyle=PRIMARY, command=self._gauss_blurr)
        self.menu_right_2_gaussblurr.config(state=DISABLED)
        self.menu_right_2_gaussblurr.grid(column=0, row=6, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_height_masking = ttkb.Button(self.menu_right_2, text='Height Masking', bootstyle=PRIMARY, command=self._height_masking)
        self.menu_right_2_height_masking.config(state=DISABLED)
        self.menu_right_2_height_masking.grid(column=0, row=7, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_rotation = ttkb.Button(self.menu_right_2, text='Rotate', bootstyle=PRIMARY, command=self._rotation)
        self.menu_right_2_rotation.config(state=DISABLED)
        self.menu_right_2_rotation.grid(column=0, row=8, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_transform_log = ttkb.Button(self.menu_right_2, text='Log(data)', bootstyle=PRIMARY, command=self._transform_log)
        self.menu_right_2_transform_log.config(state=DISABLED)
        self.menu_right_2_transform_log.grid(column=0, row=9, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_create_gif = ttkb.Button(self.menu_right_2, text='Gif Creation', bootstyle=PRIMARY, command=self._create_gif)
        self.menu_right_2_create_gif.config(state=DISABLED)
        self.menu_right_2_create_gif.grid(column=0, row=9, sticky='nsew', padx=button_padx, pady=button_pady)

        self.menu_right_2_cut_data = ttkb.Button(self.menu_right_2, text='Cut Data', bootstyle=PRIMARY, command=self._cut_data_manual)
        self.menu_right_2_cut_data.config(state=DISABLED)
        self.menu_right_2_cut_data.grid(column=0, row=10, sticky='nsew', padx=button_padx, pady=button_pady)



        help_message = """Under the 'Advanced' tab you will find funtions to manipulate the data.
You can do some simple height leveling by selecting 3 points which should be on the same level.

You can reduce slow phase dirfts by selecting two points along the y-axis to substract a linear phase slope.

You can overlay both the trace and retrace of you channels. This is experimental and only works for amplitude and height data. Useful to reduce noise.

You can create the realpart of your data by multiplying the amplitdue values with the cosine of the phase values. However, this will not automatically load the newly created channels.
The new channels are added to the channels input text field, but if you want to plot them you have to load them first. Similar for the synccorrection.

You can shift you phasedata by an arbitrary amount, e.g. to get an interesting phase transition to a better spot in the colorrange.
The overall phaseshift is arbitrary anyways in SNOM measurements.

You can do a Synccorrection. This is only needed when using transmission mode with synchronized enabled.
When this is used the phase accumulates an additional gradient due to the movement of the lower parabola (only on the x-axis).
This function will autoapply to all channels and creates corrected versions. These will not be loaded automatically.
Typically these channels will get the appendix '_corrected'. Since all channels will be corrected in parallel you don't have to load any data, just select the measurement folder.

You can add some blurr to your data to make them prettier. But don't overdo it since you will lose resolution. But square pixels aren't physical anyways...
And depending on your tip and resolution your pixels do not represent the true distribution anyways.

You can do some height masking to get rid of background or cut excess to better compare similar measurements.

The log will let you apply a logarithm to your data.

Most functions are better used with the script version of this programm but here you go.^^
Once you understood how everything works it relatively easy to add new functions and since we can use amplitude an phase we can also do operations with complex data
for example fourier filtering.
"""
        self.menu_left_help_button = ttkb.Button(self.menu_right_2, text='Help', bootstyle=INFO, command=lambda:HelpPopup(self.root, 'Advanced Operations', help_message))
        self.menu_left_help_button.grid(column=0, row=99, columnspan=1, padx=button_padx, pady=button_pady, sticky='ew')

    def _right_menu_tab3(self):# delete? todo
        self.menu_right_3 = ttkb.Frame(self.menu_right_notebook)
        self.menu_right_3.pack()

        # required:
        '''
        select channels, select filetype (gsf or txt), select appendix, change size of right menu on change of tab
        '''
        '''
        self.change_savefiletype_label = ttkb.Label(self.menu_right_3, text='Change Savefile Type:', padding=10)
        self.change_savefiletype_label.grid(column=0, row=0, sticky='e')
        self.current_savefiletype = tk.StringVar()
        self.cb_savefiletype = ttkb.Combobox(self.menu_right_3, textvariable=self.current_savefiletype, width=3, justify=CENTER)
        self.cb_savefiletype['values'] = ['gsf', 'txt']#[Object_type.DEFAULT_PLOT, Object_type.CHRONOLOGICAL_PLOT]
        self.cb_savefiletype.current(0)
        self.cb_savefiletype.grid(column=1, row=0, padx=input_padx, pady=input_pady, sticky='nsew')
        # self.savefiletype = self.cb_savefiletype.get()
        # prevent typing a value
        self.cb_savefiletype['state'] = 'readonly'
        self.cb_savefiletype.bind('<<ComboboxSelected>>', self._change_savefiletype)
        # select channels to save
        self.label_select_channels_tosave = ttkb.Label(self.menu_right_3, text='Select Channels:')
        self.label_select_channels_tosave.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.select_channels_tosave = ttkb.Entry(self.menu_right_3, justify='center')
        self.root.update_idletasks()
        self.select_channels_tosave.insert(0, self._get_channels(as_list=False))
        self.select_channels_tosave.grid(column=0, row=2, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # select appendix
        self.label_appendix_tosave = ttkb.Label(self.menu_right_3, text='Select Savefile Appendix:')
        self.label_appendix_tosave.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        self.appendix_tosave = ttkb.Entry(self.menu_right_3, justify='center')
        self.appendix_tosave.insert(0, self.default_dict['appendix'])
        self.appendix_tosave.grid(column=0, row=4, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # save button, only enable if plot was generated previously
        self.button_save_to_gsftxt = ttkb.Button(self.menu_right_3, text='Save Channels', bootstyle=SUCCESS, command=self._save_to_gsf_or_txt)
        self.button_save_to_gsftxt.config(state=DISABLED)
        self.button_save_to_gsftxt.grid(column=0, row=5, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        '''

    def _canvas_area(self):
        # canvas area
        self.canvas_area = ttkb.Frame(self.root) #, width=self.default_dict['figure_width'], height=self.default_dict['figure_height']      , width=self.canvas_width, height=self.canvas_height, width=800, height=700
        self.canvas_area.grid(column=1, row=0, sticky='nsew')
        
        self.fig = plt.figure()
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.toolbar = NavigationToolbar2Tk(self.canvas_fig, self.root, pack_toolbar=False)
        self.toolbar.update()
        # toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.toolbar.grid(column=1, row=1, columnspan=1)
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def _windowsize_changed(self, event):
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, f'{self.canvas_area.winfo_height()}')
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, f'{self.canvas_area.winfo_width()}')

        #update the canvas
        # self.canvas_frame.configure( width=self.canvas_area.winfo_width(), height=self.canvas_area.winfo_height())
        # update the size of the left menue scroll region
        self._update_scrollframes()

    def _update_scrollframes(self):
        # update the size of the left menue scroll region
        self.menu_left_scrollframe.changeCanvasHeight(self.root.winfo_height())
        # also for right menu
        self.menu_right_1_scrollframe.changeCanvasHeight(self.root.winfo_height())
        
    def _update_canvas_area(self):
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, f'{self.canvas_area.winfo_height()}')
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, f'{self.canvas_area.winfo_width()}')

    def _create_measurement(self):
        """Create the measurement instance depending on the chosen Measurement folder and plotting mode.
        Also handle which buttons are enabled or disabled depending on plotting mode.
        """
        if self.folder_path == None:
            print('No measurement found!')
        elif self.plotting_mode is MeasurementTypes.APPROACHCURVE:
            channels = self._get_channels()
            self.measurement = ApproachCurve(self.folder_path, channels=channels)

            self.generate_plot_button.config(state=ON)
            self.button_save_to_gsftxt.config(state=DISABLED)
            self.menu_right_2_height_leveling.config(state=DISABLED)
            self.menu_right_2_phase_drift_comp.config(state=DISABLED)
            self.menu_right_2_overlay.config(state=DISABLED)
            self.menu_right_2_gaussblurr.config(state=DISABLED)
            self.menu_right_2_synccorrection.config(state=DISABLED)
            self.menu_left_clear_plots_button.config(state=ON)
            self.menu_right_2_shift_phase.config(state=DISABLED)
            self.menu_right_2_create_realpart.config(state=DISABLED)
            self.menu_right_2_height_masking.config(state=DISABLED)
            self.menu_right_2_rotation.config(state=DISABLED)
            self.menu_right_2_transform_log.config(state=DISABLED)
            self.menu_right_2_cut_data.config(state=DISABLED)
            self.save_plot_button.config(state=DISABLED)
            # todo, add approach curve handling to snom package to make it also possible to store multiple curves in memory
        elif self.plotting_mode is MeasurementTypes.SCAN3D:
            channels = self._get_channels()
            self.measurement = Scan3D(self.folder_path, channels=channels)
            

            self.generate_plot_button.config(state=ON)
            self.button_save_to_gsftxt.config(state=DISABLED)
            self.menu_right_2_height_leveling.config(state=DISABLED)
            self.menu_right_2_phase_drift_comp.config(state=DISABLED)
            self.menu_right_2_overlay.config(state=DISABLED)
            self.menu_right_2_gaussblurr.config(state=DISABLED)
            self.menu_right_2_synccorrection.config(state=DISABLED)
            self.menu_left_clear_plots_button.config(state=ON)
            self.menu_right_2_shift_phase.config(state=DISABLED)
            self.menu_right_2_create_realpart.config(state=DISABLED)
            self.menu_right_2_height_masking.config(state=DISABLED)
            self.menu_right_2_rotation.config(state=DISABLED)
            self.menu_right_2_transform_log.config(state=DISABLED)
            self.menu_right_2_cut_data.config(state=DISABLED)
            self.save_plot_button.config(state=DISABLED)
        elif self.plotting_mode is MeasurementTypes.SNOM or self.plotting_mode is MeasurementTypes.AFM:
            if self.checkbox_autoscale.get() == 1:
                autoscale = True
            else:
                autoscale = False
            channels = self._get_channels()
            self.measurement = SnomMeasurement(self.folder_path, channels=channels, autoscale=autoscale)

            self.generate_plot_button.config(state=ON)
            self.button_save_to_gsftxt.config(state=ON)
            self.menu_right_2_height_leveling.config(state=ON)
            self.menu_right_2_phase_drift_comp.config(state=ON)
            self.menu_right_2_overlay.config(state=ON)
            self.menu_right_2_gaussblurr.config(state=ON)
            self.menu_left_clear_plots_button.config(state=ON)
            self.menu_right_2_shift_phase.config(state=ON)
            self.menu_right_2_create_realpart.config(state=ON)
            self.menu_right_2_height_masking.config(state=ON)
            self.menu_right_2_rotation.config(state=ON)
            self.menu_right_2_transform_log.config(state=ON)
            self.menu_right_2_create_gif.config(state=ON)
            self.menu_right_2_cut_data.config(state=ON)

            self.save_plot_button.config(state=DISABLED)
            # self.update_plot_button.config(state=DISABLED)

            PlotDefinitions.autodelete_all_subplots = False # from now on keep all subplots in memory until they are manually deleted or the program is restarted.
        elif self.plotting_mode is MeasurementTypes.SPECTRUM:
            print("Spectra plotting mode is not yet implemented!")

    def _get_allowed_channels(self):
        """This function tries to find out which channels are allowed for the current measurement folder and plotting type.
        The allowed channels are used to autocorrect the user input in the channel text field. 
        Other channels are still accepted but cannot be autocorrected."""
        snom_analysis_config = ConfigParser()
        with open(snom_analysis_config_path, 'r') as f:
            snom_analysis_config.read_file(f)
        if self.file_type == None:
            file_type = 'FILETYPE1' # todo, the snom_analysis config does not account for this none filetype
        else:
            file_type = self.file_type
        phase_channels = self._get_from_config('phase_channels', file_type, snom_analysis_config)
        amp_channels = self._get_from_config('amp_channels', file_type, snom_analysis_config)
        real_channels = self._get_from_config('real_channels', file_type, snom_analysis_config)
        imag_channels = self._get_from_config('imag_channels', file_type, snom_analysis_config)
        height_channels = self._get_from_config('height_channels', file_type, snom_analysis_config)
        mechanical_channels = self._get_from_config('mechanical_channels', file_type, snom_analysis_config)
        # default_appendix = self._get_from_config('channel_suffix_default', file_type, snom_analysis_config)
        # all_channels_default = [channel + default_appendix for channel in phase_channels + amp_channels + real_channels + imag_channels + mechanical_channels]
        all_channels_default = phase_channels + amp_channels + real_channels + imag_channels + mechanical_channels
        all_channels_default += height_channels
        # also include variations with the various suffixes
        sync_appendix = self._get_from_config('channel_suffix_synccorrected_phase', file_type, snom_analysis_config)
        all_channels_synccorrected = [channel + sync_appendix for channel in phase_channels]
        manipulated_appendix = self._get_from_config('channel_suffix_manipulated', file_type, snom_analysis_config)
        all_channels_manipulated = [channel + manipulated_appendix for channel in phase_channels + amp_channels + real_channels + imag_channels + mechanical_channels]
        overlain_appendix = self._get_from_config('channel_suffix_overlain', file_type, snom_analysis_config)
        all_channels_overlain = [channel + overlain_appendix for channel in phase_channels + amp_channels + real_channels + imag_channels + mechanical_channels]
        self.allowed_channels = all_channels_default + all_channels_synccorrected + all_channels_manipulated + all_channels_overlain
        return self.allowed_channels

    def _correct_channel_from_input(self, text_field_width, channels:str) -> list:
        self._get_allowed_channels()
        if channels == '':
            return None
        else:
            text_field_handler = ChannelTextfield(text_field_width, self.allowed_channels)
            channels = text_field_handler.decode_input(channels) # convert string to list and auto ignore linebreaks
            channels = text_field_handler.correct_channels_input(channels) # try to fix simple user mistakes like wrong separation sybol or lowercase instead of upper...
            return channels

    def _get_channels(self, as_list:bool=True):
        """Read out the current channels in the entry/text field for the channels and return as list."""
        # self.channels = self.select_channels.get()
        self.channels = self.select_channels_text.get('1.0', 'end-1c')
        # does not work properly because width in px for font is unknown...
        select_channels_text_width = (self.select_channels_text.winfo_width() - 2*button_padx)*0.12
        # select_channels_text_width = 30 # this is the allowed width for text inside the text field
        # text_field_handler = ChannelTextfield(select_channels_text_width, self.allowed_channels)
        # self.channels = text_field_handler.decode_input(self.channels) # convert string to list and auto ignore linebreaks
        # self.channels = text_field_handler.correct_channels_input(self.channels) # try to fix simple user mistakes like wrong separation sybol or lowercase instead of upper...
        self.channels = self._correct_channel_from_input(select_channels_text_width, self.channels)
        # update the channels in the text field so autocorrect the user input
        self._set_channels(self.channels.split(','))
        # als long as the speciefied channel are in the allowed list
        if as_list:
            return self.channels.split(',')
        else:
            return self.channels
    
    def _set_channels(self, channels:list) -> None:
        """Set the specified channels as the new selection and write to input field."""
        '''
        # old version based on one line entry
        self.select_channels.delete(0,END)
        self.select_channels.insert(0, channels)
        '''
        # alternative with text widget:
        self.select_channels_text.delete('0.0', END)
        # does not work properly because width in px for font is unknown...
        select_channels_text_width = (self.select_channels_text.winfo_width() - 2*button_padx)*0.12
        # select_channels_text_width = 30 # this is the allowed width for text inside the text field
        encoded_text = ChannelTextfield(select_channels_text_width, self._get_allowed_channels()).encode_input(channels)
        text_height = encoded_text.count('\n')
        # change height of text widget
        self.select_channels_text.config(height=text_height+1)
        self.select_channels_text.insert(END, encoded_text, 'center')

    def _generate_plot(self):
        plt.close(self.fig)
        # if self.plotting_mode is MeasurementTypes.APPROACHCURVE:
        #     self.save_plot_button.config(state=ON)
        #     self.measurement.measurement_title = self.measurement_title.get()
        #     self._plot_approach_curve()
        if self.plotting_mode is MeasurementTypes.APPROACHCURVE:
            self.save_plot_button.config(state=ON)
            self.measurement.measurement_title = self.measurement_title.get()
            channels = self._get_channels()
            if self.checkbox_setmintozero_var.get() == 1:
                self.measurement.set_min_to_zero()
            # self.measurement.display_channels(channels) #show_plot=False
            self.measurement.display_channels_v2(channels) #show_plot=False
            # self._fill_canvas()
        elif self.plotting_mode is MeasurementTypes.SNOM or self.plotting_mode is MeasurementTypes.AFM:
            PlotDefinitions.vmin_amp = 1 #to make shure that the values will be initialized with the first plotting command
            PlotDefinitions.vmax_amp = -1
            PlotDefinitions.vmin_real = 0
            PlotDefinitions.vmax_real = 0
            PlotDefinitions.colorbar_width = float(self.colorbar_width.get())
            if self.checkbox_hide_ticks.get() == 1:
                PlotDefinitions.hide_ticks = True
            else:
                PlotDefinitions.hide_ticks = False
            if self.checkbox_show_titles.get() == 1:
                PlotDefinitions.show_titles = True
            else:
                PlotDefinitions.show_titles = False
            if self.checkbox_tight_layout.get() == 1:
                PlotDefinitions.tight_layout = True
            else:
                PlotDefinitions.tight_layout = False
            if self.checkbox_full_phase_range.get() == 1:
                PlotDefinitions.full_phase_range = True
            else:
                PlotDefinitions.full_phase_range = False
            if self.checkbox_shared_phase_range.get() == 1:
                PlotDefinitions.shared_phase_range = True
            else:
                PlotDefinitions.shared_phase_range = False
            if self.checkbox_amp_cbar_range.get() == 1:
                PlotDefinitions.amp_cbar_range = True
            else:
                PlotDefinitions.amp_cbar_range = False
            if self.checkbox_real_cbar_range.get() == 1:
                PlotDefinitions.real_cbar_range = True
            else:
                PlotDefinitions.real_cbar_range = False
            if self.checkbox_height_cbar_range.get() == 1:
                PlotDefinitions.height_cbar_range = True
            else:
                PlotDefinitions.height_cbar_range = False
            self.generate_all_plot_button.config(state=ON)
            self.save_plot_button.config(state=ON)
            self.update_plot_button.config(state=ON)

            # PlotDefinitions.hspace = float(self.h_space.get())

            if self.checkbox_setmintozero_var.get() == 1:
                self.measurement.set_min_to_zero()
            # try to load channel to add a scalebar to, if only one is present try to convert to list anyways
            # autocorrect the scalebar_channels
            # print('scalebar channels:', self.add_scalebar.get())
            scalebar_channels = self._correct_channel_from_input(100, self.add_scalebar.get())
            # print('corrected scalebar channels:', scalebar_channels)
            # try:
            #     scalebar_channels = self.add_scalebar.get().split(',')
            # except:
            #     scalebar_channels = [self.add_scalebar.get()]
            
            if scalebar_channels is not None:
                # update corrected channels in the text field
                self.add_scalebar.delete(0, END)
                self.add_scalebar.insert(0, str(scalebar_channels))
                self.measurement.scalebar(channels=scalebar_channels)
            PlotDefinitions.show_plot = False # make shure the functions inside the snom package dont show plots, the created plots are gathered in the Fill_Canvas function
            self.measurement.measurement_title = self.measurement_title.get()
            channels = self._get_channels()
            self.measurement.display_channels(channels) #show_plot=False
        elif self.plotting_mode is MeasurementTypes.APPROACHCURVE:
            if self.checkbox_setmintozero_var.get() == 1:
                self.measurement.set_min_to_zero()
            PlotDefinitions.show_plot = False # make shure the functions inside the snom package dont show plots, the created plots are gathered in the Fill_Canvas function
            self.measurement.measurement_title = self.measurement_title.get()
            channels = self._get_channels()
            self.measurement.display_channels(channels) #show_plot=False
        elif self.plotting_mode is MeasurementTypes.SCAN3D:
            if self.checkbox_setmintozero_var.get() == 1:
                self.measurement.set_min_to_zero()
            PlotDefinitions.show_plot = False # make shure the functions inside the snom package dont show plots, the created plots are gathered in the Fill_Canvas function
            self.measurement.measurement_title = self.measurement_title.get()
            channels = self._get_channels()
            # not fully implemented yet
            # for now just display the averaged values
            # Generate all cutplane data for the channels.
            self.measurement.generate_all_cutplane_data()
            # self.measurement.average_data() # only experimental
            self.measurement.set_min_to_zero()
            self.measurement.display_cutplanes(axis='x', line=0, channels=channels)
        else:
            print("Spectra plotting mode is not yet implemented!")
        self._fill_canvas()
        # enable buttons
        # self.button_save_to_gsftxt.config(state=ON)
        # self.button_update_plot.config(state=ON)
        # self.button_generate_all_plot.config(state=ON)
               
    def _update_plot(self): #todo, right now copy of generate_plot without creation of new measurement!
        # plt.close(self.fig)
        
        if self.plotting_mode is MeasurementTypes.APPROACHCURVE:
            self._generate_plot()
            '''
            self.save_plot_button.config(state=ON)
            self.measurement.measurement_title = self.measurement_title.get()
            channels = self._get_channels()
            self.measurement.display_channels(channels) #show_plot=False
            '''
            # self._fill_canvas()
        else:
            channels = self._get_channels()
            try: 
                self.measurement.remove_last_subplots(len(channels))
            except: print('could not remove the last subplots! (Update Plot)')
            self._generate_plot()

    def _fill_canvas(self):
        self.fig = plt.gcf()
        
        # works but memory increases with each call!
        try:
            self.canvas_fig.get_tk_widget().destroy() # does not work!
        except:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.toolbar = NavigationToolbar2Tk(self.canvas_fig, self.root, pack_toolbar=False)
            self.toolbar.update()
            # toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.toolbar.grid(column=1, row=1, columnspan=1)
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        else:
            self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
            self.toolbar.update()
            self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # adjust whitespace
        try:
            # get values from sliders if they already exist:
            hspace = round(float(self.slider_change_subplots_hspace.get())/10, 2)
            wspace = round(float(self.slider_change_subplots_wspace.get())/10, 2)
            right = round(float(self.slider_change_subplots_right.get())/20 + 0.5, 2)
            left = round(float(self.slider_change_subplots_left.get())/20, 2)
            top = round(float(self.slider_change_subplots_top.get())/20 + 0.5, 2)
            bottom = round(float(self.slider_change_subplots_bottom.get())/20, 2)
        except:
            # if they don't exist take the values from the user defaults
            hspace = self.default_dict['subplot_hspace']
            wspace = self.default_dict['subplot_wspace']
            right = self.default_dict['subplot_right']
            left = self.default_dict['subplot_left']
            top = self.default_dict['subplot_top']
            bottom = self.default_dict['subplot_bottom']
        else:
            # set values to dictionary
            self.default_dict['subplot_hspace'] = hspace
            self.default_dict['subplot_wspace'] = wspace
            self.default_dict['subplot_left'] = left
            self.default_dict['subplot_right'] = right
            self.default_dict['subplot_top'] = top
            self.default_dict['subplot_bottom'] = bottom
        self.fig.subplots_adjust(hspace=hspace, wspace=wspace, right=right, left=left, top=top, bottom=bottom)
        
        self.canvas_fig.draw()        
        self._change_mainwindow_size()
        # self.fig = None
        gc.collect()
        
    def _save_plot(self):
        allowed_filetypes = (("PNG file", "*.png"), ("PDF file", "*.pdf"), ("SVG file", "*.svg"), ("EPS file", "*.ps"))
        file = filedialog.asksaveasfile(mode='wb', defaultextension=".png", filetypes=allowed_filetypes) #(("PNG file", "*.png"),("All Files", "*.*") )
        extension = file.name.split('.')[-1]
        dpi = int(self.figure_dpi.get())
        self.fig.savefig(file, format=extension, dpi=dpi)

    def _generate_savefolder(self):
        """Generate a folder in the users home directory to save the the subplot information and gui settings. The same parent folder
        as for the snom analisis tool is used."""
        self.snom_plotter_config_folder = Path(os.path.expanduser('~')) / Path('SNOM_Config') / Path('SNOM_Plotter')
        self.config_path = self.snom_plotter_config_folder / Path('user_defaults.ini')
        if not Path.exists(self.snom_plotter_config_folder):
            os.makedirs(self.snom_plotter_config_folder)

    def _get_new_folderpath(self):
        new_measuement = False
        old_folder_path = self.folder_path
        self.folder_path = filedialog.askdirectory(initialdir=self.initialdir)
        # check if folder path is valid
        if self.folder_path == '':
            self.folder_path = old_folder_path
            return
        if old_folder_path != self.folder_path:
            new_measuement = True
        self.measurement = None
        # set new initail dir for the next filedialog
        self.initialdir = Path(self.folder_path).parent

        # check if filetype has changed
        old_file_type = self.file_type
        self._get_measurement_details() # loads various new measurement details also the filetype

        # save new old folder path and corresponding filetype to config file
        config = ConfigParser()
        with open(self.config_path, 'r') as file:
            config.read_file(file)
        config['OLDMEASUREMENT'] = {'folder_path': f'<{self.folder_path}>', 'file_type': f'<{self.file_type}>', 'plotting_mode': f'<{self.plotting_mode.value}>'}
        with open(self.config_path, 'w') as file:
            config.write(file)
        self.config = ConfigParser()
        with open(self.config_path, 'r') as file:
            self.config.read_file(file)

        # do stuff if the file has changed
        if new_measuement:
            # load the user defaults
            self._load_user_defaults()
            # get the allowed channels
            self._get_allowed_channels()
            # upadate the buttons
            self._initialize_buttons()
        
        # disable plot button since new measurement has to be loaded first
        self.generate_plot_button.config(state=DISABLED)

    def _initialize_buttons(self):
        if self.file_type != None:
            self._set_channels(self._get_default_channels())
            # enable all buttons
            # print('initializing buttons')
            # print('measurement_type:', self.plotting_mode)
            if self.measurement != None: # unnecessary should not happen this function is called before the measurement is created
                self.SnomMeasurement_button.config(state=ON)
                self.generate_plot_button.config(state=ON)
                # self.button_save_to_gsftxt.config(state=ON)
                self.menu_right_2_height_leveling.config(state=ON)
                self.menu_right_2_phase_drift_comp.config(state=ON)
                self.menu_right_2_overlay.config(state=ON)
                self.menu_right_2_gaussblurr.config(state=ON)
                # self.menu_left_clear_plots_button.config(state=ON)
                self.menu_right_2_shift_phase.config(state=ON)
                self.menu_right_2_synccorrection.config(state=ON)
                self.menu_right_2_create_realpart.config(state=ON)
                self.menu_right_2_height_masking.config(state=ON)
                self.menu_right_2_rotation.config(state=ON)
                self.menu_right_2_transform_log.config(state=ON)
                self.menu_right_2_create_gif.config(state=ON)
                # self.save_plot_button.config(state=ON)
                # self.update_plot_button.config(state=ON)
            if self.plotting_mode is MeasurementTypes.SNOM or self.plotting_mode is MeasurementTypes.AFM:
                self.SnomMeasurement_button.config(state=ON)
                self.generate_plot_button.config(state=DISABLED)
                # self.button_save_to_gsftxt.config(state=ON)
                self.menu_right_2_height_leveling.config(state=DISABLED)
                self.menu_right_2_phase_drift_comp.config(state=DISABLED)
                self.menu_right_2_overlay.config(state=DISABLED)
                self.menu_right_2_gaussblurr.config(state=DISABLED)
                # self.menu_left_clear_plots_button.config(state=ON)
                self.menu_right_2_shift_phase.config(state=DISABLED)
                self.menu_right_2_synccorrection.config(state=ON)
                self.menu_right_2_create_realpart.config(state=DISABLED)
                self.menu_right_2_height_masking.config(state=DISABLED)
                self.menu_right_2_rotation.config(state=DISABLED)
                self.menu_right_2_transform_log.config(state=DISABLED)
                self.menu_right_2_create_gif.config(state=DISABLED)
                self.menu_right_2_cut_data.config(state=DISABLED)
                self.save_plot_button.config(state=DISABLED)
                self.update_plot_button.config(state=DISABLED)
            elif self.plotting_mode is MeasurementTypes.APPROACHCURVE or self.plotting_mode is MeasurementTypes.SCAN3D:
                self.SnomMeasurement_button.config(state=ON)
                self.generate_plot_button.config(state=DISABLED)
                # self.button_save_to_gsftxt.config(state=ON)
                self.menu_right_2_height_leveling.config(state=DISABLED)
                self.menu_right_2_phase_drift_comp.config(state=DISABLED)
                self.menu_right_2_overlay.config(state=DISABLED)
                self.menu_right_2_gaussblurr.config(state=DISABLED)
                # self.menu_left_clear_plots_button.config(state=ON)
                self.menu_right_2_shift_phase.config(state=DISABLED)
                self.menu_right_2_synccorrection.config(state=DISABLED)
                self.menu_right_2_create_realpart.config(state=DISABLED)
                self.menu_right_2_height_masking.config(state=DISABLED)
                self.menu_right_2_rotation.config(state=DISABLED)
                self.menu_right_2_transform_log.config(state=DISABLED)
                self.menu_right_2_create_gif.config(state=DISABLED)
                self.menu_right_2_cut_data.config(state=DISABLED)
                self.save_plot_button.config(state=DISABLED)
                self.update_plot_button.config(state=DISABLED)
            else:
                self.SnomMeasurement_button.config(state=ON)
                self.generate_plot_button.config(state=DISABLED)
                # self.button_save_to_gsftxt.config(state=ON)
                self.menu_right_2_height_leveling.config(state=DISABLED)
                self.menu_right_2_phase_drift_comp.config(state=DISABLED)
                self.menu_right_2_overlay.config(state=DISABLED)
                self.menu_right_2_gaussblurr.config(state=DISABLED)
                # self.menu_left_clear_plots_button.config(state=ON)
                self.menu_right_2_shift_phase.config(state=DISABLED)
                self.menu_right_2_synccorrection.config(state=ON)
                self.menu_right_2_create_realpart.config(state=DISABLED)
                self.menu_right_2_height_masking.config(state=DISABLED)
                self.menu_right_2_rotation.config(state=DISABLED)
                self.menu_right_2_transform_log.config(state=DISABLED)
                self.menu_right_2_create_gif.config(state=DISABLED)
                self.save_plot_button.config(state=DISABLED)
                self.update_plot_button.config(state=DISABLED)
        elif self.file_type == None:
            # make shure to update the channel field
            self.select_channels_text.delete('0.0', END)
            self.select_channels_text.config(height=1)
            self.select_channels_text.insert(END, 'unknown', 'center')
            # disable all buttons
            self.SnomMeasurement_button.config(state=DISABLED)
            self.generate_plot_button.config(state=DISABLED)
            self.generate_all_plot_button.config(state=DISABLED)
            self.button_save_to_gsftxt.config(state=DISABLED)
            self.menu_right_2_height_leveling.config(state=DISABLED)
            self.menu_right_2_phase_drift_comp.config(state=DISABLED)
            self.menu_right_2_overlay.config(state=DISABLED)
            self.menu_right_2_gaussblurr.config(state=DISABLED)
            # self.menu_left_clear_plots_button.config(state=DISABLED)
            self.menu_right_2_shift_phase.config(state=DISABLED)
            self.menu_right_2_synccorrection.config(state=DISABLED)
            self.menu_right_2_create_realpart.config(state=DISABLED)
            self.menu_right_2_height_masking.config(state=DISABLED)
            self.menu_right_2_rotation.config(state=DISABLED)
            self.menu_right_2_transform_log.config(state=DISABLED)
            self.menu_right_2_create_gif.config(state=DISABLED)
            self.menu_right_2_cut_data.config(state=DISABLED)
            self.save_plot_button.config(state=DISABLED)
            self.update_plot_button.config(state=DISABLED)
            
    def _exit(self):
        self.root.quit()
        sys.exit()

    def _init_old_measurement(self):
        # try to get the old folder path from the config file
        self._get_old_folderpath()
        # get the measurement details
        self._get_measurement_details()
        # load the user defaults
        self._load_user_defaults()
        # get the allowed channels
        self._get_allowed_channels()
        

    def _get_old_folderpath(self) -> bool:
        folder_path = None
        file_type = None
        plotting_mode_val = None
        folder_path = self._get_from_config('folder_path', 'OLDMEASUREMENT')
        file_type = self._get_from_config('file_type', 'OLDMEASUREMENT')
        plotting_mode_val = self._get_from_config('plotting_mode', 'OLDMEASUREMENT')
        if folder_path != None and file_type != None and plotting_mode_val != None:
            self.folder_path = Path(folder_path)
            self.initialdir = self.folder_path.parent
            self.file_type = file_type
            self.plotting_mode = MeasurementTypes(int(plotting_mode_val))
            return True
        else:
            self.folder_path = None
            self.initialdir = this_files_path
            self.file_type = None
            self.plotting_mode = MeasurementTypes.NONE
            return False
        
    def _get_default_channels(self, plotting_mode=None) -> list:
        """Tries to find the default channels for the given file type by opening a measurement instance and returning the defaults saved there.
        If no file type is specified, the current file type will be used instead."""
        # default_channels = self.default_dict['default_channels']
        channels = ['-unknown-']
        if plotting_mode is None:
            plotting_mode = self.plotting_mode
        if self.folder_path != None:
            if plotting_mode == MeasurementTypes.APPROACHCURVE:
                channels = self.default_dict['channels_approach_curve']
                if channels is None:
                    Measurement = ApproachCurve(self.folder_path)
                    channels = Measurement.channels
                    # auto save the new defaults to config since the old ones were not yet implemented
                    self.config[self.file_type]['channels_approach_curve'] = str(channels)
            elif plotting_mode == MeasurementTypes.SCAN3D:
                channels = self.default_dict['channels_scan3d']
                if channels is None:
                    Measurement = Scan3D(self.folder_path)
                    channels = Measurement.channels
                    # auto save the new defaults to config since the old ones were not yet implemented
                    self.config[self.file_type]['channels_scan3d'] = str(channels)
            elif plotting_mode == MeasurementTypes.SNOM:
                channels = self.default_dict['channels_snom']
                # print('default channels: ', channels)
                if channels is None:
                    # print('loading default channels from measurement...')
                    Measurement = SnomMeasurement(self.folder_path)
                    channels = Measurement.channels
                    # auto save the new defaults to config since the old ones were not yet implemented
                    self.config[self.file_type]['channels_snom'] = str(channels)
            elif plotting_mode == MeasurementTypes.AFM:
                channels = self.default_dict['channels_afm']
                if channels is None:
                    Measurement = SnomMeasurement(self.folder_path)
                    channels = Measurement.height_channels
                    # auto save the new defaults to config since the old ones were not yet implemented
                    self.config[self.file_type]['channels_afm'] = str(channels)
            elif plotting_mode == MeasurementTypes.SPECTRUM:
                channels = self.default_dict['channels_spectrum']
                if channels is None:
                    print('Spectrum channels are not yet implemented!')
                    channels = ['-unknown-']            
        # save the config file
        with open(self.config_path, 'w') as file:
            self.config.write(file)
        return channels
    
    def _get_measurement_details(self):
        if self.folder_path != None:
            Measurement = FileHandler(self.folder_path)
            self.file_type = Measurement.file_type
            self.measurement_tag_dict = Measurement.measurement_tag_dict
        else:
            self.file_type = None
            self.measurement_tag_dict = None
        # print('file type:', self.file_type)
        # try to identify the measurement type to set the correct plotting mode
        self._get_measurement_type()

    def _get_measurement_type(self):
        """Try to identify the measurement type based on the measurement tags.
        This will automatically set the plotting mode."""
        if self.file_type != None:
            try:
                # not every filetype has a scan type
                scan_type = self.measurement_tag_dict[MeasurementTags.SCAN]
            except:
                # scan_type = None
                # self.plotting_mode = MeasurementTypes.NONE
                # todo, not all filetypes have a scan type, use additional ways to identify the measurement type
                # for now assume, that all files without a scan type are standard snom measurements
                plotting_mode = MeasurementTypes.SNOM
            else:
                if 'Approach Curve' in scan_type:
                    plotting_mode = MeasurementTypes.APPROACHCURVE
                elif '3D' in scan_type:
                    plotting_mode = MeasurementTypes.SCAN3D
                elif 'Spectrum' in scan_type: # todo, not implemented yet
                    plotting_mode = MeasurementTypes.SPECTRUM
                else:
                    plotting_mode = MeasurementTypes.SNOM
        else:
            plotting_mode = MeasurementTypes.NONE
        # print('plotting mode:', plotting_mode)
        # self._change_plotting_mode(plotting_mode.value)
        self._change_plotting_mode(plotting_mode)

    def _change_mainwindow_size(self):
        # change size of main window to adjust size of plot
        self.root.update()
        new_main_window_width = int(self.canvas_fig_width.get()) + int(self.menu_left.winfo_width()) + int(self.menu_right.winfo_width()) + 2*button_padx
        new_main_window_height = int(self.canvas_fig_height.get()) +42 #+ self.toolbar.winfo_height() # just for now
        # new_main_window_height = self.root.winfo_height()
        self.root.geometry(f'{new_main_window_width}x{new_main_window_height}')# todo, resize of y axis does not work?!

        # get the screen width and height of the display used
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - new_main_window_width/2)
        center_y = int(screen_height/2 - new_main_window_height/2)
        self.root.geometry(f"{new_main_window_width}x{new_main_window_height}+{center_x}+{center_y}")

    def _synccorrection_Preview(self):# delete?
        if self.synccorrection_wavelength.get() != '':
            wavelength = float(self.synccorrection_wavelength.get())
            channels = self._get_channels()
            measurement = SnomMeasurement(self.folder_path, channels=channels, autoscale=False)
            PlotDefinitions.show_plot = False
            # scanangle = measurement.measurement_tag_dict[MeasurementTags.rotation]*np.pi/180
            measurement._create_synccorr_preview(measurement.preview_phasechannel, wavelength, nouserinput=True)
            self._fill_canvas()
    
    def _synccorrection(self): # delete?
        # print('Synccorrection')
        # print(self.measurement.measurement_tag_dict[MeasurementTags.ROTATION])
        popup = SyncCorrectionPopup(self.root, self.folder_path, self._get_channels(), self.default_dict)

    def _gauss_blurr(self): #todo
        # make it such that channels which are in memory are used instead of loading
        popup = GaussBlurrPopup(self.root, self.measurement, self.folder_path, self._get_channels(as_list=False), self.default_dict)
        scaling = popup.scaling
        sigma = popup.sigma
        channels = popup.channels
        self.measurement.scale_channels(channels, scaling)
        self.measurement.gauss_filter_channels_complex(channels, sigma)

    def _generate_all_plot(self):
        plt.close(self.fig)
        # PlotDefinitions.show_plot = True
        self.measurement.display_all_subplots()
        self._fill_canvas()

    def _clear_all_plots(self):
        # self.measurement.all_subplots = [] # doesn't work because the variable is a class variable so this would only delete it for the specific instance
        # SnomMeasurement.all_subplots = []
        self.measurement._delete_all_subplots()

        self.generate_all_plot_button.config(state=DISABLED)

    def _save_user_defaults(self):
        """Save the user defaults to the config file for the currently active filetype."""
        # get the channels from the text field
        current_channels = self._get_channels()
        if self.plotting_mode is MeasurementTypes.APPROACHCURVE:
            self.default_dict['channels_approach_curve'] = current_channels
        elif self.plotting_mode is MeasurementTypes.SCAN3D:
            self.default_dict['channels_scan3d'] = current_channels
        elif self.plotting_mode is MeasurementTypes.SNOM:
            self.default_dict['channels_snom'] = current_channels
        elif self.plotting_mode is MeasurementTypes.AFM:
            self.default_dict['channels_afm'] = current_channels
        elif self.plotting_mode is MeasurementTypes.SPECTRUM:
            self.default_dict['channels_spectrum'] = current_channels
        
        
        default_dict = {
            'default_channels'  : self.default_dict['default_channels'],
            'channels_snom'     : self.default_dict['channels_snom'],
            'channels_afm'      : self.default_dict['channels_afm'],
            'channels_approach_curve'     : self.default_dict['channels_approach_curve'],
            'channels_scan3d'  : self.default_dict['channels_scan3d'],
            'channels_spectrum' : self.default_dict['channels_spectrum'],
            'dpi'               : self.figure_dpi.get(),
            'colorbar_width'    : self.colorbar_width.get(),
            'figure_width'      : self.canvas_fig_width.get(),
            'figure_height'     : self.canvas_fig_height.get(),
            'hide_ticks'        : self.checkbox_hide_ticks.get(),
            'show_titles'       : self.checkbox_show_titles.get(),
            'tight_layout'      : self.checkbox_tight_layout.get(),
            'subplot_hspace'    : round(float(self.slider_change_subplots_hspace.get())/10, 2),
            'subplot_wspace'    : round(float(self.slider_change_subplots_wspace.get())/10, 2),
            'subplot_right'     : round(float(self.slider_change_subplots_right.get())/20 + 0.5, 2),
            'subplot_left'      : round(float(self.slider_change_subplots_left.get())/20, 2),
            'subplot_top'       : round(float(self.slider_change_subplots_top.get())/20 + 0.5, 2),
            'subplot_bottom'    : round(float(self.slider_change_subplots_bottom.get())/20, 2),
            'scalebar_channel'  : self.add_scalebar.get(),
            'set_min_to_zero'   : self.checkbox_setmintozero_var.get(),
            'autoscale'         : self.checkbox_autoscale.get(),
            'full_phase'        : self.checkbox_full_phase_range.get(),
            'shared_phase'      : self.checkbox_shared_phase_range.get(),
            'shared_amp'        : self.checkbox_amp_cbar_range.get(),
            'shared_real'       : self.checkbox_real_cbar_range.get(),
            'shared_height'     : self.checkbox_height_cbar_range.get(),
            'appendix'          : self.default_dict['appendix'], # gets only changed by the save data popup
            'synccorr_lambda'   : self.default_dict['synccorr_lambda'],
            'synccorr_phasedir' : self.default_dict['synccorr_phasedir'],
            'pixel_integration_width': self.default_dict['pixel_integration_width'],
            'height_threshold': self.default_dict['height_threshold'],
            'plotting_mode_id'     : self.plotting_mode.value
        }
        # iterate through all keys in the config file of the current filetype and update the values
        
        for key in default_dict:
            value = default_dict[key]
            if value == '':
                value = '<>'
            self.config[self.file_type][key] = str(value)
            # self.config[self.file_type][key] = default_dict[key]
        # save updated config
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def _load_user_defaults(self):
        """Load the user defaults from the config file."""
        # make shure to reload the config file in case it was changed
        self._load_user_defaults_config()
        self.default_dict = {}
        if self.file_type == None:
            file_type = 'FILETYPENONE'
        else:
            file_type = self.file_type
        # iterate through all keys in the config file of the current filetype, if no filetype is active use the first filetype
        for key in self.config[file_type]:
            self.default_dict[key] = self._get_from_config(key, file_type)

    def _load_user_defaults_config(self):
        """Load the user defaults from the config file."""
        # check if config file exists
        if not Path.exists(self.config_path):
            self._load_all_old_defaults_new()
        else:
            self.config = ConfigParser()
            with open(self.config_path, 'r') as f:
                self.config.read_file(f)
        
    def _restore_user_defaults(self):
        self._load_user_defaults()
        # reload gui
        self._update_gui_parameters()
    
    def _load_all_old_defaults_new(self):
        """Create a default config file with the default values. Only use at initial setup or to reset the config file."""
        # also load the snom analysis config to get the default channels
        # check if snom analysis config exists
        if not Path.exists(snom_analysis_config_path):
            # if not create a new one and ask the user to select a folder with a measurement to create the default config from
            folder_path = filedialog.askdirectory(initialdir=self.initialdir, title='Please select a folder with a measurement to create the default config file')
            # open the measurement, this will automatically create the config file
            measurement = FileHandler(folder_path)
        snom_analysis_config = ConfigParser()
        with open(snom_analysis_config_path, 'r') as f:
            snom_analysis_config.read_file(f)
        
        plotter_config = ConfigParser()
        # add also defaults for no filetype
        plotter_config['FILETYPENONE'] = {
            'default_channels'  : 'None',
            'channels_snom'     : 'None',
            'channels_afm'      : 'None',
            'channels_approach_curve'     : 'None',
            'channels_scan3d'  : 'None',
            'channels_spectrum' : 'None',
            'dpi'               : 300,
            'colorbar_width'    : 5,
            'figure_width'      : canvas_width,
            'figure_height'     : canvas_height,
            'hide_ticks'        : 1,
            'show_titles'       : 1,
            'tight_layout'      : 1,
            'subplot_hspace'    : 0.4,
            'subplot_wspace'    : 0.4,
            'subplot_right'     : 0.9,
            'subplot_left'      : 0.03,
            'subplot_top'       : 0.9,
            'subplot_bottom'    : 0.07,
            'scalebar_channel'  : '<>',
            'set_min_to_zero'   : 1,
            'autoscale'         : 1,
            'full_phase'        : 0,
            'shared_phase'      : 0,
            'shared_amp'        : 0,
            'shared_real'       : 0,
            'shared_height'     : 0,
            'synccorr_lambda'   : '<>',
            'synccorr_phasedir' : '<>',
            'appendix'          : '<_manipulated>',
            'pixel_integration_width': 1,
            'height_threshold'  : 0.5,
            'plotting_mode_id'  : 1
        }
        plotter_config['FILETYPE1'] = {
            'default_channels'  : snom_analysis_config['FILETYPE1']['preview_channels'],
            'channels_snom'     : 'None',
            'channels_afm'      : 'None',
            'channels_approach_curve'     : 'None',
            'channels_scan3d'  : 'None',
            'channels_spectrum' : 'None',
            'dpi'               : 300,
            'colorbar_width'    : 5,
            'figure_width'      : canvas_width,
            'figure_height'     : canvas_height,
            'hide_ticks'        : 1,
            'show_titles'       : 1,
            'tight_layout'      : 1,
            'subplot_hspace'    : 0.4,
            'subplot_wspace'    : 0.4,
            'subplot_right'     : 0.9,
            'subplot_left'      : 0.03,
            'subplot_top'       : 0.9,
            'subplot_bottom'    : 0.07,
            'scalebar_channel'  : '<>',
            'set_min_to_zero'   : 1,
            'autoscale'         : 1,
            'full_phase'        : 0,
            'shared_phase'      : 0,
            'shared_amp'        : 0,
            'shared_real'       : 0,
            'shared_height'     : 0,
            'synccorr_lambda'   : '<>',
            'synccorr_phasedir' : '<>',
            'appendix'          : '<_manipulated>',
            'pixel_integration_width': 1,
            'height_threshold'  : 0.5,
            'plotting_mode_id'  : 1
        }
        plotter_config['FILETYPE2'] = plotter_config['FILETYPE1']
        plotter_config['FILETYPE2']['default_channels'] = snom_analysis_config['FILETYPE2']['preview_channels']
        plotter_config['FILETYPE3'] = plotter_config['FILETYPE1']
        plotter_config['FILETYPE3']['default_channels'] = snom_analysis_config['FILETYPE3']['preview_channels']
        plotter_config['FILETYPE4'] = plotter_config['FILETYPE1']
        plotter_config['FILETYPE4']['default_channels'] = snom_analysis_config['FILETYPE4']['preview_channels']
        plotter_config['FILETYPE5'] = plotter_config['FILETYPE1']
        plotter_config['FILETYPE5']['default_channels'] = snom_analysis_config['FILETYPE5']['preview_channels']
        plotter_config['FILETYPE6'] = plotter_config['FILETYPE1']
        plotter_config['FILETYPE6']['default_channels'] = snom_analysis_config['FILETYPE6']['preview_channels']

        with open(self.config_path, 'w') as f:
            plotter_config.write(f)

        self.config = plotter_config

    def _load_old_defaults(self):
        """This function will only load the old defaults for the current filetype.
        """
        # load the snom analysis config to get the default channels
        snom_analysis_config = ConfigParser()
        with open(snom_analysis_config_path, 'r') as f:
            snom_analysis_config.read_file(f)
        # check if a valid filetype is selected by comparing to the section names in the config file
        if self.file_type not in snom_analysis_config.sections():
            print('No valid filetype selected, please select a valid filetype!')
            return 0

        # load user defaults if the file exists otherwise load all old defaults and recreate the user defaults file
        if not Path.exists(self.config_path):
            self._load_all_old_defaults_new()
            print('User defaults file not found, creating new one!')
            return 0
        
        self._load_user_defaults_config()

        # overwrite the section with the current filetype with the old defaults
        self.config[self.file_type] = {
            'default_channels'  : snom_analysis_config['FILETYPE1']['preview_channels'],
            'channels_snom'     : 'None',
            'channels_afm'      : 'None',
            'channels_approach_curve'     : 'None',
            'channels_scan3d'  : 'None',
            'channels_spectrum' : 'None',
            'dpi'               : 300,
            'colorbar_width'    : 5,
            'figure_width'      : canvas_width,
            'figure_height'     : canvas_height,
            'hide_ticks'        : 1,
            'show_titles'       : 1,
            'tight_layout'      : 1,
            'h_space'           : 0.4,
            'scalebar_channel'  : '<>',
            'set_min_to_zero'   : 1,
            'autoscale'         : 1,
            'full_phase'        : 0,
            'shared_phase'      : 0,
            'shared_amp'        : 0,
            'shared_real'       : 0,
            'shared_height'     : 0,
            'synccorr_lambda'   : '<>',
            'synccorr_phasedir' : '<>',
            'appendix'          : '<_manipulated>',
            'pixel_integration_width': 1,
            'height_threshold'  : 0.5,
            'plotting_mode_id'  : 1
        }
        # save the updated config file
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
    def _get_from_config(self, option:str=None, section:str=None, config_file=None):
        """This function gets the value of an option in a section of the config file.
        If no option is specified the whole section is returned."""
        if config_file is None:
            config_file = self.config
        if section is None:
            # set the section to the file type if it is not specified, but only if file_type is defined
            try: section = self.file_type
            except: print('Filetype unknown, please specify the section! (In _get_from_config)')
        if option is None:
            return dict(config_file[section])
        else:
            try:
                value = config_file[section][option]
                # replace < and > with empty string if value is a string
                if isinstance(value, str):
                    if value[0] == '<':
                        value = value.replace('<', '').replace('>', '')
                    # convert string to list if it is a list
                    # elif value[0] == '[':
                    #     value = ast.literal_eval(value)
                    # # convert string to dictionary if it is a dictionary
                    # elif value[0] == '{':
                    #     value = ast.literal_eval(value)
                    # replace string with boolean if it is a boolean
                    if value == 'True':
                        value = True
                    elif value == 'False':
                        value = False
                    elif value == 'None':
                        value = None
                    else:
                        # try to convert string to float or int or list or dict
                        try:
                            value = ast.literal_eval(value)
                        except:
                            pass
                return value
            except:
                return None
    
    def _restore_old_defaults(self):
        self._load_old_defaults()
        self._update_gui_parameters()
        
    def _update_gui_parameters(self):
        self._set_channels(self._get_default_channels())
        # self.select_channels.delete(0, END)
        # self.select_channels.insert(0, ','.join(self._get_default_channels())),
        self.figure_dpi.delete(0, END)
        self.figure_dpi.insert(0, self.default_dict['dpi']),
        self.colorbar_width.delete(0, END)
        self.colorbar_width.insert(0, self.default_dict['colorbar_width']),
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, self.default_dict['figure_width']),
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, self.default_dict['figure_height']),
        # change mainwindow size to adjust for new canvas size:
        self._change_mainwindow_size()

        self.checkbox_hide_ticks.set(self.default_dict['hide_ticks']),
        self.checkbox_show_titles.set(self.default_dict['show_titles']),
        self.checkbox_tight_layout.set(self.default_dict['tight_layout']),
        self.h_space.delete(0, END)
        self.h_space.insert(0, self.default_dict['h_space'])
        self.add_scalebar.delete(0, END)
        self.add_scalebar.insert(0, self.default_dict['scalebar_channel']),
        self.checkbox_setmintozero_var.set(self.default_dict['set_min_to_zero']),
        self.checkbox_autoscale.set(self.default_dict['autoscale']),
        # self.checkbox_gaussian_blurr.set(self.default_dict['gaussian_blurr']),
        self.checkbox_full_phase_range.set(self.default_dict['full_phase']),
        self.checkbox_shared_phase_range.set(self.default_dict['shared_phase']),
        self.checkbox_amp_cbar_range.set(self.default_dict['shared_amp']),
        self.checkbox_real_cbar_range.set(self.default_dict['shared_real']),
        self.checkbox_height_cbar_range.set(self.default_dict['shared_height']),
        # self.synccorrection_wavelength.delete(0, END)
        # self.synccorrection_wavelength.insert(0, self.default_dict['synccorr_lambda']),
        # self.synccorrection_phasedir.delete(0, END)
        # self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])

    def _change_savefiletype(self, event):#remove? todo
        self.savefiletype = self.current_savefiletype.get()
        if self.savefiletype == 'gsf':
            pass
            # self.cb_colormap.current(self.cb_colormap['values'].index('viridis'))
            # Plotting_Variables._colormap_name_default = self.current_cmap.get()
        elif self.savefiletype == 'txt':
            pass
            # self.cb_colormap.current(self.cb_colormap['values'].index('hsv'))
            # Plotting_Variables._colormap_name_chronological = self.current_cmap.get()

    def _on_tab_changed(self, event):
        event.widget.update_idletasks()

        tab = event.widget.nametowidget(event.widget.select())
        # event.widget.configure(height=tab.winfo_reqheight())
        event.widget.configure(width=tab.winfo_reqwidth())

    def _update_entry_values(self):#remove? todo
        # save to gsf channels:
        self._update_entry_value(self.select_channels_tosave, self._get_channels(as_list=False))
       
    def _update_entry_value(self, field, value):
        field.delete(0, END)
        field.insert(0, value)

    def _save_to_gsf_or_txt(self):
        popup = SavedataPopup(self.root, self._get_channels(as_list=False), self.default_dict['appendix'])
        filetype = popup.filetype
        channels = popup.channels.split(',')
        appendix = popup.appendix
        self.default_dict['appendix'] = appendix
        if filetype == 'gsf':
            self.measurement.Save_to_gsf(channels=channels, appendix=appendix)
        elif filetype == 'txt':
            self.measurement.Save_to_txt(channels=channels, appendix=appendix)
        else:
            print('Wrong filetype selcted! Files cannot be saved!')

    def _3_point_height_leveling(self):
        height_channel = None
        for channel in self._get_channels():
            if self.measurement.height_indicator in channel:
                height_channel = channel
        if height_channel is None:
            print('None of the selected channels was identified as a height channel! \nThe height leveling only works for height channels!')
            return 1
        popup = HeightLevellingPopup(self.root, self.measurement, height_channel, self.default_dict)

        self.measurement.all_data[self.measurement.channels.index(height_channel)] = popup.leveled_height_data
        self.measurement.channels_label[self.measurement.channels.index(height_channel)] += '_leveled'
        
    def _phase_drift_compensation(self):
        phase_channels = []
        for channel in self._get_channels():
            if self.measurement.phase_indicator in channel:
                phase_channels.append(channel)
        if phase_channels == []:
            print('None of the selected channels was identified as a phase channel! \nThe phase leveling only works for phase channels!')
            return 1
        preview_phasechannel = self.measurement.preview_phasechannel
        popup = PhaseDriftCompensation(self.root, self.measurement, preview_phasechannel, True, self.default_dict)

        for channel in phase_channels: # use the phase slope to correct all channels in memory
            leveled_phase_data = self.measurement._level_phase_slope(self.measurement.all_data[self.measurement.channels.index(channel)], popup.phase_slope)
            self.measurement.all_data[self.measurement.channels.index(channel)] = leveled_phase_data
            self.measurement.channels_label[self.measurement.channels.index(channel)] += '_leveled'
        
        self.measurement._write_to_logfile('phase_driftcomp_slope', popup.phase_slope)

    def _overlay_channels(self):
        forward_height_channel = self.measurement.height_channels[0]
        backward_height_channel = self.measurement.height_channels[1]
        popup = OverlayChannels(self.root, forward_height_channel, backward_height_channel, self.measurement)
        forward_channel = popup.forward_channel
        backward_channel = popup.backward_channel
        overlay_channels = popup.overlay_channels
        self._set_channels(self.measurement.channels)
        print('channels have been overlaid')

    def _change_phase_offset(self):
        # find appropriate phase channel for preview
        phase_channel = None
        for channel in self._get_channels():
            if self.measurement.phase_indicator in channel:
                phase_channel = channel # just take the first one
                break

        popup = PhaseOffsetPopup(self.root, self.measurement, phase_channel, True)
        phase_offset = popup.phase_offset
        
        # alternative using package based functionality with popup:
        # works also but does not follow the current structure and style
        # delete current plot
        # plt.close(self.fig)
        # from lib.function_popup import PhaseOffsetPopup_using_package_library
        # popup = PhaseOffsetPopup_using_package_library(self.root, self.measurement, phase_channel)
        # phase_offset = popup.phase_offset


        phase_channels = []
        for channel in self._get_channels():
            if self.measurement.phase_indicator in channel:
                phase_channels.append(channel)
        self.measurement._write_to_logfile('phase_shift', phase_offset)
        for channel in phase_channels:
            data = self.measurement.all_data[self.measurement.channels.index(channel)]
            # print min and max values of the phase data
            # print('min phase value: ', np.min(data))
            # print('max phase value: ', np.max(data))
            shifted_data = self.measurement._shift_phase_data(data, phase_offset)
            self.measurement.all_data[self.measurement.channels.index(channel)] = shifted_data
            # print min and max values of the phase data
            # print('min phase value: ', np.min(shifted_data))
            # print('max phase value: ', np.max(shifted_data))

    def _create_realpart(self):
        # pass
        amp_channel = None
        phase_channel = None
        for channel in self._get_channels():
            if self.measurement.amp_indicator in channel :
                amp_channel = channel
            elif self.measurement.phase_indicator in channel:
                phase_channel = channel
        if amp_channel is None or phase_channel is None:
            amp_channel = self.measurement.preview_ampchannel
            phase_channel = self.measurement.preview_phasechannel

        popup = CreateRealpartPopup(self.root, amp_channel, phase_channel)
        amp_channel = popup.amp_channel
        phase_channel = popup.phase_channel
        complex_type = popup.complex_type
        self.measurement.manually_create_complex_channel(amp_channel, phase_channel, complex_type)
        # the names of the newly created channels are added to the channels text field but not automatically loaded
        self._set_channels(self.measurement.channels)

    def _height_masking(self):
        popup = HeightMaskingPopup(self.root, self._get_channels(as_list=False), self.measurement, self.default_dict)

    def _rotation(self):
        popup = RotationPopup(self.root, self._get_channels(as_list=False), self.measurement, self.default_dict)

    def _transform_log(self):
        popup = LogarithmPopup(self.root, self._get_channels(as_list=False), self.measurement, self.default_dict)

    def _create_gif(self):
        """This function creates a popup and lets the user create a gif of channels in the current measurement.
        The main use is to display realpart data, therefore idealy an amplitude and phase channel should be selected.
        The do however not have to be of same demodulation order.
        """
        popup = GifCreationPopup(self.root, self.measurement)
        gif_path = popup.gif_path
        fps = popup.fps
        self._display_gif(gif_path, fps)
        
    def _display_gif(self, gif_path, fps:int=10):
        """This function displays a gif in the canvas.

        Args:
            gif_path (Path): Path to the gif file.
            fps (int, optional): The fps to display the gif in. Defaults to 10.
        """
        # delete the previous plot
        plt.close(self.fig)
        # Load the gif
        frames = imageio.mimread(gif_path)

        # Create a figure and axis
        fig, ax = plt.subplots()

        # Create a function to update the frame
        def update_image(frame):
            ax.clear()
            ax.imshow(frames[frame])
            # dont show frame around the image
            ax.axis('off')

        # Hide the axes
        ax.axis('off')

        # Create the animation
        ani = FuncAnimation(fig, update_image, frames=len(frames), interval=1000/fps, repeat=True)

        # display the gif in the canvas
        self._fill_canvas()

    def _cut_data_manual(self):
        # delete current plot
        plt.close(self.fig)
        popup = CutDataPopup_using_package_library(self.root, self.measurement)
        self.measurement = popup.measurement

    def _change_plotting_mode(self, new_plotting_mode:MeasurementTypes):
        # old_button_id = self.plotting_mode.value
        old_plotting_mode = self.plotting_mode
        self.plotting_mode = new_plotting_mode
        # change button colors according to current plotting mode and previous plotting mode
        # however, if the buttons are not yet created just change the plotting mode
        try:
            if new_plotting_mode != old_plotting_mode:
                if old_plotting_mode != None:
                    # turn off old button
                    self._change_plotting_mode_button_color(old_plotting_mode, 0)
                # set new plotting mode
                # change new button color
                self._change_plotting_mode_button_color(new_plotting_mode, 1)
                # do stuff after plotting mode was changed
                self._set_channels(self._get_default_channels())
        except:
            pass

    def _change_plotting_mode_button_color(self, new_plotting_mode:MeasurementTypes, button_state):
        SNOM = auto()
#     AFM = auto() # not used yet but could be implemented to simplify the gui for afm users like a mode switch
#     APPROACHCURVE = auto()
#     APPROACH3D = auto()
#     SPECTRUM = auto()
#     NONE = a
        if new_plotting_mode == MeasurementTypes.SNOM:
            if button_state == 0:
                self.plotting_mode_switch_1.config(bootstyle=DANGER)
            elif button_state == 1:
                self.plotting_mode_switch_1.config(bootstyle=SUCCESS)
        elif new_plotting_mode == MeasurementTypes.AFM:
            if button_state == 0:
                self.plotting_mode_switch_2.config(bootstyle=DANGER)
            elif button_state == 1:
                self.plotting_mode_switch_2.config(bootstyle=SUCCESS)
        elif new_plotting_mode == MeasurementTypes.APPROACHCURVE:
            if button_state == 0:
                self.plotting_mode_switch_3.config(bootstyle=DANGER)
            elif button_state == 1:
                self.plotting_mode_switch_3.config(bootstyle=SUCCESS)
        elif new_plotting_mode == MeasurementTypes.SCAN3D:
            if button_state == 0:
                self.plotting_mode_switch_4.config(bootstyle=DANGER)
            elif button_state == 1:
                self.plotting_mode_switch_4.config(bootstyle=SUCCESS)
        elif new_plotting_mode == MeasurementTypes.SPECTRUM:
            if button_state == 0:
                self.plotting_mode_switch_5.config(bootstyle=DANGER)
            elif button_state == 1:
                self.plotting_mode_switch_5.config(bootstyle=SUCCESS)
        else:
            print('Error occured in change button color for plotting mode selection!')

    def _update_canvas(self, event):
        self._fill_canvas()

        
    

def main():
    MainGui()

if __name__ == '__main__':
    main()


