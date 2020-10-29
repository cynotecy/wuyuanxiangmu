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

import matplotlib
import pandas as pd
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtWidgets

from plotTools.pico_specComponent import dataCorrection_v2

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class ApplicationWindow(QWidget):
    def __init__(self, fatherpath):
        super().__init__()
        self.setWindowTitle("现场电磁干扰特征库系统-20Hz~30MHz频谱查看")
        self.fatherpath = fatherpath

        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        fileLayout = QtWidgets.QHBoxLayout(self)
        self.selectFileButton = QtWidgets.QPushButton(u'选择文件')
        self.drawButton = QtWidgets.QPushButton(u'查看频谱图')
        self.fileEditLine = QtWidgets.QLineEdit()
        fileLayout.addWidget(self.selectFileButton)
        fileLayout.addWidget(self.fileEditLine)
        fileLayout.addWidget(self.drawButton)
        layout.addLayout(fileLayout)
        self.selectFileButton.clicked.connect(self.selectFile)

        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(1, 1)
        self.drawButton.clicked.connect(self.draw)

    def _update_canvas(self):
        self.draw()

    # 选择文件
    def selectFile(self):
        self.fileEditLine.clear()
        # defultPath = os.path.join(self.fatherPath, r'usrp_recvfiles\interface_cancellation')
        defaultPath = os.path.join(self.fatherpath, "pico-waterfall-data-origin")
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", defaultPath,
                                                  filter="*.csv")
        # self.logger.info("20Hz~30MHz频谱查看选择文件："+filename)
        self.fileEditLine.setText(filename)

    def getData(self):
        # 获取文件建议使用数据库id获取，方便重绘频谱图
        self.path = self.fileEditLine.text()
        if not os.path.exists(self.path):
            raise Exception
        # file = open(path)
        data = pd.read_csv(self.path, skiprows=5)
        x = data.values[15:-3, 0]
        y = list(data.values[15:-3, 1])
        x, y = dataCorrection_v2.correct(x, y)
        return x, y

    def draw(self):
        # 重绘频谱图
        try:
            x, y = self.getData()
        except Exception:
            QMessageBox.warning(self, "错误", "路径不存在，请重新选择文件！")
            return 0
        # print('successful getdata')
        # x = range(len(y))
        self.axs.cla()
        self.axs.plot(x, y)

        self.axs.set_xlabel('频率/MHz',fontsize=14)
        self.axs.set_ylabel('功率/dBm',fontsize=14)
        self.axs.figure.canvas.draw()
        print('successful draw')
        # return line


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    fatherPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    app = ApplicationWindow(fatherPath)
    app.show()
    qapp.exec_()
