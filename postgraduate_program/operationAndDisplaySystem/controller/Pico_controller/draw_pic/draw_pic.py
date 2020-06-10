"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
import sys
import os

import matplotlib
import numpy as np
import pymysql
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class ApplicationWindow(QWidget):
    def __init__(self, filepath, device_name):
        super().__init__()
        self.filepath = filepath
        self.y1List = []
        self.device_name = device_name
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)  # 实例化布局，用来塞画布
        self.freqCanvas = FigureCanvas(Figure(figsize=(12, 6)))  # 实例化画布

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(1, 2, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-100, -70)
        self.axs[1].set_xlim(100, 200)
        self.axs[1].set_ylim(-500, 0)
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
        select = ("SELECT `data` FROM `sample_data` WHERE `id`=%s") % self.device_name
        print(select)
        cursor = conn.cursor()
        cursor.execute(select)
        # 获取所有记录列表
        results = str(cursor.fetchall())
        results = results.split('/')
        # print(results)
        results = results[-1]
        results = results.split("'")
        results = results[0]
        # print(results)
        self.path = '..\EMCfile\data\sample_data\%s' % results

        # print(self.path)

        file2 = open(self.path)
        y2 = file2.read().split('\n')
        y2.pop(len(y2) - 1)
        x2 = range(len(y2))
        x2 = np.array([float(x)*0.008 for x in x2])
        y2 = np.array([float(y2) for y2 in y2])


        fileList = self.get_fileList()

        for i in range(len(fileList)):
            file = open(self.filepath+ '\\'+fileList[i])
            y_ = file.read().split('\n')
            y_.pop(len(y_) - 1)
            self.y1List.append(y_)

        # print(self.y1List[0:10][0])
        x1 = range(len(self.y1List[0]))
        x1 = np.array([float(x)*0.008 for x in x1])
        y1Array = np.asarray(self.y1List).astype('float64')
        # y1Array.astype('float64')
        # print(type(y1Array[0][0]))
        y1 = y1Array.mean(axis=0)
        # print(y1.shape)
        # y2 = np.array([float(y2) for y2 in y2])
        return x1, y1, x2, y2

    def get_fileList(self):
        lists = os.listdir(self.filepath)
        txt_list = []
        for path in lists:
            if '.txt' in path:
                txt_list.append(path)
        if txt_list:
            txt_list.sort(key=lambda fn: os.path.getmtime(self.filepath + "\\" + fn))
            txt_list = txt_list[0:9]
            return txt_list
        else:
            return "noFile"

    def draw(self):
        # 重绘频谱图
        x1, y1, x2, y2 = self.getData()
        print('successful getdata')
        # x = range(len(y))

        self.axs[0].cla()
        self.axs[0].plot(x1, y1)
        self.axs[0].set_title('信号波形图',fontsize=16)
        self.axs[0].set_xlabel('时间/us',fontsize=14)
        self.axs[0].set_ylabel('电压/v',fontsize=14)
        self.axs[1].cla()
        self.axs[1].plot(x2, y2)
        self.axs[1].set_title('样本波形图',fontsize=16)
        self.axs[1].set_xlabel('时间/us',fontsize=14)
        self.axs[1].set_ylabel('电压/v',fontsize=14)
        self.axs[0].figure.canvas.draw()
        self.axs[0].figure.canvas.flush_events()
        print('successful draw')
        # return line



if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r"..\interference_file\txt\fan\20190918171353",1)
    app.show()
    qapp.exec_()
