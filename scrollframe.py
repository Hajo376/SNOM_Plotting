
# heigth = 200
# width = 200

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import tkinter as tk
import platform

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent, heigth, width):
        self.canvas_height = heigth
        self.canvas_width = width

        self.full_menu_visible = False
        super().__init__(parent) # create a frame (self)
        # self.pack(expand=True, fill='both')

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", height=self.canvas_height, width=self.canvas_width)#, height=heigth, width=width          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.
        # print('test')
        # self.canvas.configure(height=height) 

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            if self.full_menu_visible is False:
                self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            if self.full_menu_visible is False:
                self.canvas.unbind_all("<MouseWheel>")

    def changeCanvasHeight(self, height):
        # self.canvas.itemconfig(self.canvas_window, height=height)  
        self.canvas.configure(height=height)  
        # print('viewport height: ', self.viewPort.winfo_height())
        if height > self.viewPort.winfo_height():
            self.canvas.unbind_all("<MouseWheel>")
            self.vsb.pack_forget()    
            self.full_menu_visible = True
        elif height < self.viewPort.winfo_height():
            self.canvas.bind_all("<MouseWheel>")
            self.vsb.pack(side="right", fill="y")    
            self.full_menu_visible = False

        # self.viewPort.config(height=height)  






"""
from tkinter import ttk
import tkinter as tk

appHeight = 200
class ScrollFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        s=ttk.Style()
        s.configure('TFrame', background="#eff0f1")

        #place canvas on self
        self.canvas = tk.Canvas(self, borderwidth=0, background="#eff0f1", height = appHeight)
        #place a frame on the canvas, this frame will hold the child widgets
        self.viewPort = ttk.Frame(self.canvas, style='TFrame')
        #place a scrollbar on self
        self.vsb = ttk.Scrollbar(self, orient="vertical")
        #attach scrollbar action to scroll of canvas
        self.canvas.configure(yscrollcommand=self.vsb.set)

        #pack scrollbar to right of self
        self.vsb.pack(side="right", fill="y")
        #pack canvas to left of self and expand to fil
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((4,4),
                                                 #add view port frame to canvas
                                                 window=self.viewPort, anchor="nw",
                                                 tags="self.viewPort")

        #bind an event whenever the size of the viewPort frame changes.
        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

        #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize
        self.onFrameConfigure(None)

        self.viewPort.bind('<Enter>', self._bound_to_mousewheel)
        self.viewPort.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        #whenever the size of the frame changes, alter the scroll region respectively.
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        #whenever the size of the canvas changes alter the window region respectively.
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)






"""