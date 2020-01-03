"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
import time
import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection


class ApplicationWindow(QWidget):
    def __init__(self, *arg):
        super().__init__()
        if len(arg) == 1:
            self.path = path
        elif len(arg) == 3:
        self.lineyArray = 0
        ############
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(1, 1)

        # self.axs.set_xlim(150, 200)
        # self.axs.set_ylim(-120, -70)
        self.draw()

    def _update_canvas(self):
        self.draw()

    def getData(self):
        x = np.loadtxt(self.path, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
        y = np.loadtxt(self.path, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
        x = np.asarray(np.float32(x))
        y = np.asarray(np.float32(y)-11)
        # file = open(self.path)
        # # x = file.readline().split(" ")
        # xy1 = file.read().split('\n')
        # x1 = xy1[0]
        # x1 = x1.split(' ')
        # y1 = xy1[1]
        # y1 = y1.split(' ')
        # x1.pop(len(x1) - 1)
        # y1.pop(len(y1) - 1)
        # # print(y)
        # # print(y[0:5])
        # # x = range(len(y))
        # x1 = np.array([float(x1) for x1 in x1])
        # y1 = np.array([float(y1)-11 for y1 in y1])
        #
        # file = open(self.path)
        # y2 = file.read().split(' ')
        # # x2 = xy2[0]
        # # x2 = x2.split(' ')
        # # y2 = xy2[1]
        # # y2 = y2.split(' ')
        # # x2.pop(len(x2) - 1)
        # y2.pop(len(y2) - 1)
        # # print(y)
        # # print(y[0:5])
        # # x = range(len(y))
        # # x2 = np.array([float(x2) for x2 in x2])
        # y2 = np.array([float(y2) for y2 in y2])

        return x, y
    def draw(self):
        # 绘频谱图
        x, y = self.getData()
        # print('successful getdata')
        # x = range(len(y))
        self.axs.cla()
        self.axs.plot(x, y)
        self.axs.set_xlabel('频率/MHz',fontsize=14)
        self.axs.set_ylabel('功率/dBm',fontsize=14)
        from matplotlib.widgets import Cursor
        self.cursor = Cursor(self.axs, useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        # print('successful draw')
        # return line


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r"D:/postgraduate_program/steadyInterference/Input_file/Spectrum_MCU.txt")#
    app.show()
    qapp.exec_()
