"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
"""
使用pico绘制瀑布图，暂未启用
"""
import time
import math
import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
import pandas as pd

import matplotlib
import pymysql
from scipy.io import loadmat

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection


class ApplicationWindow(QWidget):
    def __init__(self, path):
        super().__init__()
        self.n = 2
        self.id = 1
        self.bar = 0
        self.fileNum = 0
        self.path = path# 传入pico保存的文件夹地址
        # #####################
        # self.lists = os.listdir(self.path)
        # self.txt_list = []
        # for path in self.lists:
        #     if '.csv' in path:
        #         self.txt_list.append(path)
        # if self.txt_list and len(self.txt_list) > 3:
        #     self.txt_list.sort(key=lambda fn: os.path.getmtime(self.path + "\\" + fn))
        #     print(len(self.txt_list))
        # #####################
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-140, -50)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-100, 0)


        norm = matplotlib.colors.Normalize(-120, -60)
        # self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
        self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.drawFreq)
        self.start = QtWidgets.QPushButton('start')
        self.stop = QtWidgets.QPushButton('stop')

        layout.addWidget(self.start)
        layout.addWidget(self.stop)

        self.start.clicked.connect(self._start)
        self.stop.clicked.connect(self._stop)

        # 定时任务
        self._timer = self.freqCanvas.new_timer(300, [(self._update_canvas, (), {})])

    def _start(self):
        self._timer.start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw()
        # print(self.n)

    def drawFreq(self, event):  # 点击热力图重绘拼频谱图
        po = event.ydata
        self.axs[1].set_ylim(-500, 0)
        if po == None:
            print("提示:点击位置不对")
        elif -po > self.n or po > 0:
            print("提示:该位置没有数据")
        else:
            print(int(-po))
            x, y = self.getOldData(int(-po))
            if not x == "noFile":
                self.axs[0].cla()
                self.axs[0].plot(x, y)
                self.axs[0].set_ylim(-140, -50)
                self.axs[0].figure.canvas.draw()

                self.axs[0].set_title('频谱图',fontsize=16)
                self.axs[0].set_xlabel('频率/MHz',fontsize=14)
                self.axs[0].set_ylabel('功率/dBm',fontsize=14)

    def getOldData(self, n):
        path = self.path + '\\' + '1 (' + str(n) +').csv'
        if not path == "noFile":
            if os.path.exists(path):
                data = pd.read_csv(path, skiprows=5)
                x = data.values[15:2050, 0]
                y = data.values[15:2050, 1]
                return x, y
        else:
            x = "noFile"
            y = "noFile"
            return x, y

    # def get_latest_file(self):
    #     # lists = os.listdir(self.path)
    #     # txt_list = []
    #     # for path in lists:
    #     #     if '.csv' in path:
    #     #         txt_list.append(path)
    #     # print(1111111)
    #     # if txt_list and len(txt_list)>3:
    #     #     txt_list.sort(key=lambda fn: os.path.getmtime(self.path + "\\" + fn))
    #     #     print(len(txt_list))
    #         # for txt in txt_list[0:-3]:
    #         #     print(txt)
    #         #     os.remove(self.path+'\\'+txt)
    #     file_latest = os.path.join(self.path, self.txt_list[self.n])
    #     self.n += 1
    #     print(file_latest)
    #     return file_latest
    #     # else:
    #     #     print('else')
    #     #     return "noFile"

    def getData(self):
        path = self.path + '\\'+ '1 (' + str(self.n) +').csv'
        print(path)
        if not path == "noFile":
            if os.path.exists(path):
                data = pd.read_csv(path, skiprows=5)
                x = data.values[15:2050, 0]
                y = data.values[15:2050, 1]
                print(self.n)
                return x, y
        else:
            x = "noFile"
            y = "noFile"
            return x, y

    def draw(self):
        if self.n >= -self.axs[1].get_ylim()[0]:
            self.axs[1].set_ylim(int(self.axs[1].get_ylim()[0] - 100), int(self.axs[1].get_ylim()[0]))
        try:
            # 重绘频谱图
            print(self.path)
            self.fileNum = sum([len(x) for _, _, x in os.walk(os.path.dirname(self.path))])
            if self.fileNum > 3 and self.fileNum > self.n+1:
                print('start draw')
                x, y = self.getData()
                if self.bar:
                    self.bar.remove()
                self.bar = 0
                print('successful getdata')
                self.axs[0].cla()
                self.axs[0].plot(x, y)
                self.axs[0].set_ylim(-140, -50)
                self.axs[0].set_title('频谱图', fontsize=16)
                self.axs[0].set_xlabel('频率/MHz', fontsize=14)
                self.axs[0].set_ylabel('功率/dBM', fontsize=14)


                heat = np.array([-self.n for x in x])
                self.n += 1
                self.id += 1
                points = np.array([x, heat]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                # 设置一条线并添加至瀑布图的最下方
                norm = matplotlib.colors.Normalize((y.min()+200)**2, (y.max()+200)**2)
                lc = LineCollection(segments, cmap='jet', norm=norm)
                lc.set_array((y+200)**2)
                # print(type(math.log(y)))
                # print(math.log(y))

                # 设置线宽，若瀑布图放的太大线与线之间会出现空缺，若设置太大瀑布图所得比较小时会叠加宽度，可适当调节
                lc.set_linewidth(2)
                line = self.axs[1].add_collection(lc)
                self.bar = self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
                self.axs[1].figure.canvas.draw()
                self.axs[1].figure.canvas.flush_events()
                print('successful draw')
                return line
        except:
            pass


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r'D:\myPrograms\CASTProgram\postgraduate_program\usrp_recvfiles\usrp_scan\\')
    app.show()
    qapp.exec_()
