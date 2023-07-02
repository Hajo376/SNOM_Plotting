
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_parameters import *
# from matplotlib import pyplot as plt

# import matplotlib
# matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from random import randint
import os
import pathlib
this_files_path = pathlib.Path(__file__).parent.absolute()

# from SNOM_AFM_analysis.python_classes_snom import *
from SNOM_AFM_analysis.python_classes_snom import Open_Measurement, Plot_Definitions
# import numpy as np
# import scipy

class Example():
    def __init__(self):
        # self.root = tk.Tk()
        self.root = ttkb.Window(themename='darkly') # 'journal', 'darkly', 'superhero', 'solar', 'litera' (default) 
        self.root.title("SNOM Plotter")
        # self.root.attributes('-fullscreen', True)# add exit button first

        self._Main_App()

        

    def _Main_App(self):
        self._Left_Menu()
        self._Canvas_Area()
        
        # configure canvas to scale with window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # start mainloop
        self.root.mainloop()

    def _Left_Menu(self):
        self.menu_left = ttkb.Frame(self.root, width=200)
        self.menu_left.grid(column=0, row=0)
        self.menu_left_upper = ttkb.LabelFrame(self.menu_left, text='Main controls')
        self.menu_left_upper.grid(column=0, row=0)

        # top level controls for plot
        self.load_data = ttkb.Button(self.menu_left_upper, text="Load Data", bootstyle=PRIMARY, command=lambda:self._Get_Folderpath_from_Input())
        self.load_data.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')
        # self.select_channels = ttkb.Button(self.menu_left_upper, text="Select Channels", bootstyle=SECONDARY)
        # self.select_channels.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        self.select_channels_frame = ttkb.Frame(self.menu_left_upper)
        self.select_channels_frame.grid(column=0, row=1)
        # self.select_channels_label = ttkb.Label(self.select_channels_frame, text='')

        self.label_select_channels = ttkb.Label(self.select_channels_frame, text='Select Channels:')
        self.label_select_channels.grid(column=0, row=0)
        self.select_channels = ttkb.Entry(self.select_channels_frame)
        self.select_channels.insert(0, 'O2A,O2P,Z C')
        self.select_channels.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='ew')


        self.generate_plot_button = ttkb.Button(self.menu_left_upper, text="Generate Plot", bootstyle=INFO, command=lambda:self._Generate_Plot())
        self.generate_plot_button.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.save_plot_button = ttkb.Button(self.menu_left_upper, text="Save Plot", bootstyle=SUCCESS, command=lambda:self._Save_Plot())
        self.save_plot_button.grid(column=0, row=3, padx=button_padx, pady=button_pady, sticky='nsew')
        self.exit_button = ttkb.Button(self.menu_left_upper, text='Exit', command=self._Exit, bootstyle=DANGER)
        self.exit_button.grid(column=0, row=4, padx=button_padx, pady=button_pady, sticky='nsew')
        # 
        # plot channels
        # display all plots in memory
        # ...
        
        self.menu_left_separator = ttkb.Separator(self.menu_left, orient='horizontal')
        self.menu_left_separator.grid(column=0, row=1, sticky='ew', padx=button_padx, pady=20)

        # plot styles
        self.menu_left_lower = ttkb.LabelFrame(self.menu_left, text='Plot controls')
        self.menu_left_lower.grid(column=0, row=2)

        # change width of colorbar:
        self.label_colorbar_width = ttkb.Label(self.menu_left_lower, text='Colorbar width:')
        self.label_colorbar_width.grid(column=0, row=0)
        self.cb_width = ttkb.Entry(self.menu_left_lower)
        self.cb_width.insert(0, '5')
        self.cb_width.grid(column=0, row=3, padx=button_padx, pady=button_pady, sticky='ew')
        # set min to zero
        self.checkbox_setmintozero_var = ttkb.IntVar()
        self.checkbox_setmintozero_var.set(1)
        self.set_min_to_zero = ttkb.Checkbutton(self.menu_left_lower, text='Set min to zero', variable=self.checkbox_setmintozero_var, onvalue=1, offvalue=0)
        self.set_min_to_zero.grid(column=0, row=4, padx=button_padx, pady=button_pady, sticky='nsew')
        # autoscale
        self.checkbox_autoscale = ttkb.IntVar()
        self.checkbox_autoscale.set(1)
        self.autoscale = ttkb.Checkbutton(self.menu_left_lower, text='Autoscale data', variable=self.checkbox_autoscale, onvalue=1, offvalue=0)
        self.autoscale.grid(column=0, row=5, padx=button_padx, pady=button_pady, sticky='nsew')
        # hide_ticks = True
        self.checkbox_hide_ticks = ttkb.IntVar()
        self.checkbox_hide_ticks.set(1)
        self.hide_ticks = ttkb.Checkbutton(self.menu_left_lower, text='Hide ticks', variable=self.checkbox_hide_ticks, onvalue=1, offvalue=0)
        self.hide_ticks.grid(column=0, row=6, padx=button_padx, pady=button_pady, sticky='nsew')
        # show_titles = True
        self.checkbox_show_titles = ttkb.IntVar()
        self.checkbox_show_titles.set(1)
        self.show_titles = ttkb.Checkbutton(self.menu_left_lower, text='Show titles', variable=self.checkbox_show_titles, onvalue=1, offvalue=0)
        self.show_titles.grid(column=0, row=7, padx=button_padx, pady=button_pady, sticky='nsew')
        # tight_layout = True
        self.checkbox_tight_layout = ttkb.IntVar()
        self.checkbox_tight_layout.set(1)
        self.tight_layout = ttkb.Checkbutton(self.menu_left_lower, text='Tight layout', variable=self.checkbox_tight_layout, onvalue=1, offvalue=0)
        self.tight_layout.grid(column=0, row=8, padx=button_padx, pady=button_pady, sticky='nsew')
        # hspace = 0.4 #standard is 0.4
        self.label_h_space = ttkb.Label(self.menu_left_lower, text='Horizontal space:')
        self.label_h_space.grid(column=0, row=9)
        self.h_space = ttkb.Entry(self.menu_left_lower)
        self.h_space.insert(0, '0.4')
        self.h_space.grid(column=0, row=10, padx=button_padx, pady=button_pady, sticky='ew')
        # full_phase_range = True # this will overwrite the cbar
        self.checkbox_full_phase_range = ttkb.IntVar()
        self.checkbox_full_phase_range.set(1)
        self.full_phase_range = ttkb.Checkbutton(self.menu_left_lower, text='Full phase range', variable=self.checkbox_full_phase_range, onvalue=1, offvalue=0)
        self.full_phase_range.grid(column=0, row=11, padx=button_padx, pady=button_pady, sticky='nsew')
        # amp_cbar_range = True
        self.checkbox_amp_cbar_range = ttkb.IntVar()
        self.checkbox_amp_cbar_range.set(0)
        self.amp_cbar_range = ttkb.Checkbutton(self.menu_left_lower, text='Shared amp range', variable=self.checkbox_amp_cbar_range, onvalue=1, offvalue=0)
        self.amp_cbar_range.grid(column=0, row=12, padx=button_padx, pady=button_pady, sticky='nsew')
        # real_cbar_range = True
        self.checkbox_real_cbar_range = ttkb.IntVar()
        self.checkbox_real_cbar_range.set(0)
        self.real_cbar_range = ttkb.Checkbutton(self.menu_left_lower, text='Shared real range', variable=self.checkbox_real_cbar_range, onvalue=1, offvalue=0)
        self.real_cbar_range.grid(column=0, row=13, padx=button_padx, pady=button_pady, sticky='nsew')



        # apply gaussian filter
        self.checkbox_gaussian_blurr = ttkb.IntVar()
        self.checkbox_gaussian_blurr.set(0)
        self.gaussian_blurr = ttkb.Checkbutton(self.menu_left_lower, text='Blurr Data', variable=self.checkbox_gaussian_blurr, onvalue=1, offvalue=0)
        self.gaussian_blurr.grid(column=0, row=14, padx=button_padx, pady=button_pady, sticky='nsew')
        # add scalebar
        # self.checkbox_add_scalebar = ttkb.IntVar()
        # self.checkbox_add_scalebar.set(0)
        # self.add_scalebar = ttkb.Checkbutton(self.menu_left_lower, text='Add scalebar', variable=self.checkbox_add_scalebar, onvalue=1, offvalue=0)
        # self.add_scalebar.grid(column=0, row=15, padx=button_padx, pady=button_pady, sticky='nsew')
        self.label_add_scalebar = ttkb.Label(self.menu_left_lower, text='Scalebar channel:')
        self.label_add_scalebar.grid(column=0, row=15)
        self.add_scalebar = ttkb.Entry(self.menu_left_lower)
        self.add_scalebar.insert(0, '')
        self.add_scalebar.grid(column=0, row=16, padx=button_padx, pady=button_pady, sticky='ew')


        # plot title, colorbar width, colorbar, add scalebar, ...
        # height_cbar_range = True
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

    def _Canvas_Area(self):
        # canvas area
        self.canvas_area = ttkb.Frame(self.root, width=800, height=700) #, width=800, height=700
        self.canvas_area.grid(column=1, row=0, sticky='nsew')
        self.canvas = ttkb.Canvas(self.canvas_area, width=800, height=700, background="#ffffff") # , width=800, height=700, background="#ffffff"
        # self.canvas.pack()
        self.canvas.grid(column=0, row=0, sticky='nsew')


    def _Generate_Plot(self):
        Plot_Definitions.colorbar_width = float(self.cb_width.get())
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
                self.measurement.Scalebar(channels=scalebar_channel)
        self.measurement.Display_Channels(show_plot=False)
        self.fig = plt.gcf()

        # self.fig = Generate_Plot(self.folder_path).fig
        canvas = FigureCanvasTkAgg(self.fig, self.canvas_area)
        canvas.draw()
        # canvas.get_tk_widget().pack()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew") 
        # canvas.get_tk_widget().pack_forget()
        # canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=TRUE) 
    
    def _Save_Plot(self):
        file = filedialog.asksaveasfile(mode='wb', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
        self.fig.savefig(file)

    def _Get_Folderpath_from_Input(self):
        
        # check if old default path exists to use as initialdir
        try:
            with open(os.path.join(this_files_path, 'default_path.txt'), 'r') as file:
                content = file.read()
            if content[0:1] == '#':
                initialdir = content[1:] # to do change to one level higher
        except:
            initialdir = this_files_path
        self.folder_path = filedialog.askdirectory(initialdir=initialdir)
        # save filepath to txt and use as next initialdir
        with open(os.path.join(this_files_path, 'default_path.txt'), 'w') as file:
            file.write('#' + self.folder_path)

    def _Exit(self):
        self.menu_left.quit()

    # def _Set_Min_To_Zero(self):
    #     if self.checkbox_setmintozero_var == 1:
    #         self.set_min_to_zero.configure(state='enabled')
    #     else:
    #         self.set_min_to_zero.configure(state='disabled')

        # self.measurement.Set_Min_to_Zero()



class Generate_Plot():
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # self.create_figure()
        self.create_figure_test()
    
    def create_figure(self):
        self.fig = Figure()
        a = self.fig.add_subplot(111)
        x = [1,2,3,4,5,6,7,8,9,10,11,12]
        y = []
        # import random 
        
        # rng = np.random._default_rng()
        # rng.integers(2, size=10)
        for i in x:
            # rng = np.random.default_rng(12345)
            # print(rng)
            y.append(randint(0,1))
        a.plot(x,y)
    
    def create_figure_test(self):
        measurement = Open_Measurement(self.folder_path)
        measurement.Set_Min_to_Zero()
        measurement.Display_Channels(show_plot=False)
        self.fig = plt.gcf()
        
        





def main():
    Example()

if __name__ == '__main__':
    main()