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

import samplerate
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

import matplotlib
import pymysql

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection


class ApplicationWindow(QWidget):
    def __init__(self, device, layout):
        super().__init__()
        self.n = 1
        self.id = 1
        self.bar = 0
        self.countLine = 0
        self.device = device
        self.layout = layout
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        # layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-100, -70)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-100, 0)
        # while True:
        #     if os.path.exists('D:\\postgraduate_program\\48recv\\%s\\1.dat'%self.device):
        #         self.n+=1# self.n=1
        #         line = self.draw(self.n)
        #         break
        norm = matplotlib.colors.Normalize(-120, -60)
        # self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
        self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.drawFreq)
        # self.pause = buttons[0]
        # self.watchBack = buttons[1]
        # self.start = QtWidgets.QPushButton('start')
        # self.stop = QtWidgets.QPushButton('stop')
        #
        # layout.addWidget(self.start)
        # layout.addWidget(self.stop)
        #
        # self.start.clicked.connect(self._start)
        # self.stop.clicked.connect(self._stop)

        # 定时任务
        self._timer = self.freqCanvas.new_timer(1000, [(self._update_canvas, (), {})])

    def _start(self):
        self._timer.start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw(self.n)

    def drawFreq(self, event):  # 点击热力图重绘拼频谱图
        po = event.ydata
        print(po)
        self.axs[1].set_ylim(-500, 0)
        if po == None:
            print("提示:点击位置不对")
        elif -po > self.id or po > 0:
            print("提示:该位置没有数据")
        else:
            x, y = self.getOldData(int(-po))
            print(y)
            self.axs[0].cla()
            self.axs[0].plot(x, y)
            self.axs[0].figure.canvas.draw()

            self.axs[0].set_title('频谱图',fontsize=16)
            self.axs[0].set_xlabel('频率/MHz',fontsize=14)
            self.axs[0].set_ylabel('功率/dBm',fontsize=14)
            print(self.axs[0].figure.canvas==self.axs[1].figure.canvas)

    def getOldData(self, n):
        # try:
        # 获取文件建议使用数据库id获取，方便重绘频谱图
        conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        select = ("SELECT `data_path` FROM `waterfall_data_%s` WHERE `id`=%s") % (self.device, n)
        print(select)
        cursor = conn.cursor()
        cursor.execute(select)
        # 获取所有记录列表
        results = str(cursor.fetchall())
        print(results)
        results = results.split('/')
        print(results)
        results = results[-1]
        results = results.split("'")
        results = results[0]
        print(results)

        path = r'..\EMCfile\waterfall\%s\%s' % (self.device, results)
        print(path)
        if os.path.exists(path):
            print(str(n)+'exist')
            file = open(path)
        else:
            pass

        x = file.readline().split(" ")
        y = file.readline().split(" ")
        points = int(x.pop(0))
        ratio = points / (len(x) - 2)
        x.pop(len(x) - 1)
        y.pop(len(y) - 1)
        # print(type(x[0]))
        x = np.array([float(x) for x in x])
        y = np.array([float(y)-11 for y in y])
        x = self.down_sample(x, ratio)
        y = self.down_sample(y, ratio)
        return x, y
        # except:
        #     pass

    def getData(self, n):
        # try:
        # 获取文件建议使用数据库id获取，方便重绘频谱图
        conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        select = ("SELECT `data_path` FROM `waterfall_data_%s` WHERE `id`=%s") % (self.device, self.id)
        print(select)
        cursor = conn.cursor()
        cursor.execute(select)
        # 获取所有记录列表
        results = str(cursor.fetchall())
        # print(results)
        results = results.split('/')
        print(results)
        results = results[-1]
        results = results.split("'")
        results = results[0]
        # print(results)

        path = r'..\EMCfile\waterfall\%s\%s' % (self.device, results)
        print(path)
        if os.path.exists(path):
            print(str(n)+'exist')
            file = open(path)
        else:
            pass

        x = file.readline().split(" ")
        points = int(x.pop(0))

        # ratio = points/(len(x)-2)
        # print(ratio)
        y = file.readline().split(" ")
        x.pop(len(x) - 1)
        y.pop(len(y) - 1)
        x = np.asarray(x)
        y = np.asarray(y)
        # x = np.array([float(x) for x in x])
        # y = np.array([float(y)-11 for y in y])
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        # x = self.down_sample(x, ratio)
        # y = self.down_sample(y, ratio)
        y = y-11
        return x, y

    # def down_sample(self, input_data, ratio):  # 上or下采样
    #     converter = 'linear'  # or 'sinc_fastest', ...
    #     return samplerate.resample(input_data, ratio, converter)

    def draw(self, path):
        # 瀑布图超过限制调整画布大小
        if self.id >= -self.axs[1].get_ylim()[0]:
            self.axs[1].set_ylim(int(self.axs[1].get_ylim()[0] - 100), int(self.axs[1].get_ylim()[0]))
        print('self.axs[1].ylim()[0]=', end='')
        print(self.axs[1].get_ylim())
        # path = random.randint(1, 20)
        if self.bar:
            self.bar.remove()

        self.bar = 0
        try:
            # 重绘频谱图
            x, y = self.getData(path)
            print('successful getdata')
            # print(len(x))
            # print(x)
            self.axs[0].cla()
            self.axs[0].plot(x, y)
            self.axs[0].set_title('频谱图',fontsize=16)
            self.axs[0].set_xlabel('频率/MHz',fontsize=14)
            self.axs[0].set_ylabel('功率/dBm',fontsize=14)

            heat = np.array([-self.n for x in x])
            self.n += 1
            # print('draw')
            # print(self.n)
            self.id += 1
            points = np.array([x, heat]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # 设置一条线并添加至瀑布图的最下方
            norm = matplotlib.colors.Normalize(y.min(), y.max())
            lc = LineCollection(segments, cmap='jet', norm=norm)
            lc.set_array(y)

            # 设置线宽，若瀑布图放的太大线与线之间会出现空缺，若设置太大瀑布图所得比较小时会叠加宽度，可适当调节
            lc.set_linewidth(2)
            line = self.axs[1].add_collection(lc)
            self.countLine += 1

            self.bar = self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
            self.axs[1].figure.canvas.draw()
            self.axs[1].figure.canvas.flush_events()
            print('successful draw')
            return line
        except:
            pass


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow('usrp2')
    app.show()
    qapp.exec_()
