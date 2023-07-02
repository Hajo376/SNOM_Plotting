
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
        self.root.minsize(width=main_window_minwidth, height=main_window_minheight)
        self.root.title("SNOM Plotter")
        self.root.geometry(f"{1136}x{main_window_minheight}")
        # self.root.attributes('-fullscreen', True)# add exit button first
        self._Get_Old_Folderpath()
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
        # self._Change_Mainwindow_Size()
        
        # configure canvas to scale with window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # start mainloop
        self.root.bind("<Configure>", self._Windowsize_changed)
        self.root.mainloop()

    def _Left_Menu(self):
        self.menu_left = ttkb.Frame(self.root, width=200, padding=5)
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
        self.select_channels = ttkb.Entry(self.select_channels_frame, justify='center')
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
        self.cb_width = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.cb_width.insert(0, '5')
        self.cb_width.grid(column=1, row=0, padx=button_padx, pady=button_pady, sticky='ew')
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
        self.canvas_fig_width.insert(0, f'{canvas_width}')
        self.canvas_fig_width.grid(column=1, row=1, padx=button_padx, pady=button_pady, sticky='ew')

        # change figure height:
        # self.canvas_fig_height_frame = ttkb.Frame(self.menu_left_lower)
        # self.canvas_fig_height_frame.grid(column=0, row=5)
        self.label_canvas_fig_height = ttkb.Label(self.menu_left_lower, text='Figure height:')
        self.label_canvas_fig_height.grid(column=0, row=2)
        self.canvas_fig_height = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.canvas_fig_height.insert(0, f'{canvas_height}')
        self.canvas_fig_height.grid(column=1, row=2, padx=button_padx, pady=button_pady, sticky='ew')
        # hide_ticks = True
        self.checkbox_hide_ticks = ttkb.IntVar()
        self.checkbox_hide_ticks.set(1)
        self.hide_ticks = ttkb.Checkbutton(self.menu_left_lower, text='Hide ticks', variable=self.checkbox_hide_ticks, onvalue=1, offvalue=0)
        self.hide_ticks.grid(column=0, row=3, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # show_titles = True
        self.checkbox_show_titles = ttkb.IntVar()
        self.checkbox_show_titles.set(1)
        self.show_titles = ttkb.Checkbutton(self.menu_left_lower, text='Show titles', variable=self.checkbox_show_titles, onvalue=1, offvalue=0)
        self.show_titles.grid(column=0, row=4, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # tight_layout = True
        self.checkbox_tight_layout = ttkb.IntVar()
        self.checkbox_tight_layout.set(1)
        self.tight_layout = ttkb.Checkbutton(self.menu_left_lower, text='Tight layout', variable=self.checkbox_tight_layout, onvalue=1, offvalue=0)
        self.tight_layout.grid(column=0, row=5, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # hspace = 0.4 #standard is 0.4
        self.label_h_space = ttkb.Label(self.menu_left_lower, text='Horizontal space:')
        self.label_h_space.grid(column=0, row=6)
        self.h_space = ttkb.Entry(self.menu_left_lower, width=input_width, justify='center')
        self.h_space.insert(0, '0.4')
        self.h_space.grid(column=1, row=6, padx=button_padx, pady=button_pady, sticky='ew')
        # full_phase_range = True # this will overwrite the cbar
        self.checkbox_full_phase_range = ttkb.IntVar()
        self.checkbox_full_phase_range.set(1)
        self.full_phase_range = ttkb.Checkbutton(self.menu_left_lower, text='Full phase range', variable=self.checkbox_full_phase_range, onvalue=1, offvalue=0)
        self.full_phase_range.grid(column=0, row=7, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # amp_cbar_range = True
        self.checkbox_amp_cbar_range = ttkb.IntVar()
        self.checkbox_amp_cbar_range.set(0)
        self.amp_cbar_range = ttkb.Checkbutton(self.menu_left_lower, text='Shared amp range', variable=self.checkbox_amp_cbar_range, onvalue=1, offvalue=0)
        self.amp_cbar_range.grid(column=0, row=8, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # real_cbar_range = True
        self.checkbox_real_cbar_range = ttkb.IntVar()
        self.checkbox_real_cbar_range.set(0)
        self.real_cbar_range = ttkb.Checkbutton(self.menu_left_lower, text='Shared real range', variable=self.checkbox_real_cbar_range, onvalue=1, offvalue=0)
        self.real_cbar_range.grid(column=0, row=9, columnspan=2, padx=button_padx, pady=button_pady, sticky='nsew')



        
        


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

    def _Right_Menu(self):
        self.menu_right = ttkb.Frame(self.root, width=200)
        self.menu_right.grid(column=2, row=0)

        self.menu_right_upper = ttkb.LabelFrame(self.menu_right, text='Manipulate Data', width=200)
        self.menu_right_upper.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')

        
        # set min to zero
        self.checkbox_setmintozero_var = ttkb.IntVar()
        self.checkbox_setmintozero_var.set(1)
        self.set_min_to_zero = ttkb.Checkbutton(self.menu_right_upper, text='Set min to zero', variable=self.checkbox_setmintozero_var, onvalue=1, offvalue=0)
        self.set_min_to_zero.grid(column=0, row=1, padx=button_padx, pady=button_pady, sticky='nsew')
        # autoscale
        self.checkbox_autoscale = ttkb.IntVar()
        self.checkbox_autoscale.set(1)
        self.autoscale = ttkb.Checkbutton(self.menu_right_upper, text='Autoscale data', variable=self.checkbox_autoscale, onvalue=1, offvalue=0)
        self.autoscale.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        # apply gaussian filter
        self.checkbox_gaussian_blurr = ttkb.IntVar()
        self.checkbox_gaussian_blurr.set(0)
        self.gaussian_blurr = ttkb.Checkbutton(self.menu_right_upper, text='Blurr Data', variable=self.checkbox_gaussian_blurr, onvalue=1, offvalue=0)
        self.gaussian_blurr.grid(column=0, row=3, padx=button_padx, pady=button_pady, sticky='nsew')
        # add scalebar
        # self.checkbox_add_scalebar = ttkb.IntVar()
        # self.checkbox_add_scalebar.set(0)
        # self.add_scalebar = ttkb.Checkbutton(self.menu_right_upper, text='Add scalebar', variable=self.checkbox_add_scalebar, onvalue=1, offvalue=0)
        # self.add_scalebar.grid(column=0, row=15, padx=button_padx, pady=button_pady, sticky='nsew')
        self.label_add_scalebar = ttkb.Label(self.menu_right_upper, text='Scalebar channel:')
        self.label_add_scalebar.grid(column=0, row=4)
        self.add_scalebar = ttkb.Entry(self.menu_right_upper, width=input_width, justify='center')
        self.add_scalebar.insert(0, '')
        self.add_scalebar.grid(column=1, row=4, padx=button_padx, pady=button_pady, sticky='ew')

        self.menu_right_separator = ttkb.Separator(self.menu_right, orient='horizontal')
        self.menu_right_separator.grid(column=0, row=1, sticky='ew', padx=button_padx, pady=20)

        # additional controls
        self.menu_right_additional_controls = ttkb.LabelFrame(self.menu_right, text='Additional controls', width=200)
        self.menu_right_additional_controls.grid(column=0, row=2, padx=button_padx, pady=button_pady, sticky='nsew')
        self.menu_right_additional_controls_button = ttkb.Button(self.menu_right_additional_controls)
        self.menu_right_additional_controls_button.grid(column=0, row=0, padx=button_padx, pady=button_pady, sticky='nsew')



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
        # plt.clf()
        self.measurement.Display_Channels(show_plot=False)
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


        
        # canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=TRUE) 
    
    def _Save_Plot(self):
        file = filedialog.asksaveasfile(mode='wb', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
        self.fig.savefig(file)

    def _Get_Folderpath_from_Input(self):
        
        # check if old default path exists to use as initialdir
        self._Get_Old_Folderpath()
        self.folder_path = filedialog.askdirectory(initialdir=self.initialdir)
        # save filepath to txt and use as next initialdir
        with open(os.path.join(this_files_path, 'default_path.txt'), 'w') as file:
            file.write('#' + self.folder_path)

    def _Exit(self):
        self.menu_left.quit()

    def _Get_Old_Folderpath(self):
        try:
            with open(os.path.join(this_files_path, 'default_path.txt'), 'r') as file:
                content = file.read()
            if content[0:1] == '#':
                self.initialdir = content[1:] # to do change to one level higher
        except:
            self.initialdir = this_files_path
        #set old path to folder as default
        self.folder_path = self.initialdir

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

class Generate_Plot():
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.create_figure_test()
    
    def create_figure_test(self):
        measurement = Open_Measurement(self.folder_path)
        measurement.Set_Min_to_Zero()
        measurement.Display_Channels(show_plot=False)
        self.fig = plt.gcf()
        
        





def main():
    Example()

if __name__ == '__main__':
    main()