# -*- coding: UTF-8 -*-
from Ui_usrp.Ui_MainWindow_usrp import Ui_MainWindow
# import samplerate
from current_controller import collect_thread,scan_thread
from cursorPos import getPos
from PyQt4.QtGui import *
import uuid
import sip
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from PyQt4 import QtGui
import Message
import os
import shutil
import sys
import thread
import zmq
import time
from time import ctime
import Queue
import matplotlib.pyplot as plt

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # 定义发布、订阅和同步的地址
        self.pub_address = 'tcp://192.168.0.100:7777'
        # self.pub_address = 'tcp://192.168.0.100:6666'
        # self.pub_address = 'tcp://127.0.0.1:6666'

        self.sub_address = 'tcp://192.168.0.5:9999'
        # self.sub_address = 'tcp://192.168.0.5:5555'
        # self.sub_address = 'tcp://127.0.0.1:5555'

        # self.rep_address = 'tcp://192.168.0.100:7778'
        # self.rep_address = 'tcp://192.168.0.100:6667'
        # self.rep_address = 'tcp://127.0.0.1:6667'

        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_address)

        # self.rep_socket = self.pub_context.socket(zmq.REQ)
        # self.rep_socket.bind(self.rep_address)
        # # time.sleep(1)

        self.sub_context = zmq.Context()
        self.sub_socket = self.sub_context.socket(zmq.SUB)
        self.sub_socket.connect(self.sub_address)
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')

        self.pushButton_4.clicked.connect(self.on_pushButton_clicked_4)# 开始扫频
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)# 开始采集
        self.pushButton_5.clicked.connect(self.on_pushButton_clicked_5)# 保存频谱
        self.pushButton_6.clicked.connect(self.on_pushButton_clicked_6)# 门限选定
        thread.start_new_thread(self.mouseListening, ())
        self.picFlag = 0
        self.q = Queue.Queue()
        self.picQ = Queue.Queue()
        self.qSaveThreshold = Queue.Queue()
        # 初始化回传数据变量
        self.freq_list = []
        self.bins = []
        # self.synchronization()
    #
    # # 同步线程
    # def syncThread(self):
    #     recv = ''
    #     while 1:
    #         self.rep_socket.send('hello client')
    #         recv = self.rep_socket.recv()
    #         if recv == 'hello server':
    #             # 同步完成
    #             self.q.put('synchronization')
    #             self.rep_socket.close()
    #             break
    #         else:
    #             # self.rep_socket.send('nothing')
    #             time.sleep(1)
    #
    # # 同步线程调用，同步的过程中使用loading阻塞主界面防止用户输入
    # def synchronization(self):
    #     thread.start_new_thread(self.syncThread, ())
    #     loading = Message.Loading(self.q)
    #     loading.label.setText(_fromUtf8("正在同步，请稍候……"))
    #     loading.pushButton_1.setEnabled(False)
    #     loading.setWindowModality(Qt.ApplicationModal)
    #     loading.show()
    #     gui = QApplication.processEvents
    #     while self.q.empty():
    #         gui()
    #     else:
    #         qContent = self.q.get()
    #         if qContent == 'synchronization':
    #             loading.close()
    #             # self.label_17.setText(_fromUtf8("同步完成"))

    # 扫频，需完成指令发送和回传图片置入布局操作
    def on_pushButton_clicked_4(self):
        print '4'
        # 初始化回传数据变量
        # 还需要初始化布局
        self.freq_list = []
        self.bins = []
        # 指令生成和发送
        freq_start = self.lineEdit.text()+'e6'
        freq_end = self.lineEdit_2.text()+'e6'
        point_num = self.lineEdit_4.text()
        if not(freq_start.isEmpty() or freq_end.isEmpty() or point_num.isEmpty()):
            self.scan_recv = scan_thread.Recv(self.q, self.sub_socket)
            self.scan_send = scan_thread.Send(freq_start, freq_end, self.pub_socket)
            self.scan_recv.start()
            self.scan_send.run()
            loading = Message.Loading(self.q)
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QApplication.processEvents
            # self.loading.setWindowModality(Qt.ApplicationModal)
            while self.q.empty():
                gui()
            else:
                print self.q.qsize()
                self.bins = self.q.get()
                print "self.bins type",type(self.bins)
                if self.bins == "HeSaidStop":
                    loading.close()
                    self.scan_recv.terminate()
                else:
                    # 回传接收、绘图
                    loading.close()
                    self.freq_list = self.q.get()
                    self.bins = [c-11 for c in self.bins]
                    # ratio = int(point_num)/len(self.freq_list)
                    # self.freq_list = self.down_sample(self.freq_list, ratio)
                    # self.bins = self.down_sample(self.bins, ratio)
                    print len(self.bins)
                    print len(self.freq_list)
                    #####置入绘图####
                    if self.picFlag:
                        self.verticalLayout.removeWidget(self.getPosition)
                        sip.delete(self.getPosition)
                        self.getPosition = getPos.getPos(self.freq_list, self.bins, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.picFlag = 1
                    else:
                        self.getPosition = getPos.getPos(self.freq_list, self.bins, self.picQ)
                        self.verticalLayout.addWidget(self.getPosition)
                        self.picFlag = 1
        else:
            QMessageBox.warning(self, _fromUtf8('错误'), _fromUtf8("请输入正确参数！"), QMessageBox.Yes)

    # 门限选定，生成门限文件
    def on_pushButton_clicked_6(self):
        if self.lineEdit_8.text():
            thread.start_new_thread(self.saveThreshold, ())
            loading = Message.Loading(self.qSaveThreshold)
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QApplication.processEvents
            # self.loading.setWindowModality(Qt.ApplicationModal)
            while self.qSaveThreshold.empty():
                gui()
            else:
                if self.bins == "saved!":
                    loading.close()

    # 门限文件存储函数
    def saveThreshold(self):
        if not self.qSaveThreshold.empty():
            self.qSaveThreshold.get()
        # 先清空文件夹，保证文件夹中只有一个门限文件
        shutil.rmtree(r'D:\postgraduate_program\usrp_recvfiles\threshold')
        time.sleep(1)
        os.mkdir(r'D:\postgraduate_program\usrp_recvfiles\threshold')
        # 生成Uid用来命名门限文件
        id = uuid.uuid1()
        f = open(r'D:\postgraduate_program\usrp_recvfiles\threshold\%s.txt' % id, 'w+')
        # 写入门限文件，第一行是门限，第二行是频点，第三行是幅值
        f.write(self.lineEdit_8.text())
        f.write('\n')
        for i in range(len(self.freq_list)):
            f.write(str(self.freq_list[i]) + ' ')
        f.write('\n')
        for i in range(len(self.bins)):
            f.write(str(self.bins[i] + 11) + ' ')
        f.close()
        print self.lineEdit_8.text()
        self.qSaveThreshold.put("saved!")

    # 鼠标监听线程
    def mouseListening(self):
        print 'self.picQ.empty()', self.picQ.empty()
        while 1:
            if not self.picQ.empty():
                self.lineEdit_8.setText(str(self.picQ.get()))

    # 保存频谱按键（仅用作信噪比判断）
    def on_pushButton_clicked_5(self):
        # 保存频谱前判断是否有回传数据
        if self.freq_list and self.bins:
            self.localtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            filename = 'D:\postgraduate_program\usrp_recvfiles\usrp_scan\%s.txt' % self.localtime
            f = open(filename, 'w+')
            print filename
            for i in range(len(self.freq_list)):
                f.write(str(self.freq_list[i]) + ' ')
            f.write('\n')
            for i in range(len(self.bins)):
                f.write(str(self.bins[i]) + ' ')
            f.write('\n')
            f.close()
            print 'written'
        else:
            QMessageBox.warning(self, _fromUtf8('错误'), _fromUtf8("没有频谱数据，保存失败，请先扫频！"), QMessageBox.Yes)

    # 采集，需完成采集指令发送，文件写入程序在调用的方法里写了
    def on_pushButton_clicked_1(self):
        print '1'
        centre = self.lineEdit_3.text()+'e6'
        item = self.lineEdit_7.text()
        samprate = self.lineEdit_6.text()+'e6'
        bdwidth = self.lineEdit_5.text()
        if item.isEmpty():
            item = _fromUtf8('未命名')
        local_time1 = time.strftime("%Y%m%d%H%M%S", time.localtime( time.time() ))
        path1 = r'D:\postgraduate_program\usrp_recvfiles\%s_%s.dat' % (item, local_time1)
        print path1
        if not centre.isEmpty():
            self.collect_recv = collect_thread.Recv(self.q, self.sub_socket, path=path1)
            self.collect_send = collect_thread.Send(centre, samprate, bdwidth, self.pub_socket)
            self.collect_recv.start()
            self.collect_send.run()
            loading = Message.Loading(self.q)
            loading.setWindowModality(Qt.ApplicationModal)
            loading.show()
            gui = QApplication.processEvents
            # self.loading.setWindowModality(Qt.ApplicationModal)
            while self.q.empty():
                gui()
            else:
                rturn = self.q.get()
                if rturn =="HeSaidStop":
                    loading.close()
                    self.collect_recv.terminate()
                else:
                    loading.close()
                    print rturn
        else:
            QMessageBox.warning(self, _fromUtf8('错误'), _fromUtf8("请输入正确参数！"), QMessageBox.Yes)

    # def down_sample(self, input_data, ratio):  # 上or下采样
    #     converter = 'linear'  # or 'sinc_fastest', ...
    #     return samplerate.resample(input_data, ratio, converter)

    def closeEvent(self, event):
        self.pub_socket.close()
        self.sub_socket.close()
        if self.pub_socket.closed:
            print 'self.pub_socket.closed'
        if self.sub_socket.closed:
            print 'self.sub_socket.closed'
        sys.exit()


app = QApplication(sys.argv)
ui = MainWindow()
ui.show()
sys.exit(app.exec_())