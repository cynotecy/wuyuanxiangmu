"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
import os
import sys
import time
import datetime
import pandas as pd
import datetime

import matplotlib
import numpy as np
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from scipy.io import loadmat
import logging
logging.getLogger('matplotlib.font_manager').disabled = True


"""
"""
class MaxminRealpart(QWidget):
    def __init__(self, path, logger):
        super().__init__()
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.currenttime = datetime.datetime.now()
        self.path = path
        self.logger = logger
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 12)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1)
        self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.drawFreq)

        # self.axs.set_xlim(150, 200)
        # self.axs.set_ylim(-100, -70)
        self.draw()

    def getData(self, mat_list):
        list_num = len(mat_list)-1
        # print(list_num)
        dat_path = self.path
        # print(dat_path)
        max_group = []
        min_group = []
        # print('min_group')
        firsttime = os.path.getmtime(dat_path+'\\'+mat_list[0])
        endtime = os.path.getmtime(dat_path + '\\' + mat_list[-2])
        # print(firsttime)
        # print(type(endtime))
        self.firsttime = datetime.datetime.fromtimestamp(firsttime)
        self.endtime = datetime.datetime.fromtimestamp(endtime)
        self.countFiles = len(mat_list)-1
        # print('len lists',self.countFiles)
        for num in range(list_num):
            datas = pd.read_csv(dat_path+'\\'+mat_list[num], skiprows=1, usecols=[1])
            datas = datas.values[:, 0]
            # datas = np.loadtxt(open(dat_path+'\\'+mat_list[num], "rb"), delimiter=",", skiprows=3)[:, 1]
            # for i in range(len(datas)):
            datas = datas.astype(np.float32)
            max_group.append(np.max(datas))
            min_group.append(np.min(datas))
        # txt = np.loadtxt(file_latest, dtype=str)[:]
        # print(max_group)
        # print(len(max_group))

        # min_group = [0.1 for _ in range(len(max_group))]
        return max_group, min_group

    def getDataList(self):
        lists = os.listdir(self.path)
        mat_list = []
        for path in lists:
            if '.csv' in path:
                mat_list.append(path)
        if mat_list:
            mat_list.sort(key=lambda fn: os.path.getmtime(self.path + "\\" + fn))
            return mat_list

    def draw(self):
        # 获得排序后的文件列表
        mat_list = self.getDataList()
        #####
        max_group, min_group = self.getData(mat_list)
        # 生成一个matplotli认得的days序列
        delay = (self.endtime - self.firsttime)/self.countFiles
        # print(type(secs))
        # delay = datetime.timedelta(seconds=secs)
        # end_time_ = self.currenttime + delay * (len(max_group) - 1)
        # print(end_time_)
        self.time_range_2 = matplotlib.dates.drange(self.firsttime, self.endtime, delay)
        # print('len')
        # print(len(self.time_range_2))
        # print(len(max_group))
        # 为了解决薛定谔的drange，根据drange尺寸决定要不要丢掉一个y
        if len(self.time_range_2) < len(max_group):
            max_group = max_group[:len(self.time_range_2)]
            min_group = min_group[:len(self.time_range_2)]
        elif len(self.time_range_2) > len(max_group):
            self.time_range_2 = self.time_range_2[:len(max_group)]
        # print('len2')
        # print(len(self.time_range_2))
        # print(len(max_group))
        # fig, ax = plt.subplots()
        # plt.xlabel('时间')
        # plt.ylabel('电压/v')
        self.axs[0].cla()
        self.axs[0].plot_date(self.time_range_2, max_group, linestyle='-', marker='')
        self.axs[0].plot_date(self.time_range_2, min_group, linestyle='-', marker='')
        # 生成游标
        from matplotlib.widgets import Cursor
        self.cursor = Cursor(self.axs[0], useblit=True, color='red', linewidth=2, vertOn=True, horizOn=True)
        # print(cursor)
        self.axs[0].set_title('时域信号监测',fontsize=16)
        self.axs[0].set_xlabel('时间',fontsize=14)
        self.axs[0].set_ylabel('电压/mv',fontsize=14)
        date_format = matplotlib.dates.DateFormatter('%H:%M:%S')
        self.axs[0].xaxis.set_major_formatter(date_format, )
        # print('successful draw')
        self.logger.info("成功绘制时域监测图")

    def drawFreq(self, event):  # 点击回溯
        po = event.xdata
        # print(po)
        if po == None:
            # print("提示:点击位置不对")
            self.logger.info("时域监测回溯-无效位置")
        elif po>self.time_range_2[-1] or po<self.time_range_2[0]:
            # print("提示:该位置没有数据")
            self.logger.info("时域监测回溯-点击位置无数据")
        else:
            mat_list = self.getDataList()
            y = self.getOldData(mat_list, po)
            self.axs[1].cla()
            self.axs[1].plot(y)
            self.axs[1].figure.canvas.draw()

            self.axs[1].set_title('时域信号图', fontsize=16)
            self.axs[1].set_xlabel('时间/us', fontsize=14)
            self.axs[1].set_ylabel('电压/mV', fontsize=14)
            self.logger.info("成功查看时域监测图历史回溯")

    def getOldData(self, mat_list, po):
        dat_path = self.path
        num = len(self.time_range_2)-int(len(self.time_range_2)*(self.time_range_2[-1]-po)/(self.time_range_2[-1]-self.time_range_2[0]))
        # print(num)
        # print(dat_path + '\\' + mat_list[num-1])
        self.logger.info("时域监测图历史回溯文件路径"+dat_path + '\\' + mat_list[num-1])
        datas = pd.read_csv(dat_path + '\\' + mat_list[num-1], skiprows=1, usecols=[1])
        datas = datas.values[:, 0]
        datas = datas.astype(np.float32)
        y = datas
        return y

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = MaxminRealpart(r'D:\myPrograms\CASTProgram\postgraduate_program\data\realpart_recvfiles\pico')
    app.show()
    qapp.exec_()
