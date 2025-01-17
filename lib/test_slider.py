import tkinter as tk

def update_entry(event):
    # Update the Entry widget with the current slider value
    value = slider.get()
    entry_var.set(value)

def update_slider(*args):
    # Update the slider with the current Entry value
    try:
        # value = int(entry_var.get())
        value = float(entry_var.get())
        slider.set(value)
    except ValueError:
        print("Invalid input in the Entry widget")
        pass  # Ignore invalid input in the Entry widget

# Create the main Tkinter window
root = tk.Tk()
root.title("Slider and Entry Popup")

# Create a Frame to hold the widgets
frame = tk.Frame(root, padx=20, pady=20)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create a Scale (slider) widget
slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", length=300, digits=1, resolution=0.1)
slider.grid(row=0, column=0, padx=10, pady=10)
slider.bind("<Motion>", update_entry)

# Create an Entry widget
entry_var = tk.StringVar()
entry = tk.Entry(frame, textvariable=entry_var, width=10)
entry.grid(row=0, column=1, padx=10, pady=10)
entry_var.trace_add("write", update_slider)

# Initialize the slider and entry with a default value
slider.set(50)
entry_var.set("50")

# Run the application
root.mainloop()
