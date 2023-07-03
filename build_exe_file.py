import os
# Just add or remove values to this list based on the imports you don't want : )
excluded_modules = [
    # 'tkterm',
    # 'tkterminal'
    # 'numpy' # must be included!
    # 'scipy'
    # 'kiwisolver'
    # 'altgraph',
    # 'contourpy'
    # 'cycler',
    # 'fonttools',
    # 'importlib-resources',
    # 'pefile',
    # 'Pillow',
    # 'pip',
    # 'pyinstaller',
    # 'pyinstaller-hooks-contrib',
    # 'zipp'
    # '',
    # '',
    # '',
    # 'jedi',
    # 'PIL',
    # 'psutil',
    # 'tk',
    # 'ipython',
    # 'tcl',
    # 'tcl8',
    # 'tornado'
]

append_string = ''
for mod in excluded_modules:
    append_string += f' --exclude-module {mod}'

# Run the shell command with all the exclude module parameters
os.system(f'pyinstaller snom_plotting.py --noconfirm {append_string}') # --onefile