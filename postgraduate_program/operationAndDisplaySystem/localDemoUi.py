import sys
import datetime
import os
import time
import win32api
import shutil
import queue
from multiprocessing import Queue as mq
import threading
from PyQt5.QtCore import Qt, QFileInfo, QTimer
import logging
from PyQt5.QtGui import QGuiApplication,QFont
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog, QApplication

from loadingDialog import Message
from function import plotWithCursor, filesOrDirsOperate, algorithmThreads
from monitor.The48hRealPart import the_48h_realpart_inQt
from Ui.UitoPy.Ui_socketDEMO import Ui_MainWindow
from controller.usrp_controller.usrp_shibie import oc_list_display_v1
from controller.usrp_controller.specEnvelope_shibie import specEnvelopeDrawpic
from controller.usrp_controller.steadyStateInterference_shibie import display_v4
from controller.Pico_controller.draw_pic import draw_pic
from monitor.waterfall import waterfallDialogEngin, waterfallDialogEnginFor3900, WaterFallForPico
from monitor.spectrum_analyze import spec_analyze_v3
from function.numOrLetters import *
from communication import zmqLocal
from function.dbInfo import dbInfo
from controller.usrp_controller.usrp_shibie.component import freqListQuery
from communication import circulationZmqThread, communicationProxy, pluralCommunicationProxy
from communication.ceyearController import ceyearProxy
from monitor.spectrum_view import realtimeSpecView
from plotTools import compare_draw

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        filesOrDirsOperate.makesureDirExist("./logs")
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m/%d %H:%M:%S %p', filename='./logs/debugLog.log', filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.info(u"日志记录开始")

        self.logger = logging.getLogger("Main")
        self.logger.addHandler(console)
        self.logger.debug("start")
        self.IQAccuracyLogger = logging.getLogger("IQAccuracy")
        fh = logging.FileHandler("./logs/IQAccuracyLog.log")
        # 识别结果日志格式：时间-[序号]-内容
        self.IQAccuracyLogId = 0
        formatter = logging.Formatter('%(asctime)s- %(message)-2s')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        self.IQAccuracyLogger.addHandler(fh)
        self.dbInfo = dbInfo

        # 初始化当前路径和其父路径，用于拼接后续地址进行非文件夹依赖的寻址
        self.currentPath = os.path.dirname(__file__)
        self.fatherPath = os.path.join(os.path.dirname(self.currentPath), "data")
        # 初始化队列
        self.zmqLocalQ = mq()
        self.dataQ = mq()
        self.algorithmProcessQ = mq()  # 算法线程队列，用来判断算法线程是否结束
        self.savingProcessQ = mq()  # 存储线程队列，用来判断存储线程是否结束
        self.ocCollectPathQ = mq()  # 批量识别地址存储队列，采集线程往里面塞入采集文件的存储地址，识别线程从里面取出地址进行识别
        self.steadyTabRowNum = queue.Queue()  # 稳态干扰表格双击监听队列
        # 初始化标志位
        self.specPicFlag = 0  # 频谱图标志位，为0表示布局中没有绘图，为1表示布局中有在线扫频图，为2表示布局中有离线频谱图
        self.ocTableDisplayFlag = 0
        self.specEnvelopeFlag = 0  # 包络图标志位
        self.pulsePicFlag = 0  # 脉冲图标志位
        self.steadyStatePicStateFlag = 0  # 稳态干扰图区状态，0代表没有图，1代表原始图，2代表结果图
        self.steadyStateTableFlag = 0  # 稳态干扰表区标志位
        self.steadyStateHistoryFigFlag = 0  # 稳态干扰历史图区标志位
        self.realpart_flag = 0  # 时域监测图区标志位
        self.specAnalyze_flag = 0  # 实时频谱分析图区标志位
        self.interferenceCancellationFigFlag = 0  # 干扰对消图区标志位
        self.realtimeSpecAnalyzeDataSaveFlag = 0  # 实时频谱分析数据存储标志位
        self.specPicFlag = 0  # 扫频图区标志位
        self.realtimeSpecViewFigFlag = 0  # 实时频谱查看图区
        self.deviceCompareFigFlag = 0  # 设备比对图区标志位
        self.antennaCompareFigFlag = 0  # 天线比对图区标志位
        # 初始化变量
        self.steadyStateHistoryData = []  # 稳态干扰历史数据
        self.steadyStateHistoryResult = []  # 稳态干扰历史结果
        self.childWindowDic = {}
        self.scanRslt = ''
        self.SNRData = ''
        self.circultaionZmqThread = None
        # 实例化zmq
        self.usrpCommu = zmqLocal.localZMQ()
        self.av3900Commu = ceyearProxy.CeyearProxy("172.141.11.202", self.fatherPath)
        # 第一页，IQ识别
        ## 自动识别
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)  # 扫频
        self.pushButton_9.clicked.connect(self.on_pushButton_clicked_9)  # 保存频谱
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)  # 频谱选择文件
        self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)  # 查看频谱图
        self.pushButton_8.clicked.connect(self.on_pushButton_clicked_8)  # 超频点查看
        self.pushButton_7.clicked.connect(self.on_pushButton_clicked_7)  # IQ自动识别
        ## 手动识别
        self.pushButton_2.setText("预采集")
        self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 采集识别
        self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # IQ选择文件
        self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)  # 离线识别

        #第二页，频谱包络识别
        self.pushButton_12.clicked.connect(self.on_pushButton_clicked_12)  # 开始识别
        self.pushButton_10.clicked.connect(self.on_pushButton_clicked_10)  # 选择文件
        self.pushButton_11.clicked.connect(self.on_pushButton_clicked_11)  # 离线识别

        # 第三页，开关脉冲识别
        self.pushButton_13.clicked.connect(self.on_pushButton_clicked_13)  # pico信号采集
        self.pushButton_14.clicked.connect(self.on_pushButton_clicked_14)  # 在线识别
        self.pushButton_15.clicked.connect(self.on_pushButton_clicked_15)  # 选择文件
        self.pushButton_16.clicked.connect(self.on_pushButton_clicked_16)  # 离线识别

        # 第四页，稳态干扰识别
        self.pushButton_17.clicked.connect(self.on_pushButton_clicked_17)  # 扫频
        self.pushButton_18.clicked.connect(self.on_pushButton_clicked_18)  # 选择文件
        self.pushButton_19.clicked.connect(self.on_pushButton_clicked_19)  # 干扰判断
        self.pushButton_20.clicked.connect(self.on_pushButton_clicked_20)  # 历史查看
        self.pushButton_21.clicked.connect(self.on_pushButton_clicked_21)  # 刷新
        self.pushButton_22.clicked.connect(self.on_pushButton_clicked_22)  # 查看频谱图

        # 第五页，频谱监测
        # 设备在线情况检测
        self.pushButton_43.clicked.connect(self.on_pushButton_clicked_43)  # 设备在线情况检测
        # 频谱监测
        self.pushButton_23.clicked.connect(self.on_pushButton_clicked_23)  # usrp1开始监测
        self.pushButton_24.clicked.connect(self.on_pushButton_clicked_24)  # usrp2开始监测
        self.pushButton_25.clicked.connect(self.on_pushButton_clicked_25)  # usrp3开始监测
        self.pushButton_26.clicked.connect(self.on_pushButton_clicked_26)  # usrp4开始监测
        # self.pushButton_85.clicked.connect(self.on_pushButton_clicked_85)  # 3900开始监测
        self.pushButton_42.clicked.connect(self.on_pushButton_clicked_42)  # 30MHz以下频谱监测

        # 第六页，时域监测
        self.pushButton_34.clicked.connect(self.on_pushButton_clicked_34)  # 采集
        self.pushButton_35.clicked.connect(self.on_pushButton_clicked_35)  # 绘图
        self.pushButton_62.clicked.connect(self.on_pushButton_clicked_62)  # 数据清空

        # 第七页，实时分析
        # 实时频谱查看
        # self.pushButton_27.clicked.connect(self.on_pushButton_clicked_27)  # 单次扫频
        # self.pushButton_32.clicked.connect(self.on_pushButton_clicked_32)  # 连续扫频

        # 实时频谱分析
        self.pushButton_37.clicked.connect(self.on_pushButton_clicked_37)  # 开始/停止绘图

        # 第八页，位置比对
        # 1，干扰对消
        self.pushButton_29.clicked.connect(self.on_pushButton_clicked_29)  # 在线对消
        self.pushButton_41.clicked.connect(self.on_pushButton_clicked_41)  # 离线对消
        self.pushButton_30.clicked.connect(self.on_pushButton_clicked_30)  # 选择文件1
        self.pushButton_31.clicked.connect(self.on_pushButton_clicked_31)  # 选择文件2

        # 2，天线比对
        self.pushButton_28.clicked.connect(self.on_pushButton_clicked_28)  # 天线比对
        self.pushButton_46.clicked.connect(self.on_pushButton_clicked_46)  # 选择文件
        self.pushButton_44.clicked.connect(self.on_pushButton_clicked_44)  # 离线比对

        # 3，设备比对
        self.pushButton_33.clicked.connect(self.on_pushButton_clicked_33)  # 设备比对
        self.pushButton_47.clicked.connect(self.on_pushButton_clicked_47)  # 选择文件
        self.pushButton_45.clicked.connect(self.on_pushButton_clicked_45)  # 离线比对

        # 第九页，信噪比分析
        # self.pushButton_36.clicked.connect(self.on_pushButton_clicked_36)  # 采集分析
        # self.pushButton_40.clicked.connect(self.on_pushButton_clicked_40)  # 保存数据
        # self.pushButton_38.clicked.connect(self.on_pushButton_clicked_38)  # 选择文件
        # self.pushButton_39.clicked.connect(self.on_pushButton_clicked_39)  # 离线分析

        self.updateFreqListTable()

    # 初始化频点识别列表名
    def updateFreqListTable(self):
        tableNameReg = r'used_freq_point_list*'
        freqList = freqListQuery.getFreqPointTableList(self.dbInfo, tableNameReg)
        for index in range(len(freqList)):
            self.comboBox_14.addItem("")
            self.comboBox_14.setItemText(index, freqList[index])

    # 设备在线情况检测
    def on_pushButton_clicked_43(self):
        msg = ("USRP,device check")
        communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu,
                                                                    self.av3900Commu)
        communicationThread.start()
        # 调用loading
        loading = Message.Loading()
        loading.setWindowModality(Qt.ApplicationModal)
        loading.show()
        gui = QGuiApplication.processEvents
        while self.zmqLocalQ.empty():
            gui()
        else:
            loading.close()
            reslt = self.zmqLocalQ.get()
            local_time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(time.time()))
            self.textBrowser.append("{}-".format(local_time)+reslt)

    # IQ扫频按键
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
                deviceNum = self.comboBox_2.currentText()
                msg = (deviceNum + ',scan,IQ,'
                          + str(startfreq) + ";" +str(endfreq))
                communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu, self.av3900Commu)
                communicationThread.start()
                # 调用loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
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
                        return 0
                    elif reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    else:
                        resltList = reslt.split(';')
                        self.scanRslt = resltList
                        freqList = resltList[0].split(' ')
                        binsList = resltList[1].split(" ")
                        self.onlineSpecX = [float(i) for i in freqList]
                        self.onlineSpecY = [float(i) for i in binsList]
                        #####置入绘图####
                        if self.specPicFlag:
                            self.verticalLayout.removeWidget(self.getPosition)
                            self.getPosition.deleteLater()
                        self.getPosition = plotWithCursor.getPos('originOnline', self.onlineSpecX,
                                                                 self.onlineSpecY,
                                                                 self.lineEdit_6)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.specPicFlag = 1
                        endtime = datetime.datetime.now()
                        strTime = 'IQ扫频耗时:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        self.logger.info(strTime)
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
            while not self.savingProcessQ.empty():
                self.savingProcessQ.get()
            dirPath = os.path.join(self.fatherPath, r'usrp_recvfiles\usrp_scan')
            filesOrDirsOperate.makesureDirExist(dirPath)
            localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            filePath = os.path.join(dirPath, r'scan_spectrum_{}.txt'.format(localTime))
            saveT = algorithmThreads.SaveSpectrumThread(filePath, self.scanRslt, self.savingProcessQ)
            saveT.start()
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.savingProcessQ.empty():
                gui()
            else:
                loading.close()
                self.logger.info('IQ扫频-频谱保存-频谱文件存储于：'+self.savingProcessQ.get())
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
        self.logger.info("IQ频谱图查看-选择文件："+filename)
        self.lineEdit_3.setText(filename)

    # 查看频谱图
    def on_pushButton_clicked_6(self):
        if self.lineEdit_3.text():
            path = self.lineEdit_3.text()
            if os.path.exists(path):
                try:
                    #####置入绘图####
                    if self.specPicFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        self.getPosition.deleteLater()
                    self.getPosition = plotWithCursor.getPos('originOfflineWithoutMouseListening', path)
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
                                                                           self.algorithmProcessQ)
                    overThresholdThread.start()
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QApplication.processEvents
                    while self.algorithmProcessQ.empty():
                        gui()
                    else:
                        self.ocOverThresholdList = self.algorithmProcessQ.get()
                        loading.close()
                        if self.ocOverThresholdList:
                            # 置入超频点列表
                            if self.ocTableDisplayFlag:
                                self.verticalLayout_4.removeWidget(self.ocTableDisplay)
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
            self.logger.debug('IQ自动识别-用户选中的行为:'+str(self.ocRowNumSelectList))
            if self.ocRowNumSelectList:
                while not self.algorithmProcessQ.empty():
                    self.algorithmProcessQ.get()
                # self.logger.debug(u"算法结果队列清空完成")
                deviceNum = self.comboBox_2.currentText()
                # 频点列表查询
                tableName = 'used_freq_point'
                freqList = freqListQuery.freqListQuery(self.dbInfo, tableName)
                # self.logger.debug(u"频点列表查询完成")
                # 创建行号-IQ识别结果字典
                self.ocRsltDict = dict.fromkeys(self.ocRowNumSelectList, 'null')
                # self.ocRsltDict.keys()
                # self.logger.debug(u"结果字典创建完成")
                collectThread = algorithmThreads.OcCollectThread(deviceNum, self.ocRsltDict,
                                                                 self.ocOverThresholdList, self.usrpCommu,
                                                                 self.av3900Commu, self.ocCollectPathQ)
                recognizeThread = algorithmThreads.OcRecognizeThread(self.ocRsltDict,
                                                                     self.ocCollectPathQ, self.algorithmProcessQ, freqList)
                collectThread.start()
                recognizeThread.start()
                self.logger.debug(u"自动识别采集、识别线程开启")
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.algorithmProcessQ.empty():
                    gui()
                else:
                    loading.close()
                    self.ocRsltDict = self.algorithmProcessQ.get()
                    for row in self.ocRsltDict:
                        rowName = int(row)
                        item1 = QTableWidgetItem(self.ocRsltDict[rowName][2])  # 调制方式
                        item2 = QTableWidgetItem(self.ocRsltDict[rowName][3])  # 频点识别
                        self.ocTableDisplay.tableWidget.setItem(rowName, 3, item1)
                        self.ocTableDisplay.tableWidget.setItem(rowName, 4, item2)
                    endtime = datetime.datetime.now()
                    strTime = "IQ自动识别-条数：%i，耗时：%sms" % (len(self.ocRowNumSelectList),
                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                    self.logger.info(strTime)
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
        """
        1.频谱采集1次
        2.频谱采集2次+IQ采集
        3.IQ数据传入IQ识别算法和SNR算法2，频谱采集1、2次数据传入SNR算法1
        4.等待IQ识别结果、等待SNR算法1、2比对结果
        5.结果呈现
        """
        try:
            # 初始化生成SNR算法1所需的两个频谱文件的名称
            self.SNRSpecfileTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            SNRIQDirPath = os.path.join(self.fatherPath, r'SNR_data')
            filesOrDirsOperate.makesureDirExist(SNRIQDirPath)
            SNRIQfileName1 = "SNRIQPro_{}.txt".format(self.SNRSpecfileTime)
            SNRIQfileName2 = "SNRIQCurrent_{}.txt".format(self.SNRSpecfileTime)

            # SNRSpecDirPath = os.path.join(self.fatherPath, r'SNR_data')
            # SNRSpecfileName1 = "SNRSpecPro_{}.txt".format(self.SNRSpecfileTime)
            # SNRSpecfileName2 = "SNRSpecCurrent_{}.txt".format(self.SNRSpecfileTime)
            # 结果表格列数刷新
            self.tableWidget_3.setColumnCount(5)
            # 获取用户期望的查表谐波次数
            harmonicNum = int(self.comboBox_13.currentText())
            # 结果表格刷新
            self.tableWidget_3.clearContents()
            self.logger.info("开始手动IQ识别……")
            starttime = datetime.datetime.now()
            while not self.zmqLocalQ.empty():
                self.zmqLocalQ.get()
            centrefreq = self.lineEdit_4.text()
            bdwidth = self.lineEdit_5.text()
            samprate = self.lineEdit_8.text()
            # 判断用户输入的参数是否合理
            if isNum(centrefreq) and isNum(bdwidth) and isNum(samprate):
                centrefreq = float(centrefreq)
                bdwidth = float(bdwidth)
                samprate = float(samprate)
                # 为保证扫频不超限，这里的参数判断需算入扫频宽度
                # if centrefreq <= 6000-6.25 and centrefreq >= 30+6.25:
                if centrefreq < 6000 and centrefreq > 30:
                    # 获取IQ采集数据
                    centrefreq = centrefreq * 1000000
                    bdwidth = bdwidth * 1000000
                    samprate = samprate * 1000000
                    # # 获取扫频数据（for SNR1）
                    # startfreq = centrefreq - 6.25e6
                    # endfreq = centrefreq + 6.25e6
                    # 获取用户所选的设备号
                    deviceNum = self.comboBox_3.currentText()

                    if self.pushButton_2.text() == "预采集":
                        self.pushButton_2.setText("正式采集")
                        # # 一次扫频
                        # self.logger.debug("IQ频域信噪比一次扫频开始")
                        # freqMsg = (deviceNum + ',scan,IQ,'
                        #           + str(startfreq) + ";" +str(endfreq))

                        # 一次IQ采集
                        self.logger.debug("IQ信噪比一次采集开始")
                        iqMsg = (deviceNum + ',collect,IQsingle,'+ str(centrefreq) + ";" + str(bdwidth) + ";" + str(samprate))
                        communicationThread = communicationProxy.CommunicationProxy(iqMsg, self.zmqLocalQ, self.usrpCommu,
                                                                                    self.av3900Commu)
                        communicationThread.start()
                        # 调用识别loading
                        loading = Message.Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        gui = QGuiApplication.processEvents
                        while self.zmqLocalQ.empty():
                            gui()
                        else:
                            loading.close()
                        # # 一次扫频数据（for SNR1）
                        # self.SNRSpec1 = self.zmqLocalQ.get()
                        # 一次IQ数据（for SNR1）
                        self.SNRIQ1 = self.zmqLocalQ.get()
                        if self.SNRIQ1 == "":
                            self.pushButton_2.setText("预采集")
                            QMessageBox.warning(self,
                                                '错误',
                                                "设备未启用！",
                                                QMessageBox.Yes,
                                                QMessageBox.Yes)
                            return 0
                        # 开启一次数据存储线程
                        while not self.savingProcessQ.empty():
                            self.savingProcessQ.get()
                        # savingProcess = algorithmThreads.SaveSpectrumThread(os.path.join(SNRSpecDirPath, SNRSpecfileName1),
                        #                                                     self.SNRSpec1.split(";"), self.savingProcessQ)
                        savingProcess = algorithmThreads.SNRIQDataSaveProcess(os.path.join(SNRIQDirPath, SNRIQfileName1),
                                                                            self.SNRIQ1, self.savingProcessQ)
                        savingProcess.start()
                        # 调用识别loading
                        loading = Message.Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        gui = QGuiApplication.processEvents
                        while self.savingProcessQ.empty():
                            gui()
                        else:
                            loading.close()
                            # self.logger.info("频域信噪比算法一次扫频结束，数据存储于："+self.savingProcessQ.get())
                            self.logger.info("频域信噪比算法一次采集结束，数据存储于："+self.savingProcessQ.get())
                    elif self.pushButton_2.text() == "正式采集":
                        self.pushButton_2.setText("预采集")
                        # # 二次扫频
                        # self.logger.debug("IQ频域信噪比二次扫频开始")
                        # freqMsg = (deviceNum + ',scan,IQ,'
                        #            + str(startfreq) + ";" + str(endfreq))
                        # while not self.zmqLocalQ.empty():
                        #     self.zmqLocalQ.get()
                        # communicationThread = communicationProxy.CommunicationProxy(freqMsg, self.zmqLocalQ, self.usrpCommu,
                        #                                                             self.av3900Commu)
                        # communicationThread.start()
                        # # 调用识别loading
                        # loading = Message.Loading()
                        # loading.setWindowModality(Qt.ApplicationModal)
                        # loading.show()
                        # gui = QGuiApplication.processEvents
                        # while self.zmqLocalQ.empty():
                        #     gui()
                        # else:
                        #     loading.close()
                        # # 二次扫频数据（for SNR1）
                        # SNRSpec2 = self.zmqLocalQ.get()
                        # # 开启二次扫频数据存储线程
                        # while not self.savingProcessQ.empty():
                        #     self.savingProcessQ.get()
                        # savingProcess = algorithmThreads.SaveSpectrumThread(os.path.join(SNRSpecDirPath, SNRSpecfileName2),
                        #                                                     SNRSpec2.split(";"), self.savingProcessQ)
                        # savingProcess.start()
                        # # 调用识别loading
                        # loading = Message.Loading()
                        # loading.setWindowModality(Qt.ApplicationModal)
                        # loading.show()
                        # gui = QGuiApplication.processEvents
                        # while self.savingProcessQ.empty():
                        #     gui()
                        # else:
                        #     loading.close()
                        #     self.logger.info("频域信噪比算法二次采集结束，数据存储于：" + self.savingProcessQ.get())

                        # IQ采集
                        msg = (deviceNum + ',collect,IQsingle,'+ str(centrefreq) + ";" + str(bdwidth)
                              + ";" + str(samprate))
                        while not self.zmqLocalQ.empty():
                            self.zmqLocalQ.get()
                        communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu,
                                                                                    self.av3900Commu)
                        communicationThread.start()
                        # 调用识别loading
                        loading = Message.Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        gui = QGuiApplication.processEvents
                        while self.zmqLocalQ.empty():
                            gui()
                        else:
                            loading.close()
                            reslt = self.zmqLocalQ.get()
                            if reslt == "超时":
                                loading.close()
                                QMessageBox.warning(self,
                                                    '错误',
                                                    "本地连接超时！",
                                                    QMessageBox.Yes,
                                                    QMessageBox.Yes)
                                return 0
                            elif reslt == "":
                                self.pushButton_2.setText("预采集")
                                QMessageBox.warning(self,
                                                    '错误',
                                                    "设备未启用！",
                                                    QMessageBox.Yes,
                                                    QMessageBox.Yes)
                                return 0
                            else:
                                while not self.algorithmProcessQ.empty():
                                    self.algorithmProcessQ.get()
                                while not self.savingProcessQ.empty():
                                    self.savingProcessQ.get()
                                # 开启SNRIQ2数据存储线程
                                SNRIQ2 = reslt
                                snr2savingQ = queue.Queue()
                                savingProcess = algorithmThreads.SNRIQDataSaveProcess(
                                    os.path.join(SNRIQDirPath, SNRIQfileName2),
                                    SNRIQ2, snr2savingQ)
                                savingProcess.start()
                                # 开启IQ数据存储线程
                                savingProcess = algorithmThreads.IQDataSaveProcess(reslt, self.savingProcessQ)
                                savingProcess.start()
                                # self.logger.debug("IQ数据存储开始……")
                                while not self.algorithmProcessQ.empty():
                                    self.algorithmProcessQ.get()
                                tableName = self.comboBox_14.currentText()
                                freqList = freqListQuery.freqListQuery(self.dbInfo, tableName)
                                # recognizeProcess = algorithmThreads.IQSingleProcess(reslt, self.algorithmProcessQ, freqList,
                                #                                                     harmonicNum, self.SNRSpec1, SNRSpec2)
                                recognizeProcess = algorithmThreads.IQSingleProcess(reslt, self.algorithmProcessQ, freqList,
                                                                                    harmonicNum, self.SNRIQ1, SNRIQ2)
                                recognizeProcess.start()
                                # 调用识别loading
                                loading = Message.Loading()
                                loading.setWindowModality(Qt.ApplicationModal)
                                loading.show()
                                # while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
                                while self.algorithmProcessQ.empty() or self.savingProcessQ.empty() or snr2savingQ.empty():
                                    gui()
                                else:
                                    loading.close()
                                    recognizeResult = self.algorithmProcessQ.get()
                                    dataPath = self.savingProcessQ.get()
                                    # IQsnr专用
                                    snr2savingPath = snr2savingQ.get()
                                    self.logger.info("频域信噪比算法二次采集结束，数据存储于：" + snr2savingPath)
                                    # 识别结果输出至文件
                                    dirPath = os.path.join(self.fatherPath, r'usrp_recvfiles/IQrecogonizeOutput')
                                    filesOrDirsOperate.makesureDirExist(dirPath)
                                    local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                                    filePath = os.path.join(dirPath, r'IQrecogonizeOutput_{}.txt'.format(local_time))
                                    with open(filePath, 'w+') as file_object:
                                        file_object.write("data path: "+ dataPath +"\n")
                                        file_object.write("中心频率（MHz）："+recognizeResult[0]+"\n")
                                        file_object.write("带宽（Hz）：" + recognizeResult[1]+"\n")
                                        file_object.write("调制方式：" + recognizeResult[2]+"\n")
                                        file_object.write("信噪比（dB）：" + recognizeResult[4]+"\n")
                                        file_object.write("频点识别：")
                                        for freqPoint in recognizeResult[3]:
                                            file_object.write(str(freqPoint)+":"+recognizeResult[3][freqPoint] + ",")
                                    # 界面表格显示
                                    item1 = QTableWidgetItem("%.1f" % float(recognizeResult[0]))  # 中心频率
                                    item2 = QTableWidgetItem("%.1f" % float(recognizeResult[1]))  # 带宽
                                    item3 = QTableWidgetItem(recognizeResult[2])  # 调制方式
                                    item4 = QTableWidgetItem("%.2f" % float(recognizeResult[4]))  # 信噪比
                                    self.tableWidget_3.setItem(0, 1, item1)
                                    self.tableWidget_3.setItem(0, 2, item2)
                                    self.tableWidget_3.setItem(0, 3, item3)
                                    self.tableWidget_3.setItem(0, 4, item4)
                                    freqPointDic = recognizeResult[3]
                                    for freqPoint in freqPointDic:
                                        item = QTableWidgetItem(freqPointDic[freqPoint])
                                        column = self.tableWidget_3.columnCount()
                                        self.tableWidget_3.insertColumn(column)
                                        self.tableWidget_3.setHorizontalHeaderItem(column, item)
                                        item.setText(freqPointDic[freqPoint])
                                        item = QTableWidgetItem(freqPoint)  # 调制方式
                                        self.tableWidget_3.setItem(0, column, item)

                                    endtime = datetime.datetime.now()
                                    strTime = 'IQ手动在线识别结束，耗时:%dms' % (
                                            (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                                    self.logger.info(strTime+"，数据存储于：" + dataPath + "，识别结果存储于：" + filePath)
                                    snr = recognizeResult[4]
                                    accuracyContent = "中心频率：%.1f，带宽：%.1f，信噪比：%.2f，调制方式：%s，信噪比详情：%s" % (
                                        float(recognizeResult[0]),float(recognizeResult[1]), float(snr), recognizeResult[2],
                                        recognizeResult[5])
                                    self.IQAccuracyLogId += 1
                                    self.IQAccuracyLogger.info(str(self.IQAccuracyLogId)+","+accuracyContent)

                else:
                    QMessageBox.warning(self,
                                        '错误',
                                        "请输入正确参数！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                    self.pushButton_2.setText("预采集")
            else:
                QMessageBox.warning(self,
                                    '错误',
                                    "请输入正确参数！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
                self.pushButton_2.setText("预采集")
        except Exception as e:
            self.logger.error("IQ手动识别："+repr(e))

    # IQ选择文件
    def on_pushButton_clicked_3(self):
        self.lineEdit_7.clear()
        defultPath = os.path.join(self.fatherPath, r'usrp_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        # self.path = filename
        # fileinfo = QFileInfo(filename)
        # self.name = fileinfo.fileName()
        self.logger.info("IQ频谱图查看选择文件："+filename)
        self.lineEdit_7.setText(filename)

    # IQ手动离线识别
    def on_pushButton_clicked_4(self):
        self.tableWidget_3.setColumnCount(5)
        harmonicNum = int(self.comboBox_13.currentText())
        self.tableWidget_3.clearContents()
        self.logger.info("开始手动IQ识别（离线）……")
        starttime = datetime.datetime.now()
        if self.lineEdit_7.text():
            dataPath = self.lineEdit_7.text()
            tableName = self.comboBox_14.currentText()
            freqList = freqListQuery.freqListQuery(self.dbInfo, tableName)
            recognizeProcess = algorithmThreads.IQSingleProcess(dataPath, self.algorithmProcessQ, freqList, harmonicNum)
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
                dirPath = os.path.join(self.fatherPath, r'usrp_recvfiles/IQrecogonizeOutput')
                filesOrDirsOperate.makesureDirExist(dirPath)
                local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                filePath = os.path.join(dirPath, r'IQrecogonizeOutput_{}.txt'.format(local_time))
                with open(filePath, 'w+') as file_object:
                    file_object.write("data path: " + dataPath + "\n")
                    file_object.write("中心频率（MHz）：" + recognizeResult[0] + "\n")
                    file_object.write("带宽（Hz）：" + recognizeResult[1] + "\n")
                    file_object.write("调制方式：" + recognizeResult[2] + "\n")
                    file_object.write("信噪比（dB）：" + recognizeResult[4] + "\n")
                    file_object.write("频点识别：")
                    for freqPoint in recognizeResult[3]:
                        file_object.write(str(freqPoint) + ":" + recognizeResult[3][freqPoint] + ",")
                item1 = QTableWidgetItem("%.1f" % float(recognizeResult[0]))  # 中心频率
                item2 = QTableWidgetItem("%.1f" % float(recognizeResult[1]))  # 带宽
                item3 = QTableWidgetItem(recognizeResult[2])  # 调制方式
                # item4 = QTableWidgetItem(recognizeResult[3])  # 频点识别
                item5 = QTableWidgetItem(recognizeResult[4])  # 信噪比
                self.tableWidget_3.setItem(0, 1, item1)
                self.tableWidget_3.setItem(0, 2, item2)
                self.tableWidget_3.setItem(0, 3, item3)
                # self.tableWidget_3.setItem(0, 4, item4)
                self.tableWidget_3.setItem(0, 4, item5)
                freqPointDic = recognizeResult[3]
                for freqPoint in freqPointDic:
                    item = QTableWidgetItem(freqPointDic[freqPoint])
                    column = self.tableWidget_3.columnCount()
                    self.tableWidget_3.insertColumn(column)
                    self.tableWidget_3.setHorizontalHeaderItem(column, item)
                    item.setText(freqPointDic[freqPoint])
                    item = QTableWidgetItem(freqPoint)  # 调制方式
                    self.tableWidget_3.setItem(0, column, item)
                endtime = datetime.datetime.now()
                strTime = 'IQ手动离线识别结束，耗时:%dms' % (
                        (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                self.logger.info(strTime + "，识别结果存储于："+filePath)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 频谱包络在线识别
    def on_pushButton_clicked_12(self):
        self.tableWidget_7.clearContents()
        # 清空数据队列
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        # 清空识别结果队列
        while not self.algorithmProcessQ.empty():
            self.algorithmProcessQ.get()
        # 清空存储地址队列
        while not self.savingProcessQ.empty():
            self.savingProcessQ.get()
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_10.text()
        endfreq = self.lineEdit_11.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 150:
                startfreq = startfreq * 1000000
                endfreq = endfreq * 1000000
                deviceNum = self.comboBox_4.currentText()
                msg = (deviceNum + ',scan,specEnvelope,'
                       + str(startfreq) + ";" + str(endfreq))
                specEnvelopThread = algorithmThreads.specEnvelopeOnlineProcess(self.usrpCommu, self.av3900Commu,
                                                                               msg, self.dataQ,
                                                                               self.algorithmProcessQ,
                                                                               self.savingProcessQ)
                specEnvelopThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
                    gui()
                else:
                    loading.close()
                    recognizeResult = self.algorithmProcessQ.get()
                    saveResult = self.savingProcessQ.get()
                    data = self.dataQ.get()
                    if recognizeResult == '超时':
                        QMessageBox.warning(self,
                                            '错误',
                                            "本地连接超时！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    elif recognizeResult == '设备未启用':
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    elif len(recognizeResult) == 1:
                        newItem1 = QTableWidgetItem(str(recognizeResult[0]))
                        self.tableWidget_7.setItem(0, 1, newItem1)
                        # 识别不出结果或超限时，且图区有图，则清空图区
                        if self.specEnvelopeFlag:
                            self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                            self.specEnvelopeFlag = 0
                    elif len(recognizeResult) == 6:
                        # 表格显示识别结果
                        newItem1 = QTableWidgetItem(recognizeResult[0])# 识别结果
                        newItem2 = QTableWidgetItem(str(recognizeResult[1]))# 相似度
                        # 起止频率
                        newItem3 = QTableWidgetItem(str(recognizeResult[5][0]) + ',' + str(recognizeResult[5][1]))
                        self.tableWidget_7.setItem(0, 1, newItem1)
                        self.tableWidget_7.setItem(0, 2, newItem2)
                        self.tableWidget_7.setItem(0, 3, newItem3)
                        signalLimit = recognizeResult[2] # 相似信号范围
                        sampleLimit = recognizeResult[3] # 相似模板范围
                        sampleInnerId = recognizeResult[4] # 相似编号
                        ##############画信号图###############
                        # 生成对应的样本图id
                        if recognizeResult[0] == 'GSM900':
                            self.specEnvelopeSampleFigId = 5
                        elif recognizeResult[0] == 'WCDMA':
                            self.specEnvelopeSampleFigId = 11
                        elif recognizeResult[0] == 'WLAN(2.4G)':
                            self.specEnvelopeSampleFigId = 17
                        elif recognizeResult[0] == 'CDMA800':
                            self.specEnvelopeSampleFigId = 24
                        elif recognizeResult[0] == 'TD_SCDMA':
                            self.specEnvelopeSampleFigId = 30
                        elif recognizeResult[0] == 'FDD_LTE':
                            self.specEnvelopeSampleFigId = 33
                        elif recognizeResult[0] == 'GSM1800':
                            self.specEnvelopeSampleFigId = 37

                        # 画信号图和样本图
                        if self.specEnvelopeSampleFigId and self.specEnvelopeFlag:
                            # 标志位为1时清空图区
                            self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                            self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(data,
                                                                                               self.specEnvelopeSampleFigId,
                                                                                               sampleInnerId,
                                                                                               signalLimit,
                                                                                               sampleLimit)
                            self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                            self.specEnvelopeFlag = 1
                            self.specEnvelopeSampleFigId = ''
                        elif self.specEnvelopeSampleFigId:
                            self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(data,
                                                                                               self.specEnvelopeSampleFigId,
                                                                                               sampleInnerId,
                                                                                               signalLimit,
                                                                                               sampleLimit)
                            self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                            self.specEnvelopeFlag = 1
                            self.specEnvelopeSampleFigId = ''
                            ##############
                        endtime = datetime.datetime.now()
                        strTime = '频谱包络识别耗时:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        self.logger.info("频谱包络识别结束，结果："+recognizeResult[0]+"，耗时："+strTime+"，包络数据存储于："+saveResult)
            else:
                QMessageBox.warning(self,
                                    '错误',
                                    "请输入正确范围内的参数，\n"
                                    "起始频率不小于30MHz截止频率不大于6000MHz，\n"
                                    "频率差不超过150MHz！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入参数应为数字！",
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
        self.logger.info("频谱包络识别选择文件："+filename)
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
            recognizeProcess = algorithmThreads.specEnvelopeOfflineProcess(filePath, self.algorithmProcessQ)
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
                    if recognizeResult[0] == 'GSM900':
                        self.specEnvelopeSampleFigId = 5
                    elif recognizeResult[0] == 'WCDMA':
                        self.specEnvelopeSampleFigId = 11
                    elif recognizeResult[0] == 'WLAN(2.4G)':
                        self.specEnvelopeSampleFigId = 17
                    elif recognizeResult[0] == 'CDMA800':
                        self.specEnvelopeSampleFigId = 24
                    elif recognizeResult[0] == 'TD_SCDMA':
                        self.specEnvelopeSampleFigId = 30
                    elif recognizeResult[0] == 'FDD_LTE':
                        self.specEnvelopeSampleFigId = 33
                    elif recognizeResult[0] == 'GSM1800':
                        self.specEnvelopeSampleFigId = 37

                    # 画信号图和样本图
                    if self.specEnvelopeSampleFigId and self.specEnvelopeFlag:
                        # 标志位为1时清空图区
                        self.verticalLayout_22.removeWidget(self.specEnvelopeSampleFig)
                        # sip.delete(self.specEnvelopeSampleFig)
                        self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(filePath,
                                                                                           self.specEnvelopeSampleFigId,
                                                                                           sampleInnerId,
                                                                                           signalLimit,
                                                                                           sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                        self.specEnvelopeFlag = 1
                        self.specEnvelopeSampleFigId = ''
                    elif self.specEnvelopeSampleFigId:
                        self.specEnvelopeSampleFig = specEnvelopeDrawpic.ApplicationWindow(filePath,
                                                                                           self.specEnvelopeSampleFigId,
                                                                                           sampleInnerId,
                                                                                           signalLimit,
                                                                                           sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelopeSampleFig)
                        self.specEnvelopeFlag = 1
                        self.specEnvelopeSampleFigId = ''
                            ##############
                        endtime = datetime.datetime.now()
                        strTime = '频谱包络离线识别结束，结果：'+recognizeResult[0]+'，耗时:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        self.logger.info(strTime)
        else:
            QMessageBox.warning(self,
                                '提示',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # pico信号采集
    def on_pushButton_clicked_13(self):
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            time = QTimer(self)
            self.pushButton_13.setEnabled(False)
        except Exception as e:
            self.logger.error("脉冲识别pico采集："+e)

        def forbidden():
            self.pushButton_13.setEnabled(True)

        time.setInterval(10000)
        time.start()
        time.timeout.connect(forbidden)

    # 脉冲在线识别
    def on_pushButton_clicked_14(self):
        try:
            length = 10
            dirPath = os.path.join(self.fatherPath, r'interference_files\matfile')
            self.logger.debug("脉冲在线识别文件地址："+dirPath)
            filesOrDirsOperate.makesureDirExist(dirPath)
            pulseRecognizeOnlineT = algorithmThreads.PulseRecognizeOnlineProcess(dirPath, self.algorithmProcessQ,
                                                                                 length, self.fatherPath)
            pulseRecognizeOnlineT.start()
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.algorithmProcessQ.empty():
                gui()
            else:
                loading.close()
                result = self.algorithmProcessQ.get()
                targetFile = self.algorithmProcessQ.get()
                if result == '0':
                    QMessageBox.warning(self, "错误", "文件夹中没有文件，请先采集！")
                else:
                    if result == 'fan':
                        display = '风扇'
                        self.pulseSampleFigId = 1
                    elif result == 'PA51':
                        self.pulseSampleFigId = 2
                        display = 'PA51'
                    elif result == 'WD_200':
                        self.pulseSampleFigId = 3
                        display = 'WD_200'
                    elif result == 'shipeiqi':
                        self.pulseSampleFigId = 4
                        display = '适配器'
                    newItem = QTableWidgetItem(display)
                    self.tableWidget_6.setItem(0, 1, newItem)
                    ##############画信号图###############
                    if self.pulsePicFlag:
                        # 标志位为1时清空图区
                        self.verticalLayout_20.removeWidget(self.samplefig)
                        self.samplefig = draw_pic.ApplicationWindow(targetFile, self.pulseSampleFigId, self.logger)
                        self.verticalLayout_20.addWidget(self.samplefig)
                        self.pulsePicFlag = 1
                    else:
                        self.samplefig = draw_pic.ApplicationWindow(targetFile, self.pulseSampleFigId, self.logger)
                        self.verticalLayout_20.addWidget(self.samplefig)
                        self.pulsePicFlag = 1
                    ##############
        except Exception as e:
            self.logger.error("脉冲识别："+e)

    # 脉冲选择文件
    def on_pushButton_clicked_15(self):
        self.tableWidget_6.clearContents()
        dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹", os.path.join(self.fatherPath,
                                                                               r'interference_files\txt'))

        self.logger.info("脉冲离线识别选择文件夹："+dirpath)
        dirname = dirpath.split('/')[-1]
        self.pulsePath = dirpath
        newItem = QTableWidgetItem(dirname)
        self.tableWidget_6.setItem(0, 0, newItem)

    # 脉冲离线识别
    def on_pushButton_clicked_16(self):
        try:
            if not self.pulsePath:
                QMessageBox.information(self, "提示", "请选择文件")
            else:
                # self.logger.info('脉冲离线识别选择识别的文件夹为：'+self.pulsePath)
                filesOrDirsOperate.makesureDirExist(self.pulsePath)
                length = 10
                pulseRecognizeOfflineT = algorithmThreads.PulseRecognizeOfflineProcess(self.pulsePath,
                                                                                       self.algorithmProcessQ,
                                                                                       length, self.fatherPath)
                pulseRecognizeOfflineT.start()
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.algorithmProcessQ.empty():
                    gui()
                else:
                    loading.close()
                    result = self.algorithmProcessQ.get()
                    if result =='0':
                        QMessageBox.warning(self, "错误", "文件夹中没有文件！")
                    else:
                        if result == 'fan':
                            self.pulseSampleFigId = 1
                            display = '风扇'
                        elif result == 'PA51':
                            self.pulseSampleFigId = 2
                            display = 'PA51'
                        elif result == 'WD_200':
                            self.pulseSampleFigId = 3
                            display = 'WD_200'
                        elif result == 'shipeiqi':
                            self.pulseSampleFigId = 4
                            display = '适配器'
                        newItem = QTableWidgetItem(display)
                        self.tableWidget_6.setItem(0, 1, newItem)
                        targetFile = self.pulsePath
                        ##############画信号图###############
                        if self.pulsePicFlag:
                            # 标志位为1时清空图区
                            self.verticalLayout_20.removeWidget(self.samplefig)
                            self.samplefig = draw_pic.ApplicationWindow(targetFile, self.pulseSampleFigId, self.logger)
                            self.verticalLayout_20.addWidget(self.samplefig)
                            self.pulsePicFlag = 1
                        else:
                            self.samplefig = draw_pic.ApplicationWindow(targetFile, self.pulseSampleFigId, self.logger)
                            self.verticalLayout_20.addWidget(self.samplefig)
                            self.pulsePicFlag = 1
                        ##############

        except Exception as e:
            self.logger.error("脉冲离线识别："+e)

    # 稳态干扰扫频
    def on_pushButton_clicked_17(self):
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_12.text()
        endfreq = self.lineEdit_13.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 5000:
                startfreq = startfreq*1000000
                endfreq = endfreq*1000000
                deviceNum = self.comboBox_5.currentText()
                msg = (deviceNum + ',scan,steadyStateInterference,'
                          + str(startfreq) + ";" + str(endfreq))
                communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu,
                                                                            self.av3900Commu)
                communicationThread.start()
                # 调用loading
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
                        return 0
                    elif reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    else:
                        resltList = reslt.split(';')
                        steadyStateScanRslt = resltList  # 用于存储
                        # 开启存储线程
                        while not self.savingProcessQ.empty():
                            self.savingProcessQ.get()
                        dirPath = os.path.join(self.fatherPath, r'steadyStateInterference_recvfiles')
                        filesOrDirsOperate.makesureDirExist(dirPath)
                        localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                        filePath = os.path.join(dirPath, r'steady_state_spectrum_{}.txt'.format(localTime))
                        saveT = algorithmThreads.SaveSpectrumThread(filePath,
                                                                    steadyStateScanRslt, self.savingProcessQ)
                        saveT.start()
                        ##
                        freqList = resltList[0].split(' ')
                        binsList = resltList[1].split(" ")
                        # 用于绘图
                        specX = [float(i) for i in freqList]
                        specY = [float(i) for i in binsList]
                        self.steadyStateData = [specX, specY]# 用于干扰判断算法调用
                        #####置入绘图####
                        if not self.steadyStatePicStateFlag == 0:
                            # 如果图区有图，不管是原图还是结果图，都刷掉
                            self.verticalLayout_30.removeWidget(self.steadyStateFig)
                            self.steadyStateFig.deleteLater()
                            self.steadyStateFig = None
                        self.steadyStateFig = plotWithCursor.getPos('originOnline',
                                                                       specX, specY, self.lineEdit_16)
                        self.verticalLayout_30.addWidget(self.steadyStateFig)
                        self.steadyStatePicStateFlag = 1
                        endtime = datetime.datetime.now()
                        strTime = '稳态干扰扫频结束，耗时:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        self.logger.info(strTime)
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

    # 稳态干扰选择文件
    def on_pushButton_clicked_18(self):
        self.lineEdit_17.clear()
        defultPath = os.path.join(self.fatherPath, r'steadyStateInterference_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.logger.info("稳态干扰选择文件："+filename)
        self.lineEdit_17.setText(filename)

    # 稳态干扰离线频谱图查看
    def on_pushButton_clicked_22(self):
        if self.lineEdit_17.text():
            path = self.lineEdit_17.text()
            if os.path.exists(path):
                try:
                    #####置入绘图####
                    if not self.steadyStatePicStateFlag == 0:
                        # 如果图区有图，不管是原图还是结果图，都刷掉
                        self.verticalLayout_30.removeWidget(self.steadyStateFig)
                        self.steadyStateFig.deleteLater()
                        self.steadyStateFig = None
                    self.steadyDataQ = queue.Queue()
                    self.steadyStateFig = plotWithCursor.getPos('originOffline',
                                                                   path, self.lineEdit_16,
                                                                   self.steadyDataQ)
                    self.steadyStateData = self.steadyDataQ.get()
                    self.verticalLayout_30.addWidget(self.steadyStateFig)
                    self.steadyStatePicStateFlag = 2
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

    # 稳态干扰判断
    def on_pushButton_clicked_19(self):
        if not self.lineEdit_16.text():
            QMessageBox.warning(self,
                                '提示',
                                "请输入限值！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        elif self.steadyStatePicStateFlag == 0:
            QMessageBox.warning(self,
                                '提示',
                                "请先扫频或查看频谱图！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        else:
            if self.steadyStateTableFlag:
                self.verticalLayout_31.removeWidget(self.steadyStateTab)
                self.steadyStateTab.deleteLater()
                self.steadyStateTab = None
            self.steadyStateTab = display_v4.WindowClass(self.steadyTabRowNum)
            self.verticalLayout_31.addWidget(self.steadyStateTab)
            self.steadyStateTableFlag = 1

            while not self.algorithmProcessQ.empty():
                self.algorithmProcessQ.get()
            dirPath = os.path.join(self.fatherPath, r'steadyStateInterference_outputfiles')
            filesOrDirsOperate.makesureDirExist(dirPath)
            localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            filePath = os.path.join(dirPath, r'steady_state_output_{}.txt'.format(localTime))
            steadyStateRecognizeT = algorithmThreads.steadyStateRecognizeProcess(self.algorithmProcessQ,
                                                                                 self.steadyStateData[0],
                                                                                 self.steadyStateData[1],
                                                                                 self.lineEdit_16.text(),
                                                                                 filePath)
            steadyStateRecognizeT.start()
            # 调用loading
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            # while self.algorithmProcessQ.empty() or self.savingProcessQ.empty():
            while self.algorithmProcessQ.empty():
                gui()
            else:
                loading.close()
                self.steadyStateHistoryData.append(self.steadyStateData)  # 历史数据表更新
                reslt = self.algorithmProcessQ.get()
                self.steadyStateHistoryResult.append(reslt)  # 历史识别记录表更新
                self.steadyStateTab.pushButton(self.steadyStateHistoryResult)
                #####置入绘图####
                if not self.steadyStatePicStateFlag == 0:
                    # 如果图区有图，不管是原图还是结果图，都刷掉
                    self.verticalLayout_30.removeWidget(self.steadyStateFig)
                    self.steadyStateFig.deleteLater()
                    self.steadyStateFig = None
                self.steadyStateFig = plotWithCursor.getPos('after',
                                                            self.steadyStateData[0],
                                                            self.steadyStateData[1],
                                                            self.lineEdit_16.text())
                self.verticalLayout_30.addWidget(self.steadyStateFig)
                self.steadyStatePicStateFlag = 3
                self.logger.info("稳态干扰判断结束")

    # 稳态干扰历史查看
    def on_pushButton_clicked_20(self):
        if not self.steadyTabRowNum.empty():
            if self.steadyStateHistoryFigFlag:
                self.verticalLayout_32.removeWidget(self.steadyStateHistoryFig)
                self.steadyStateHistoryFig.deleteLater()
                self.steadyStateHistoryFig = None
            rowNum = self.steadyTabRowNum.get()
            data = self.steadyStateHistoryData[rowNum]
            self.steadyStateHistoryFig = plotWithCursor.getPos('history',
                                                            data[0],
                                                            data[1])
            self.verticalLayout_32.addWidget(self.steadyStateHistoryFig)
            self.steadyStateHistoryFigFlag = 1
        else:
            QMessageBox.warning(self, "提示", "请先双击需查看的行")

    #稳态干扰刷新
    def on_pushButton_clicked_21(self):
        '''信号图区清空'''
        if self.steadyStatePicStateFlag:
            self.verticalLayout_30.removeWidget(self.steadyStateFig)
            self.steadyStateFig.deleteLater()
            self.steadyStateFig = None
            self.steadyStatePicStateFlag = 0 # 信号图像标志位
        '''历史图区清空'''
        if self.steadyStateHistoryFigFlag:
            self.verticalLayout_32.removeWidget(self.steadyStateHistoryFig)
            self.steadyStateHistoryFig.deleteLater()
            self.steadyStateHistoryFig = None
            self.steadyStateHistoryFigFlag = 0
        '''表区清空'''
        if self.steadyStateTableFlag:
            self.verticalLayout_31.removeWidget(self.steadyStateTab)
            self.steadyStateTab.deleteLater()
            self.steadyStateTab = None
            self.steadyStateTableFlag = 0
        '''全局变量清空'''
        self.steadyStateHistoryData = []
        self.steadyStateHistoryResult = []
        '''行号监听队列清空'''
        self.steadyTabRowNum.queue.clear()
        '''输入框清空'''
        self.lineEdit_12.clear()
        self.lineEdit_13.clear()
        self.lineEdit_17.clear()
        self.lineEdit_16.clear()

    # usrp1, 48h频谱监测
    def on_pushButton_clicked_23(self):
        usrpNum = "1"
        startfreq = self.lineEdit_27.text()
        endfreq = self.lineEdit_26.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 25):
                startfreq = startfreq * 1000000
                endfreq = endfreq * 1000000
                msg = (usrpNum + ',scan,specMonitor,'
                       + str(startfreq) + ";" + str(endfreq))
                zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                             args=(self.usrpCommu, msg, self.zmqLocalQ))
                zmqThread.start()
                while self.zmqLocalQ.empty():
                    pass
                else:
                    paraRepStartReslt = self.zmqLocalQ.get()
                    # print(paraRepStartReslt)
                    if paraRepStartReslt == 'paraSocket {} build failed'.format(usrpNum) or paraRepStartReslt == '超时':
                        QMessageBox.warning(self, '错误：', '子窗口通信建立失败！\n {}'.format(paraRepStartReslt))
                        return 0
                    elif paraRepStartReslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    else:
                        paraSocket = zmqLocal.localZMQ(paraRepStartReslt)
                        # 弹出子窗口
                        dbFilesRootDir = os.path.join(self.fatherPath, 'EMCfile')
                        self.childWindowDic[usrpNum] = waterfallDialogEngin.WaterfallDialog(usrpNum, paraSocket,
                                                                                startfreq, endfreq, dbFilesRootDir)
                        # self.childWindow = waterfallDialogEngin.WaterfallDialog()
                        self.childWindowDic[usrpNum].signal.connect(self.waterfallDialogCloseSlot)
                        self.childWindowDic[usrpNum].show()

                        # 开启循环任务
                        self.circulateT = threading.Timer(1, self.childWindowDic[usrpNum].circulate)
                        self.circulateT.start()
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

    # usrp2, 48h频谱监测
    def on_pushButton_clicked_24(self):
        usrpNum = "2"
        startfreq = self.lineEdit_29.text()
        endfreq = self.lineEdit_28.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            # if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 25):
            startfreq = startfreq * 1000000
            endfreq = endfreq * 1000000
            msg = (usrpNum + ',scan,specMonitor,'
                   + str(startfreq) + ";" + str(endfreq))
            zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                         args=(self.usrpCommu, msg, self.zmqLocalQ))
            zmqThread.start()
            while self.zmqLocalQ.empty():
                pass
            else:
                paraRepStartReslt = self.zmqLocalQ.get()
                # print(paraRepStartReslt)
                if paraRepStartReslt == 'paraSocket {} build failed'.format(usrpNum) or paraRepStartReslt == '超时':
                    QMessageBox.warning(self, '错误：', '子窗口通信建立失败！\n {}'.format(paraRepStartReslt))
                    return 0
                elif paraRepStartReslt == "":
                    QMessageBox.warning(self,
                                        '错误',
                                        "设备未启用！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                    return 0
                else:
                    paraSocket = zmqLocal.localZMQ(paraRepStartReslt)
                    # 弹出子窗口
                    dbFilesRootDir = os.path.join(self.fatherPath, 'EMCfile')
                    self.childWindowDic[usrpNum] = waterfallDialogEngin.WaterfallDialog(usrpNum, paraSocket,
                                                                            startfreq, endfreq, dbFilesRootDir)
                    # self.childWindow = waterfallDialogEngin.WaterfallDialog()
                    self.childWindowDic[usrpNum].signal.connect(self.waterfallDialogCloseSlot)
                    self.childWindowDic[usrpNum].show()

                    # 开启循环任务
                    self.circulateT = threading.Timer(1, self.childWindowDic[usrpNum].circulate)
                    self.circulateT.start()
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # usrp3, 48h频谱监测
    def on_pushButton_clicked_25(self):
        usrpNum = "3"
        startfreq = self.lineEdit_31.text()
        endfreq = self.lineEdit_30.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            # if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 25):
            startfreq = startfreq * 1000000
            endfreq = endfreq * 1000000
            msg = (usrpNum + ',scan,specMonitor,'
                   + str(startfreq) + ";" + str(endfreq))
            zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                         args=(self.usrpCommu, msg, self.zmqLocalQ))
            zmqThread.start()
            while self.zmqLocalQ.empty():
                pass
            else:
                paraRepStartReslt = self.zmqLocalQ.get()
                # print(paraRepStartReslt)
                if paraRepStartReslt == 'paraSocket {} build failed'.format(usrpNum) or paraRepStartReslt == '超时':
                    QMessageBox.warning(self, '错误：', '子窗口通信建立失败！\n {}'.format(paraRepStartReslt))
                    return 0
                elif paraRepStartReslt == "":
                    QMessageBox.warning(self,
                                        '错误',
                                        "设备未启用！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                    return 0
                else:
                    paraSocket = zmqLocal.localZMQ(paraRepStartReslt)
                    # 弹出子窗口
                    dbFilesRootDir = os.path.join(self.fatherPath, 'EMCfile')
                    self.childWindowDic[usrpNum] = waterfallDialogEngin.WaterfallDialog(usrpNum, paraSocket,
                                                                                        startfreq, endfreq,
                                                                                        dbFilesRootDir)
                    # self.childWindow = waterfallDialogEngin.WaterfallDialog()
                    self.childWindowDic[usrpNum].signal.connect(self.waterfallDialogCloseSlot)
                    self.childWindowDic[usrpNum].show()

                    # 开启循环任务
                    self.circulateT = threading.Timer(1, self.childWindowDic[usrpNum].circulate)
                    self.circulateT.start()
            # else:
            # QMessageBox.warning(self,
            #                     '错误',
            #                     "请输入正确参数！",
            #                     QMessageBox.Yes,
            #                     QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # usrp4, 48h频谱监测
    def on_pushButton_clicked_26(self):
        usrpNum = "4"
        startfreq = self.lineEdit_22.text()
        endfreq = self.lineEdit_23.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            # if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 25):
            startfreq = startfreq * 1000000
            endfreq = endfreq * 1000000
            msg = (usrpNum + ',scan,specMonitor,'
                   + str(startfreq) + ";" + str(endfreq))
            zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                         args=(self.usrpCommu, msg, self.zmqLocalQ))
            zmqThread.start()
            while self.zmqLocalQ.empty():
                pass
            else:
                paraRepStartReslt = self.zmqLocalQ.get()
                # print(paraRepStartReslt)
                if paraRepStartReslt == 'paraSocket {} build failed'.format(usrpNum) or paraRepStartReslt == '超时':
                    QMessageBox.warning(self, '错误：', '子窗口通信建立失败！\n {}'.format(paraRepStartReslt))
                    return 0
                elif paraRepStartReslt == "":
                    QMessageBox.warning(self,
                                        '错误',
                                        "设备未启用！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
                    return 0
                else:
                    paraSocket = zmqLocal.localZMQ(paraRepStartReslt)
                    # 弹出子窗口
                    dbFilesRootDir = os.path.join(self.fatherPath, 'EMCfile')
                    self.childWindowDic[usrpNum] = waterfallDialogEngin.WaterfallDialog(usrpNum, paraSocket,
                                                                                        startfreq, endfreq,
                                                                                        dbFilesRootDir)
                    # self.childWindow = waterfallDialogEngin.WaterfallDialog()
                    self.childWindowDic[usrpNum].signal.connect(self.waterfallDialogCloseSlot)
                    self.childWindowDic[usrpNum].show()

                    # 开启循环任务
                    self.circulateT = threading.Timer(1, self.childWindowDic[usrpNum].circulate)
                    self.circulateT.start()
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 3900, 48h频谱监测
    def on_pushButton_clicked_85(self):
        deviceNum = "3900"
        startfreq = self.lineEdit_76.text()
        endfreq = self.lineEdit_75.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            # if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 25):
            startfreq = startfreq * 1000000
            endfreq = endfreq * 1000000
            msg = (deviceNum + ',scan,specMonitor,'
                   + str(startfreq) + ";" + str(endfreq))
            # zmqThread = threading.Thread(target=zmqLocal.zmqThread,
            #                              args=(self.usrpCommu, msg, self.zmqLocalQ))
            # zmqThread.start()
            # while self.zmqLocalQ.empty():
            #     pass
            # else:
            #     paraRepStartReslt = self.zmqLocalQ.get()
                # print(paraRepStartReslt)
                # dosnt work
            # if paraRepStartReslt == 'paraSocket {} build failed'.format(deviceNum) or paraRepStartReslt == '超时':
            #     QMessageBox.warning(self, '错误：', '子窗口通信建立失败！\n {}'.format(paraRepStartReslt))
            # else:
            paraSocket = self.av3900Commu
            # 弹出子窗口
            dbFilesRootDir = os.path.join(self.fatherPath, 'EMCfile')
            self.childWindowDic[deviceNum] = waterfallDialogEnginFor3900.WaterfallDialog(deviceNum, paraSocket,
                                                                                msg,
                                                                                dbFilesRootDir)
            # self.childWindow = waterfallDialogEngin.WaterfallDialog()
            self.childWindowDic[deviceNum].signal.connect(self.waterfallDialogCloseSlot)
            self.childWindowDic[deviceNum].show()

            # 开启循环任务
            self.circulateT = threading.Timer(1, self.childWindowDic[deviceNum].circulate)
            self.circulateT.start()
        else:
            QMessageBox.warning(self,
                                '错误',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    def on_pushButton_clicked_42(self):
        self.picoSpecWindow = WaterFallForPico.ApplicationWindow(os.path.join(self.fatherPath, r'pico-waterfall-data\\'),
                                os.path.join(self.fatherPath, "EMCfile"))
        self.picoSpecWindow.show()

    def waterfallDialogCloseSlot(self, signalContent):
        self.logger.info('瀑布图{}号子窗口关闭'.format(signalContent))
        self.childWindowDic[signalContent] = ""

    # 时域图采集
    def on_pushButton_clicked_34(self):
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            # time = QTimer(self)
        except Exception as e:
            self.logger.error(e)

    # 时域图绘图
    def on_pushButton_clicked_35(self):
        dirPath = os.path.join(self.fatherPath, r'realpart_recvfiles')
        # 判断文件夹中是否有文件
        lists = os.listdir(dirPath)
        self.logger.debug("时域监测绘图文件数：" + str(len(lists)))
        if not len(lists) == 0:
            for path in lists:
                if '.csv' in path:
                    ####################
                    if self.realpart_flag:
                        # 标志位为1时清空图区
                        self.verticalLayout_33.removeWidget(self.realpart_fig)
                        self.realpart_fig = the_48h_realpart_inQt.MaxminRealpart(
                            dirPath, self.logger)
                        self.verticalLayout_33.addWidget(self.realpart_fig)
                        self.path = ''
                    else:
                        self.realpart_fig = the_48h_realpart_inQt.MaxminRealpart(
                            dirPath, self.logger)
                        self.verticalLayout_33.addWidget(self.realpart_fig)
                        self.realpart_flag = 1
                        self.path = ''
                    ####################
                    break
                else:
                    QMessageBox.warning(self, '错误', '请先采集数据', )
                    break
        else:
            QMessageBox.warning(self, '错误', '请先采集数据')

    # 时域图清空数据
    def on_pushButton_clicked_62(self):
        dirPath = os.path.join(self.fatherPath, r'realpart_recvfiles')
        self.logger.info("时域监测数据清空，路径"+dirPath)
        shutil.rmtree(dirPath)
        time.sleep(1)
        os.mkdir(dirPath)

    # 实时频谱查看 单次扫频
    def on_pushButton_clicked_27(self):
        while not self.zmqLocalQ.empty():
            self.zmqLocalQ.get()
        starttime = datetime.datetime.now()
        startfreq = self.lineEdit_20.text()
        endfreq = self.lineEdit_21.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq < endfreq and startfreq >= 30 and endfreq <= 5000:
                startfreq = startfreq*1000000
                endfreq = endfreq*1000000
                deviceNum = self.comboBox_8.currentText()
                msg = (deviceNum + ',scan,IQ,'
                          + str(startfreq) + ";" +str(endfreq))
                communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu,
                                                                            self.av3900Commu)
                communicationThread.start()
                # 调用loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
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
                        return 0
                    elif reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    else:
                        resltList = reslt.split(';')
                        self.scanRslt = resltList
                        freqList = resltList[0].split(' ')
                        binsList = resltList[1].split(" ")
                        self.onlineSpecX = [float(i) for i in freqList]
                        self.onlineSpecY = [float(i) for i in binsList]
                        #####置入绘图####
                        if self.realtimeSpecViewFigFlag:
                            self.verticalLayout_27.removeWidget(self.realtimeSpecViewFig)
                        self.realtimeSpecViewFig = plotWithCursor.getPos('history', self.onlineSpecX,
                                                                 self.onlineSpecY)
                        self.verticalLayout_27.addWidget(self.realtimeSpecViewFig)
                        self.realtimeSpecViewFigFlag = 1
                        endtime = datetime.datetime.now()
                        strTime = '实时频谱查看扫频结束，耗时:%dms' % (
                                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                        self.logger.info(strTime)
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

    # 实时频谱查看 连续扫频
    def on_pushButton_clicked_32(self):
        startfreq = self.lineEdit_20.text()
        endfreq = self.lineEdit_21.text()
        deviceNum = self.comboBox_8.currentText()

        self.realtimeSpecViewStopFlag = 0
        if self.pushButton_32.text() == "连续扫频":
            if isNum(startfreq) and isNum(endfreq):
                startfreq = float(startfreq)
                endfreq = float(endfreq)
                if startfreq < endfreq and startfreq >= 30 and endfreq <= 5000:
                    self.pushButton_32.setText("停止扫频")
                    startfreq = startfreq * 1000000
                    endfreq = endfreq * 1000000
                    msg = (deviceNum + ',scan,IQ,'
                           + str(startfreq) + ";" + str(endfreq))
                    dataCach = queue.Queue()
                    condition = threading.Condition()
                    waitNum = 2
                    notifyNum = 1
                    self.circultaionZmqThread = circulationZmqThread.CircultaionZmqThread(self.usrpCommu,
                                                                                          self.av3900Commu,
                                                                                          msg, dataCach,
                                                                                          condition, waitNum)
                    self.circultaionZmqThread.start()

                    #####置入绘图####
                    if self.realtimeSpecViewFigFlag:
                        self.verticalLayout_27.removeWidget(self.realtimeSpecViewFig)
                    self.realtimeSpecViewFig = realtimeSpecView.ApplicationWindow(condition, notifyNum, dataCach)
                    self.verticalLayout_27.addWidget(self.realtimeSpecViewFig)
                    self.realtimeSpecViewFig._start()

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

        elif self.pushButton_32.text() == "停止扫频":
            self.realtimeSpecViewFig._stop()
            self.verticalLayout_27.removeWidget(self.realtimeSpecViewFig)
            self.verticalLayout_27.update()
            self.realtimeSpecViewFigFlag = 0
            if self.circultaionZmqThread is not None:
                self.circultaionZmqThread.stop()
                self.circultaionZmqThread = None
            self.pushButton_32.setText("连续扫频")

    # 实时频谱分析开始/停止绘图
    def on_pushButton_clicked_37(self):
        if self.pushButton_37.text() == "开始绘图":
            self.pushButton_37.setText("停止绘图")
            # 确认是否存储数据及存储路径初始化
            dirPath = ""
            if self.comboBox_11.currentText() == "是":
                self.realtimeSpecAnalyzeDataSaveFlag = 1
                dirPath = os.path.join(self.fatherPath, "realtime_recvfiles")
            else:
                self.realtimeSpecAnalyzeDataSaveFlag = 0
            # 开启数据采集线程，使用Q作为异步数据池，暴露停止方法
            startfreq = self.lineEdit_24.text()
            endfreq = self.lineEdit_25.text()
            deviceNum = self.comboBox_9.currentText()
            if isNum(startfreq) and isNum(endfreq):
                startfreq = float(startfreq)
                endfreq = float(endfreq)
                if startfreq < endfreq and startfreq >= 30 and endfreq <= 5000:
                    startfreq = startfreq * 1000000
                    endfreq = endfreq * 1000000
                    msg = (deviceNum + ',scan,IQ,'
                           + str(startfreq) + ";" + str(endfreq))
                    dataCach = queue.Queue()
                    condition = threading.Condition()
                    waitNum = sys.maxsize
                    notifyNum = 2
                    self.circultaionZmqThread = circulationZmqThread.CircultaionZmqThread(self.usrpCommu,
                                                                                          self.av3900Commu,
                                                                                          msg, dataCach,
                                                                                          condition, waitNum,
                                                                                          dataNumPerCell=5)
                    self.circultaionZmqThread.start()
                    # 开启绘图线程，使用Q作为异步数据池，暴露停止方法
                    ####################
                    if self.specAnalyze_flag:
                        self.specAnalyze_fig._timer.stop()
                        # 标志位为1时清空图区
                        self.verticalLayout_35.removeWidget(self.specAnalyze_fig)
                        self.specAnalyze_fig = spec_analyze_v3.ApplicationWindow(self.realtimeSpecAnalyzeDataSaveFlag,
                                                                                 dirPath, condition, notifyNum, dataCach)
                        self.verticalLayout_35.addWidget(self.specAnalyze_fig)
                        self.specAnalyze_fig._start()
                    else:
                        self.specAnalyze_fig = spec_analyze_v3.ApplicationWindow(self.realtimeSpecAnalyzeDataSaveFlag,
                                                                                 dirPath, condition, notifyNum, dataCach)
                        self.verticalLayout_35.addWidget(self.specAnalyze_fig)
                        self.specAnalyze_fig._start()
                        self.specAnalyze_flag = 1
                    ####################
                    pass
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
        elif self.pushButton_37.text() == "停止绘图":
            self.pushButton_37.setText("开始绘图")
            self.circultaionZmqThread.stop()
            # 绘图线程停止
            if self.specAnalyze_flag:
                self.specAnalyze_fig._stop()

    # 干扰对消在线
    def on_pushButton_clicked_29(self):
        if self.comboBox_7.currentText() == self.comboBox_12.currentText():
            QMessageBox.warning(self, '提示', "请选择不同的一体化单元！")
        else:
            deviceNum1 = self.comboBox_7.currentText()
            deviceNum2 = self.comboBox_12.currentText()
            deviceList = [deviceNum1, deviceNum2]
            startfreq = self.lineEdit_19.text()
            endfreq = self.lineEdit_38.text()
            if isNum(startfreq) and isNum(endfreq):
                startfreq = float(startfreq)
                endfreq = float(endfreq)
                if (startfreq < endfreq and startfreq >= 30 and endfreq <= 5000 and (endfreq - startfreq) <= 100):
                    startfreq = startfreq * 1000000
                    endfreq = endfreq * 1000000
                    msg = (',scan,plural,'
                           + str(startfreq) + ";" + str(endfreq))
                    pluralcommunicationThread = pluralCommunicationProxy.PluralCommunicationProxy(deviceList,
                                                                                                  msg, self.zmqLocalQ,
                                                                                                  self.usrpCommu,
                                                                                                  self.av3900Commu)
                    pluralcommunicationThread.start()
                    # 调用loading
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
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
                            return 0
                        elif reslt == "":
                            QMessageBox.warning(self,
                                                '错误',
                                                "设备未启用！",
                                                QMessageBox.Yes,
                                                QMessageBox.Yes)
                            return 0
                        data = reslt.split("|")
                        data1 = data[0]
                        data2 = data[1]
                        interferenceCancellationT = algorithmThreads.interferenceCancellationProcess(
                            self.algorithmProcessQ, (data1, data2))
                        interferenceCancellationT.start()
                        # 调用loading
                        loading = Message.Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        gui = QGuiApplication.processEvents
                        while self.algorithmProcessQ.empty():
                            gui()
                        else:
                            loading.close()
                            xyList = self.algorithmProcessQ.get()
                            #####置入绘图####
                            if self.interferenceCancellationFigFlag:
                                self.verticalLayout_25.removeWidget(self.getPosition)
                                self.getPosition.deleteLater()
                            self.getPosition = plotWithCursor.getPos('history', xyList[0], xyList[1])
                            self.verticalLayout_42.addWidget(self.getPosition)
                            self.interferenceCancellationFigFlag = 1
                else:
                    QMessageBox.warning(self,
                                        '错误1',
                                        "请输入正确参数！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)
            else:
                QMessageBox.warning(self,
                                '错误2',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 干扰对消离线
    def on_pushButton_clicked_41(self):
        if self.lineEdit_18.text() and self.lineEdit_39.text():
            path1 = self.lineEdit_18.text()
            path2 = self.lineEdit_39.text()
            if os.path.exists(path1) and os.path.exists(path2):
                try:
                    while not self.algorithmProcessQ.empty():
                        self.algorithmProcessQ.get()
                    interferenceCancellationT = algorithmThreads.interferenceCancellationProcess(self.algorithmProcessQ,
                                                                                                 (path1, path2))
                    interferenceCancellationT.start()
                    # 调用loading
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
                    while self.algorithmProcessQ.empty():
                        gui()
                    else:
                        loading.close()
                        xyList = self.algorithmProcessQ.get()
                        #####置入绘图####
                        if self.interferenceCancellationFigFlag:
                            self.verticalLayout_25.removeWidget(self.getPosition)
                            self.getPosition.deleteLater()
                        self.getPosition = plotWithCursor.getPos('history', xyList[0], xyList[1])
                        self.verticalLayout_42.addWidget(self.getPosition)
                        self.interferenceCancellationFigFlag = 1
                        self.logger.info("干扰对消结束")
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

    # 干扰对消选择文件1
    def on_pushButton_clicked_30(self):
        self.lineEdit_18.clear()
        defultPath = os.path.join(self.fatherPath, r'antenna_compare_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.logger.info("干扰对消选择文件1："+filename)
        self.lineEdit_18.setText(filename)

    # 干扰对消选择文件2
    def on_pushButton_clicked_31(self):
        self.lineEdit_39.clear()
        defultPath = os.path.join(self.fatherPath, r'antenna_compare_recvfiles')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.logger.info("干扰对消选择文件2："+filename)
        self.lineEdit_39.setText(filename)

    # 信噪比分析采集计算
    def on_pushButton_clicked_36(self):
        starttime = datetime.datetime.now()
        # 请求数据，调用算法
        deviceNum = self.comboBox_10.currentText()
        centrefreq = self.lineEdit_32.text()
        bandwidth = self.lineEdit_33.text()
        sampleRate = self.lineEdit_34.text()
        if isNum(centrefreq) and isNum(bandwidth) and isNum(sampleRate):
            centrefreq = float(centrefreq)
            bandwidth = float(bandwidth)
            sampleRate = float(sampleRate)
            if centrefreq <= 5000 and centrefreq >= 30:
                centrefreq = centrefreq * 1000000
                bandwidth = bandwidth * 1000000
                sampleRate = sampleRate * 1000000
                msg = (deviceNum + ',collect,IQsingle,' + str(centrefreq) + ";" + str(bandwidth)
                       + ";" + str(sampleRate))
                communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ,
                                                                            self.usrpCommu, self.av3900Commu)
                communicationThread.start()
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    loading.close()
                    reslt = self.SNRData = self.zmqLocalQ.get()
                    if reslt == "超时":
                        QMessageBox.warning(self,
                                            '错误',
                                            "本地连接超时！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    elif reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    else:
                        while not self.algorithmProcessQ.empty():
                            self.algorithmProcessQ.get()
                        # 开启识别进程/线程
                        recognizeProcess = algorithmThreads.SNREstimationIntegrationThread(reslt,
                                                                                           self.algorithmProcessQ)
                        recognizeProcess.start()
                        # 调用识别loading
                        loading = Message.Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        while self.algorithmProcessQ.empty():
                            gui()
                        else:
                            loading.close()
                            recognizeResult = self.algorithmProcessQ.get()
                            # self.logger.debug("信噪比分析结果："+recognizeResult)
                            self.lineEdit_36.setText(recognizeResult)
                            endtime = datetime.datetime.now()
                            strTime = '信噪比分析结束，结果：'+("%.1f" % recognizeResult)+'，耗时:%dms' % (
                                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                            self.logger.debug(strTime)
            else:
                QMessageBox.warning(self,
                                    '错误1',
                                    "请输入正确参数！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '错误2',
                                "请输入正确参数！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 信噪比分析保存数据
    def on_pushButton_clicked_40(self):
        if self.SNRData == '':
            QMessageBox.warning(self,
                                '错误',
                                "无数据！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)
        else:
            while not self.savingProcessQ.empty():
                self.savingProcessQ.get()
            dirPath = os.path.join(self.fatherPath, r'SNR_data')
            filesOrDirsOperate.makesureDirExist(dirPath)
            SNRSavingThread = algorithmThreads.SNRDataSave(self.SNRData, dirPath,
                                                           "SNR_data", self.savingProcessQ)
            SNRSavingThread.start()
            loading = Message.Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            gui = QGuiApplication.processEvents
            loading.show()
            while self.savingProcessQ.empty():
                gui()
            else:
                loading.close()
                self.logger.info("信噪比数据存储成功，路径：{}".format(self.savingProcessQ.get()))
                self.SNRData = ''

    # 信噪比分析选择文件
    def on_pushButton_clicked_38(self):
        self.lineEdit_35.clear()
        defultPath = os.path.join(self.fatherPath, r'SNR_data')
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  defultPath, "*.txt")
        self.logger.info("信噪比分析选择文件："+filename)
        self.lineEdit_35.setText(filename)

    # 信噪比分析离线计算
    def on_pushButton_clicked_39(self):
        # 读取文件中的数据，调用算法
        starttime = datetime.datetime.now()
        if self.lineEdit_35.text():
            filePath = self.lineEdit_35.text()
            if os.path.exists(filePath):
                while not self.algorithmProcessQ.empty():
                    self.algorithmProcessQ.get()
                # 开启识别进程/线程
                recognizeProcess = algorithmThreads.SNREstimationIntegrationThread(filePath,
                                                                                   self.algorithmProcessQ)
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
                    # self.logger.debug("信噪比分析结果："+recognizeResult)
                    self.lineEdit_36.setText(recognizeResult)
                    endtime = datetime.datetime.now()
                    strTime = '信噪比离线分析结束，结果：' + ("%.1f" % recognizeResult) + '，耗时:%dms' % (
                            (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
                    self.logger.info(strTime)
            else:
                QMessageBox.warning(self,
                                    '错误1',
                                    "所选路径无文件！",
                                    QMessageBox.Yes,
                                    QMessageBox.Yes)
        else:
            QMessageBox.warning(self,
                                '错误2',
                                "请先选择文件！",
                                QMessageBox.Yes,
                                QMessageBox.Yes)

    # 天线比对
    def on_pushButton_clicked_28(self):
        # 初始化空的数据请求字典，用来存储设备名和天线名
        deviceName = self.comboBox_6.currentText()
        antenna1 = "antenna1"
        antenna2 = "antenna2"
        startfreq = self.lineEdit_14.text()
        endfreq = self.lineEdit_15.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq > 30 and endfreq < 5000 and startfreq < endfreq:
                startfreq = startfreq * 1000000
                endfreq = endfreq * 1000000
                msg = (deviceName+',scan,antennaCompare,' + str(startfreq) + ";" + str(endfreq))
                # 调用通信代理，传入数据请求字典、采集指令内容和等待结果队列
                while not self.zmqLocalQ.empty():
                    self.zmqLocalQ.get()
                communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ,self.usrpCommu,self.av3900Commu)
                communicationThread.start()
                # 等待回传
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    loading.close()
                    reslt = self.zmqLocalQ.get()
                    if reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    dataRsltList = reslt.split("|")
                    paramList = dataRsltList
                    remark = deviceName
                    localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                    dirPath = os.path.join(self.fatherPath, r'antenna_compare_recvfiles/{}/'.format(localTime))
                    filesOrDirsOperate.makesureDirExist(dirPath)
                    while not self.savingProcessQ.empty():
                        self.savingProcessQ.get()
                    savingThread = algorithmThreads.compareSaveProcess(paramList, remark, dirPath, self.savingProcessQ)
                    savingThread.start()
                    # 调用识别loading
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
                    while self.savingProcessQ.empty():
                        gui()
                    else:
                        loading.close()
                    self.logger.info(u"天线比对采集结束,数据存储于" + self.savingProcessQ.get())
                    #####置入绘图####
                    if self.antennaCompareFigFlag:
                        self.verticalLayout_41.removeWidget(self.antennaComparePic)
                        self.antennaComparePic.deleteLater()
                    self.antennaComparePic = compare_draw.ApplicationWindow(dataRsltList, deviceName)
                    self.verticalLayout_41.addWidget(self.antennaComparePic)
                    self.antennaCompareFigFlag = 1
            else:
                QMessageBox.warning(self, '错误', "请输入正确参数！")
        else:
            QMessageBox.warning(self, '错误', "请输入正确参数！")

    # 天线比对选择文件夹
    def on_pushButton_clicked_46(self):
        self.lineEdit_37.clear()
        defultPath = os.path.join(self.fatherPath, r'antenna_compare_recvfiles')
        dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹", defultPath)
        self.logger.info("天线比对选择文件夹：" + dirpath)
        self.lineEdit_37.setText(dirpath)

    # 天线比对离线
    def on_pushButton_clicked_44(self):
        # 初始化空的数据请求字典，用来存储设备名和天线名
        antenna1 = "antenna1"
        antenna2 = "antenna2"
        if self.lineEdit_37.text():
            dirpath = self.lineEdit_37.text()
            #####置入绘图####
            if self.antennaCompareFigFlag:
                self.verticalLayout_41.removeWidget(self.antennaComparePic)
                self.antennaComparePic.deleteLater()
            self.antennaComparePic = compare_draw.ApplicationWindow([dirpath], '')
            self.verticalLayout_41.addWidget(self.antennaComparePic)
            self.antennaCompareFigFlag = 1
            # else:
            #     QMessageBox.warning(self, '错误', "请输入正确参数！")
        else:
            QMessageBox.warning(self, '提示', "请先选择文件夹！")

    # 设备比对
    def on_pushButton_clicked_33(self):
        # 初始化空的数据请求字典，用来存储设备名和天线名
        deviceList = []
        device1 = "USRP1"
        device2 = "USRP2"
        device3 = "USRP3"
        device4 = "USRP4"
        # antenna1 = "antenna1"
        # antenna2 = "antenna2"
        # 生成数据请求字典
        if self.checkBox.isChecked():
            deviceList.append(device1)
            # currentDeviceName = "USRP1"
            # if (not self.checkBox_6.isChecked()) and (not self.checkBox_7.isChecked()):
            #     QMessageBox.warning(self, '错误', "{}未选中天线！".format(currentDeviceName))
            #     return 0
            # else:
            #     compareReqDic[currentDeviceName] = []
            #     if self.checkBox_6.isChecked():
            #         compareReqDic[currentDeviceName].append(antenna1)
            #     elif self.checkBox_7.isChecked():
            #         compareReqDic[currentDeviceName].append(antenna2)
        if self.checkBox_2.isChecked():
            deviceList.append(device2)
        if self.checkBox_3.isChecked():
            deviceList.append(device3)
        if self.checkBox_4.isChecked():
            deviceList.append(device4)
        if (not self.checkBox.isChecked()) and (not self.checkBox_2.isChecked()) and (not self.checkBox_3.isChecked()) and (not self.checkBox_4.isChecked()):
            QMessageBox.warning(self, '错误', "未选择设备！")
            return 0
        if len(deviceList) < 2:
            QMessageBox.warning(self, '错误', "请选择至少两个设备！")
            return 0
        startfreq = self.lineEdit_74.text()
        endfreq = self.lineEdit_73.text()
        if isNum(startfreq) and isNum(endfreq):
            startfreq = float(startfreq)
            endfreq = float(endfreq)
            if startfreq > 30 and endfreq < 5000 and startfreq < endfreq:
                startfreq = startfreq * 1000000
                endfreq = endfreq * 1000000
                # msgHead = ";".join(deviceList)
                msg = (',scan,plural,' + str(startfreq) + ";" + str(endfreq))
                # 调用通信代理，传入数据请求字典、采集指令内容和等待结果队列
                communicationThread = pluralCommunicationProxy.PluralCommunicationProxy(deviceList,
                                                                                        msg, self.zmqLocalQ,
                                                                            self.usrpCommu, self.av3900Commu)
                communicationThread.start()
                # 等待回传
                # 调用识别loading
                loading = Message.Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.zmqLocalQ.empty():
                    gui()
                else:
                    loading.close()
                    reslt = self.zmqLocalQ.get()
                    if reslt == "":
                        QMessageBox.warning(self,
                                            '错误',
                                            "设备未启用！",
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
                        return 0
                    dataRsltList = reslt.split("|")
                    paramList = dataRsltList
                    remark = "RF2"
                    localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                    dirPath = os.path.join(self.fatherPath, r'device_compare_recvfiles/{}/'.format(localTime))
                    filesOrDirsOperate.makesureDirExist(dirPath)
                    while not self.savingProcessQ.empty():
                        self.savingProcessQ.get()
                    savingThread = algorithmThreads.compareSaveProcess(paramList, remark, dirPath, self.savingProcessQ)
                    savingThread.start()
                    # 调用识别loading
                    loading = Message.Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
                    while self.savingProcessQ.empty():
                        gui()
                    else:
                        loading.close()
                    self.logger.info(u"设备比对采集结束,数据存储于" + self.savingProcessQ.get())
                    #####置入绘图####
                    if self.deviceCompareFigFlag:
                        self.verticalLayout_39.removeWidget(self.deviceComparePic)
                        self.deviceComparePic.deleteLater()
                    self.deviceComparePic = compare_draw.ApplicationWindow(dataRsltList, "RF2")
                    self.verticalLayout_39.addWidget(self.deviceComparePic)
                    self.deviceCompareFigFlag = 1
            else:
                QMessageBox.warning(self, '错误', "请输入正确参数！")
        else:
            QMessageBox.warning(self, '错误', "请输入正确参数！")

    # 设备比对选择文件夹
    def on_pushButton_clicked_47(self):
        self.lineEdit_40.clear()
        defultPath = os.path.join(self.fatherPath, r'device_compare_recvfiles')
        dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹", defultPath)
        self.logger.info("设备比对选择文件夹：" + dirpath)
        self.lineEdit_40.setText(dirpath)

    # 设备比对离线
    def on_pushButton_clicked_45(self):
        # 初始化空的数据请求字典，用来存储设备名和天线名
        antenna1 = "antenna1"
        antenna2 = "antenna2"
        if self.lineEdit_40.text():
            dirpath = self.lineEdit_40.text()
            #####置入绘图####
            if self.deviceCompareFigFlag:
                self.verticalLayout_39.removeWidget(self.deviceComparePic)
                self.deviceComparePic.deleteLater()
            self.deviceComparePic = compare_draw.ApplicationWindow([dirpath], "")
            self.verticalLayout_39.addWidget(self.deviceComparePic)
            self.deviceCompareFigFlag = 1
            # else:
            #     QMessageBox.warning(self, '错误', "请输入正确参数！")
        else:
            QMessageBox.warning(self, '提示', "请先选择文件夹！")

    # 重写关闭事件
    def closeEvent(self, event):
        # os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务

        # socketThread = threading.Thread(target=zmqLocal.zmqThread,
        #                                 args=(self.zmqLocal, "StopAll", self.zmqLocalQ), daemon=True)
        # socketThread.start()
        # while not self.zmqLocalQ.empty():
        #     sys.exit()
        #     break
        self.usrpCommu.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
