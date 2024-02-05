import tkinter as tk 
from tkinter import ttk 
  
  
window = tk.Tk() 
window.title("Text Widget Example") 
window.geometry('400x200') 
  
ttk.Label(window, text="Enter your comment :", 
          font=("Times New Roman", 15)).grid( 
  column=0, row=0, padx=10, pady=25) 
  
# Text Widget 
t = tk.Text(window, width=20, height=3) 
  
t.grid(column=1, row=0) 

def print_text():
    print(t.get(1.0, "end-1c"))

# Button to print text
button = tk.Button(window, text='Print', command=print_text)
button.grid(column=0, columnspan=2, row=1, padx=10, pady=25)


  
window.mainloop() 