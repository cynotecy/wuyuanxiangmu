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

import matplotlib
import numpy as np
import pymysql
import os
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class ApplicationWindow(QWidget):
    def __init__(self,mode):
        super().__init__()
        self.mode = mode
        self.path = r'..\antenna_recv'
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(1, 1)
        self.draw()

    # def _update_canvas(self):
    #     self.draw()

    def getData(self, pos1, pos2):
        lists = os.listdir(self.path)
        txt_list = []
        for path in lists:
            if '.txt' in path:
                txt_list.append(path)
        if txt_list:
            print(txt_list)
            # 获取pos(n)位置的文件并切分文件名
            # 文件名格式为"mode(n)_usrp(n)_localtime_RF(n).txt"
            txt_list.sort(key=lambda fn: os.path.getmtime(self.path + "\\" + fn))
            file_1 = os.path.join(self.path, txt_list[pos1])#RF2
            fileName_1 = txt_list[pos1].split('_')
            fileName_1[-1] = fileName_1[-1].replace('.txt', '')
            file_2 = os.path.join(self.path, txt_list[pos2])#RF1
            fileName_2 = txt_list[pos2].split('_')
            fileName_2[-1] = fileName_2[-1].replace('.txt', '')
            # 至此fileName_1/2均为['mode(n)','usrp(n)','localtime','RF(n)']的格式


            # self.file_1 = os.path.join(self.path, txt_list[-2])#RF2
            # self.file_2 = os.path.join(self.path, txt_list[-1])#RF1


            file1 = open(file_1)
            xy1 = file1.read().split("\n")
            x = xy1[0].split(' ')
            y1 = xy1[1].split(' ')
            x.pop(len(x)-1)
            y1.pop(len(y1) - 1)
            print(x[0:5])
            # print(y)
            print(y1[0:5])
            x = np.array([float(x) for x in x])
            y1 = np.array([float(y1)-11 for y1 in y1])

            file2 = open(file_2)
            xy2 = file2.read().split("\n")
            y2 = xy2[1].split(' ')
            y2.pop(len(y2) - 1)
            # print(y)
            print(y2[0:5])
            y2 = np.array([float(y2)-11 for y2 in y2])
            return x, y1, y2, fileName_1[1], fileName_1[3], fileName_2[1], fileName_2[3]

    def draw(self):
        try:
        # 绘频谱图
            if self.mode == 1:
                x, y1, y2, usrpName1, RFName1, usrpName2, RFName2 = self.getData(-2, -1)
                print('successful getdata')

                self.axs.cla()
                self.axs.plot(x, y1, label = usrpName1+'_'+RFName1, color='red')
                self.axs.plot(x, y2, label = usrpName2+'_'+RFName2, color='black')
                self.axs.legend(loc='upper left')
                self.axs.set_title('天线效果对比图',fontsize=16)
                self.axs.set_xlabel('频率/MHz',fontsize=14)
                self.axs.set_ylabel('功率/dBm',fontsize=14)
                self.axs.figure.canvas.draw()
                self.axs.figure.canvas.flush_events()
                print('successful draw 2 lines')
            elif self.mode == 2:
                x, y1, y2, usrpName1, RFName1, usrpName2, RFName2 = self.getData(-2, -1)
                x, y3, y4, usrpName3, RFName3, usrpName4, RFName4 = self.getData(-4, -3)

                print('successful getdata')

                self.axs.cla()
                self.axs.plot(x, y1, label = usrpName1+'_'+RFName1, color='red')
                self.axs.plot(x, y2, label = usrpName2+'_'+RFName2, color='black')
                self.axs.plot(x, y3, label = usrpName3+'_'+RFName3, color='blue')
                self.axs.plot(x, y4, label = usrpName4+'_'+RFName4, color='orange')
                self.axs.legend(loc='upper left')
                self.axs.set_title('天线效果对比图', fontsize=16)
                self.axs.set_xlabel('频率/MHz', fontsize=14)
                self.axs.set_ylabel('功率/dBm', fontsize=14)
                self.axs.figure.canvas.draw()
                self.axs.figure.canvas.flush_events()
                print('successful draw 4 lines')
        except:
            print("error")



if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(2)
    app.show()
    qapp.exec_()
