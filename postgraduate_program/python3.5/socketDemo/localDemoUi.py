import sys
from threading import Thread
import datetime
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
        # 绘图布局标志位，为0表示布局中没有绘图，为1表示布局中有在线扫频图，为2表示布局中有离线频谱图
        self.specPicFlag = 0
        self.zmqLocal = zmqLocal.localZMQ()
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)  # 扫频
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)  # 选择文件
        self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)  # 查看频谱图
        self.pushButton_7.clicked.connect(self.on_pushButton_clicked_7)  # IQ自动识别
        #
        # self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 采集识别
        # self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # 选择文件
        # self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)  # 离线识别

    # 鼠标监听线程，用来监听扫频图区有没有鼠标点击
    def mouseListening(self):
        while 1:
            if not self.picQ.empty() and self.specPicFlag == 1:
                self.lineEdit_6.setText(str(self.picQ.get()))

    # 扫频按键
    def on_pushButton_clicked_1(self):
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_1.text()
        endfreq = self.lineEdit_2.text()
        # freqFilePath = self.lineEdit_3.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 6000:
                startfreq = startfreq*1000000
                endfreq = endfreq*1000000
                usrpNum = self.comboBox_2.currentText()
                reslt = self.zmqLocal.sendMessege(usrpNum + ',scan,IQ,' + str(startfreq) + ";" +str(endfreq))
                if reslt == "超时":
                    QMessageBox.warning(self,
                                        '错误',
                                        "本地连接超时！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                else:
                    # specPath = reslt

                    # 根据地址绘图
                    # print('specPath:', specPath)
                    # 根据数值绘图
                    resltList = reslt.split(' ')
                    # print(len(resltList))
                    x = [float(i) for i in resltList[0:int(len(resltList)/2-1)]]
                    # print(len(x))
                    y = [float(i) for i in resltList[int(len(resltList)/2):-1]]
                    # print(len(y))
                    #####置入绘图####
                    if self.specPicFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        # sip.delete(self.getPosition)
                        self.getPosition = plotWithCursor.getPos(x, y, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
                    else:
                        self.getPosition = plotWithCursor.getPos(x, y, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
                    endtime = datetime.datetime.now()
                    strTime = 'funtion time use:%dms' % (
                            (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                    print(strTime)
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

    # 选择文件&查看频谱图按键
    def on_pushButton_clicked_5(self):
        self.lineEdit_3.clear()
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\..\usrp_recvfiles\usrp_scan", "*.dat")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print("IQ频谱图查看选择文件：", filename)
        self.lineEdit_3.setText(self.path)

    def on_pushButton_clicked_6(self):
        if self.lineEdit_3.text():
            path = self.lineEdit_3.text()
            if os.path.exists(path):
                try:
                    #####置入绘图####
                    if self.specPicFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        self.getPosition = plotWithCursor.getPos(path)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 2
                    else:
                        self.getPosition = plotWithCursor.getPos(path)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 2
                except:
                    QMessageBox.warning(self,
                                        '错误',
                                        "绘图失败，请检查文件格式。",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)

            else:
                QMessageBox.warning(self,
                                    '提示',
                                    "文件不存在！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # IQ自动识别
    def on_pushButton_clicked_7(self):


class py2Thread(Thread):
    def __init__(self):
        super(py2Thread, self).__init__()
    def run(self):
        os.system('python2 ..\..\py27usrp\socketTest\demo.py')

app = QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())