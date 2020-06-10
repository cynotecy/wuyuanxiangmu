"""
不知道干啥的脚本，从来没用过
"""
# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt5. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt5app.py is a very simple type of PyQt5 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application
import os
import sys
from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = 'F:\Anaconda3\\tcl\\tcl8.6'
os.environ['TK_LIBRARY'] = 'F:\Anaconda3\\tcl\\tcl8.6'

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': ['atexit', 'numpy.core._methods', 'numpy.lib.format', 'wave', 'tensorflow'],
        'include_files': ['F:\python3.5\code','F:\python3.5\controller','F:\python3.5\\nets','F:\python3.5\\recognition',
                          'F:\python3.5\SNR','F:\python3.5\Theme','F:\python3.5\\Ui','F:\python3.5\web']
    }
}

executables = [
    Executable('MainWindow.py', base=base)
]

setup(name='simple_PyQt5',
      version='0.1',
      description='Sample cx_Freeze PyQt5 script',
      options=options,
      executables=executables
      )
