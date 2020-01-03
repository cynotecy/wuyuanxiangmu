# -*- coding: utf-8 -*-
import os
import queue
import sys
import time
from threading import Thread
import shutil
import _thread
import threading
from PyQt5.QtCore import QThread

import PyQt5.QtGui
import pymysql
import sip
import win32api
import zmq
from PyQt5.QtCore import Qt, QFileInfo, QTimer
from PyQt5.QtGui import QCursor, QIcon, QGuiApplication
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMessageBox, QTableWidgetItem, QFileDialog, QProgressDialog, \
    QApplication

from Message import Loading
from MessageForOc import OcLoading
from SNR import snrDrawPic
from SNR.SNR_Estimate import SNR_finally
from Ui.UitoPy.Ui_MainWindow import Ui_MainWindow
from Ui.file_ui import show_png
from Wave import UsrpProcess, OcUsrpProcess, PicoProcess_online, PicoProcess_offline, specEnvelopeProcess, steadyStateInterference
from controller.Pico_controller.draw_pic import draw_pic
from controller.usrp_controller.specEnvelope_shibie import specEnvelopeDrawpic
from controller.usrp_controller.steadyStateInterference_shibie import steadyFirst_draw, steadyResult_draw, display_v4
from database_upload import wirelessDialog, equipDialog, envelopeDialog, steadyDialog
from monitor.The48hRealPart import the_48h_realpart_inQt
from monitor.waterfall import WaterFall, WaterFallForPico
from function import filesOrDirsOperate
from plotTools import Timer, spec, antenna_draw
from spectrum_analyze import spec_analyze_v2
from controller.usrp_controller.usrp_shibie import oc_list_getting_v1,oc_list_display_v1


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.showFullScreen()
        self.showMaximized()
        self.showMaximized()
        self.pushButton_16.setEnabled(True)
        self.pushButton_26.setEnabled(True)
        self.pushButton_50.setEnabled(True)
        ## 初始化socket连接，用来检测仪器连接状况
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://192.168.0.5:7000")######根据实际情况更改ip

        self.poll = zmq.Poller()# 超时判断
        self.poll.register(self.socket, zmq.POLLIN)
        ##
        self.path = ''# 初始化路径，将路径置空
        ## 图像标志位们，用来判断布局中是否有画布
        self.pic_flag = 0# 脉冲识别
        self.steadyStateInterference = 0  # 稳态干扰识别
        self.waterfallusrp1_flag = 0
        self.waterfallusrp2_flag = 0
        self.waterfallpico_flag = 0
        self.plotToolIQ_flag = 0
        self.plotToolTime_flag = 0
        self.plotToolSpec_flag = 0
        self.realpart_flag = 0# 时域最值图
        self.specEnvelope_flag = 0# 频域包络识别信号图
        self.specEnvelope_sample_fig_id = ''# 频谱包络识别样本图
        self.specAnalyze_flag = 0# 频谱仪
        self.steadyStateInterference_flag = 0  # 稳态干扰识别当前信号图
        self.steadyStateInterference_lastfig_flag = 0   # 稳态干扰识别当前信号图（按种类划分：在线、离线、选择、结果）
        self.steadyState_tab_flag = 0   # 稳态干扰表格
        self.steadyState_origFig_flag = 0  # 稳态干扰历史图
        self.oldSsiResult = []  # 稳态干扰历史结果全局变量，用于给表格传参
        self.allSsiPath = []    # 稳态干扰历史文件路径全局变量，用于双击表格行显示该行对应的图像
        self.antenna_flag = 0# 天线对比图
        self.antenna_usrp_flag = 0# 天线usrp连接状况
        self.antenna_mode_flag = 0# 天线模式标志位，用来决定画图时读最新的四个文件还是最新两个文件
        self.snr_flag = 0# 信噪比
        self.oc_display1_flag = 0# 超频点列表第一次显示
        print(self.oc_display1_flag)
        ##
        ########时间标志们，用来判断在线识别是否在线
        self.currenttime = 0#usrp IQ
        self.currenttime_envelope = 0
        self.currenttime_steadyState = 0
        #########

        self.q = queue.Queue()# FIFO队列
        self.rowNum = queue.Queue()# 稳态干扰识别专用FIFO
        self.oc_fileQuantity_infolder = queue.Queue() # 超频点文件夹扫描队列，当文件夹中的文件数达到要求时该队列被置入文件数目
        self.oc_rowNum_select = 0# 超频点选择
        self.class_name = ''
        # 设置状态栏图标以及message
        icon = QIcon(':/图标/ooopic_1521110980.ico')
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(icon)
        self.trayIcon.show()
        self.trayIcon.showMessage("Success", "程序启动成功")
        # 设置windows任务栏图标
        import ctypes
        # 这个窗口强制使用单独的AppUserModelID ，拥有了一个新资源支配权限，可单独拥有任务栏图标。
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        # 设置无边框且点击任务栏图标可以最小化
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowSystemMenuHint|Qt.WindowMinimizeButtonHint)
        # 设定结果显示表格列宽
        # IQ识别结果
        self.tableWidget_3.setColumnWidth(4, 280)
        self.tableWidget_3.setColumnWidth(3, 280)
        self.tableWidget_3.setColumnWidth(2, 280)
        self.tableWidget_3.setColumnWidth(1, 280)
        self.tableWidget_3.setColumnWidth(0, 280)
        # 包络识别结果
        self.tableWidget_7.setColumnWidth(0, 280)
        self.tableWidget_7.setColumnWidth(1, 230)
        self.tableWidget_7.setColumnWidth(2, 230)
        self.tableWidget_7.setColumnWidth(3, 280)
        # 开关脉冲识别
        self.tableWidget_6.setColumnWidth(0, 280)
        self.tableWidget_6.setColumnWidth(1, 230)
        # 信噪比
        self.tableWidget_5.setColumnWidth(0, 280)
        self.tableWidget_5.setColumnWidth(1, 230)

        self.pushButton_17.clicked.connect(self.on_pushButton_clicked_17)#USRP
        self.pushButton_48.clicked.connect(self.on_pushButton_clicked_48)  # 频域包络
        self.pushButton_22.clicked.connect(self.on_pushButton_clicked_22)#信噪比
        self.pushButton_24.clicked.connect(self.on_pushButton_clicked_24)#脉冲
        self.pushButton_55.clicked.connect(self.on_pushButton_clicked_55)  # 稳态干扰
        # 开始识别
        # self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)#ESMD
        self.pushButton_65.clicked.connect(self.on_pushButton_clicked_65)  # IQ超频点查看
        self.pushButton_66.clicked.connect(self.on_pushButton_clicked_66)  # IQ超频点识别

        self.pushButton_39.clicked.connect(self.on_pushButton_clicked_39)  # IQ手动在线
        self.pushButton_18.clicked.connect(self.on_pushButton_clicked_18)# IQ手动离线
        self.pushButton_47.clicked.connect(self.on_pushButton_clicked_47)  # 频域包络在线
        self.pushButton_49.clicked.connect(self.on_pushButton_clicked_49)  # 频域包络离线
        self.pushButton_23.clicked.connect(self.on_pushButton_clicked_23)#信噪比
        self.pushButton_38.clicked.connect(self.on_pushButton_clicked_38)  # 脉冲在线
        self.pushButton_25.clicked.connect(self.on_pushButton_clicked_25)#脉冲离线
        self.pushButton_53.clicked.connect(self.on_pushButton_clicked_53)  # 稳态干扰在线
        self.pushButton_54.clicked.connect(self.on_pushButton_clicked_54)  # 稳态干扰离线
        self.pushButton_56.clicked.connect(self.listeningTab)#稳态干扰历史查看
        self.pushButton_60.clicked.connect(self.on_pushButton_clicked_60)  # 稳态干扰刷新
        # usrp采集
        self.pushButton_51.clicked.connect(self.on_pushButton_clicked_51)  # 连接检测
        self.pushButton_26.clicked.connect(self.on_pushButton_clicked_16)# IQ自动、手动识别
        self.pushButton_16.clicked.connect(self.on_pushButton_clicked_16)  # IQ自动、手动识别
        self.pushButton_50.clicked.connect(self.on_pushButton_clicked_50)# 频域包络
        # pico采集
        # self.pushButton_19.clicked.connect(self.on_pushButton_clicked_19)# IQ
        self.pushButton_33.clicked.connect(self.on_pushButton_clicked_33)# 脉冲识别
        self.pushButton_52.clicked.connect(self.on_pushButton_clicked_52)  # 稳态干扰识别
        # 48h监测
        self.pushButton_30.clicked.connect(self.on_pushButton_clicked_30)# 连接检测
        self.pushButton_31.clicked.connect(self.on_pushButton_clicked_31)  # 调用usrp1
        self.pushButton_32.clicked.connect(self.on_pushButton_clicked_32)  # 调用usrp2
        self.pushButton_40.clicked.connect(self.on_pushButton_clicked_40)  # 调用pico
        self.pushButton_57.clicked.connect(self.on_pushButton_clicked_57)  # USRP1清空数据库及文件夹
        self.pushButton_58.clicked.connect(self.on_pushButton_clicked_58)  # USRP2清空数据库及文件夹
        self.pushButton_59.clicked.connect(self.on_pushButton_clicked_59)  # pico清空数据库及文件夹
        # 时域最值图
        self.pushButton_34.clicked.connect(self.on_pushButton_clicked_34)# 采集
        self.pushButton_35.clicked.connect(self.on_pushButton_clicked_35)# 绘图
        self.pushButton_62.clicked.connect(self.on_pushButton_clicked_62)  # 数据清空
        # 实时频谱监测
        self.pushButton_36.clicked.connect(self.on_pushButton_clicked_36)  # 采集
        self.pushButton_37.clicked.connect(self.on_pushButton_clicked_37)  # 绘图
        self.pushButton_63.clicked.connect(self.on_pushButton_clicked_63)  # 数据清空
        # 记录上传
        # self.pushButton_26.clicked.connect(self.wireless_signal_upload)# ESMD
        self.pushButton_27.clicked.connect(self.wireless_signal_upload)# IQ
        self.pushButton_41.clicked.connect(self.envelope_signal_upload)  # 包络
        # self.pushButton_28.clicked.connect(self.wireless_signal_upload)# 示波器
        self.pushButton_29.clicked.connect(self.equipment_signal_upload)# 脉冲识别
        self.pushButton_42.clicked.connect(self.steady_signal_upload)# 稳态干扰识别
        ## 工具
        # 选择文件
        # self.pushButton_41.clicked.connect(self.on_pushButton_clicked_41)  # IQ
        self.pushButton_43.clicked.connect(self.on_pushButton_clicked_43)  # Timer
        self.pushButton_45.clicked.connect(self.on_pushButton_clicked_45)  # Spec
        # 画图
        # self.pushButton_42.clicked.connect(self.on_pushButton_clicked_42)  # IQ
        self.pushButton_44.clicked.connect(self.on_pushButton_clicked_44)  # Timer
        self.pushButton_46.clicked.connect(self.on_pushButton_clicked_46)  # Spec
        # 切换天线
        self.pushButton_61.clicked.connect(self.on_pushButton_clicked_61) # 采集
        self.pushButton_64.clicked.connect(self.on_pushButton_clicked_64) # 绘图

    # 重写全屏方法
    def showMaximized(self):
        # 得到桌面控件
        desktop = PyQt5.QtWidgets.QApplication.desktop()
        # 得到屏幕可显示尺寸
        rect = desktop.availableGeometry()
        # 设置窗口尺寸
        self.setGeometry(rect)
        # 设置窗口显示
        self.show()

    # 仪器连接图展示
    def on_pushButton_clicked_3(self):
        try:
            png = show_png.Example()
            png.my_UI()
        except:
            reply = QMessageBox.warning(self,
                                        '错误',
                                        "连接示意图打开失败！",
                                        QMessageBox.Yes,
                                        QMessageBox.Yes)


    # 信噪比识别选择文件
    def on_pushButton_clicked_22(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\usrp_recvfiles\usrp_scan", "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        newItem = QTableWidgetItem(self.name)
        self.tableWidget_5.setItem(0, 0, newItem)

    # 信噪比识别按键
    def on_pushButton_clicked_23(self):
        try:
            if not self.path:
                QMessageBox.information(self, "提示", "请选择文件")
            elif not self.lineEdit_17.text():
                QMessageBox.information(self, "提示", "请输入带宽")
            else:
                bdwidth = float(self.lineEdit_17.text())
                print(bdwidth)
                SNR = SNR_finally(self.path, bdwidth, self.q)
                SNR.start()
                print('snr start')
                loading = Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    loading.close()
                    # box.button(QMessageBox.Ok)
                    QMessageBox.information(self, "提示", "判断完毕")
                    newItem1 = QTableWidgetItem(self.q.get())
                    self.tableWidget_5.setItem(0, 1, newItem1)
                    ##############画信号图###############
                    if self.snr_flag:
                        # 标志位为1时清空图区
                        self.verticalLayout_18.removeWidget(self.snrfig)
                        sip.delete(self.snrfig)
                        self.snrfig = snrDrawPic.ApplicationWindow(self.path)
                        self.verticalLayout_18.addWidget(self.snrfig)
                        self.snr_flag = 1
                        self.path = ''
                    else:
                        self.snrfig = snrDrawPic.ApplicationWindow(self.path)
                        self.verticalLayout_18.addWidget(self.snrfig)
                        self.snr_flag = 1
                        self.path = ''
                    ##############

                    # self.path = ""
        except:
            QMessageBox.information(self, "提示", "请正确输入带宽")

    # IQ采集检查仪器连接
    def on_pushButton_clicked_51(self):
        self.socket.send(str.encode('Imok'))
        socks = dict(self.poll.poll(3000))
        if socks.get(self.socket) == zmq.POLLIN:
            result = bytes.decode(self.socket.recv())  # addr: 192.168.10.2 192.168.20.2
            # self.socket.close()
            print(result)
            if '192.168.10.2' in result:
                QMessageBox.information(self, '检测完成', "usrp已连接，ip为192.168.10.2")
                self.pushButton_16.setEnabled(True)
                self.pushButton_26.setEnabled(True)
                self.pushButton_50.setEnabled(True)
            else:
                QMessageBox.information(self, '检测完成', "没有设备连接")
        else:
            # self.socket.close()
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)

            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect("tcp://192.168.0.5:7000")  ######根据实际情况更改ip

            self.poll = zmq.Poller()  # 超时判断
            self.poll.register(self.socket, zmq.POLLIN)
            QMessageBox.information(self, '检测失败', "请重新检测")


    # usrp数据采集按键    注：此按键将弹出另一个窗口
    # 移植时注意更改路径
    def on_pushButton_clicked_16(self):
        self.currenttime = time.time()
        usrp_collect = usrpCollect()
        usrp_collect.start()

    # IQ超频点查看
    def on_pushButton_clicked_65(self):
        dirPath = r"..\usrp_recvfiles\threshold"
        fileType = 'txt'
        filePath = ''
        filesOrDirsOperate.makesureDirExist(dirPath)
        if filesOrDirsOperate.dirNotEmpty(fileType, dirPath):
            filePath = filesOrDirsOperate.getLatestFile(fileType, dirPath)
            print('在位置' + "'" + filePath + "'" + '读取门限文件')
            self.oc_list = oc_list_getting_v1.position(filePath)
            print('超频点列表为' + str(self.oc_list))
            print('列表区域是否存在列表：' + str(self.oc_display1_flag))
            if self.oc_list:
                if self.oc_display1_flag:
                    self.verticalLayout_46.removeWidget(self.oc_display1)
                    sip.delete(self.oc_display1)
                    self.oc_display1 = oc_list_display_v1.WindowClass()
                    self.oc_display1.pushButton(self.oc_list)
                    self.verticalLayout_46.addWidget(self.oc_display1)
                    self.oc_display1_flag = 1
                else:
                    self.oc_display1 = oc_list_display_v1.WindowClass()
                    self.oc_display1.pushButton(self.oc_list)
                    self.verticalLayout_46.addWidget(self.oc_display1)
                    self.oc_display1_flag = 1
            else:
                QMessageBox.warning(self, "结果：", "门限位置无信号")
        else:
            QMessageBox.warning(self, "错误", "文件位置%s未找到频谱文件" % dirPath)
        del filePath, dirPath, fileType

    # IQ超频点识别
    # 采集识别一步到位
    def on_pushButton_clicked_66(self):
        os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
        # 当界面上有表格显示时
        if self.oc_display1_flag:
            # 获取行号
            self.oc_rowNum_select = self.oc_display1.getRow()
            print('用户选中的行为:', self.oc_rowNum_select)
            if self.oc_rowNum_select:
                ##################辅助文件写入，即将中心频率和带宽存入辅助文件供py2脚本读取
                dirPath = r"..\usrp_recvfiles\oc_selected_rows"
                filesOrDirsOperate.makesureDirExist(dirPath)
                fw = open((dirPath + "\collectList.txt"), 'w')  # 将要输出保存的文件地址
                for i in range(len(self.oc_rowNum_select)):
                    rowName_ = self.oc_rowNum_select[i]
                    centreWrite = float(self.oc_list[0][rowName_][2])
                    start = float(self.oc_list[0][rowName_][0])
                    print('start=', start)
                    end = float(self.oc_list[0][rowName_][1])
                    print('end=', end)
                    bdwidthWrite = int((end - start)*1000000)
                    if bdwidthWrite>2e6:
                        bdwidthWrite = 2e6
                    elif bdwidthWrite<2e5:
                        bdwidthWrite = 2e5
                    print('bdwidth=', bdwidthWrite)
                    fw.write(str(centreWrite) + ' ')
                    fw.write(str(bdwidthWrite) + '\n')
                fw.close()
                ##################辅助文件写入完毕#################
                rowQuantity = len(self.oc_rowNum_select)# 记录一共有多少行被选中
                # 清空采集文件夹
                dirName = r'..\usrp_recvfiles\auto_recognize'
                filesOrDirsOperate.cleanDir(dirName)
                # 调用py2批量采集脚本
                ocCollectThread = OcCollectThread()
                ocCollectThread.start()
                ########文件夹扫描线程，用来看py2是否采集完毕
                # 开启文件夹扫描线程,将文件夹中的文件数与rowQuantity比较，相等时在self.oc_fileQuantity_infolder中置入文件数目
                _thread.start_new_thread(filesOrDirsOperate.floderScanThread, (dirName, rowQuantity, self.oc_fileQuantity_infolder,))
                #############采集loading线程
                selectLoading = OcLoading(self.oc_fileQuantity_infolder)
                selectLoading.setWindowModality(Qt.ApplicationModal)
                selectLoading.show()
                gui = QGuiApplication.processEvents
                while self.oc_fileQuantity_infolder.empty():
                    gui()
                else:
                    time.sleep(3)
                    rturn = self.oc_fileQuantity_infolder.get()
                    selectLoading.close()
                    if rturn == "HeSaidStop":
                        ocCollectThread.terminate()
                        print('采集线程运行：', ocCollectThread.isRunning())
                        os.system('taskkill /f /t /im python2.exe')# 杀掉python2任务
                    else:
                        print('采集完毕，共', rturn, '个文件')
                        # print(self.q.empty())
                        # 采集结束，调用识别脚本
                        ocShibie = OcUsrpProcess(self.q)
                        ocShibie.start()
                        ###########采集loading结束
                        # 调用识别loading
                        loading = Loading()
                        loading.setWindowModality(Qt.ApplicationModal)
                        loading.show()
                        gui = QGuiApplication.processEvents
                        while self.q.empty():
                            gui()
                        else:
                            loading.close()
                            os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务
                            # 识别结束开始显示
                            recognizeResult = self.q.get()
                            print('识别结果为：', recognizeResult)
                            if len(self.oc_rowNum_select) > 1:
                                for i in range(len(recognizeResult)):
                                    rowName = int(self.oc_rowNum_select[i])
                                    item1 = QTableWidgetItem(recognizeResult[i][2])  # 调制方式
                                    item2 = QTableWidgetItem(recognizeResult[i][3])  # 频点识别
                                    self.oc_display1.tableWidget.setItem(rowName, 3, item1)
                                    self.oc_display1.tableWidget.setItem(rowName, 4, item2)
                            elif len(self.oc_rowNum_select) == 1:
                                rowName = int(self.oc_rowNum_select[0])
                                item1 = QTableWidgetItem(recognizeResult[0][2])  # 调制方式
                                item2 = QTableWidgetItem(recognizeResult[0][3])  # 频点识别
                                self.oc_display1.tableWidget.setItem(rowName, 3, item1)
                                self.oc_display1.tableWidget.setItem(rowName, 4, item2)
                        QMessageBox.information(self, "提示", "识别完毕")
            else:
                QMessageBox.warning(self, "提示", "请先选择超频点")
        else:
            QMessageBox.warning(self,"错误", "请先查看超频点，生成超频点列表。")

    # usrp在线识别按键
    def on_pushButton_clicked_39(self):
        self.tableWidget_3.clearContents()
        dirPath = r'..\usrp_recvfiles'
        filesOrDirsOperate.makesureDirExist(dirPath)
        if filesOrDirsOperate.dirNotEmpty('dat', dirPath):
            fileLatest = filesOrDirsOperate.getLatestFile('dat', dirPath)
            self.path = fileLatest
            try:
                self.usrp = UsrpProcess(self.path, self.q)
                self.usrp.start()
                loading = Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    loading.close()
                    QMessageBox.information(self, "提示", "识别完毕")
                    resltList = self.q.get()
                    #############TXT输出##############
                    self.localtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                    outPutPath = '..\IqOutput'
                    filesOrDirsOperate.makesureDirExist(outPutPath)
                    filename = (outPutPath + '\IQoutput_%s.txt') % self.localtime
                    fw = open(filename, 'w')
                    print('IQ输出存储于：', filename)
                    fw.write('中心频率' + resltList[0] + '(MHz) ;')
                    fw.write('带宽' + resltList[1] + '(Hz) ;')
                    fw.write('调制方式' + resltList[2] + ' ;')
                    fw.write('频点识别' + resltList[3] + ' ;')
                    fw.close()
                    #################################
                    newItem = QTableWidgetItem(resltList[0])
                    self.tableWidget_3.setItem(0, 1, newItem)
                    newItem = QTableWidgetItem(resltList[1])
                    self.tableWidget_3.setItem(0, 2, newItem)
                    newItem = QTableWidgetItem(resltList[2])
                    self.tableWidget_3.setItem(0, 3, newItem)
                    newItem = QTableWidgetItem(resltList[3])
                    self.tableWidget_3.setItem(0, 4, newItem)
                    self.path = ""
            except:
                pass
        else:
            print('no file')
            QMessageBox.warning(self, "错误", "文件位置%s未找到数据文件" % dirPath)

    # usrp选择文件
    def on_pushButton_clicked_17(self):
        self.tableWidget_3.clearContents()
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\usrp_recvfiles", "*.dat")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        newItem = QTableWidgetItem(self.name)
        self.tableWidget_3.setItem(0, 0, newItem)

    # usrp离线识别按键
    # 不同系统间的移植，注意'\'、'/'的写法，Windows应用'\'，Linux应用'/'
    def on_pushButton_clicked_18(self):
        if not self.path:
            QMessageBox.information(self, "提示", "请选择文件")
        else:
            if not os.path.exists(self.path):
                QMessageBox.warning(self, "错误", "指定路径%s中没有文件" % self.path)
            else:
                self.usrp = UsrpProcess(self.path, self.q)
                self.usrp.start()
                loading = Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    loading.close()
                    QMessageBox.information(self, "提示", "识别完毕")
                    reslt_list = self.q.get()
                    #############TXT输出##############
                    self.localtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                    outPutPath = '..\IqOutput'
                    filesOrDirsOperate.makesureDirExist(outPutPath)
                    filename = (outPutPath + '\IQoutput_%s.txt') % self.localtime
                    f = open(filename, 'w')
                    print('IQ输出存储于：', filename)
                    f.write('中心频率' + reslt_list[0] + '(MHz) ;')
                    f.write('带宽' + reslt_list[1] + '(Hz) ;')
                    f.write('调制方式' + reslt_list[2] + ' ;')
                    f.write('频点识别' + reslt_list[3] + ' ;')
                    f.close()
                    #################################
                    newItem = QTableWidgetItem(reslt_list[0])
                    self.tableWidget_3.setItem(0, 1, newItem)
                    newItem = QTableWidgetItem(reslt_list[1])
                    self.tableWidget_3.setItem(0, 2, newItem)
                    newItem = QTableWidgetItem(reslt_list[2])
                    self.tableWidget_3.setItem(0, 3, newItem)
                    newItem = QTableWidgetItem(reslt_list[3])
                    self.tableWidget_3.setItem(0, 4, newItem)
                    self.path = ""

    # 频域包络采集按键
    def on_pushButton_clicked_50(self):
        self.currenttime_envelope = time.time()
        usrp_specEnvelope = usrpScan_specEnvelope()
        usrp_specEnvelope.start()

    # 频域包络在线识别按键
    def on_pushButton_clicked_47(self):
        self.tableWidget_7.clearContents()
        dataPath = r'..\specEnvelope_recvfiles'
        filesOrDirsOperate.makesureDirExist(dataPath)
        if filesOrDirsOperate.dirNotEmpty('txt', dataPath):
            self.path = filesOrDirsOperate.getLatestFile('txt', dataPath)
            self.specEnvelope = specEnvelopeProcess(self.path, self.q)
            self.specEnvelope.start()
            loading = Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.q.empty():
                gui()
            else:
                loading.close()
                QMessageBox.information(self, "提示", "识别完毕")
                results = self.q.get()
                if len(results) == 1:
                    print(results)
                    print(type(results))
                    newItem1 = QTableWidgetItem(str(results[0]))
                    self.tableWidget_7.setItem(0, 1, newItem1)
                    # 识别不出结果或超限时，且图区有图，则清空图区
                    if self.specEnvelope_flag:
                        self.verticalLayout_22.removeWidget(self.specEnvelope_samplefig)
                        sip.delete(self.specEnvelope_samplefig)
                        self.specEnvelope_flag = 0
                elif len(results) == 6:
                    newItem1 = QTableWidgetItem(results[0])
                    newItem2 = QTableWidgetItem(str(results[1]))
                    newItem3 = QTableWidgetItem(str(results[5][0])+','+str(results[5][1]))
                    self.tableWidget_7.setItem(0, 1, newItem1)
                    self.tableWidget_7.setItem(0, 2, newItem2)
                    self.tableWidget_7.setItem(0, 3, newItem3)
                    signalLimit = results[2]
                    sampleLimit = results[3]
                    sampleInner_id = results[4]
                    ##############画信号图###############
                    # 生成对应的样本图id
                    if len(results) == 6 and results[0] == 'GSM900':
                        self.specEnvelope_sample_fig_id = 5
                    elif len(results) == 6 and results[0] == 'WCDMA':
                        self.specEnvelope_sample_fig_id = 11
                    elif len(results) == 6 and results[0] == 'WLAN(2.4G)':
                        self.specEnvelope_sample_fig_id = 17
                    elif len(results) == 6 and results[0] == 'CDMA800':
                        self.specEnvelope_sample_fig_id = 23
                    elif len(results) == 6 and results[0] == 'TD_SCDMA':
                        self.specEnvelope_sample_fig_id = 29
                    elif len(results) == 6 and results[0] == 'FDD_LTE':
                        self.specEnvelope_sample_fig_id = 32
                    elif len(results) == 6 and results[0] == 'GSM1800':
                        self.specEnvelope_sample_fig_id = 36

                    # 画信号图和样本图
                    if self.specEnvelope_sample_fig_id and self.specEnvelope_flag:
                        # 标志位为1时清空图区
                        self.verticalLayout_22.removeWidget(self.specEnvelope_samplefig)
                        sip.delete(self.specEnvelope_samplefig)
                        self.specEnvelope_samplefig = specEnvelopeDrawpic.ApplicationWindow(self.path,
                                                                                            self.specEnvelope_sample_fig_id, sampleInner_id
                                                                                            , signalLimit, sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelope_samplefig)
                        self.specEnvelope_flag = 1
                        self.specEnvelope_sample_fig_id = ''
                        self.path = ''
                    elif self.specEnvelope_sample_fig_id:
                        self.specEnvelope_samplefig = specEnvelopeDrawpic.ApplicationWindow(self.path,
                                                                                            self.specEnvelope_sample_fig_id, sampleInner_id
                                                                                            , signalLimit, sampleLimit)
                        self.verticalLayout_22.addWidget(self.specEnvelope_samplefig)
                        self.specEnvelope_flag = 1
                        self.path = ''
                        self.specEnvelope_sample_fig_id = ''
                ##############
                    self.path = ""
        else:
            QMessageBox.warning(self, "错误", "文件位置%s未找到数据文件" % dataPath)

    # 频域包络识别选择文件
    def on_pushButton_clicked_48(self):
        self.tableWidget_7.clearContents()
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\specEnvelope_recvfiles", "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        newItem = QTableWidgetItem(self.name)
        self.tableWidget_7.setItem(0, 0, newItem)

    # 频域包络离线识别按键
    def on_pushButton_clicked_49(self):
        if not self.path:
            QMessageBox.information(self, "提示", "请选择文件")
        else:
            if not os.path.exists(self.path):
                QMessageBox.warning(self, "错误", "指定路径%s中没有文件" % self.path)
            else:
                self.specEnvelope = specEnvelopeProcess(self.path, self.q)
                self.specEnvelope.start()
                loading = Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    loading.close()
                    QMessageBox.information(self, "提示", "识别完毕")
                    results = self.q.get()
                    print(results)
                    if len(results) == 1:
                        print(results)
                        print(type(results))
                        newItem1 = QTableWidgetItem(str(results[0]))
                        self.tableWidget_7.setItem(0, 1, newItem1)
                        # 识别不出结果或超限时，且图区有图，则清空图区
                        if self.specEnvelope_flag:
                            self.verticalLayout_22.removeWidget(self.specEnvelope_samplefig)
                            sip.delete(self.specEnvelope_samplefig)
                            self.specEnvelope_flag = 0
                    elif len(results) == 6:
                        newItem1 = QTableWidgetItem(results[0])
                        newItem2 = QTableWidgetItem(str(results[1]))
                        newItem3 = QTableWidgetItem(str(results[5][0]) + ',' + str(results[5][1]))
                        self.tableWidget_7.setItem(0, 1, newItem1)
                        self.tableWidget_7.setItem(0, 2, newItem2)
                        self.tableWidget_7.setItem(0, 3, newItem3)
                        signalLimit = results[2]
                        sampleLimit = results[3]
                        sampleInner_id = results[4]
                        ##############画信号图###############
                        if len(results) == 6 and results[0] == 'GSM900':
                            self.specEnvelope_sample_fig_id = 5
                        elif len(results) == 6 and results[0] == 'WCDMA':
                            self.specEnvelope_sample_fig_id = 11
                        elif len(results) == 6 and results[0] == 'WLAN(2.4G)':
                            self.specEnvelope_sample_fig_id = 17
                        elif len(results) == 6 and results[0] == 'CDMA800':
                            self.specEnvelope_sample_fig_id = 23
                        elif len(results) == 6 and results[0] == 'TD_SCDMA':
                            self.specEnvelope_sample_fig_id = 29
                        elif len(results) == 6 and results[0] == 'FDD_LTE':
                            self.specEnvelope_sample_fig_id = 32
                        elif len(results) == 6 and results[0] == 'GSM1800':
                            self.specEnvelope_sample_fig_id = 36

                        print(self.specEnvelope_sample_fig_id)
                        if self.specEnvelope_sample_fig_id and self.specEnvelope_flag:
                            # 标志位为1时清空图区
                            self.verticalLayout_22.removeWidget(self.specEnvelope_samplefig)
                            sip.delete(self.specEnvelope_samplefig)
                            self.specEnvelope_samplefig = specEnvelopeDrawpic.ApplicationWindow(self.path, self.specEnvelope_sample_fig_id, sampleInner_id
                                                                                                , signalLimit, sampleLimit)
                            self.verticalLayout_22.addWidget(self.specEnvelope_samplefig)
                            self.specEnvelope_flag = 1
                            self.specEnvelope_sample_fig_id = ''
                            self.path = ''
                        elif self.specEnvelope_sample_fig_id:
                            self.specEnvelope_samplefig = specEnvelopeDrawpic.ApplicationWindow(self.path, self.specEnvelope_sample_fig_id, sampleInner_id
                                                                                                , signalLimit, sampleLimit)
                            self.verticalLayout_22.addWidget(self.specEnvelope_samplefig)
                            self.specEnvelope_flag = 1
                            self.path = ''
                            self.specEnvelope_sample_fig_id = ''
                    ##############
                    self.path = ""

    # PicoScope6示波器采集按键
    def on_pushButton_clicked_19(self):
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            time = QTimer(self)
            self.pushButton_19.setEnabled(False)
        except:
            pass

        def forbidden():
            self.pushButton_19.setEnabled(True)

        time.setInterval(10000)
        time.start()
        time.timeout.connect(forbidden)

    # 脉冲识别数据采集
    def on_pushButton_clicked_33(self):
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            time = QTimer(self)
            self.pushButton_33.setEnabled(False)
        except:
            pass

        def forbidden():
            self.pushButton_33.setEnabled(True)

        time.setInterval(10000)
        time.start()
        time.timeout.connect(forbidden)

    # 脉冲在线识别按键
    def on_pushButton_clicked_38(self):
        try:
            length = '10'
            self.path = r'..\interference_file\matfile'
            self.pp_on = PicoProcess_online(self.path, self.q, length)
            self.pp_on.start()
            loading = Loading()
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QGuiApplication.processEvents
            while self.q.empty():
                gui()
            else:
                result = self.q.get()
                target_file_path = self.q.get()
                target_file = target_file_path
                print(result)
                print(target_file)
                loading.close()
                if result == '0':
                    QMessageBox.warning(self, "错误", "文件夹中没有文件，请先采集！")
                else:
                    QMessageBox.information(self, "提示", "识别完毕")
                    if result == 'fan':
                        self.display = '风扇'
                    elif result == 'power':
                        self.display = '电源'
                    elif result == 'WD_200':
                        self.display = 'WD_200'
                    elif result == 'shipeiqi':
                        self.display = '适配器'
                    newItem = QTableWidgetItem(self.display)
                    self.tableWidget_6.setItem(0, 1, newItem)
                    ##############画信号图###############
                    if result == 'fan':
                        self.pulse_sample_fig_id = 1
                    elif result == 'power':
                        self.pulse_sample_fig_id = 2
                    elif result == 'WD_200':
                        self.pulse_sample_fig_id = 3
                    elif result == 'shipeiqi':
                        self.pulse_sample_fig_id = 4
                    if self.pic_flag:
                        # 标志位为1时清空图区
                        self.verticalLayout_20.removeWidget(self.samplefig)
                        sip.delete(self.samplefig)
                        self.samplefig = draw_pic.ApplicationWindow(target_file, self.pulse_sample_fig_id)
                        self.verticalLayout_20.addWidget(self.samplefig)
                        self.pic_flag = 1
                        self.pulse_sample_fig_id = ''
                        self.path = ''
                    else:
                        self.samplefig = draw_pic.ApplicationWindow(target_file, self.pulse_sample_fig_id)
                        self.verticalLayout_20.addWidget(self.samplefig)
                        self.pic_flag = 1
                        self.path = ''
                        self.pulse_sample_fig_id = ''
                    ##############
                    self.path = ""

        except:
            pass

    # 脉冲识别选择文件夹
    def on_pushButton_clicked_24(self):
        self.tableWidget_6.clearContents()
        dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹")
                                                   # ,r"..\interference_file\matfile")
        dirname = dirpath.split('/')[-1]
        print(dirname)
        self.path = dirpath
        newItem = QTableWidgetItem(dirname)
        self.tableWidget_6.setItem(0, 0, newItem)

    # 脉冲离线识别按键
    def on_pushButton_clicked_25(self):
        try:
            if not self.path:
                QMessageBox.information(self, "提示", "请选择文件")
            else:
                length = '10'
                self.pp_off = PicoProcess_offline(self.path, self.q, length)
                self.pp_off.start()
                loading = Loading()
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QGuiApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    result = self.q.get()
                    if result =='0':
                        loading.close()
                        QMessageBox.warning(self, "错误", "文件夹中没有文件！")
                    else:
                        loading.close()
                        QMessageBox.information(self, "提示", "识别完毕")
                        if result == 'fan':
                            self.display = '风扇'
                        elif result == 'power':
                            self.display = '电源'
                        elif result == 'WD_200':
                            self.display = 'WD_200'
                        elif result == 'shipeiqi':
                            self.display = '适配器'
                        newItem = QTableWidgetItem(self.display)
                        self.tableWidget_6.setItem(0, 1, newItem)
                        target_file = self.path
                        ##############画信号图###############
                        if result == 'fan':
                            self.pulse_sample_fig_id = 1
                        elif result == 'power':
                            self.pulse_sample_fig_id = 2
                        elif result == 'WD_200':
                            self.pulse_sample_fig_id = 3
                        elif result == 'shipeiqi':
                            self.pulse_sample_fig_id = 4
                        if self.pic_flag:
                            # 标志位为1时清空图区
                            self.verticalLayout_20.removeWidget(self.samplefig)
                            sip.delete(self.samplefig)
                            self.samplefig = draw_pic.ApplicationWindow(target_file, self.pulse_sample_fig_id)
                            self.verticalLayout_20.addWidget(self.samplefig)
                            self.pic_flag = 1
                            self.pulse_sample_fig_id = ''
                            self.path = ''
                        else:
                            self.samplefig = draw_pic.ApplicationWindow(target_file, self.pulse_sample_fig_id)
                            self.verticalLayout_20.addWidget(self.samplefig)
                            self.pic_flag = 1
                            self.path = ''
                            self.pulse_sample_fig_id = ''
                        ##############
                        self.path = ""

        except:
            pass

    # 稳态干扰识别数据采集
    def on_pushButton_clicked_52(self):
        self.currenttime_steadyState = time.time()
        usrp_collect = usrpScan_steadyStateInterference()
        usrp_collect.start()

    # 稳态干扰在线识别按键
    def on_pushButton_clicked_53(self):
        if self.pushButton_53.text() == '范围选定':
            data_path = r'..\steadyStateInterference_recvfiles'
            lists = os.listdir(data_path)
            txt_list = []
            for path in lists:
                if '.txt' in path:
                    txt_list.append(path)
            if txt_list:
                txt_list.sort(key=lambda fn: os.path.getmtime(data_path + "\\" + fn))
                file_latest = os.path.join(data_path, txt_list[-1])
                create_time = os.path.getmtime(file_latest)
                if self.currenttime_steadyState and create_time > self.currenttime_steadyState:
                    self.path = file_latest
                    ##############画信号图###############
                    if self.steadyStateInterference_flag:
                        print('steadyStateInterference_flag = 1')
                        # 标志位为1时清空图区
                        if self.steadyStateInterference_lastfig_flag == 'online first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_online)
                            sip.delete(self.steadyState_firstFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'online result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_online)
                            sip.delete(self.steadyState_resultFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'offline first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_offline)
                            sip.delete(self.steadyState_firstFig_offline)
                        elif self.steadyStateInterference_lastfig_flag == 'offline result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_offline)
                            sip.delete(self.steadyState_resultFig_offline)
                        self.steadyState_firstFig_online = steadyFirst_draw.ApplicationWindow(self.path)
                        self.verticalLayout_30.addWidget(self.steadyState_firstFig_online)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'online first'
                    else:
                        print('steadyStateInterference_flag = 0')
                        self.steadyState_firstFig_online = steadyFirst_draw.ApplicationWindow(self.path)
                        self.verticalLayout_30.addWidget(self.steadyState_firstFig_online)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'online first'
                    ##############
                    self.pushButton_53.setText('在线识别')
                else:
                    QMessageBox.warning(self, "错误", "请先采集")
            else:
                print('no file')
                QMessageBox.warning(self, "错误", "请先采集")
        else:
            if self.lineEdit_14.text():
                try:
                    float(self.lineEdit_14.text())
                    liney = self.lineEdit_14.text()
                    if self.steadyState_tab_flag:
                        self.verticalLayout_31.removeWidget(self.steadyState_tab)
                        sip.delete(self.steadyState_tab)
                        self.steadyState_tab = display_v4.WindowClass(self.rowNum)
                        self.verticalLayout_31.addWidget(self.steadyState_tab)
                    else:
                        self.steadyState_tab = display_v4.WindowClass(self.rowNum)
                        self.verticalLayout_31.addWidget(self.steadyState_tab)
                        self.steadyState_tab_flag = 1

                    self.ssip = steadyStateInterference(self.path, liney, self.q)
                    self.ssip.start()
                    loading = Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
                    while self.q.empty():
                        gui()
                    else:
                        loading.close()
                        QMessageBox.information(self, "提示", "识别完毕")
                        self.allSsiPath.append(self.path)
                        result = self.q.get()
                        print(result)
                        self.oldSsiResult.append(result)
                        self.steadyState_tab.pushButton(self.oldSsiResult)
                    ##############画信号图###############
                    if self.steadyStateInterference_flag:
                        # 标志位为1时清空图区
                        if self.steadyStateInterference_lastfig_flag == 'online first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_online)
                            sip.delete(self.steadyState_firstFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'online result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_online)
                            sip.delete(self.steadyState_resultFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'offline first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_offline)
                            sip.delete(self.steadyState_firstFig_offline)
                        elif self.steadyStateInterference_lastfig_flag == 'offline result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_offline)
                            sip.delete(self.steadyState_resultFig_offline)
                        print('delete')
                        self.steadyState_resultFig_online = steadyResult_draw.ApplicationWindow(self.path,liney)
                        self.verticalLayout_30.addWidget(self.steadyState_resultFig_online)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'online result'
                        self.path = ''
                    else:
                        self.steadyState_resultFig_online = steadyResult_draw.ApplicationWindow(self.path,liney)
                        self.verticalLayout_30.addWidget(self.steadyState_resultFig_online)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'online result'
                        self.path = ''
                    ##############
                    self.pushButton_53.setText('范围选定')
                except:
                    QMessageBox.warning(self, "错误", "请输入正确参数")
            else:
                QMessageBox.warning(self, "错误", "请输入参数")


    # 稳态干扰识别选择文件
    def on_pushButton_clicked_55(self):
        # self.tableWidget_8.clearContents()
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\steadyStateInterference_recvfiles", "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        # newItem = QTableWidgetItem(self.name)
        # self.tableWidget_8.setItem(0, 0, newItem)

    # 稳态干扰离线识别按键
    def on_pushButton_clicked_54(self):

        # tabListeningThread = Thread(target=self.listeningTab, args=())
        # tabListeningThread.start()
        # self.rowNum.put(0)
        # self.allSsiPath.append(r"D:/postgraduate_program/steadyInterference/Input_file/PC.txt")
        # print("初始化完毕")
        if self.pushButton_54.text() == '范围选定':
            if self.path:
                ##############画信号图###############
                if self.steadyStateInterference_flag:
                    # 标志位为1时清空图区
                    if self.steadyStateInterference_lastfig_flag == 'online first':
                        self.verticalLayout_30.removeWidget(self.steadyState_firstFig_online)
                        sip.delete(self.steadyState_firstFig_online)
                    elif self.steadyStateInterference_lastfig_flag == 'online result':
                        self.verticalLayout_30.removeWidget(self.steadyState_resultFig_online)
                        sip.delete(self.steadyState_resultFig_online)
                    elif self.steadyStateInterference_lastfig_flag == 'offline first':
                        self.verticalLayout_30.removeWidget(self.steadyState_firstFig_offline)
                        sip.delete(self.steadyState_firstFig_offline)
                    elif self.steadyStateInterference_lastfig_flag == 'offline result':
                        self.verticalLayout_30.removeWidget(self.steadyState_resultFig_offline)
                        sip.delete(self.steadyState_resultFig_offline)
                    self.steadyState_firstFig_offline = steadyFirst_draw.ApplicationWindow(self.path)
                    self.verticalLayout_30.addWidget(self.steadyState_firstFig_offline)
                    self.steadyStateInterference_flag = 1
                    self.steadyStateInterference_lastfig_flag = 'offline first'
                else:
                    self.steadyState_firstFig_offline = steadyFirst_draw.ApplicationWindow(self.path)
                    self.verticalLayout_30.addWidget(self.steadyState_firstFig_offline)
                    self.steadyStateInterference_flag = 1
                    self.steadyStateInterference_lastfig_flag = 'offline first'
                    ##############


                # if self.steadyState_origFig_flag:
                #     print('一')
                #     self.verticalLayout_32.removeWidget(self.steadyState_origFig)
                #     sip.delete(self.steadyState_origFig)
                #     self.steadyState_origFig = steadyFirst_draw.ApplicationWindow(path)
                #     self.verticalLayout_32.addWidget(self.steadyState_origFig)
                #     self.steadyState_origFig_flag = 1
                # else:
                #     rowNum = self.rowNum.get()
                #     path = self.allSsiPath[rowNum]
                #     print('二')
                #     print(path)
                #     self.steadyState_origFig = steadyFirst_draw.ApplicationWindow(path)
                #     print(2222222222)
                #     self.verticalLayout_32.addWidget(self.steadyState_origFig)
                #     print(333333333333333)
                #     self.steadyState_origFig_flag = 1
                #     print(self.steadyState_origFig_flag)



                self.pushButton_54.setText('离线识别')
            else:
                QMessageBox.warning(self, "错误", "请先选择文件")
        else:
            if self.lineEdit_16.text():
                try:
                    float(self.lineEdit_16.text())
                    liney = self.lineEdit_16.text()
                    if self.steadyState_tab_flag:
                        self.verticalLayout_31.removeWidget(self.steadyState_tab)
                        sip.delete(self.steadyState_tab)
                        self.steadyState_tab = display_v4.WindowClass(self.rowNum)
                        self.verticalLayout_31.addWidget(self.steadyState_tab)
                    else:
                        self.steadyState_tab = display_v4.WindowClass(self.rowNum)
                        self.verticalLayout_31.addWidget(self.steadyState_tab)
                        self.steadyState_tab_flag = 1

                    self.ssip = steadyStateInterference(self.path, liney, self.q)
                    self.ssip.start()
                    loading = Loading()
                    loading.setWindowModality(Qt.ApplicationModal)
                    loading.show()
                    gui = QGuiApplication.processEvents
                    while self.q.empty():
                        gui()
                    else:
                        loading.close()
                        QMessageBox.information(self, "提示", "识别完毕")
                        self.allSsiPath.append(self.path)
                        result = self.q.get()
                        self.oldSsiResult.append(result)
                        self.steadyState_tab.pushButton(self.oldSsiResult)


                    ##############画信号图###############
                    if self.steadyStateInterference_flag:
                        # 标志位为1时清空图区
                        if self.steadyStateInterference_lastfig_flag == 'online first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_online)
                            sip.delete(self.steadyState_firstFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'online result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_online)
                            sip.delete(self.steadyState_resultFig_online)
                        elif self.steadyStateInterference_lastfig_flag == 'offline first':
                            self.verticalLayout_30.removeWidget(self.steadyState_firstFig_offline)
                            sip.delete(self.steadyState_firstFig_offline)
                        elif self.steadyStateInterference_lastfig_flag == 'offline result':
                            self.verticalLayout_30.removeWidget(self.steadyState_resultFig_offline)
                            sip.delete(self.steadyState_resultFig_offline)
                        self.steadyState_resultFig_offline = steadyResult_draw.ApplicationWindow(self.path, liney)
                        self.verticalLayout_30.addWidget(self.steadyState_resultFig_offline)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'offline result'
                        self.path = ''
                    else:
                        self.steadyState_resultFig_offline = steadyResult_draw.ApplicationWindow(self.path, liney)
                        self.verticalLayout_30.addWidget(self.steadyState_resultFig_offline)
                        self.steadyStateInterference_flag = 1
                        self.steadyStateInterference_lastfig_flag = 'offline result'
                        self.path = ''
                        ##############
                    self.pushButton_54.setText('范围选定')
                except:
                    QMessageBox.warning(self, "错误", "请输入正确参数")
            else:
                QMessageBox.warning(self, "错误", "请输入参数")

    # 稳态干扰鼠标双击事件响应
    def listeningTab(self):
        if not self.rowNum.empty():
            if self.steadyState_origFig_flag:
                rowNum = self.rowNum.get()
                path = self.allSsiPath[rowNum]
                self.verticalLayout_32.removeWidget(self.steadyState_origFig)
                sip.delete(self.steadyState_origFig)
                self.steadyState_origFig = steadyFirst_draw.ApplicationWindow(path)
                self.verticalLayout_32.addWidget(self.steadyState_origFig)
                self.steadyState_origFig_flag = 1
            else:
                rowNum = self.rowNum.get()
                path = self.allSsiPath[rowNum]
                self.steadyState_origFig = steadyFirst_draw.ApplicationWindow(path)
                self.verticalLayout_32.addWidget(self.steadyState_origFig)
                self.steadyState_origFig_flag = 1
        else:
            QMessageBox.warning(self, "提示", "请先双击需查看的行")

    # 稳态干扰刷新
    def on_pushButton_clicked_60(self):
        '''信号图区清空'''
        if self.steadyStateInterference_flag:
            # 标志位为1时清空图区
            if self.steadyStateInterference_lastfig_flag == 'online first':
                self.verticalLayout_30.removeWidget(self.steadyState_firstFig_online)
                sip.delete(self.steadyState_firstFig_online)
            elif self.steadyStateInterference_lastfig_flag == 'online result':
                self.verticalLayout_30.removeWidget(self.steadyState_resultFig_online)
                sip.delete(self.steadyState_resultFig_online)
            elif self.steadyStateInterference_lastfig_flag == 'offline first':
                self.verticalLayout_30.removeWidget(self.steadyState_firstFig_offline)
                sip.delete(self.steadyState_firstFig_offline)
            elif self.steadyStateInterference_lastfig_flag == 'offline result':
                self.verticalLayout_30.removeWidget(self.steadyState_resultFig_offline)
                sip.delete(self.steadyState_resultFig_offline)
            self.steadyStateInterference_flag = 0 # 信号图像标志位
            self.steadyStateInterference_lastfig_flag = 0 # 信号图像类型标志位
            self.path = ''
        '''历史图区清空'''
        if self.steadyState_origFig_flag:
            self.verticalLayout_32.removeWidget(self.steadyState_origFig)
            sip.delete(self.steadyState_origFig)
            self.steadyState_origFig_flag = 0
        '''表区清空'''
        if self.steadyState_tab_flag:
            self.verticalLayout_31.removeWidget(self.steadyState_tab)
            sip.delete(self.steadyState_tab)
            self.steadyState_tab_flag = 0
        '''全局变量清空'''
        self.oldSsiResult = []
        self.allSsiPath = []
        '''按键重置'''
        self.pushButton_53.setText('范围选定')
        self.pushButton_54.setText('范围选定')





    # 仪器连接检查
    def on_pushButton_clicked_30(self):
        self.socket.send(str.encode('Imok'))
        socks = dict(self.poll.poll(3000))
        if socks.get(self.socket) == zmq.POLLIN:
            result = bytes.decode(self.socket.recv())  # addr: 192.168.10.2 192.168.20.2
            # self.socket.close()
            print(result)
            if 'No UHD Device Found' in result:
                print('no usrp')
                QMessageBox.information(self, '检测完成', "没有设备连接")
            elif ('192.168.10.2' in result) and ('192.168.20.2' not in result):
                print('ip为192.168.10.2的usrp已连上')
                self.pushButton_31.setEnabled(True)
                QMessageBox.information(self, '检测完成', "usrp1已连接，ip为192.168.10.2")
            elif ('192.168.20.2' in result) and ('192.168.10.2' not in result):
                print('ip为192.168.20.2的usrp已连上')
                self.pushButton_32.setEnabled(True)
                QMessageBox.information(self, '检测完成', "usrp2已连接，ip为192.168.20.2")
            elif ('192.168.10.2' in result) and ('192.168.20.2' in result):
                QMessageBox.information(self, '检测完成', "usrp1已连接，ip为192.168.10.2\nusrp2已连接，ip为192.168.20.2")
                self.pushButton_31.setEnabled(True)
                self.pushButton_32.setEnabled(True)
        else:
            # self.socket.close()
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)

            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect("tcp://192.168.0.5:7000")  ######根据实际情况更改ip

            self.poll = zmq.Poller()  # 超时判断
            self.poll.register(self.socket, zmq.POLLIN)
            QMessageBox.information(self, '检测失败', "请重新检测")

        # result = bytes.decode(self.socket.recv())# addr: 192.168.10.2 192.168.20.2
        # print(result)
        # # result = result.split(' ')
        # # result.remove(' ')
        # # usrp_nums = len(result)
        # if 'No UHD Device Found' in result:
        #     print('no usrp')
        #     QMessageBox.information(self, '检测完成', "没有设备连接")
        # elif ('192.168.10.2' in result) and ('192.168.20.2' not in result):
        #     print('ip为192.168.10.2的usrp已连上')
        #     self.pushButton_31.setEnabled(True)
        #     QMessageBox.information(self, '检测完成', "usrp1已连接，ip为192.168.10.2")
        # elif ('192.168.20.2' in result) and ('192.168.10.2' not in result):
        #     print('ip为192.168.20.2的usrp已连上')
        #     self.pushButton_32.setEnabled(True)
        #     QMessageBox.information(self, '检测完成', "usrp2已连接，ip为192.168.20.2")
        # elif ('192.168.10.2' in result) and ('192.168.20.2' in result):
        #     QMessageBox.information(self, '检测完成', "usrp1已连接，ip为192.168.10.2\nusrp2已连接，ip为192.168.20.2")
        #     self.pushButton_31.setEnabled(True)
        #     self.pushButton_32.setEnabled(True)
    # usrp1扫频48h
    def on_pushButton_clicked_31(self):
        print("31 pushed")
        usrp1_scan_48h = usrp1Scan_48h()
        usrp1_scan_48h.start()  # 很慢

        ####################
        if self.waterfallusrp1_flag:
            # 标志位为1时清空图区
            self.waterfall_usrp1._timer.stop()# 停止定时任务，防止其一直循环
            self.verticalLayout_7.removeWidget(self.waterfall_usrp1)
            sip.delete(self.waterfall_usrp1)
            self.waterfall_usrp1 = WaterFall.ApplicationWindow('usrp1')
            self.verticalLayout_7.addWidget(self.waterfall_usrp1)
        else:
            self.waterfall_usrp1 = WaterFall.ApplicationWindow('usrp1')
            self.verticalLayout_7.addWidget(self.waterfall_usrp1)
            self.waterfallusrp1_flag = 1
        ####################
    # usrp2扫频48h
    def on_pushButton_clicked_32(self):
        print("32 pushed")
        usrp2_scan_48h = usrp2Scan_48h()
        usrp2_scan_48h.start()  # 很慢
        ####################
        if self.waterfallusrp2_flag:
            # 标志位为1时清空图区
            self.waterfall_usrp2._timer.stop()# 停止定时任务，防止其一直循环
            self.verticalLayout_10.removeWidget(self.waterfall_usrp2)
            sip.delete(self.waterfall_usrp2)
            self.waterfall_usrp2 = WaterFall.ApplicationWindow('usrp2')
            self.verticalLayout_10.addWidget(self.waterfall_usrp2)
        else:
            self.waterfall_usrp2 = WaterFall.ApplicationWindow('usrp2')
            self.verticalLayout_10.addWidget(self.waterfall_usrp2)
            self.waterfallusrp2_flag = 1
        ####################
    # pico扫频48h
    def on_pushButton_clicked_40(self):
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            time = QTimer(self)
            # time2specWaterfall.save_spectrum(r'..\48recv\pico_original')
            # self.pushButton_40.setEnabled(False)
            ####################
            if self.waterfallpico_flag:
                # 标志位为1时清空图区
                self.waterfall_pico._timer.stop()# 停止定时任务，防止其一直循环
                self.verticalLayout_12.removeWidget(self.waterfall_pico)
                sip.delete(self.waterfall_pico)
                self.waterfall_pico = WaterFallForPico.ApplicationWindow(r'..\48recv\pico')
                self.verticalLayout_12.addWidget(self.waterfall_pico)
            else:
                self.waterfall_pico = WaterFallForPico.ApplicationWindow(r'..\48recv\pico')
                self.verticalLayout_12.addWidget(self.waterfall_pico)
                self.waterfallpico_flag = 1
            ####################
        except:
            pass

        def forbidden():
            self.pushButton_19.setEnabled(True)

        time.setInterval(10000)
        time.start()
        time.timeout.connect(forbidden)

    # usrp1清空数据库
    def on_pushButton_clicked_57(self):
        ##############清空数据库表###########
        conn = pymysql.connect(host='localhost',  # ID地址
                                    port=3306,  # 端口号
                                    user='root',  # 用户名
                                    passwd='root',  # 密码
                                    db='cast',  # 库名
                                    charset='utf8')  # 链接字符集
        cur = conn.cursor()  # 创建游标
        delete = 'truncate table `waterfall_data_usrp1`'
        cur.execute(delete)
        cur.close()
        ###################################
        ##############清空数据库磁盘存储#############
        shutil.rmtree(r'..\EMCfile\waterfall\usrp1')
        time.sleep(1)
        os.mkdir(r'..\EMCfile\waterfall\usrp1')
        ##########################################
        ###############清空本地磁盘存储##############
        shutil.rmtree(r'..\48recv\usrp1')
        time.sleep(1)
        os.mkdir(r'..\48recv\usrp1')
        ##########################################


    # usrp2清空数据库
    def on_pushButton_clicked_58(self):
        ##############清空数据库###########
        conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        cur = conn.cursor()  # 创建游标
        delete = 'truncate table `waterfall_data_usrp2`'
        cur.execute(delete)
        cur.close()
        #################################
        ##############清空数据库磁盘存储#############
        shutil.rmtree(r'..\EMCfile\waterfall\usrp2')
        time.sleep(1)
        os.mkdir(r'..\EMCfile\waterfall\usrp2')
        ##########################################
        ###############清空本地磁盘存储##############
        shutil.rmtree(r'..\48recv\usrp2')
        time.sleep(1)
        os.mkdir(r'..\48recv\usrp2')
        ##########################################

    # pico清空数据库
    def on_pushButton_clicked_59(self):
        ###############清空本地磁盘存储##############
        shutil.rmtree(r'..\48recv\pico')
        time.sleep(1)
        os.mkdir(r'..\48recv\pico')
        ##########################################

    # 时域图采集
    def on_pushButton_clicked_34(self):
        print("34 pushed")
        try:
            win32api.ShellExecute(0, "open", "controller\\Pico_controller\\PicoScope 6.lnk", "", "", 1)
            # time = QTimer(self)
        except:
            pass



    # 时域图绘图
    def on_pushButton_clicked_35(self):
        print("35 pushed")
        # 判断文件夹中是否有文件
        lists = os.listdir(r'..\realpart_files\pico')

        if not len(lists) == 0:
            for path in lists:
                if '.csv' in path:
                    ####################
                    if self.realpart_flag:
                        # 标志位为1时清空图区
                        self.verticalLayout_21.removeWidget(self.realpart_fig)
                        sip.delete(self.realpart_fig)
                        self.realpart_fig = the_48h_realpart_inQt.MaxminRealpart(
                            r'..\realpart_files\pico')
                        self.verticalLayout_21.addWidget(self.realpart_fig)
                        self.path = ''
                    else:
                        self.realpart_fig = the_48h_realpart_inQt.MaxminRealpart(
                            r'..\realpart_files\pico')
                        self.verticalLayout_21.addWidget(self.realpart_fig)
                        self.realpart_flag = 1
                        self.path = ''
                    ####################
                    break
                else:
                    QMessageBox.warning(self, '错误','请先采集数据',)
                    break
        else:
            QMessageBox.warning(self, '错误', '请先采集数据')

    # 时域图清空数据
    def on_pushButton_clicked_62(self):
        # try:
        shutil.rmtree(r'..\realpart_files\pico')
        # except:
        #     pass
        # try:
        time.sleep(1)
        os.mkdir(r'..\realpart_files\pico')
        # except:
        #     pass
    # 实时频谱分析采集
    def on_pushButton_clicked_36(self):
        print("36 pushed")
        usrp_scan_time = usrpScan_realtime_spec()
        usrp_scan_time.start()  # 很慢

    # 实时频谱分析仪绘图
    def on_pushButton_clicked_37(self):
        print(self.specAnalyze_flag)
        ####################
        if self.specAnalyze_flag:
            self.specAnalyze_fig._timer.stop()
            # 标志位为1时清空图区
            self.verticalLayout_26.removeWidget(self.specAnalyze_fig)
            sip.delete(self.specAnalyze_fig)
            self.specAnalyze_fig = spec_analyze_v2.ApplicationWindow(
                r'..\realtime_recv')
            self.verticalLayout_26.addWidget(self.specAnalyze_fig)
            self.path = ''
        else:
            self.specAnalyze_fig = spec_analyze_v2.ApplicationWindow(
                r'..\realtime_recv')
            self.verticalLayout_26.addWidget(self.specAnalyze_fig)
            self.specAnalyze_flag = 1
            self.path = ''
        ####################

    # 时域图清空数据
    def on_pushButton_clicked_63(self):
        # try:
        shutil.rmtree(r'..\realtime_recv')
        time.sleep(1)
        os.mkdir(r'..\realtime_recv')

    # IQ信号数据入库
    def wireless_signal_upload(self):
        self.wireless_dialog = wirelessDialog.MainWindow()
        self.wireless_dialog.show()

    # 包络识别信号数据入库
    def envelope_signal_upload(self):
        self.envelope_dialog = envelopeDialog.MainWindow()
        self.envelope_dialog.show()
    # 脉冲信号数据入库
    def equipment_signal_upload(self):
        self.equipment_dialog = equipDialog.MainWindow()
        self.equipment_dialog.show()
    # 稳态干扰信号数据入库
    def steady_signal_upload(self):
        self.steady_dialog = steadyDialog.MainWindow()
        self.steady_dialog.show()
    ############### 画图工具 ################
    # # IQ选择文件
    # def on_pushButton_clicked_41(self):
    #     filename, _ = QFileDialog.getOpenFileName(self, "选择文件", ".", "*.dat")
    #     self.path = filename
    #     fileinfo = QFileInfo(filename)
    #     self.name = fileinfo.fileName()
    #     print(filename)
    #     self.lineEdit_11.setText(self.path)
    #
    # # IQ绘图
    # def on_pushButton_clicked_42(self):
    #     ####################
    #     if self.path and self.plotToolIQ_flag:
    #         # 标志位为1时清空图区
    #         self.verticalLayout_13.removeWidget(self.plotTool_IQ)
    #         sip.delete(self.plotTool_IQ)
    #         self.plotTool_IQ = IQ.ApplicationWindow(self.path)
    #         self.verticalLayout_13.addWidget(self.plotTool_IQ)
    #         self.path = ''
    #     elif self.path:
    #         self.plotTool_IQ = IQ.ApplicationWindow(self.path)
    #         self.verticalLayout_13.addWidget(self.plotTool_IQ)
    #         self.plotToolIQ_flag = 1
    #         self.path = ''
    #     else:
    #         QMessageBox.information(self, '提示', '请选择文件')
    #     ####################

    # Timer选择文件
    def on_pushButton_clicked_43(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", ".", "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        self.lineEdit_12.setText(self.path)

    # Timer绘图
    def on_pushButton_clicked_44(self):
        ####################
        if self.path and self.plotToolTime_flag:
            # 标志位为1时清空图区
            self.verticalLayout_14.removeWidget(self.plotTool_Timer)
            sip.delete(self.plotTool_Timer)
            self.plotTool_Timer = Timer.ApplicationWindow(self.path)
            self.verticalLayout_14.addWidget(self.plotTool_Timer)
            self.path = ''
        elif self.path:
            self.plotTool_Timer = Timer.ApplicationWindow(self.path)
            self.verticalLayout_14.addWidget(self.plotTool_Timer)
            self.plotToolTime_flag = 1
            self.path = ''
        else:
            QMessageBox.information(self, '提示', '请选择文件')
        ####################

    # spec选择文件
    def on_pushButton_clicked_45(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", ".", "*.txt")
        self.path = filename
        fileinfo = QFileInfo(filename)
        self.name = fileinfo.fileName()
        print(filename)
        self.lineEdit_13.setText(self.path)

    # spec绘图
    def on_pushButton_clicked_46(self):
        ####################
        if self.path and self.plotToolSpec_flag:
            # 标志位为1时清空图区
            self.verticalLayout_15.removeWidget(self.plotTool_spec)
            print('delete 1')
            sip.delete(self.plotTool_spec)
            print('delete 2')
            self.plotTool_spec = spec.ApplicationWindow(self.path)
            self.verticalLayout_15.addWidget(self.plotTool_spec)
            self.path = ''
        elif self.path:
            self.plotTool_spec = spec.ApplicationWindow(self.path)
            self.verticalLayout_15.addWidget(self.plotTool_spec)
            self.plotToolSpec_flag = 1
            self.path = ''
        else:
            QMessageBox.information(self, '提示', '请选择文件')
        ####################

    # 天线比对采集
    def on_pushButton_clicked_61(self):
        print("61 pushed")
        ##########检测连接状况###############
        self.socket.send(str.encode('Imok'))
        socks = dict(self.poll.poll(3000))
        if socks.get(self.socket) == zmq.POLLIN:# 如果检测成功
            # 检测连接状况并置位
            result = bytes.decode(self.socket.recv())  # addr: 192.168.10.2 192.168.20.2
            print(result)
            if 'No UHD Device Found' in result:
                print('no usrp')
                self.antenna_usrp_flag = 0
                # QMessageBox.information(self, '错误', "没有usrp连接")
            elif ('192.168.10.2' in result) and ('192.168.20.2' not in result):
                self.antenna_usrp_flag = 1
                print('ip为192.168.10.2的usrp已连上')
            elif ('192.168.20.2' in result) and ('192.168.10.2' not in result):
                self.antenna_usrp_flag = 2
                print('ip为192.168.20.2的usrp已连上')
            elif ('192.168.10.2' in result) and ('192.168.20.2' in result):
                self.antenna_usrp_flag = 12
            # 读取下拉列表中的内容，与usrp连接状态标志位联合判断是否可以工作
            usrp_name = self.comboBox.currentText()
            if usrp_name == '一体化单元一' and (self.antenna_usrp_flag == 1 or self.antenna_usrp_flag == 12):
                self.antenna_mode_flag = 1
                usrp1_scan_antenna = usrpScan_antenna_mode1()
                usrp1_scan_antenna.start()
                self.antenna_usrp_flag = 0
            elif usrp_name == '一体化单元一' and not (self.antenna_usrp_flag == 1 or self.antenna_usrp_flag == 12):
                QMessageBox.information(self, '错误', "usrp1未连接!")
            elif usrp_name == '一体化单元二' and (self.antenna_usrp_flag == 2 or self.antenna_usrp_flag == 12):
                self.antenna_mode_flag = 1
                usrp2_scan_antenna = usrpScan_antenna_mode2()
                usrp2_scan_antenna.start()
                self.antenna_usrp_flag = 0
            elif usrp_name == '一体化单元二' and not (self.antenna_usrp_flag == 2 or self.antenna_usrp_flag == 12):
                QMessageBox.information(self, '错误', "usrp2未连接!")
            elif usrp_name == '一体化单元一、二' and self.antenna_usrp_flag == 12:
                self.antenna_mode_flag = 2
                usrp12_scan_antenna = usrpScan_antenna_mode12()
                usrp12_scan_antenna.start()
                self.antenna_usrp_flag = 0
            elif usrp_name == '一体化单元一、二' and not self.antenna_usrp_flag == 12:
                if self.antenna_usrp_flag:
                    QMessageBox.information(self, '错误', "仅usrp%s有连接！" % self.antenna_usrp_flag)
                else:
                    QMessageBox.information(self, '错误', "没有usrp连接!")
            # else:
            #     QMessageBox.information(self, '错误', "没有usrp连接!")
        else:# 如果检测失败
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)

            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect("tcp://192.168.0.5:7000")  ######根据实际情况更改ip

            self.poll = zmq.Poller()  # 超时判断
            self.poll.register(self.socket, zmq.POLLIN)
            QMessageBox.information(self, '错误', "检测连接状况失败，请重新操作")
            ####################################

    # 天线比对绘图
    def on_pushButton_clicked_64(self):
        if self.antenna_flag and self.antenna_mode_flag:
            # 标志位为1时清空图区
            self.verticalLayout_38.removeWidget(self.antennaPic)
            sip.delete(self.antennaPic)
            self.antennaPic = antenna_draw.ApplicationWindow(self.antenna_mode_flag)
            self.verticalLayout_38.addWidget(self.antennaPic)
            # self.antenna_mode_flag = 0
            self.path = ''
        elif self.antenna_mode_flag:
            self.antennaPic = antenna_draw.ApplicationWindow(self.antenna_mode_flag)
            self.verticalLayout_38.addWidget(self.antennaPic)
            self.antenna_flag = 1
            # self.antenna_mode_flag = 0
            self.path = ''
            # self.antenna_mode_flag = 0
        elif not self.antenna_mode_flag:
            QMessageBox.information(self, '错误', "请先采集数据")

    def closeEvent(self, event):
        """
                重写closeEvent方法，实现MainWindow窗体关闭时执行一些代码
                :param event: close()触发的事件
                :return: None
                """
        reply = QMessageBox.question(self,
                                     '确认窗口',
                                     "是否要退出程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            event.ignore()

    # 无边框窗体鼠标事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
class usrpCollect(Thread):
    def __init__(self):
        super(usrpCollect, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_usrp.py')
class usrp1Scan_48h(Thread):
    def __init__(self):
        super(usrp1Scan_48h, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_monitor1.py')
class usrp2Scan_48h(Thread):
    def __init__(self):
        super(usrp2Scan_48h, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_monitor2.py')
class usrp_timeplot(Thread):
    def __init__(self):
        super(usrp_timeplot, self).__init__()
    def run(self):
        os.system(r'python ..\python3.5\monitor\The48hRealPart\the_48h_realpart.py')
class usrpScan_realtime_spec(Thread):
    def __init__(self):
        super(usrpScan_realtime_spec, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_realtime_spec.py')
class usrpScan_specEnvelope(Thread):
    def __init__(self):
        super(usrpScan_specEnvelope, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_specEnvelope.py')
class usrpScan_steadyStateInterference(Thread):
    def __init__(self):
        super(usrpScan_steadyStateInterference, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_steadyStateInterference.py')
class usrpScan_antenna_mode1(Thread):
    def __init__(self):
        super(usrpScan_antenna_mode1, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_antenna_usrp1.py')

class usrpScan_antenna_mode2(Thread):
    def __init__(self):
        super(usrpScan_antenna_mode2, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_antenna_usrp2.py')

class usrpScan_antenna_mode12(Thread):
    def __init__(self):
        super(usrpScan_antenna_mode12, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\MainWindow_antenna_usrp1and2.py')

class OcCollectThread(QThread):
    def __init__(self):
        super(OcCollectThread, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\current_controller\oc_collect_allinone.py')

    # def stop(self):
    #     # self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
    #     self.__running.clear()  # 设置为False




app = QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())
