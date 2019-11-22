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
    def __init__(self, path, liney):
        super().__init__()
        self.path = path
        self.liney = liney
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
        # self.axs.set_ylim(-100, -70)
        self.draw()
##########
    def _update_canvas(self):
        self.draw()

    def getData(self):
        x = np.loadtxt(self.path, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
        y = np.loadtxt(self.path, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
        x = np.asarray(np.float32(x))
        y = np.asarray(np.float32(y)-11)
        return x, y
    def draw(self):
        # 绘频谱图
        x, y = self.getData()
        self.lineyArray = [self.liney for _ in range(len(x))]
        self.lineyArray = np.array([float(_) for _ in self.lineyArray])
        self.axs.cla()
        self.axs.plot(x, y)
        self.axs.plot(x, self.lineyArray)
        self.axs.set_xlabel('频率/MHz',fontsize=14)
        self.axs.set_ylabel('功率/dBm',fontsize=14)
        # print('successful draw')
        # return line


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r"..\steadyInterference\Input_file\Spectrum_HUB.txt",'-101')#
    app.show()
    qapp.exec_()
