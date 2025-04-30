Description:
------------

This repo contains a GUI for the snom-analysis package (https://github.com/Hajo376/SNOM_AFM_analysis). The GUI can quickly visualize data,
apply simple modifications and save data or plots with modifications. So far it's mostly for 2D SNOM data,
but it also supports 3D and approach curve data. Spectra are not yet implemented.

Usage:
------

A detailed description of the GUI is still missing, but each menu has a help button explaining the basics.
A Typical workflow would be:
1. select a measurement folder
2. select the channels to load
3. load the channels
4. apply modifications to the data (e.g. filter, crop, etc.)
5. plot the data
6. save the data or image
7. close the GUI

You can also compare multiple measurements by loding them into the GUI. The GUI shares the same plot 
memory as the snom-analysis package, meaning every plot you create will be saved in the memory. 
The plot memory is only deleted when you close the GUI or when you delete it manually by pressing 'Clear All Plots'.
Thus, if you want to apply modifications and monitor the changes without adding them to the plot memory, 
you should use the 'Update Plot' button instead of the 'Plot' button. This will remove the previous plot from the memory.

The GUI uses the same matplotlib style file as the snom-analysis package, which is located in the users home directory.
You can change the style file to your needs, but be aware that this will also change the style for the snom-analysis package.
Similarly, you can also change the config.ini which contains the data settings.

If you are unshure about the functions you can check out the snom-analysis package documentation (https://snom-analysis.readthedocs.io/en/latest/index.html), as the GUI is just a wrapper around the package.

Installation:
-------------

If you are using a windows machine you can just download the most recent setup.exe which will open an install-wizard.
So far the GUI is only tested on windows, but it should work on linux and mac as well. You can simply clone the repo and create your own installer.
For the install-wizard i use the Inno Setup Compiler, which is a free installer for Windows programs, but any other installer should work as well.