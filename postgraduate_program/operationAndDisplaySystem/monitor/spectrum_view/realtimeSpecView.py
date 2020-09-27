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
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

import matplotlib
import pymysql

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from monitor.waterfall.compresse.dbOperation import decompress
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
logger = logging.getLogger("Main.realtimeSpecView")


class ApplicationWindow(QWidget):
    def __init__(self, condition, notifyNum, dataCach):
        super().__init__()
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        self.condition = condition
        self.notifyNum = notifyNum
        self.dataCach = dataCach

        self.layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.add_subplot(111)
        # 定时任务
        self._timer = self.freqCanvas.new_timer(1000, [(self._update_canvas, (), {})])

    def _start(self):
        self._timer.start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw()

    # 从dataCach中读出数据
    def getData(self):
        x, y = None, None
        try:
            if self.dataCach.qsize() >= self.notifyNum:
                data = self.dataCach.get()[0][0]
                xList = data.split(";")[0]
                yList = data.split(";")[1]
                x = np.asarray(np.float32(xList.split(" ")))
                y = np.asarray(np.float32(yList.split(" ")))
            else:
                self.condition.acquire()
                self.condition.notify()
                self.condition.release()
        except Exception as e:
            logger.error(e)
        return x, y

    def draw(self):
        x, y = self.getData()
        if (x is None) or (y is None):
            logger.debug("等待数据")
        else:
            self.axs.cla()
            self.axs.plot(x, y)
            self.axs.figure.canvas.draw()
            self.axs.set_ylim(-120, -30)
            self.axs.set_xlabel('频率/MHz', fontsize=14)
            self.axs.set_ylabel('功率/dBM', fontsize=14)

if __name__ == "__main__":
    from communication import zmqLocal
    import queue
    import threading
    from communication import circulationZmqThread

    socket = zmqLocal.localZMQ()
    startfreq = 900 * 1000000
    endfreq = 950 * 1000000
    usrpNum = "USRP1"
    msg = (usrpNum + ',scan,IQ,' + str(startfreq) + ";" + str(endfreq))
    dataCach = queue.Queue()
    condition = threading.Condition()
    waitNum = 4
    circultaionZmqThread = circulationZmqThread.CircultaionZmqThread(socket, msg, dataCach, condition, waitNum)
    circultaionZmqThread.start()

    qapp = QtWidgets.QApplication(sys.argv)
    appw = ApplicationWindow(condition, 2, dataCach)
    appw.show()
    appw._start()
    qapp.exec_()
    while 1:
        ipt = input()
        if ipt == "q":
            logger.debug("input q")
            circultaionZmqThread.stop()
            break
        elif ipt == "r":
            logger.debug("input r")
            circultaionZmqThread.reset()