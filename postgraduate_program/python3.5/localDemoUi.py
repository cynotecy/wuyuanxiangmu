import sys
from threading import Thread
import datetime
import os
import sip
import queue
import threading
import zmq
from PyQt5.QtCore import Qt, QFileInfo, QTimer
from PyQt5.QtGui import QCursor, QIcon, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMessageBox, QTableWidgetItem, QFileDialog, QProgressDialog, \
    QApplication

import Message
from function import plotWithCursor
from Ui.UitoPy.Ui_socketDEMO import Ui_MainWindow
from controller.usrp_controller.usrp_shibie import (oc_list_getting_v2, oc_list_display_v1,
                                                    usrp_shibie_v3)
from function.numOrLetters import *
from socketDemo import zmqLocal

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
        py2 = py2Thread()
        py2.start()


        self.currentPath = os.path.dirname(__file__)
        self.fatherPath = os.path.dirname(self.currentPath)
        # self.specPicQ = queue.Queue()
        self.overThresholdQ = queue.Queue()
        self.ocCollectPathQ = queue.Queue()
        self.ocLoadingQ = queue.Queue()
        # 绘图布局标志位，为0表示布局中没有绘图，为1表示布局中有在线扫频图，为2表示布局中有离线频谱图
        self.specPicFlag = 0
        self.ocTableDisplayFlag = 0

        self.zmqLocal = zmqLocal.localZMQ()
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)  # 扫频
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)  # 选择文件
        self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)  # 查看频谱图
        self.pushButton_8.clicked.connect(self.on_pushButton_clicked_8)  # 超频点查看
        self.pushButton_7.clicked.connect(self.on_pushButton_clicked_7)  # IQ自动识别
        #
        self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 采集识别
        # self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # 选择文件
        # self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)  # 离线识别


    def on_pushButton_clicked_2(self):

        defultPath = os.path.join(self.fatherPath, 'usrp_recvfiles', 'usrp_scan')
        print(defultPath)

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
                reslt = self.zmqLocal.sendMessege(usrpNum + ',scan,IQ,'
                                                  + str(startfreq) + ";" +str(endfreq))
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
                    self.onlineSpecX = [float(i) for i in resltList[0:int(len(resltList)/2-1)]]
                    # print(len(x))
                    self.onlineSpecY = [float(i) for i in resltList[int(len(resltList)/2):-1]]
                    # print(len(y))
                    #####置入绘图####
                    if self.specPicFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        # sip.delete(self.getPosition)
                        self.getPosition = plotWithCursor.getPos(self.onlineSpecX,
                                                                 self.onlineSpecY,
                                                                 self.lineEdit_6)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
                    else:
                        self.getPosition = plotWithCursor.getPos(self.onlineSpecX,
                                                                 self.onlineSpecY,
                                                                 self.lineEdit_6)
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
        defultPath = os.path.join(self.fatherPath, r'usrp_recvfiles\usrp_scan')
        # print(defultPath)
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.dat")
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
                    else:
                        self.getPosition = plotWithCursor.getPos(path)
                        self.verticalLayout.addWidget(self.getPosition)
                    self.specPicFlag = 2
                    del self.onlineSpecX
                    del self.onlineSpecY
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

    # 超频点查看
    def on_pushButton_clicked_8(self):
        if self.specPicFlag == 2:
            QMessageBox.warning(self,
                                '提示',
                                "无法查看离线频谱图的超频点！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        elif self.specPicFlag == 0:
            QMessageBox.warning(self,
                                '提示',
                                "请先扫频！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        elif not self.lineEdit_6.text():
            QMessageBox.warning(self,
                                '提示',
                                "请先单击频谱图选定门限，或手动输入门限！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        elif self.specPicFlag == 1:
            try:
                threshold = float(self.lineEdit_6.text())
            except:
                QMessageBox.warning(self,
                                    '提示',
                                    "门限值应为数字！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
            else:
                if threshold > min(self.onlineSpecY) and threshold < max(self.onlineSpecY):
                    overThresholdThread = threading.Thread(target=self.IQOverThreshold,
                                                           name="超频点判断线程", args=(threshold, ))
                    overThresholdThread.start()
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QApplication.processEvents
                    while self.overThresholdQ.empty():
                        gui()
                    else:
                        self.overThresholdQ.get()
                        loading.close()
                        if self.ocOverThresholdList:
                            # 置入超频点列表
                            if self.ocTableDisplayFlag:
                                self.verticalLayout_4.removeWidget(self.ocTableDisplay)
                                # sip.delete(self.ocTableDisplay)
                                self.ocTableDisplay = oc_list_display_v1.WindowClass()
                                self.ocTableDisplay.pushButton(self.ocOverThresholdList)
                                self.verticalLayout_4.addWidget(self.ocTableDisplay)
                                self.ocTableDisplayFlag = 1
                            else:
                                self.ocTableDisplay = oc_list_display_v1.WindowClass()
                                self.ocTableDisplay.pushButton(self.ocOverThresholdList)
                                self.verticalLayout_4.addWidget(self.ocTableDisplay)
                                self.ocTableDisplayFlag = 1
                        else:
                            QMessageBox.warning(self, "结果：", "门限位置无信号")
                else:
                    QMessageBox.warning(self,
                                        '提示',
                                        "门限超限，请选定正确的门限值！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)

    def IQOverThreshold(self, thre):
        self.ocOverThresholdList = oc_list_getting_v2.position(self.onlineSpecX, self.onlineSpecY,
                                                   thre, self.overThresholdQ)

    # IQ自动识别
    def on_pushButton_clicked_7(self):
        if self.ocTableDisplayFlag:
            # 获取行号
            starttime = datetime.datetime.now()
            self.ocRowNumSelectList = self.ocTableDisplay.getRow()
            print('用户选中的行为:', self.ocRowNumSelectList)
            if self.ocRowNumSelectList:
                self.ocLoadingQ.queue.clear()
                collectThread = threading.Thread(target=self.ocCollectThread, name='自动识别采集线程')
                recognizeThread = threading.Thread(target=self.ocRecognizeThread, name='自动识别识别线程')
                collectThread.start()
                recognizeThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.ocLoadingQ.empty():
                    gui()
                else:
                    loading.close()
                    for row in self.ocRsltDict:
                        rowName = int(row)
                        item1 = QTableWidgetItem(self.ocRsltDict[rowName][2])  # 调制方式
                        item2 = QTableWidgetItem(self.ocRsltDict[rowName][3])  # 频点识别
                        self.ocTableDisplay.tableWidget.setItem(rowName, 3, item1)
                        self.ocTableDisplay.tableWidget.setItem(rowName, 4, item2)
                    endtime = datetime.datetime.now()
                    strTime = "本次识别耗时：%sms" % ((endtime - starttime).seconds * 1000
                                             + (endtime - starttime).microseconds / 1000)
                    print(strTime)
            else:
                QMessageBox.warning(self,
                                    '提示',
                                    "请先选中超频点！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先查看超频点列表！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        pass

    def ocCollectThread(self):
        """
        IQ自动识别线程1，根据表格选中行生成采集参数list，并依次发送lsit中的采集指令
        :return:无返回值，将IQ文件的存储路径存入FIFO队列ocCollectPathQ
        """
        # if self.ocTableDisplayFlag:
        #     # 获取行号
        #     self.ocRowNumSelectList = self.ocTableDisplay.getRow()
        #     print('用户选中的行为:', self.ocRowNumSelectList)
        # 创建行号-IQ识别结果字典
        self.ocRsltDict = dict.fromkeys(self.ocRowNumSelectList, 'null')
        for i in self.ocRsltDict:
            startFreq = float(self.ocOverThresholdList[0][i][0])*1000000
            endFreq = float(self.ocOverThresholdList[0][i][1])*1000000
            centreFreq = float(self.ocOverThresholdList[0][i][2])*1000000
            bdWidth = endFreq - startFreq

            usrpNum = self.comboBox_2.currentText()
            msg = usrpNum + ',collect,IQoc,' + str(centreFreq) + ";" + str(bdWidth)
            reslt = self.zmqLocal.sendMessege(msg)

            if reslt == "超时":
                QMessageBox.warning(self,
                                    '错误',
                                    "本地连接超时！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
            else:
                self.ocCollectPathQ.put(reslt)

    def ocRecognizeThread(self):
        """
        自动识别线程，共识别len(self.ocRowNumSelectList)次，从self.ocCollectPathQ队列中取文件地址并识别
        将识别结果存在dic中
        :return:
        """
        for num in self.ocRsltDict:
            while 1:
                if self.ocCollectPathQ.empty():
                    continue
                else:
                    path = self.ocCollectPathQ.get()
                    recognizeResult = usrp_shibie_v3.play(path)
                    self.ocRsltDict[int(num)] = recognizeResult
                    break
        self.ocLoadingQ.put('ok')

    # 重写关闭事件
    def closeEvent(self, event):
        os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
        sys.exit()


class py2Thread(Thread):
    def __init__(self):
        super(py2Thread, self).__init__()
        self.currentPath = os.path.dirname(__file__)
        self.fatherPath = os.path.dirname(self.currentPath)
    def run(self):
        scriptPath = os.path.join(self.fatherPath, r'py27usrp/socketTest/demo.py')
        os.system('python2 {}'.format(scriptPath))

app = QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())