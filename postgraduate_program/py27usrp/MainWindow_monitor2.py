# -*- coding: UTF-8 -*-
from Ui_usrp.Ui_monitor_usrp import Ui_MainWindow
from current_controller import scan_thread_48h
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from PyQt4 import QtGui
import Message
import sys
import zmq
import time
import thread
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
        self.setWindowTitle(_fromUtf8("usrp2频谱监测"))
        self.label.setText(_translate("MainWindow", "频谱监测:本机端口7777，工程机端口9999", None))
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint)
        # self.setWindowFlags(QtCore.Qt.ToolTip)
        self.pub_address = 'tcp://192.168.0.100:7777'
        # self.pub_address = 'tcp://127.0.0.1:8888'
        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_address)

        self.rep_address = 'tcp://192.168.0.100:7778'
        # self.rep_address = 'tcp://192.168.0.100:6667'
        # self.rep_address = 'tcp://127.0.0.1:6667'

        self.rep_socket = self.pub_context.socket(zmq.REQ)
        self.rep_socket.bind(self.rep_address)

        self.sub_context = zmq.Context()
        self.sub_socket = self.sub_context.socket(zmq.SUB)
        self.sub_socket.connect('tcp://192.168.0.5:9999')
        # self.sub_socket.connect('tcp://127.0.0.1:9999')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.q = Queue.Queue()
        self.synchronization()

        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)

    # 同步线程
    def syncThread(self):
        recv = ''
        while 1:
            self.rep_socket.send('hello client')
            recv = self.rep_socket.recv()
            if recv == 'hello server':
                # 同步完成
                self.q.put('synchronization')
                self.rep_socket.close()
                break
            else:
                # self.rep_socket.send('nothing')
                time.sleep(1)

    # 同步线程调用，同步的过程中使用loading阻塞主界面防止用户输入
    def synchronization(self):
        thread.start_new_thread(self.syncThread, ())
        loading = Message.Loading(self.q)
        loading.label.setText(_fromUtf8("正在同步，请稍候……"))
        loading.pushButton_1.setEnabled(False)
        loading.setWindowModality(Qt.ApplicationModal)
        loading.show()
        gui = QApplication.processEvents
        while self.q.empty():
            gui()
        else:
            qContent = self.q.get()
            if qContent == 'synchronization':
                loading.close()

    def on_pushButton_clicked_1(self):
        text = self.pushButton_1.text()
        if text == _fromUtf8("开始监测"):
            self.pushButton_1.setText(_fromUtf8("停止监测"))
            freq_start = self.lineEdit.text()+'e6'
            freq_end = self.lineEdit_2.text()+'e6'
            RBW = self.comboBox.currentText()
            # self.scan_send = scan_thread_48h.Send('100e6', '200e6', '1000000', self.pub_socket)
            self.scan_send = scan_thread_48h.Send(freq_start, freq_end, '1000000', self.pub_socket)
            self.scan_recv = scan_thread_48h.Recv(self.sub_socket, 'usrp2', RBW, path=r'D:\postgraduate_program\48recv\usrp2\%s.dat')
            self.scan_send.start()
            self.scan_recv.start()
        elif text == _fromUtf8("停止监测"):
            self.pushButton_1.setText(_fromUtf8("开始监测"))
            self.scan_send.terminate()
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