import sys
from threading import Thread
from multiprocessing import Process
import datetime
import os
import time
import sip
import queue
from multiprocessing import Process, Queue as mq
import threading
import zmq
from PyQt5.QtCore import Qt, QFileInfo, QTimer
from PyQt5.QtGui import QCursor, QIcon, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMessageBox, QTableWidgetItem, QFileDialog, QProgressDialog, \
    QApplication

import Message
from function import plotWithCursor, filesOrDirsOperate
from Ui.UitoPy.Ui_socketDEMO import Ui_MainWindow
from controller.usrp_controller.usrp_shibie import (oc_list_getting_v2, oc_list_display_v1,
                                                    usrp_shibie_v3)
from controller.usrp_controller.specEnvelope_shibie import specEnvelopeDrawpic
from function.numOrLetters import *
from socketDemo import zmqLocal
import algorithmThreads

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
        py2 = py2Thread()
        py2.start()

        # 初始化当前路径和其父路径，用于拼接后续地址进行非文件夹依赖的寻址
        self.currentPath = os.path.dirname(__file__)
        self.fatherPath = os.path.dirname(self.currentPath)
        # 初始化队列
        self.zmqLocalQ = mq()
        self.algorithmProcessQ = mq()  # 算法线程队列，用来判断算法线程是否结束
        self.savingProcessQ = mq()  # 算法线程队列，用来判断算法线程是否结束
        self.overThresholdQ = mq()
        self.ocCollectPathQ = mq()
        self.ocLoadingQ = mq()
        # 绘图布局标志位，为0表示布局中没有绘图，为1表示布局中有在线扫频图，为2表示布局中有离线频谱图
        self.specPicFlag = 0
        self.ocTableDisplayFlag = 0
        self.specEnvelopeFlag = 0# 包络图标志位

        self.zmqLocal = zmqLocal.localZMQ()
        # 第一页，IQ识别
        ## 自动识别
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)  # 扫频
        self.pushButton_9.clicked.connect(self.on_pushButton_clicked_9)  # 保存频谱
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)  # 频谱选择文件
        self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)  # 查看频谱图
        self.pushButton_8.clicked.connect(self.on_pushButton_clicked_8)  # 超频点查看
        self.pushButton_7.clicked.connect(self.on_pushButton_clicked_7)  # IQ自动识别
        ## 手动识别
        self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 采集识别
        self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # IQ选择文件
        self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)  # 离线识别

        #第二页，频谱包络识别
        self.pushButton_12.clicked.connect(self.on_pushButton_clicked_12)  # 开始识别
        self.pushButton_10.clicked.connect(self.on_pushButton_clicked_10)  # 选择文件
        self.pushButton_11.clicked.connect(self.on_pushButton_clicked_11)  # 离线识别

    # 扫频按键
    def on_pushButton_clicked_1(self):
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_1.text()
        endfreq = self.lineEdit_2.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 6000:
                startfreq = startfreq*1000000
                endfreq = endfreq*1000000
                usrpNum = self.comboBox_2.currentText()
                msg = (usrpNum + ',scan,IQ,'
                          + str(startfreq) + ";" +str(endfreq))
                zmqThread = threading.Thread(target=zmqLocal.zmqThread, args=(self.zmqLocal, msg, self.zmqLocalQ))
                zmqThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                # while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    loading.close()
                    reslt = self.zmqLocalQ.get()
                    if reslt == "超时":
                        QMessageBox.warning(self,
                                            '错误',
                                            "本地连接超时！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                    else:
                        resltList = reslt.split(' ')
                        self.onlineSpecX = [float(i) for i in resltList[0:int(len(resltList)/2-1)]]
                        self.onlineSpecY = [float(i) for i in resltList[int(len(resltList)/2):-1]]
                        #####置入绘图####
                        if self.specPicFlag:
                            self.verticalLayout.removeWidget(self.getPosition)
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

    # 保存频谱
    def on_pushButton_clicked_9(self):
        if self.specPicFlag == 1:
            dirPath = os.path.join(self.fatherPath, r'usrp_recvfiles\usrp_scan')
            filesOrDirsOperate.makesureDirExist(dirPath)
            localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            filePath = os.path.join(dirPath, r'scan_spectrum_{}.txt'.format(localTime))
            freqList = list(map(str, self.onlineSpecX))
            binsList = list(map(str, self.onlineSpecY))
            freqStr = " ".join(freqList)
            binsStr = " ".join(binsList)
            with open(filePath, 'w') as f:
                f.write(freqStr)
                f.write('\n')
                f.write(binsStr)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先扫频！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 频谱选择文件
    def on_pushButton_clicked_5(self):
        self.lineEdit_3.clear()
        defultPath = os.path.join(self.fatherPath, r'usrp_recvfiles\usrp_scan')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print("IQ频谱图查看选择文件：", filename)
        self.lineEdit_3.setText(self.path)

    # 查看频谱图
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
                    # 启用超频点判断线程
                    overThresholdThread = algorithmThreads.IQOverThreshold(self.onlineSpecX,
                                                                         self.onlineSpecY, threshold,
                                                                         self.overThresholdQ)
                    overThresholdThread.start()
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QApplication.processEvents
                    while self.overThresholdQ.empty():
                        gui()
                    else:
                        self.ocOverThresholdList = self.overThresholdQ.get()
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

    # IQ自动识别
    def on_pushButton_clicked_7(self):
        if self.ocTableDisplayFlag:
            # 获取行号
            starttime = datetime.datetime.now()
            self.ocRowNumSelectList = self.ocTableDisplay.getRow()
            print('用户选中的行为:', self.ocRowNumSelectList)
            if self.ocRowNumSelectList:
                while not self.ocLoadingQ.empty():
                    self.ocLoadingQ.get()
                usrpNum = self.comboBox_2.currentText()
                # 创建行号-IQ识别结果字典
                self.ocRsltDict = dict.fromkeys(self.ocRowNumSelectList, 'null')
                collectThread = algorithmThreads.OcCollectThread(usrpNum,self.ocRsltDict,
                                              self.ocOverThresholdList, self.zmqLocal, self.ocCollectPathQ)
                recognizeThread = algorithmThreads.OcRecognizeThread(self.ocRsltDict,
                                                                     self.ocCollectPathQ, self.ocLoadingQ)
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
                    self.ocRsltDict = self.ocLoadingQ.get()
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

    # IQ手动识别（并行）
    def on_pushButton_clicked_2(self):
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        starttime = datetime.datetime.now()
        centrefreq = self.lineEdit_4.text()
        bdwidth = self.lineEdit_5.text()
        samprate = self.lineEdit_8.text()
        if isNum(centrefreq) and isNum(bdwidth) and isNum(samprate):
            centrefreq = float(centrefreq)
            bdwidth = float(bdwidth)
            samprate = float(samprate)
            if centrefreq <= 5000 and centrefreq >= 30:
                centrefreq = centrefreq * 1000000
                bdwidth = bdwidth * 1000000
                samprate = samprate * 1000000
                usrpNum = self.comboBox_3.currentText()
                msg = (usrpNum + ',collect,IQsingle,'+ str(centrefreq) + ";" + str(bdwidth)
                      + ";" + str(samprate))
                zmqThread = threading.Thread(target=zmqLocal.zmqThread,args=(self.zmqLocal, msg, self.zmqLocalQ))
                zmqThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    reslt = self.zmqLocalQ.get()
                    if reslt == "超时":
                        loading.close()
                        QMessageBox.warning(self,
                                            '错误',
                                            "本地连接超时！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                    else:
                        print('data type=', str(type(reslt)))
                        while not self.algorithmProcessQ.empty():
                            self.algorithmProcessQ.get()
                        while not self.savingProcessQ.empty():
                            self.savingProcessQ.get()
                        # 开启识别进程/线程
                        recognizeProcess = algorithmThreads.IQSingleProcess(reslt, self.algorithmProcessQ)
                        recognizeProcess.start()
                        # 开启存储进程/线程
                        savingProcess = algorithmThreads.IQDataSaveProcess(reslt, self.savingProcessQ)
                        savingProcess.start()
                        while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
                            pass
                        else:
                            loading.close()
                            dataPath = self.savingProcessQ.get()
                            print("IQ数据存储于：", dataPath)
                            recognizeResult = self.algorithmProcessQ.get()
                            item1 = QTableWidgetItem("%.1f" % float(recognizeResult[0]))  # 中心频率
                            item2 = QTableWidgetItem("%.1f" % float(recognizeResult[1]))  # 带宽
                            item3 = QTableWidgetItem(recognizeResult[2])  # 调制方式
                            item4 = QTableWidgetItem(recognizeResult[3])  # 频点识别
                            self.tableWidget_3.setItem(0, 1, item1)
                            self.tableWidget_3.setItem(0, 2, item2)
                            self.tableWidget_3.setItem(0, 3, item3)
                            self.tableWidget_3.setItem(0, 4, item4)
                            endtime = datetime.datetime.now()
                            strTime = '并行识别花费:%dms' % (
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

    # IQ选择文件
    def on_pushButton_clicked_3(self):
        self.lineEdit_7.clear()
        defultPath = os.path.join(self.fatherPath, r'usrp_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print("IQ频谱图查看选择文件：", filename)
        self.lineEdit_7.setText(self.path)

    # IQ手动离线识别
    def on_pushButton_clicked_4(self):
        starttime = datetime.datetime.now()
        if self.lineEdit_7.text():
            filePath = self.lineEdit_7.text()
            recognizeProcess = algorithmThreads.IQSingleProcess(filePath, self.algorithmProcessQ)
            recognizeProcess.start()
            # 调用识别loading
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.algorithmProcessQ.empty():
                gui()
            else:
                loading.close()
                recognizeResult = self.algorithmProcessQ.get()
                item1 = QTableWidgetItem("%.1f" % float(recognizeResult[0]))  # 中心频率
                item2 = QTableWidgetItem("%.1f" % float(recognizeResult[1]))  # 带宽
                item3 = QTableWidgetItem(recognizeResult[2])  # 调制方式
                item4 = QTableWidgetItem(recognizeResult[3])  # 频点识别
                self.tableWidget_3.setItem(0, 1, item1)
                self.tableWidget_3.setItem(0, 2, item2)
                self.tableWidget_3.setItem(0, 3, item3)
                self.tableWidget_3.setItem(0, 4, item4)
                endtime = datetime.datetime.now()
                strTime = 'funtion time use:%dms' % (
                        (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                print(strTime)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 频谱包络在线识别
    def on_pushButton_clicked_12(self):
        self.tableWidget_7.clearContents()
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_10.text()
        endfreq = self.lineEdit_11.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if (startfreq < endfreq and startfreq >= 30
                    and endfreq <= 6000 and (endfreq - startfreq) <= 150):
                startfreq = startfreq * 1000000
                endfreq = endfreq * 1000000
                usrpNum = self.comboBox_4.currentText()
                msg = (usrpNum + ',scan,specEnvelope,'
                       + str(startfreq) + ";" + str(endfreq))
                zmqThread = threading.Thread(target=zmqLocal.zmqThread, args=(self.zmqLocal, msg, self.zmqLocalQ))
                zmqThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    reslt = self.zmqLocalQ.get()
                    if reslt == "超时":
                        QMessageBox.warning(self,
                                            '错误',
                                            "本地连接超时！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                    else:
                        while not self.algorithmProcessQ.empty():
                            self.algorithmProcessQ.get()
                        while not self.savingProcessQ.empty():
                            self.savingProcessQ.get()
                        # 开启识别进程/线程
                        recognizeProcess = algorithmThreads.IQSingleProcess(reslt, self.algorithmProcessQ)
                        recognizeProcess.start()
                        # 开启存储进程/线程
                        savingProcess = algorithmThreads.specEnvelopeDataSaveProcess(reslt, self.savingProcessQ)
                        savingProcess.start()
                        while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
                            pass
                        else:
                            loading.close()
                            dataPath = self.savingProcessQ.get()
                            print("频谱包络数据存储于：", dataPath)
                            recognizeResult = self.algorithmProcessQ.get()
                            ########################################################
                        if len(recognizeResult) == 1:
                            # print(recognizeResult)
                            # print(type(recognizeResult))
                            newItem1 = QTableWidgetItem(str(recognizeResult[0]))
                            self.tableWidget_7.setItem(0, 1, newItem1)
                            # 识别不出结果或超限时，且图区有图，则清空图区
                            if self.specEnvelopeFlag:
                                self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                                # sip.delete(self.specEnvelopeSampleFig)
                                self.specEnvelopeFlag = 0
                        elif len(recognizeResult) == 6:
                            newItem1 = QTableWidgetItem(recognizeResult[0])
                            newItem2 = QTableWidgetItem(str(recognizeResult[1]))
                            newItem3 = QTableWidgetItem(str(recognizeResult[5][0]) + ',' + str(recognizeResult[5][1]))
                            self.tableWidget_7.setItem(0, 1, newItem1)
                            self.tableWidget_7.setItem(0, 2, newItem2)
                            self.tableWidget_7.setItem(0, 3, newItem3)
                            signalLimit = recognizeResult[2]
                            sampleLimit = recognizeResult[3]
                            sampleInnerId = recognizeResult[4]
                            ##############画信号图###############
                            # 生成对应的样本图id
                            if len(recognizeResult) == 6 and recognizeResult[0] == 'GSM900':
                                self.specEnvelopeSampleFigId = 5
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'WCDMA':
                                self.specEnvelopeSampleFigId = 11
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'WLAN(2.4G)':
                                self.specEnvelopeSampleFigId = 17
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'CDMA800':
                                self.specEnvelopeSampleFigId = 23
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'TD_SCDMA':
                                self.specEnvelopeSampleFigId = 29
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'FDD_LTE':
                                self.specEnvelopeSampleFigId = 32
                            elif len(recognizeResult) == 6 and recognizeResult[0] == 'GSM1800':
                                self.specEnvelopeSampleFigId = 36

                            # 画信号图和样本图
                            if self.specEnvelopeSampleFigId and self.specEnvelopeFlag:
                                # 标志位为1时清空图区
                                self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                                # sip.delete(self.specEnvelopeSampleFig)
                                self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(recognizeResult,
                                                                                                   self.specEnvelopeSampleFigId,
                                                                                                   sampleInnerId,
                                                                                                   signalLimit,
                                                                                                   sampleLimit)
                                self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                                self.specEnvelopeFlag = 1
                                self.specEnvelopeSampleFigId = ''
                            elif self.specEnvelopeSampleFigId:
                                self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(recognizeResult,
                                                                                                   self.specEnvelopeSampleFigId,
                                                                                                   sampleInnerId,
                                                                                                   signalLimit,
                                                                                                   sampleLimit)
                                self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                                self.specEnvelopeFlag = 1
                                self.specEnvelopeSampleFigId = ''
                            ##############
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

    # 频谱包络识别选择文件
    def on_pushButton_clicked_10(self):
        self.lineEdit_9.clear()
        defultPath = os.path.join(self.fatherPath, r'specEnvelope_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print("频谱包络识别选择文件：", filename)
        self.lineEdit_9.setText(self.path)

    # 频谱包络离线识别
    def on_pushButton_clicked_11(self):
        self.tableWidget_7.clearContents()
        if self.lineEdit_9.text():
            filePath = self.lineEdit_9.text()
            starttime = datetime.datetime.now()
            while not self.algorithmProcessQ.empty():
                self.algorithmProcessQ.get()
            # 开启识别进程/线程
            recognizeProcess = algorithmThreads.IQSingleProcess(filePath, self.algorithmProcessQ)
            recognizeProcess.start()
            # 调用识别loading
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.algorithmProcessQ.empty():
                gui()
            else:
                loading.close()
                recognizeResult = self.algorithmProcessQ.get()
                ########################################################
                if len(recognizeResult) == 1:
                    newItem1 = QTableWidgetItem(str(recognizeResult[0]))
                    self.tableWidget_7.setItem(0, 1, newItem1)
                    # 识别不出结果或超限时，且图区有图，则清空图区
                    if self.specEnvelopeFlag:
                        self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                        # sip.delete(self.specEnvelopeSampleFig)
                        self.specEnvelopeFlag = 0
                elif len(recognizeResult) == 6:
                    newItem1 = QTableWidgetItem(recognizeResult[0])
                    newItem2 = QTableWidgetItem(str(recognizeResult[1]))
                    newItem3 = QTableWidgetItem(
                        str(recognizeResult[5][0]) + ',' + str(recognizeResult[5][1]))
                    self.tableWidget_7.setItem(0, 1, newItem1)
                    self.tableWidget_7.setItem(0, 2, newItem2)
                    self.tableWidget_7.setItem(0, 3, newItem3)
                    signalLimit = recognizeResult[2]
                    sampleLimit = recognizeResult[3]
                    sampleInnerId = recognizeResult[4]
                    ##############画信号图###############
                    # 生成对应的样本图id
                    if len(recognizeResult) == 6 and recognizeResult[0] == 'GSM900':
                        self.specEnvelopeSampleFigId = 5
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'WCDMA':
                        self.specEnvelopeSampleFigId = 11
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'WLAN(2.4G)':
                        self.specEnvelopeSampleFigId = 17
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'CDMA800':
                        self.specEnvelopeSampleFigId = 23
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'TD_SCDMA':
                        self.specEnvelopeSampleFigId = 29
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'FDD_LTE':
                        self.specEnvelopeSampleFigId = 32
                    elif len(recognizeResult) == 6 and recognizeResult[0] == 'GSM1800':
                        self.specEnvelopeSampleFigId = 36

                    # 画信号图和样本图
                    if self.specEnvelopeSampleFigId and self.specEnvelopeFlag:
                        # 标志位为1时清空图区
                        self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                        # sip.delete(self.specEnvelopeSampleFig)
                        self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(recognizeResult,
                                                                                           self.specEnvelopeSampleFigId,
                                                                                           sampleInnerId,
                                                                                           signalLimit,
                                                                                           sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                        self.specEnvelopeFlag = 1
                        self.specEnvelopeSampleFigId = ''
                    elif self.specEnvelopeSampleFigId:
                        self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(recognizeResult,
                                                                                           self.specEnvelopeSampleFigId,
                                                                                           sampleInnerId,
                                                                                           signalLimit,
                                                                                           sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                        self.specEnvelopeFlag = 1
                        self.specEnvelopeSampleFigId = ''
                            ##############
                        endtime = datetime.datetime.now()
                        strTime = 'funtion time use:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        print(strTime)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())