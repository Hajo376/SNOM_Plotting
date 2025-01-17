import tkinter as tk
from tkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import time

def update_plot(val):
    """Update the plot based on the slider value."""
    try:
        value = float(slider_var.get())
        x = np.linspace(0, 10, 100)
        y = np.sin(value * x)
        # add sleep to simulate long running process
        time.sleep(0.1)
        ax.clear()
        ax.plot(x, y, label=f"y = sin({value}x)")
        ax.legend()
        canvas.draw()
    except ValueError:
        pass

def update_slider(*args):
    """Update the slider when the text entry changes."""
    try:
        value = float(slider_var.get())
        slider.set(value)
        update_plot(value)
    except ValueError:
        pass

def update_text(val):
    """Update the text entry when the slider changes."""
    slider_var.set(f"{slider.get():.2f}")
    update_plot(val)

def slider_click(event):
    """Handle clicking on the slider to set the value directly."""
    slider_length = slider.winfo_width()
    slider_start = slider.winfo_rootx()
    click_position = event.x_root - slider_start
    value = slider.cget("from") + (click_position / slider_length) * (slider.cget("to") - slider.cget("from"))
    slider.set(value)
    slider_var.set(f"{value:.2f}")
    update_plot(value)

# Create the main Tkinter window
root = tk.Tk()
root.title("Matplotlib Popup with Slider")

# Create the matplotlib figure and axes
fig, ax = plt.subplots(figsize=(5, 4))
fig.tight_layout(pad=3)

# Initial plot
x = np.linspace(0, 10, 100)
y = np.sin(1 * x)
ax.plot(x, y, label="y = sin(x)")
ax.legend()

# Embed the plot in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

# Create the menu frame
menu_frame = tk.Frame(root, padx=10, pady=10)
menu_frame.grid(row=0, column=1, sticky=tk.N)

# Add a text field to display and edit the slider value
slider_var = StringVar(value="1.00")
entry = tk.Entry(menu_frame, textvariable=slider_var, width=10)
entry.grid(row=0, column=0, pady=5)
slider_var.trace_add("write", update_slider)

# Add a slider
slider = tk.Scale(menu_frame, from_=0.1, to=10, resolution=0.1, orient="horizontal", length=200)
slider.set(1)
slider.grid(row=1, column=0, pady=5)
slider.configure(command=update_text)
slider.bind("<Button-1>", slider_click)

# Run the application
update_plot(1)
root.mainloop()
