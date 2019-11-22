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
    def __init__(self, path):
        super().__init__()
        self.path = path

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

    def _update_canvas(self):
        self.draw()

    def getData(self):
        # 获取文件建议使用数据库id获取，方便重绘频谱图
        print(self.path)
        # file = open(path)
        file = open(self.path)

        # x = file.readline().split(" ")
        xy = file.read().split('\n')
        x = xy[0]
        x = x.split(' ')
        y = xy[1]
        y = y.split(' ')
        x.pop(len(x) - 1)
        y.pop(len(y) - 1)
        # print(y)
        # print(y[0:5])
        # x = range(len(y))
        x = np.array([float(x) for x in x])
        y = np.array([float(y)-11 for y in y])
        return x, y

    def draw(self):
        # 重绘频谱图
        x, y = self.getData()
        print('successful getdata')
        # x = range(len(y))
        self.axs.cla()
        self.axs.plot(x, y)

        self.axs.set_xlabel('频率/MHz',fontsize=14)
        self.axs.set_ylabel('功率/dBm',fontsize=14)
        print('successful draw')
        # return line


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r"..\specEnvelope_recvfiles\20190814180613.txt")
    app.show()
    qapp.exec_()
