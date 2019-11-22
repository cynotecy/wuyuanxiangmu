'''
实时频谱分析程序说明：
(1)该程序需给定文件夹，文件夹内存储频谱数据，格式为txt
(2)该程序会自动寻找文件夹内最新的txt文件作为数据来源
(3)该程序输出的频谱颜色代表该频点出现的频次或概率
'''
"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
import math
import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

import matplotlib
import matplotlib.pyplot as plt
import collections

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection


class ApplicationWindow(QWidget):

    def __init__(self, path):
        super().__init__()
        self.n = 1
        self.id = 0
        self.path = path

        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)
        self.axs = self.freqCanvas.figure.subplots(1, 1, sharex=True)


        # self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
        # self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.drawFreq)
        self.start = QtWidgets.QPushButton('start')
        self.stop = QtWidgets.QPushButton('stop')

        layout.addWidget(self.start)
        layout.addWidget(self.stop)

        self.start.clicked.connect(self._start)
        self.stop.clicked.connect(self._stop)

        # 定时任务
        self._timer = self.freqCanvas.new_timer(1000, [(self._update_canvas, (), {})])
        # self.axs.figure.colorbar(line, ax=self.axs)# 设置colorbar，需要在init中初始化第一条line
        self.bar = 0


        # 实时频谱分析数据的初始化
        # self.data_path = r'D:\Code_test_data\spectrum\test 1800-1900'
        # self.warning_report = ['Error:文件夹中无频谱数据!']
        # self.plot_report = ['分析频谱中……']

    def _start(self):
        self._timer.start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw(self.n)

    # 获得频谱数据
    def get_spectrum_file(self, n):

        frequency_raw = []
        amplitude_raw = []
        frequency_int_raw = []
        amplitude_int_raw = []
        spectrum = []

        spectrum_file = self.path + '\\' + str(n) + ".txt"
        print(spectrum_file)
        if os.path.exists(spectrum_file):

            #  存储整数作为统计频点的标准，所有整数部分相同的坐标判为同一个坐标
            file_int = np.loadtxt(spectrum_file).astype(np.int)
            #  存储实际频点和幅度用作画图
            file = np.loadtxt(spectrum_file).astype(np.float32)

            for i in range(len(file)):
                if i % 2 == 0:
                    frequency_raw.append(file[i])
                else:
                    amplitude_raw.append(file[i])

            for i in range(len(file_int)):
                if i % 2 == 0:
                    frequency_int_raw.append(file_int[i])
                else:
                    amplitude_int_raw.append(file_int[i])

            # 将txt中的频点和幅值的整数部分分别存储为1*N维数组，作为判别值
            frequency_int = np.array(frequency_int_raw).flatten()
            amplitude_int = np.array(amplitude_int_raw).flatten()

            # 将频点和幅值数组合并，维数为N*2
            array_num_int = np.column_stack((frequency_int, amplitude_int))

            # 将频点和幅值存成坐标，放到列表中

            for i in array_num_int:
                spectrum.append(tuple(i))

            # 统计频次，coordinate存放坐标，dot_count存放频次
            spectrum_dict = collections.Counter(spectrum)
            coordinate_standard = list(spectrum_dict.keys())
            dot_count_standard = list(spectrum_dict.values())
            probability_standard = []
            sum_dot = 0
            for i in dot_count_standard:
                sum_dot = sum_dot + i
            for i in dot_count_standard:
                # probability_standard.append(i/sum_dot*100)
                probability_standard.append(math.log(i))

            # 创建坐标对应频次的字典
            # spectrum_probability_dict = dict(zip(coordinate_standard, dot_count_standard))
            spectrum_probability_dict = dict(zip(coordinate_standard, probability_standard))
            frequency = np.array(frequency_raw)
            amplitude = np.array(amplitude_raw)

            dot_num_raw = []
            for i in range(frequency.shape[0]):
                array_num = np.column_stack((frequency[i], amplitude[i]))
                num_each_rows = []
                for j in array_num:
                    j = tuple(j.astype(np.int))
                    num_each_rows.append(spectrum_probability_dict.get(j))
                    array_num_each_rows = num_each_rows
                array_num_each_rows = np.array(array_num_each_rows)
                dot_num_raw.append(array_num_each_rows)
            dot_num = np.array(dot_num_raw)
            return frequency_raw, amplitude_raw, dot_num
        else:
            pass

    def draw(self, n):
        try:
            # 重绘频谱图
            print(self.n)
            fre_raw, amp_raw, dot_num = self.get_spectrum_file(n)
            if self.bar:
                self.bar.remove()
            self.bar = 0
            self.axs.cla()
            for i in range(len(fre_raw)):

                # self.axs.scatter(fre_raw[i], amp_raw[i], c=dot_num[i], cmap=plt.cm.rainbow, marker='d', linewidths=0)
                # self.axs.figure.canvas.draw()
                # self.axs.figure.canvas.flush_events()
                heat = np.array(dot_num[i])
                points = np.array([fre_raw[i], amp_raw[i]]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                norm = matplotlib.colors.Normalize(heat.min(), heat.max())
                lc = LineCollection(segments, cmap='rainbow', norm=norm)
                lc.set_array(heat)

                # 设置线宽，若瀑布图放的太大线与线之间会出现空缺，若设置太大瀑布图所得比较小时会叠加宽度，可适当调节
                lc.set_linewidth(1)
                line = self.axs.add_collection(lc)
                self.axs.set_xlim(min(fre_raw[i]), max(fre_raw[i]))
                self.axs.set_ylim(min(amp_raw[i]), max(amp_raw[i]))

                if not self.bar:
                    self.bar = self.axs.figure.colorbar(line, ax=self.axs)

                self.axs.figure.canvas.draw()
                self.axs.figure.canvas.flush_events()
                self.axs.set_xlabel('频率/MHz', fontsize=14)
                self.axs.set_ylabel('功率/dBm', fontsize=14)



                # bar_label.set_label(u'频点出现频次')
                # plt.ylabel(u'功率幅度（dB）')

            print('successful draw')
            self.n += 1
            # print(self.n)
            self.id += 1
            # return self.plot_report
        except:
            pass


if __name__ == "__main__":
    # if (QT_VERSION >= QT_VERSION_CHECK(5, 6, 0))
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r'..\realtime_recv')
    app.show()
    qapp.exec_()
