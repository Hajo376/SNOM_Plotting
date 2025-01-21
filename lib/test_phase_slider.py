import tkinter as tk
from tkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import time
from snom_analysis.main import SnomMeasurement
from snom_analysis.lib.snom_colormaps import SNOM_amplitude, SNOM_phase, SNOM_height
from PIL import Image, ImageTk
import ttkbootstrap as tkkb
import gc

pi = 3.14

class PhaseSlider:

    def __init__(self):
        # Create the main Tkinter window
        self.root = tkkb.Window()
        self.zoom_factor = 1
        # self.root = tk.Tk()
        self.window_width = 800
        self.window_height = 600
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        
        self.root.title("Popup with Slider")

        self.canvas_frame = tkkb.Frame(self.root)
        self.canvas_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)
        self.canvas = tkkb.Canvas(self.canvas_frame, background='black', width=700, height=600)
        # self.canvas = tk.Canvas(self.root)
        # self.canvas.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky=tk.NW)
        self.canvas.pack()

        self.load_data()
        

        # scale data 
        phase_data_scaled = ((self.phase_data - np.min(self.phase_data)) / (np.max(self.phase_data) - np.min(self.phase_data)) * 255).astype(np.uint8)

        # Initial plot
        # create image
        self.cmap = SNOM_phase
        self.image = Image.fromarray(np.uint8(self.cmap(phase_data_scaled)*255))
        # resize image
        # self.image = self.image.resize((800, 600))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Create the menu frame
        self.menu_frame = tkkb.Frame(self.root)
        self.menu_frame.grid(row=0, column=1, sticky=tk.N)

        # Add a text field to display and edit the slider value
        self.slider_var = StringVar(value="0.00")
        self.entry = tkkb.Entry(self.menu_frame, textvariable=self.slider_var, width=10)
        # entry = tk.Entry(self.menu_frame, textvariable=self.slider_var, width=10)
        self.entry.grid(row=0, column=0)
        self.slider_var.trace_add("write", self.update_slider)

        # Add a slider
        # self.slider = tkkb.Scale(self.menu_frame, from_=0, to=2*pi)
        self.slider = tkkb.Scale(self.menu_frame, from_=0, to=100) # sadyl ttk is stupid and we cannot change the stepsize and trying so leads to wired buggy behaviour
        self.slider.set(0)
        self.slider.grid(row=1, column=0)
        self.slider.configure(command=self.update_text)
        # self.slider.bind("<Button-1>", self.slider_click)

        # all the space for canvas
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # adjust main window size to fit data and menu
        self.update_window_size()

        # Run the application
        self.root.mainloop()

    def load_data(self):
        #data
        folder_path = 'C:/Users/Hajo/git_projects/SNOM_Plotting/testdata/2020-01-08 1337 PH denmark_skurve_02_synchronize'
        # folder_path = 'C:/Users/Hajo/git_projects/SNOM_Plotting/testdata/2022-04-25 1212 PH pentamer_840nm_s50_1'
        measurement = SnomMeasurement(folder_path, channels=['O2P'])
        # measurement.scale_channels()
        # measurement.gauss_filter_channels_complex()
        phase_data = measurement.all_data[0]
        self.root.update_idletasks()
        self.phase_data = self.resize_data_new(phase_data, [self.canvas_frame.winfo_width(), self.canvas_frame.winfo_height()], min_dev=0.5)
        self.phase_data = self.shift_phase(0)

    def resize_data_new(self, data, bounds:list=[500,500], min_dev=0.3, max_scaling:int=5):
        # bounds = [x,y] in px
        # min dev means if data is more than min_dev (in percent) smaller that the respective bound it should be upscaled
        x_bound, y_bound = bounds
        # print('x_bound, y_bound:', x_bound, y_bound)
        xres = len(data[0])
        yres = len(data)
        x_scaling, y_scaling = 1, 1
        print('xres:', xres, 'yres:', yres)
        
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
            print('Resizing data')
            print('xres:', xres, 'yres:', yres)
            print('x_scaling:', x_scaling, 'y_scaling:', y_scaling)
            if min([x_scaling, y_scaling]) > 5: 
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
    
    def resize_data_old(self, data):
        xres = len(data[0])
        yres = len(data)
        x_scaling, y_scaling = 1, 1
        print('xres:', xres, 'yres:', yres)
        self.root.update_idletasks()
        print('canvas size:', self.canvas_frame.winfo_width(), self.canvas_frame.winfo_height())
        # if resolutionis larger than the canvas size, resize the data
        if xres > self.canvas_frame.winfo_width():
            xres = self.canvas_frame.winfo_width()
            x_scaling = (xres / len(data[0]))
            y_scaling = x_scaling
            yres = int(yres * x_scaling)
        elif yres > self.canvas_frame.winfo_height():
            yres = self.canvas_frame.winfo_height()
            y_scaling = (yres / len(data))
            x_scaling = y_scaling
            xres = int(xres * y_scaling)
        elif xres < self.canvas_frame.winfo_width() and yres < self.canvas_frame.winfo_height():
            x_scaling = self.canvas_frame.winfo_width() / xres
            y_scaling = self.canvas_frame.winfo_height() / yres
            if x_scaling < y_scaling:
                xres = self.canvas_frame.winfo_width()
                yres = int(yres * x_scaling)
            else:
                yres = self.canvas_frame.winfo_height()
                xres = int(xres * y_scaling)
        print('x_scaling:', x_scaling, 'y_scaling:', y_scaling)
        if (xres != len(data[0]) or yres != len(data)) and ((x_scaling > 1.3 and y_scaling > 1.3) or (x_scaling < 0.7 and y_scaling < 0.7)):
            print('Resizing data')
            print('xres:', xres, 'yres:', yres)
            print('x_scaling:', x_scaling, 'y_scaling:', y_scaling)
            # return np.resize(data, (yres, xres))
            img = Image.fromarray(data)
            img = img.resize((xres, yres), Image.Resampling.NEAREST)
            return np.array(img)
        print('Data not resized')
        return data
            
    def shift_phase(self, shift):
        def apply_shift(x):
            return (x + shift) % (2*pi)
        return np.vectorize(apply_shift)(self.phase_data)        

    def update_plot(self, val):
        """Update the plot based on the slider value."""
        shifted_phase_data = self.shift_phase(float(val))
        phase_data_scaled = ((shifted_phase_data - np.min(shifted_phase_data)) / (np.max(shifted_phase_data) - np.min(shifted_phase_data)) * 255).astype(np.uint8)
        image = Image.fromarray(np.uint8(self.cmap(phase_data_scaled)*255))
        tk_image = ImageTk.PhotoImage(image)
        self.canvas.imgref = tk_image
        self.canvas.itemconfig(self.image_on_canvas, image=tk_image)
        # if self.zoom_factor != 1:
            # tk_image = tk_image.zoom(int(self.zoom_factor))
            # print('trying to scale canvas')
            # self.canvas.scale(self.image_on_canvas, xOrigin=0, yOrigin=0, x_Scale=5, y_Scale=5)
            # self.canvas.scale(self.image_on_canvas, 5)

    def update_slider(self, *args):
        """Update the slider when the text entry changes."""
        try:
            value = float(self.slider_var.get())
            slider_val = value/(2*pi)*100
            self.slider.set(slider_val)
            self.update_plot(value)
        except ValueError:
            pass

    def update_text(self, val):
        """Update the text entry when the slider changes."""
        phase = 2*pi/100*float(val)
        self.slider_var.set(f"{phase:.2f}")
        self.update_plot(phase)

    def update_window_size(self):
        self.root.update_idletasks()
        # get current size:
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        # get image size:
        xres = len(self.phase_data[0])
        yres = len(self.phase_data)
        # get menu width:
        menu_width = self.menu_frame.winfo_width()
        menu_height = self.menu_frame.winfo_height()
        # total needed size:
        x_total = xres + menu_width + 50 # somehow there is some unknown padding or so...
        y_total = yres + menu_height + 50 # somehow there is some unknown padding or so...
        # adjust winwo size:
        # get the screen width and height of the display used
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - x_total/2)
        center_y = int(screen_height/2 - y_total/2)
        self.root.geometry(f"{x_total}x{y_total}+{center_x}+{center_y}")


def main():
    app = PhaseSlider()
    

if __name__ == "__main__":
    main()