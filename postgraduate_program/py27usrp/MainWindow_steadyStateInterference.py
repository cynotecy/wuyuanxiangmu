# -*- coding: UTF-8 -*-
from Ui_usrp.Ui_specEnvelope_usrp import Ui_MainWindow
from current_controller import scan_thread_specEnvelope
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
        self.label.setText(_fromUtf8("稳态干扰识别——扫频"))
        self.pub_address = 'tcp://192.168.0.100:6666'
        # self.pub_address = 'tcp://127.0.0.1:6666'
        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_address)

        # self.rep_address = 'tcp://192.168.0.100:7778'
        self.rep_address = 'tcp://192.168.0.100:6667'
        # self.rep_address = 'tcp://127.0.0.1:6667'

        self.rep_socket = self.pub_context.socket(zmq.REQ)
        self.rep_socket.bind(self.rep_address)

        self.sub_context = zmq.Context()
        self.sub_socket = self.sub_context.socket(zmq.SUB)
        self.sub_socket.connect('tcp://192.168.0.5:5555')
        # self.sub_socket.connect('tcp://127.0.0.1:5555')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.q = Queue.Queue()

        # self.synchronization()

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
        # freq_start = self.lineEdit.text()
        # freq_end = self.lineEdit_2.text()
        # RBW = self.comboBox.currentText()
        # self.scan_send = scan_thread_48h.Send('100e6', '200e6', '1000000', self.pub_socket)
        if self.lineEdit.text() and self.lineEdit_2.text():
            try:
                float(self.lineEdit.text())
                float(self.lineEdit_2.text())
                freq_start = self.lineEdit.text()+'e6'
                freq_end = self.lineEdit_2.text()+'e6'
                print freq_start
                print freq_end
                self.scan_send = scan_thread_specEnvelope.Send(freq_start, freq_end, '1000000', self.pub_socket)
                self.scan_recv = scan_thread_specEnvelope.Recv(self.q, self.sub_socket,path=r'D:\postgraduate_program\steadyStateInterference_recvfiles\%s.txt')
                # self.scan_recv = scan_thread_realtime.Recv(self.sub_socket)
                self.scan_send.start()
                self.scan_recv.start()
                """加上loading之后接收慢了"""
                loading = Message.Loading(self.q)
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QApplication.processEvents
                while self.q.empty():
                    gui()
                else:
                    rturn = self.q.get()
                    if rturn == "HeSaidStop":
                        loading.close()
                        self.scan_recv.terminate()
                    else:
                        loading.close()
                        print rturn
                    # rturn = self.q.get()
                    # print rturn
                    # loading.close()
            except:
                QMessageBox.warning(self,_fromUtf8('错误'),_fromUtf8('请输入正确的参数'))
        else:
            QMessageBox.warning(self, _fromUtf8('错误'), _fromUtf8('请输入参数'))
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