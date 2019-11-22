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
import pymysql
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
    def __init__(self, path, sampleOutter_id, sampleInner_id, signalLimit, sampleLimit):
        # path是信号地址，sample_id是样本外编号，sampleInner_id是样本内编号
        super().__init__()
        self.filepath = path
        self.sampleOutter_id = sampleOutter_id
        self.sampleInner_id = sampleInner_id
        self.sample_id = self.sampleOutter_id+self.sampleInner_id
        self.signalLimit = signalLimit
        self.sampleLimit = sampleLimit
        print(self.sample_id)
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(14, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(1, 2)

        # self.axs.set_xlim(150, 200)
        # self.axs.set_ylim(-100, -70)
        self.draw()

    def _update_canvas(self):
        self.draw()

    def getData(self):
        # 获取文件建议使用数据库id获取，方便重绘频谱图
        conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        select = ("SELECT `data` FROM `sample_data` WHERE `id`=%s") % self.sample_id
        print(select)
        cursor = conn.cursor()
        cursor.execute(select)
        # 获取所有记录列表
        results = str(cursor.fetchall())
        results = results.split('/')
        results = results[-1]
        results = results.split("'")
        results = results[0]
        print(results)
        self.path = '..\EMCfile\data\sample_data\%s' % results
        print(self.path)


        print(self.filepath)
        file = open(self.filepath)
        # x = file.readline().split(" ")
        xy1 = file.read().split('\n')
        x1 = xy1[0]
        x1 = x1.split(' ')
        y1 = xy1[1]
        y1 = y1.split(' ')
        x1.pop(len(x1) - 1)
        y1.pop(len(y1) - 1)
        x1 = np.array([float(x1) for x1 in x1])
        y1 = np.array([float(y1) for y1 in y1])
        # 生成需要标红部分的列表
        x1RedIndex = []
        # x1RedIndex.append(np.argwhere(x1 == self.signalLimit[0]))
        # x1RedIndex.append(np.argwhere(x1 == self.signalLimit[1]))
        x1Red = x1[self.signalLimit[0]:self.signalLimit[1]]
        y1Red = y1[self.signalLimit[0]:self.signalLimit[1]]

        file = open(self.path)
        y2 = file.read().split('\n')
        y2.pop(len(y2) - 1)
        x2 = range(len(y2))
        x2 = np.array([float(x2) for x2 in x2])
        y2 = np.array([float(y2) for y2 in y2])
        # 生成需要标红的列表
        x2Red = x2[self.sampleLimit[0]:self.sampleLimit[1]]
        y2Red = y2[self.sampleLimit[0]:self.sampleLimit[1]]


        return x1, y1, x1Red, y1Red, x2, y2, x2Red, y2Red

    def draw(self):
        # 重绘频谱图
        x1, y1, x1Red, y1Red, x2, y2, x2Red, y2Red = self.getData()
        print('successful getdata')
        xnum = len(y2)
        print(xnum)
        # # 生成样本图横坐标
        # # GSM
        # if self.sampleOutter_id == 5:
        #     step = (960-935)/xnum
        #     self.x2 = np.arange(935.0, 960.0, step)
        #     print(len(self.x2))
        # # WCDMA
        # elif self.sample_id == 6:
        #     step = (2145-2130)/xnum
        #     self.x2 = np.arange(2130.0, 2145.0, step)
        #     print(len(self.x2))
        # # WLAN
        # elif self.sample_id == 7:
        #     step = (2483-2400)/xnum
        #     self.x2 = np.arange(2400.0, 2483.0, step)
        #     print(len(self.x2))
        # # CDMA800
        # elif self.sample_id == 8:
        #     step = (880-870)/xnum
        #     self.x2 = np.arange(870.0, 880.0, step)
        #     print(len(self.x2))
        # # TD_SCDMA
        # elif self.sample_id == 9:
        #     step = (2025 - 2010) / xnum
        #     self.x2 = np.arange(2010.0, 2025.0, step)
        #     print(len(self.x2))
        # # FDD-LTE
        # elif self.sample_id == 10:
        #     step = (1875 - 1850) / xnum
        #     self.x2 = np.arange(1850.0, 1875.0, step)
        #     print(len(self.x2))
        # # GSM1800
        # elif self.sample_id == 11:
        #     step = (1840 - 1805) / xnum
        #     self.x2 = np.arange(1805.0, 1840.0, step)
        #     print(len(self.x2))
        # x = range(len(y))
        self.axs[0].cla()
        self.axs[0].plot(x1, y1)
        self.axs[0].plot(x1Red, y1Red, color='red')
        # self.axs[0].plot(y1)
        self.axs[0].set_title('信号波形图',fontsize=16)
        self.axs[0].axis('off')
        # self.axs[0].set_xlabel('频率/MHz',fontsize=14)
        # self.axs[0].set_ylabel('功率/dBM',fontsize=14)
        self.axs[1].cla()
        self.axs[1].plot(y2)
        self.axs[1].plot(x2Red,y2Red, color='red')
        self.axs[1].set_title('样本波形图',fontsize=16)
        self.axs[1].axis('off')
        # self.axs[1].set_xlabel('频率/MHz',fontsize=14)
        # self.axs[1].set_ylabel('功率/dBM')
        print('successful draw')
        # return line


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r"..\specEnvelope_recvfiles\20190717105938.txt", 32, 1, [2, 8191], [0, 813])
    app.show()
    qapp.exec_()
