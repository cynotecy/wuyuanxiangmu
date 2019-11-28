# coding=UTF-8
import matplotlib
import numpy as np
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import sys

class getPos(QWidget):
    def __init__(self, x, y, q, parent=None):
        super(getPos, self).__init__(parent)
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.x = x
        self.y = y
        self.q = q
        layout = QtWidgets.QVBoxLayout(self)  # 实例化布局，用来塞画布
        self.freqCanvas = FigureCanvas(Figure(figsize=(12, 6)))  # 实例化画布
        self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.on_key_press)  # 事件绑定至响应函数

        self.toolbar = NavigationToolbar(self.freqCanvas, self)  # 添加工具栏
        layout.addWidget(self.toolbar)  # 布局塞入工具栏
        layout.addWidget(self.freqCanvas)  # 布局塞入画布

        self.axs = self.freqCanvas.figure.add_subplot(111)  # 从画布中实例化axs
        self.cursor = Cursor(self.axs, useblit=True, color='red', linewidth=2)  # 实例化游标

        self.draw()

    def getData(self):
        print(self.path)
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
        y = np.array([float(y) for y in y])
        return x, y

    def draw(self):
        # x, y = self.getData()
        x = self.x
        y = self.y
        self.axs.cla()
        self.axs.plot(x, y)
        self.axs.figure.canvas.draw()
        self.axs.set_xlabel('频率/MHz', fontsize=14)
        self.axs.set_ylabel('功率/dBM', fontsize=14)

    # 定义响应函数
    def on_key_press(self, event):
        pos = event.ydata
        if not self.q.empty():
            self.q.get()
            self.q.put(pos)
        else:
            self.q.put(pos)
        print('print in on_key_press:' + str(pos))
        # print(event.key)




if __name__ == '__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    x = range(300)
    y = range(300)
    import queue
    q = queue.Queue()
    path = r"..\..\usrp_recvfiles\specfiles\20191126155337.dat"
    app = getPos(path, q)
    app.show()
    qapp.exec_()