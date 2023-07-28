
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import *
# from matplotlib import pyplot as plt

# import matplotlib
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
#import backends explicitly or they wont work in exe format
import matplotlib.backends.backend_pdf
import matplotlib.backends.backend_ps
import matplotlib.backends.backend_svg
# from random import randint
import sys
import os
import pathlib
this_files_path = pathlib.Path(__file__).parent.absolute()

# from SNOM_AFM_analysis.python_classes_snom import *
from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions, Tag_Type, File_Type
import numpy as np
# import scipy
#for scrollframe
import platform
from scrollframe import ScrollFrame
import pickle # for saving of defaults in a binary dictionary

class Example():
    def __init__(self):
        # self.root = tk.Tk()
        self.root = ttkb.Window(themename='darkly') # 'journal', 'darkly', 'superhero', 'solar', 'litera' (default) 
        self.root.minsize(width=main_window_minwidth, height=main_window_minheight)
        self.root.title("SNOM Plotter")
        self.root.geometry(f"{1100}x{570}")
        self.root.iconbitmap(os.path.join(this_files_path,'snom_plotting.ico'))
        # try:
        #     from ctypes import windll  # Only exists on Windows.

        #     myappid = "mycompany.myproduct.subproduct.version"
        #     windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        # except ImportError:
        #     pass
        # self.root.attributes('-fullscreen', True)# add exit button first
        self._Generate_Savefolder()
        self._Get_Old_Folderpath()
        self._Load_User_Defaults()
        # self._Load_Old_Defaults()
        # print(self.folder_path)
        self._Main_App()
        
    # def _Get_initial_Geometry(self):
    #     root_width = self.root.winfo_width()
    #     root_height = self.root.winfo_height()
    #     canvas_width = self.canvas_area.winfo_width()
    #     canvas_height = self.canvas_area.winfo_height()
    #     menu_width = root_width-canvas_width

    #     pass


    def _Windowsize_changed(self, event):
        # print('window width =', self.root.winfo_width())
        # print('window height =', self.root.winfo_height())
        # print('canvas width =', self.canvas_area.winfo_width())
        # print('canvas height =', self.canvas_area.winfo_height())
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, f'{self.canvas_area.winfo_height()}')
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, f'{self.canvas_area.winfo_width()}')

        # update the size of the left menue scroll region
        self.menu_left_scrollframe.changeCanvasHeight(self.root.winfo_height())
        # also for right menu
        self.menu_right_1_scrollframe.changeCanvasHeight(self.root.winfo_height())
        # self.menu_left_scrollframe.changeCanvasHeight(self.root.winfo_height())
        # print('changed the scroll region height')
        # self._Update_Canvas_Area()
        # frame.update_idletasks()
        # pass    

    def _Main_App(self):
        self._Left_Menu()
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self._Canvas_Area()
        self._Right_Menu()
        # new_main_window_width = canvas_width + self.menu_left.winfo_width() + self.menu_right.winfo_width()
        # self.root.geometry(f'{new_main_window_width}x{main_window_minheight}')
        # self.root.update()
        # self._Fill_Canvas()
        # self._Change_Mainwindow_Size()
        
        # configure canvas to scale with window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # start mainloop
        self.root.bind("<Configure>", self._Windowsize_changed)
        self.root.mainloop()

    def _Left_Menu(self):
        self.menu_left = ttkb.Frame(self.root, padding=5)
        self.menu_left.grid(column=0, row=0)

        # self.menu_left_scrollframe = ScrollFrame(self.menu_left, main_window_minheight-2*button_pady, 160) # make adaptable to fig height
        self.menu_left_scrollframe = ScrollFrame(self.menu_left, main_window_minheight-2*button_pady) #, 160 make adaptable to fig height
        # self.menu_left_scrollframe = ScrollFrame(self.menu_left, self.canvas_fig_height, 200)
        # self.menu_left_scrollframe.grid(column=0, row=0, sticky='ns')
        self.menu_left_scrollframe.pack(expand=True, fill='both')
        # self.menu_left_scrollframe.changeCanvasHeight(200)
        # print(self.root.winfo_height())
        self.menu_left_scrollframe.changeCanvasHeight(self.root.winfo_height()) # initialize to stretch to full height

        self.menu_left_upper = ttkb.LabelFrame(self.menu_left_scrollframe.viewPort, text='Main controls')
        self.menu_left_upper.grid(column=0, row=0, padx=button_padx, pady=button_pady)

        # top level controls for plot
        self.load_data = ttkb.Button(self.menu_left_upper, text="Load Data", bootstyle=PRIMARY, command=lambda:self._Get_Folderpath_from_Input())
        self.load_data.grid(column=0, row=0, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.select_channels = ttkb.Button(self.menu_left_upper, text="Select Channels", bootstyle=SECONDARY)
        # self.select_channels.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.select_channels_frame = ttkb.Frame(self.menu_left_upper)
        # self.select_channels_frame.grid(column=0, row=1)
        # self.select_channels_label = ttkb.Label(self.select_channels_frame, text='')

        self.label_select_channels = ttkb.Label(self.menu_left_upper, text='Select Channels:')
        self.label_select_channels.grid(column=0, row=1, columnspan=2, sticky='nsew')
        self.select_channels = ttkb.Entry(self.menu_left_upper, justify='center')
        default_channels = self._Get_Default_Channels()
        self._Set_Default_Channels(default_channels)
        
        # self.select_channels.insert(0, default_channels) # 'O2A,O2P,Z C'
        self.select_channels.grid(column=0, row=2, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')


        self.generate_plot_button = ttkb.Button(self.menu_left_upper, text="Generate Plot", bootstyle=INFO, command=lambda:self._Generate_Plot())
        self.generate_plot_button.grid(column=0, row=3, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # set dpi for save method
        self.label_figure_dpi = ttkb.Label(self.menu_left_upper, text='DPI:')
        self.label_figure_dpi.grid(column=0, row=4)
        self.figure_dpi = ttkb.Entry(self.menu_left_upper, width=input_width, justify='center')
        # self.figure_dpi.insert(0, '100')
        self.figure_dpi.insert(0, self.default_dict['dpi'])
        self.figure_dpi.grid(column=1, row=4, padx=button_padx, pady=button_pady, sticky='ew')
        self.save_plot_button = ttkb.Button(self.menu_left_upper, text="Save Plot", bootstyle=SUCCESS, command=lambda:self._Save_Plot())
        self.save_plot_button.grid(column=0, row=6, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.exit_button = ttkb.Button(self.menu_left_upper, text='Exit', command=self._Exit, bootstyle=DANGER)
        self.exit_button.grid(column=0, row=7, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # plot all plot in memory:
        self.generate_all_plot_button = ttkb.Button(self.menu_left_upper, text="Generate all Plots", bootstyle=PRIMARY, command=self._Generate_all_Plot)
        self.generate_all_plot_button.grid(column=0, row=8, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # save all defaults:
        self.save_defaults_button = ttkb.Button(self.menu_left_upper, text='Save User Defaults', bootstyle=SUCCESS, command=self._Save_User_Defaults)
        self.save_defaults_button.grid(column=0, row=9, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # load all defaults:
        self.load_defaults_button = ttkb.Button(self.menu_left_upper, text='Restore User Defaults', bootstyle=WARNING, command=self._Restore_User_Defaults)
        self.load_defaults_button.grid(column=0, row=10, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # restore all old defaults:
        self.restore_defaults_button = ttkb.Button(self.menu_left_upper, text='Restore Defaults', bootstyle=SUCCESS, command=self._Restore_Old_Defaults)
        self.restore_defaults_button.grid(column=0, row=11, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')

        # 
        # plot channels
        # display all plots in memory
        # ...
        
        self.menu_left_separator = ttkb.Separator(self.menu_left_scrollframe.viewPort, orient='horizontal')
        self.menu_left_separator.grid(column=0, row=1, columnspan=1, sticky='ew', padx=button_padx, pady=20)

        

        # self.menu_left_lower_scrollframe = ScrollFrame(self.menu_left, heigth=200, width=200)
        # self.menu_left_lower_scrollframe.grid(column=0, row=2)

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
        # self.canvas_fig_width_frame = ttkb.Frame(self.menu_left_lower)
        # self.canvas_fig_width_frame.grid(column=0, row=4)
        # self.label_canvas_fig_width = ttkb.Label(self.canvas_fig_width_frame, text='Figure width:')
        # self.label_canvas_fig_width.grid(column=0, row=0)
        # self.canvas_fig_width = ttkb.Entry(self.canvas_fig_width_frame, width=input_width)
        # self.canvas_fig_width.insert(0, '10')
        # self.canvas_fig_width.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')

        self.label_canvas_fig_width = ttkb.Label(self.menu_left_lower, text='Figure width:')
        self.label_canvas_fig_width.grid(column=0, row=1)
        self.canvas_fig_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.canvas_fig_width.insert(0, f'{canvas_width}')
        self.canvas_fig_width.insert(0, self.default_dict['figure_width'])
        self.canvas_fig_width.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')

        # change figure height:
        # self.canvas_fig_height_frame = ttkb.Frame(self.menu_left_lower)
        # self.canvas_fig_height_frame.grid(column=0, row=5)
        self.label_canvas_fig_height = ttkb.Label(self.menu_left_lower, text='Figure height:')
        self.label_canvas_fig_height.grid(column=0, row=2)
        self.canvas_fig_height = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        # self.canvas_fig_height.insert(0, f'{canvas_height}')
        self.canvas_fig_height.insert(0, self.default_dict['figure_height'])
        self.canvas_fig_height.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # hide_ticks = True
        self.checkbox_hide_ticks = ttkb.IntVar()
        # self.checkbox_hide_ticks.set(1)
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
        # self.checkbox_add_scalebar = ttkb.IntVar()
        # self.checkbox_add_scalebar.set(0)
        # self.add_scalebar = ttkb.Checkbutton(self.menu_right_upper, text='Add scalebar', variable=self.checkbox_add_scalebar, onvalue=1, offvalue=0)
        # self.add_scalebar.grid(column=0, row=15, padx=button_padx, pady=button_pady, sticky='nsew')
        self.label_add_scalebar = ttkb.Label(self.menu_left_lower, text='Scalebar channel:')
        self.label_add_scalebar.grid(column=0, row=7)
        self.add_scalebar = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.add_scalebar.insert(0, self.default_dict['scalebar_channel'])
        self.add_scalebar.grid(column=1, row=7, padx=button_padx, pady=button_pady, sticky='ew')
        
        # reconfigure size of left menu
        self.menu_left.update()
        print('left menu width: ', self.menu_left.winfo_width())
        print('left menu upper: ', self.menu_left_upper.winfo_width())
        print('left menu lower: ', self.menu_left_lower.winfo_width())
        # upper_menu_width = self.menu_left_upper.winfo_width()
        # lower_menu_width = self.menu_left_lower.winfo_width()
        # if upper_menu_width > lower_menu_width: width = upper_menu_width 
        width = max(self.menu_left_upper.winfo_width() + 3*button_padx, self.menu_left_lower.winfo_width() + 3*button_padx)
        self.menu_left_scrollframe.canvas.config(width=width)

        
        


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

    def _Right_Menu(self):
        self.menu_right = ttkb.Frame(self.root) #, width=200
        self.menu_right.grid(column=2, row=0, padx=button_padx, pady=button_pady)

        # organize multiple menues in notebooks -> tabs
        self.menu_right_notebook = ttkb.Notebook(self.menu_right)
        self.menu_right_notebook.pack()
        # self.menu_right_notebook.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='ew')

        self.menu_right_1_scrollframe = ScrollFrame(self.menu_right_notebook, main_window_minheight-2*button_pady) # , 170
        self.menu_right_1_scrollframe.pack()
        # self.menu_right_1_scrollframe.changeCanvasHeight(self.menu_right_1_scrollframe.viewPort.winfo_height())

        self.menu_right_1 = ttkb.Frame(self.menu_right_1_scrollframe.viewPort)
        # self.menu_right_1 = ttkb.Frame(self.menu_right_notebook)
        self.menu_right_1.grid(column=0, row=0)

        #add scrollframe:
        # self.menu_right_1_scrollframe = ScrollFrame(self.menu_left, main_window_minheight-2*button_pady, 160)
        # self.menu_right_1_scrollframe.grid(column=0, row=0)

        # self.menu_right_upper = ttkb.LabelFrame(self.menu_right, text='Manipulate Data', width=200)
        self.menu_right_upper = ttkb.LabelFrame(self.menu_right_1, text='Manipulate Data') # , width=200
        self.menu_right_upper.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.menu_right_upper.pack(fill=BOTH, expand=1)

        
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
        # apply gaussian filter
        self.checkbox_gaussian_blurr = ttkb.IntVar()
        self.checkbox_gaussian_blurr.set(self.default_dict['gaussian_blurr'])
        self.gaussian_blurr = ttkb.Checkbutton(self.menu_right_upper, text='Blurr Data', variable=self.checkbox_gaussian_blurr, onvalue=1, offvalue=0)
        self.gaussian_blurr.grid(column=0, row=3, padx=button_padx, pady=button_pady, sticky='nsew')
        # full_phase_range = True # this will overwrite the cbar
        self.checkbox_full_phase_range = ttkb.IntVar()
        self.checkbox_full_phase_range.set(self.default_dict['full_phase'])
        # self._Set_Phase_Range()
        
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
        

        # self.menu_right_separator = ttkb.Separator(self.menu_right, orient='horizontal')
        self.menu_right_separator = ttkb.Separator(self.menu_right_1, orient='horizontal')
        self.menu_right_separator.grid(column=0, row=1, sticky='ew', padx=button_padx, pady=20)
        # self.menu_right_separator.pack()

        # additional controls
        # self.menu_right_synccorrection = ttkb.LabelFrame(self.menu_right, text='Synccorrection', width=200)
        self.menu_right_synccorrection = ttkb.LabelFrame(self.menu_right_1, text='Synccorrection', width=200)
        self.menu_right_synccorrection.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.menu_right_synccorrection.pack(fill=BOTH, expand=1)
        # synccorrection
        self.label_synccorrection_wavelength = ttkb.Label(self.menu_right_synccorrection, text='Wavelength in µm:')
        self.label_synccorrection_wavelength.grid(column=0, row=0)
        self.synccorrection_wavelength = ttkb.Entry(self.menu_right_synccorrection, width=input_width, justify='center')
        self.synccorrection_wavelength.insert(0, self.default_dict['synccorr_lambda'])
        self.synccorrection_wavelength.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
        # first generate preview
        self.button_synccorrection_preview = ttkb.Button(self.menu_right_synccorrection, text='Generate preview', command=self._Synccorrection_Preview)
        self.button_synccorrection_preview.grid(column=0, row=1, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # then enter phasedir from preview
        self.label_synccorrection_phasedir = ttkb.Label(self.menu_right_synccorrection, text='Phasedir (n or p):')
        self.label_synccorrection_phasedir.grid(column=0, row=2)
        self.synccorrection_phasedir = ttkb.Entry(self.menu_right_synccorrection, width=input_width, justify='center')
        self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])
        self.synccorrection_phasedir.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # if phasedir and wavelength are known start synccorrection
        self.button_synccorrection = ttkb.Button(self.menu_right_synccorrection, text='Synccorrection', bootstyle=PRIMARY, command=self._Synccorrection)
        self.button_synccorrection.grid(column=0, row=3, columnspan=2, sticky='nsew', padx=button_padx, pady=button_pady)
        # self.menu_right_additional_controls_button = ttkb.Button(self.menu_right_additional_controls)
        # self.menu_right_additional_controls_button.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')

        # second tab:
        self.menu_right_2 = ttkb.Frame(self.menu_right_notebook)
        # self.menu_right_2.grid(column=0, row=1)
        self.menu_right_2.pack()

        self.menu_right_2_test = ttkb.Button(self.menu_right_2, text='test')
        self.menu_right_2_test.grid(column=0, row=0)

        self.menu_right_notebook.add(self.menu_right_1_scrollframe, text='Basic')
        self.menu_right_notebook.add(self.menu_right_2, text='Advanced')
        #reconfigure canvas size 
        self.menu_right_1.update()
        # print('width of right menu: ',self.menu_right_1.winfo_width())
        self.menu_right_1_scrollframe.canvas.config(width=self.menu_right_1.winfo_width())

    def _Canvas_Area(self):
        # canvas area
        self.canvas_area = ttkb.Frame(self.root) #, width=self.canvas_width, height=self.canvas_height, width=800, height=700
        self.canvas_area.grid(column=1, row=0, sticky='nsew')
        # self.canvas = ttkb.Canvas(self.canvas_area) # , width=800, height=700, background="#ffffff"
        # self.canvas.pack(fill=tk.BOTH, expand=1)
        # self.canvas.grid(column=0, row=0, sticky='nsew')#.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1) 
        # self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1) 

    def _Update_Canvas_Area(self):
        # self.canvas_area.update_idletasks()
        # self.canvas_area.configure(width=self.canvas_fig_width, height=self.canvas_fig_height)
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, f'{self.canvas_area.winfo_height()}')
        # self.canvas_fig_height.insert(str(self.canvas_area.winfo_height()))
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, f'{self.canvas_area.winfo_width()}')
        # pass

    def _Generate_Plot(self):
        
        Plot_Definitions.vmin_amp = 1 #to make shure that the values will be initialized with the first plotting command
        Plot_Definitions.vmax_amp = -1
        # Plot_Definitions.phase_cbar_range = True
        # Plot_Definitions.vmin_phase = 0
        # Plot_Definitions.vmax_phase = 0
        Plot_Definitions.vmin_real = 0
        Plot_Definitions.vmax_real = 0
        Plot_Definitions.colorbar_width = float(self.colorbar_width.get())
        if self.checkbox_hide_ticks.get() == 1:
            Plot_Definitions.hide_ticks = True
        else:
            Plot_Definitions.hide_ticks = False
        if self.checkbox_show_titles.get() == 1:
            Plot_Definitions.show_titles = True
        else:
            Plot_Definitions.show_titles = False
        if self.checkbox_tight_layout.get() == 1:
            Plot_Definitions.tight_layout = True
        else:
            Plot_Definitions.tight_layout = False
        if self.checkbox_full_phase_range.get() == 1:
            Plot_Definitions.full_phase_range = True
        else:
            Plot_Definitions.full_phase_range = False
        if self.checkbox_amp_cbar_range.get() == 1:
            Plot_Definitions.amp_cbar_range = True
        else:
            Plot_Definitions.amp_cbar_range = False
        if self.checkbox_real_cbar_range.get() == 1:
            Plot_Definitions.real_cbar_range = True
        else:
            Plot_Definitions.real_cbar_range = False
        if self.checkbox_height_cbar_range.get() == 1:
            Plot_Definitions.height_cbar_range = True
        else:
            Plot_Definitions.height_cbar_range = False

        
        Plot_Definitions.hspace = float(self.h_space.get())



        if self.checkbox_autoscale.get() == 1:
            autoscale = True
        else:
            autoscale = False
        channels = self.select_channels.get().split(',')
        self.measurement = Open_Measurement(self.folder_path, channels=channels, autoscale=autoscale)
        if self.checkbox_setmintozero_var.get() == 1:
            self.measurement.Set_Min_to_Zero()
        if self.checkbox_gaussian_blurr.get() == 1:
            self.measurement.Scale_Channels()
            self.measurement.Gauss_Filter_Channels_complex()
        # if self.checkbox_add_scalebar.get() == 1:
        #     self.measurement.Scalebar()
        try:
            scalebar_channel = self.add_scalebar.get().split(',')
        except:
            scalebar_channel = [self.add_scalebar.get()]
        if scalebar_channel != '':
            # if len(scalebar_channel) == 1:
            #     scalebar_channel = [scalebar_channel]
            # print(scalebar_channel)
            self.measurement.Scalebar(channels=scalebar_channel)
        # plt.clf()
        Plot_Definitions.show_plot = False
        self.measurement.Display_Channels() #show_plot=False
        self._Fill_Canvas()
        
        '''
        self.fig = plt.gcf()
        # change fig size and possibly dpi
        # self.fig.set_figheight(int(self.canvas_fig_height.get()))
        # self.fig.set_figwidth(int(self.canvas_fig_width.get()))
        # self.canvas_area.configure(width=int(self.canvas_fig_width.get()), height=int(self.canvas_fig_height.get()))
        

        # self.canvas_area.pack_propagate(0)
        # self.canvas_area.configure(width=int(self.canvas_fig_width.get())), 

        # self.canvas.delete("all")
        # self.fig = Generate_Plot(self.folder_path).fig
        # self.canvas.pack_forget()
        # self.canvas.pack()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        # self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        # self.canvas_fig.get_tk_widget().pack()
        # canvas_fig.get_tk_widget().grid(row=0, column=0, sticky="nsew") 
        # self.canvas_area.configure(width=400, height=200)
        # self.canvas_area.pack_propagate(0)

        # calculate plot area size:
        # plot_area_width = self.root.winfo_width()- self.menu_left.winfo_width() - self.menu_right.winfo_width()
        # print('plot area width: ', plot_area_width)
        self._Change_Mainwindow_Size()

        # self.canvas_area.update_idletasks()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 
        # self.canvas_fig.get_tk_widget().grid(column=0, row=0)
        '''


        
        # canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=TRUE) 
    
    def _Fill_Canvas(self):
        self.fig = plt.gcf()
        try:
            self.canvas_fig.get_tk_widget().destroy()
        except:
            pass
        self.canvas_fig = FigureCanvasTkAgg(self.fig, self.canvas_area)
        self.canvas_fig.draw()
        self._Change_Mainwindow_Size()
        self.canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=1) 

    def _Save_Plot(self):
        allowed_filetypes = (("PNG file", "*.png"), ("PDF file", "*.pdf"), ("SVG file", "*.svg"), ("EPS file", "*.ps"))
        file = filedialog.asksaveasfile(mode='wb', defaultextension=".png", filetypes=allowed_filetypes) #(("PNG file", "*.png"),("All Files", "*.*") )
        extension = file.name.split('.')[-1]
        dpi = int(self.figure_dpi.get())
        self.fig.savefig(file, format=extension, dpi=dpi)

    def _Generate_Savefolder(self):
        self.logging_folder = os.path.join(os.environ['APPDATA'], 'SNOM_Plotter')
        if not os.path.exists(self.logging_folder):
            os.makedirs(self.logging_folder)

    def _Get_Folderpath_from_Input(self):
        
        # check if old default path exists to use as initialdir
        self._Get_Old_Folderpath()
        self.folder_path = filedialog.askdirectory(initialdir=self.initialdir)
        # save filepath to txt and use as next initialdir
        # first check if folder_path is correct, user might abort filedialog
        if len(self.folder_path) > 5:
            with open(os.path.join(self.logging_folder, 'default_path.txt'), 'w') as file:
                file.write('#' + self.folder_path)
        # reinitialize the default channels
        # default_channels = self._Get_channels)
        # self._Set_Phase_Range()

    def _Exit(self):
        # self.menu_left.quit()
        self.root.quit()
        sys.exit()

    def _Get_Old_Folderpath(self):
        try:
            with open(os.path.join(self.logging_folder, 'default_path.txt'), 'r') as file:
                content = file.read()
            if content[0:1] == '#' and len(content) > 5:
                self.initialdir = content[1:] # to do change to one level higher
        except:
            self.initialdir = this_files_path
        else:
            try:
                #check if the program can read in the default channels otherwise the folder might not exist anymore
                self._Get_Default_Channels()
            except:
                self.initialdir = this_files_path
        #set old path to folder as default
        self.folder_path = self.initialdir

    def _Get_Default_Channels(self) -> list:
        if self.folder_path != this_files_path:
            Measurement = Open_Measurement(self.folder_path)
            default_channels = Measurement.channels
            return default_channels
        else:
            return ['O2A','O2P','Z C']

    def _Set_Default_Channels(self, default_channels):
        default_channels = ','.join(default_channels)
        self.select_channels.delete(0,END)
        self.select_channels.insert(0, default_channels)

    def _Set_Phase_Range(self):
        filetype = self._Get_Measurement_Filetype()
        if filetype is File_Type.aachen_ascii:
            self.checkbox_full_phase_range.set(0)  
        else: 
            self.checkbox_full_phase_range.set(1)

    def _Get_Measurement_Filetype(self) -> File_Type:
        if self.folder_path != this_files_path:
            Measurement = Open_Measurement(self.folder_path)
            filetype = Measurement.file_type
            return filetype
        else:
            return None

    def _Change_Mainwindow_Size(self):
        # change size of main window to adjust size of plot
        new_main_window_width = int(self.canvas_fig_width.get()) + int(self.menu_left.winfo_width()) + int(self.menu_right.winfo_width())
        new_main_window_height = self.canvas_fig_height.get()
        self.root.geometry(f'{new_main_window_width}x{new_main_window_height}')
        # print()
        # print('window width =', self.root.winfo_width())
        # print('window height =', self.root.winfo_height())
        # print('canvas width =', self.canvas_area.winfo_width())
        # print('canvas height =', self.canvas_area.winfo_height())
        # print('fig-widdth: ', self.canvas_fig_width.get())
        # self.root.update_idletasks()

    def _Synccorrection_Preview(self):
        if self.synccorrection_wavelength.get() != '':
            wavelength = float(self.synccorrection_wavelength.get())
            channels = self.select_channels.get().split(',')
            measurement = Open_Measurement(self.folder_path, channels=channels, autoscale=False)
            # measurement.show_plot = False
            Plot_Definitions.show_plot = False
            scanangle = measurement.measurement_tag_dict[Tag_Type.rotation]*np.pi/180
            measurement._Create_Synccorr_Preview(measurement.preview_phasechannel, wavelength, nouserinput=True)
            self._Fill_Canvas()
            # self.fig = plt.gcf()
            # plt.show()
    
    def _Synccorrection(self):
        if self.synccorrection_wavelength.get() != '' and self.synccorrection_phasedir != '':
            wavelength = float(self.synccorrection_wavelength.get())
            phasedir = str(self.synccorrection_phasedir.get())
            if phasedir == 'n':
                phasedir = -1
            elif phasedir == 'p':
                phasedir = 1
            else:
                print('Phasedir must be either \'n\' or \'p\'')
            # print('trying to do the synccorrection')
            # print('wavelength = ', wavelength)
            channels = self.select_channels.get().split(',')
            measurement = Open_Measurement(self.folder_path, channels=channels, autoscale=False)
            # measurement.show_plot = False
            # phasedir = measurement._Create_Synccorr_Preview(measurement.preview_phasechannel, wavelength)
            # self.fig = plt.gcf()
            # plt.show()
            measurement.Synccorrection(wavelength, phasedir)
            print('finished synccorrection')

    def _Generate_all_Plot(self):
        self.measurement.Display_All_Subplots()
        self._Fill_Canvas()

    def _Save_User_Defaults(self):
        default_dict = {
            'channels'          : self.select_channels.get(),
            'dpi'               : self.figure_dpi.get(),
            'colorbar_width'    : self.colorbar_width.get(),
            'figure_width'      : self.canvas_fig_width.get(),
            'figure_height'     : self.canvas_fig_height.get(),
            'hide_ticks'        : self.checkbox_hide_ticks.get(),
            'show_titles'       : self.checkbox_show_titles.get(),
            'tight_layout'      : self.checkbox_tight_layout.get(),
            'h_space'           : self.h_space.get(),
            'scalebar_channel'  : self.add_scalebar.get(),
            'set_min_to_zero'   : self.checkbox_setmintozero_var.get(),
            'autoscale'         : self.checkbox_autoscale.get(),
            'gaussian_blurr'    : self.checkbox_gaussian_blurr.get(),
            'full_phase'        : self.checkbox_full_phase_range.get(),
            'shared_amp'        : self.checkbox_amp_cbar_range.get(),
            'shared_real'       : self.checkbox_real_cbar_range.get(),
            'shared_height'     : self.checkbox_height_cbar_range.get(),
            'synccorr_lambda'   : self.synccorrection_wavelength.get(),
            'synccorr_phasedir' : self.synccorrection_phasedir.get()

        }
        with open(os.path.join(self.logging_folder, 'user_defaults.pkl'), 'wb') as f:
            pickle.dump(default_dict, f)

    def _Load_User_Defaults(self):
        try:
            with open(os.path.join(self.logging_folder, 'user_defaults.pkl'), 'rb') as f:
                self.default_dict = pickle.load(f)
        except:
            self._Load_Old_Defaults()
            print('Could not find user defaults, continouing with old defaults!')

    def _Restore_User_Defaults(self):
        self._Load_User_Defaults()
        # reload gui
        self._Update_Gui_Parameters()

    def _Load_Old_Defaults(self):
        self.default_dict = {
            'channels'          : 'O2A,O2P,Z C',
            'dpi'               : 100,
            'colorbar_width'    : 5,
            'figure_width'      : canvas_width,
            'figure_height'     : canvas_height,
            'hide_ticks'        : 1,
            'show_titles'       : 1,
            'tight_layout'      : 1,
            'h_space'           : '0.4',
            'scalebar_channel'  : '',
            'set_min_to_zero'   : 1,
            'autoscale'         : 1,
            'gaussian_blurr'    : 0,
            'full_phase'        : 0,
            'shared_amp'        : 0,
            'shared_real'       : 0,
            'shared_height'     : 0,
            'synccorr_lambda'   : '',
            'synccorr_phasedir' : ''

        }
    
    def _Restore_Old_Defaults(self):
        self._Load_Old_Defaults()
        self._Update_Gui_Parameters()
        
    def _Update_Gui_Parameters(self):
        self.select_channels.delete(0, END)
        self.select_channels.insert(0, self.default_dict['channels']),
        self.figure_dpi.delete(0, END)
        self.figure_dpi.insert(0, self.default_dict['dpi']),
        self.colorbar_width.delete(0, END)
        self.colorbar_width.insert(0, self.default_dict['colorbar_width']),
        self.canvas_fig_width.delete(0, END)
        self.canvas_fig_width.insert(0, self.default_dict['figure_width']),
        self.canvas_fig_height.delete(0, END)
        self.canvas_fig_height.insert(0, self.default_dict['figure_height']),
        # change mainwindow size to adjust for new canvas size:
        self._Change_Mainwindow_Size()

        self.checkbox_hide_ticks.set(self.default_dict['hide_ticks']),
        self.checkbox_show_titles.set(self.default_dict['show_titles']),
        self.checkbox_tight_layout.set(self.default_dict['tight_layout']),
        self.h_space.delete(0, END)
        self.h_space.insert(0, self.default_dict['h_space'])
        self.add_scalebar.delete(0, END)
        self.add_scalebar.insert(0, self.default_dict['scalebar_channel']),
        self.checkbox_setmintozero_var.set(self.default_dict['set_min_to_zero']),
        self.checkbox_autoscale.set(self.default_dict['autoscale']),
        self.checkbox_gaussian_blurr.set(self.default_dict['gaussian_blurr']),
        self.checkbox_full_phase_range.set(self.default_dict['full_phase']),
        self.checkbox_amp_cbar_range.set(self.default_dict['shared_amp']),
        self.checkbox_real_cbar_range.set(self.default_dict['shared_real']),
        self.checkbox_height_cbar_range.set(self.default_dict['shared_height']),
        self.synccorrection_wavelength.delete(0, END)
        self.synccorrection_wavelength.insert(0, self.default_dict['synccorr_lambda']),
        self.synccorrection_phasedir.delete(0, END)
        self.synccorrection_phasedir.insert(0, self.default_dict['synccorr_phasedir'])

# class Generate_Plot():
#     def __init__(self, folder_path):
#         self.folder_path = folder_path
#         self.create_figure_test()
    
#     def create_figure_test(self):
#         measurement = Open_Measurement(self.folder_path)
#         measurement.Set_Min_to_Zero()
#         measurement.Display_Channels(show_plot=False)
#         self.fig = plt.gcf()
        
        





def main():
    Example()

if __name__ == '__main__':
    main()