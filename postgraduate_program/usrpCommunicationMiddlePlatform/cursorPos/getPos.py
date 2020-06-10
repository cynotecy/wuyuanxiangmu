# coding=UTF-8
import matplotlib
import numpy as np
from PyQt4.QtGui import QWidget
from matplotlib.backends.qt_compat import QtWidgets
from PyQt4 import QtCore
# matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import sys
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
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

    # def getData(self):
    #     x = range(1, 10)
    #     y = [2 * v for v in x]
    #     print x, y
    #     return x,y
    def draw(self):
        # x, y = self.getData()
        self.axs.cla()
        self.axs.plot(self.x, self.y)
        self.axs.figure.canvas.draw()
        self.axs.set_xlabel(_fromUtf8('频率/MHz'),fontsize=14)
        self.axs.set_ylabel(_fromUtf8('功率/dBM'),fontsize=14)

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
    import Queue
    q = Queue
    app = getPos(x,y,q)
    app.show()
    qapp.exec_()