import sys
from threading import Thread
import os
import sip
import queue
import zmq
from PyQt5.QtCore import Qt, QFileInfo, QTimer
from PyQt5.QtGui import QCursor, QIcon, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMessageBox, QTableWidgetItem, QFileDialog, QProgressDialog, \
    QApplication

from function import plotWithCursor
from Ui.UitoPy.Ui_socketDEMO import Ui_MainWindow
from function.numOrLetters import *
from socketDemo import zmqLocal

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
        py2 = py2Thread()
        py2.start()
        self.picQ = queue.Queue()
        self.specPicFlag = 0
        self.zmqLocal = zmqLocal.localZMQ()
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)  # 扫频
        # self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)  # 选择文件
        # self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)  # 查看频谱图
        #
        # self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 采集识别
        # self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # 选择文件
        # self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)  # 离线识别

    def on_pushButton_clicked_1(self):
        startfreq = self.lineEdit_1.text()
        endfreq = self.lineEdit_2.text()
        # freqFilePath = self.lineEdit_3.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 6000:
                startfreq = startfreq*1000000
                endfreq = endfreq*1000000
                reslt = self.zmqLocal.sendMessege('2,scan,IQ,' + str(startfreq) + ";" +str(endfreq))
                if reslt == "超时":
                    QMessageBox.warning(self,
                                        '错误',
                                        "本地连接超时！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                else:
                    specPath = reslt
                    # 根据地址绘图
                    print('specPath:', specPath)
                    #####置入绘图####
                    if self.specPicFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        # sip.delete(self.getPosition)
                        self.getPosition = plotWithCursor.getPos(specPath, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
                    else:
                        self.getPosition = plotWithCursor.getPos(specPath, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
            else:
                QMessageBox.warning(self,
                                    '错误',
                                    "请输入正确参数！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

class py2Thread(Thread):
    def __init__(self):
        super(py2Thread, self).__init__()
    def run(self):
        os.system('python2 ..\..\py27usrp\socketTest\demo.py')

app = QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())