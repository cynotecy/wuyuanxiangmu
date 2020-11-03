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
import time
import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
import threading
import logging
import matplotlib
import matplotlib.pyplot as plt
import collections
import math
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
import datetime
import queue
from communication import zmqLocal, circulationZmqThread
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

logging.getLogger('matplotlib.font_manager').disabled = True
#
# filename = r'D:\ProgramData\spectrum_analyze\spectrum_analyze.log',
# filemode = 'w',  # 模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志

class ApplicationWindow(QWidget):

    def __init__(self, saveflag, dirpath, condition, notifyNum, dataCash):
        super().__init__()
        self.saveflag = saveflag
        self.dirpath = dirpath
        self.condition = condition
        self.notifyNum = notifyNum
        self.dataCash = dataCash

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
        # self.start = QtWidgets.QPushButton('start')
        # self.stop = QtWidgets.QPushButton('stop')
        #
        # layout.addWidget(self.start)
        # layout.addWidget(self.stop)

        # self.start.clicked.connect(self._start)
        # self.stop.clicked.connect(self._stop)

        # 定时任务
        self.startFlag = 1
        self.bar = 0
        self._timer = self.freqCanvas.new_timer(1000, [(self._update_canvas, (), {})])
        # self.axs.figure.colorbar(line, ax=self.axs)# 设置colorbar，需要在init中初始化第一条line

    def _start(self):
        self._timer.start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw()

    # 获得频谱数据
    def get_spectrum_file(self):

        frequency_raw = []
        amplitude_raw = []
        frequency_int_raw = []
        amplitude_int_raw = []
        spectrum = []
        spectrum_file = []
        dot_num = 0
        try:
            if self.dataCash.qsize() >= 1:
                logging.debug("data cache is available")
                # self.startFlag = 0
                data_list = self.dataCash.get()
                file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
                path = os.path.join(self.dirpath, 'spectrum_' + file_name + '.txt')
                # saveflag为true时，将频谱数据存储到self.dirpath文件夹下，文件名格式为“spectrum_%Y-%m-%d-%H%M%S”
                # 数据格式为‘频率\n幅度\n’
                if self.saveflag:
                    with open(path, 'w+') as f:
                        for i in data_list:
                            data = ''.join(i).split(';', -1)
                            for j in data:
                                f.write(''.join(j))
                                f.write('\n')
                    f = open(path, "rb+")
                    f.seek(-1, os.SEEK_END)
                    if f.__next__() == bytes('\n', encoding="utf8"):
                        f.seek(-2, os.SEEK_END)
                        f.truncate()
                    f.close()
                    logging.debug("save file in: "+path)
                # 将list格式从[['900 910 920;-100 -99 -98']]转为[['900','910','920';'-100','-99','-98']]
                # 将str转为float和int
                for i in data_list:
                    data = ''.join(i).split(';', -1)
                    d = [i.split(' ', -1) for i in data]
                    fre_list = list(map(float, d[0]))
                    amp_list = list(map(float, d[1]))
                    frequency_raw.append(fre_list)
                    amplitude_raw.append(amp_list)

                for i in frequency_raw:
                    fre_list = list(map(int, i))
                    frequency_int_raw.append(fre_list)
                for i in amplitude_raw:
                    amp_list = list(map(int, i))
                    amplitude_int_raw.append(amp_list)

                # 将txt中的频点和幅值的整数部分分别存储为1*N维数组，作为判别值
                frequency_int = np.array(frequency_int_raw).flatten()
                amplitude_int = np.array(amplitude_int_raw).flatten()

                frequency_int = frequency_int.astype(np.int)
                amplitude_int = (amplitude_int / 5).astype(np.int) * 5
                flag = max(amplitude_int)
                # 将频点和幅值数组合并，维数为N*2
                array_num_int = np.column_stack((frequency_int, amplitude_int))
                # 将频点和幅值存成坐标，放到列表中

                for i in array_num_int:
                    if i[1] > flag - 50:
                        spectrum.append(tuple(i))
                    else:
                        pass

                # 统计频次，coordinate存放坐标，dot_count存放频次
                spectrum_dict = collections.Counter(spectrum)
                coordinate_standard = list(spectrum_dict.keys())
                dot_count_standard = list(spectrum_dict.values())
                probability_standard = []
                for i in dot_count_standard:
                    probability_standard.append(math.log(i))

                # 创建坐标对应频次的字典
                # spectrum_probability_dict = dict(zip(coordinate_standard, dot_count_standard))
                spectrum_probability_dict = dict(zip(coordinate_standard, probability_standard))
                frequency = np.array(frequency_raw)
                amplitude = np.array(amplitude_raw)

                dot_num_raw = []
                for i in range(frequency.shape[0]):
                    frequency[i] = frequency[i].astype(np.int)
                    amplitude[i] = (amplitude[i] / 5).astype(np.int) * 5
                    array_num = np.column_stack((frequency[i], amplitude[i]))
                    num_each_rows = []
                    for j in array_num:
                        if j[1] > flag - 50:
                            # j = tuple(j.astype(np.int))
                            j = tuple(j)
                            num_each_rows.append(spectrum_probability_dict.get(j))
                        else:
                            num_each_rows.append(0)
                        array_num_each_rows = num_each_rows
                    array_num_each_rows = np.array(array_num_each_rows)
                    dot_num_raw.append(array_num_each_rows)
                dot_num = np.array(dot_num_raw)
            # elif self.startFlag != 1:
            #     print("startFlag != 1")
            #     self.condition.acquire()
            #     self.condition.notify()
            #     self.condition.release()
            else:
                logging.debug("data cache isnt full")
        except Exception as e:
            logging.error(e)
        return frequency_raw, amplitude_raw, dot_num


    def draw(self):
        # try:
            # 重绘频谱图
        # print(self.n)
        fre_raw, amp_raw, dot_num = self.get_spectrum_file()
        if (fre_raw == []) or (amp_raw == []):
            logging.debug("等待数据")
            return 0
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
            self.axs.set_xlabel('频率/MHz')
            self.axs.set_ylabel('功率/dBm')
            time.sleep(1)

        logging.debug('successful draw')



if __name__ == "__main__":

    connection = zmqLocal.localZMQ(address="tcp://10.128.216.125:5678")
    startfreq = 900 * 1000000
    endfreq = 950 * 1000000
    usrpNum = "USRP1"
    msg = (usrpNum + ',scan,IQ,' + str(startfreq) + ";" + str(endfreq))
    dataCach = queue.Queue()
    condition = threading.Condition()
    waitNum = sys.maxsize
    circultaionZmqThread = circulationZmqThread.CircultaionZmqThread(connection, "", msg, dataCach,
                                                                     condition, waitNum, dataNumPerCell=10)
    circultaionZmqThread.start()
    saveflag = True
    dirpath = r'D:\ProgramData\testname'

    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(saveflag,  dirpath, condition, 1, dataCach)
    app.show()
    qapp.exec_()
