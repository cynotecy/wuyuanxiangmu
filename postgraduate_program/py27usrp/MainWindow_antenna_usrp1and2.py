# -*- coding: UTF-8 -*-
from Ui_usrp.Ui_specEnvelope_usrp import Ui_MainWindow
from current_controller import scan_thread_antenna
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4 import QtCore
from PyQt4 import QtGui
import Message
import sys
import zmq
import thread
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

startEndFreq1 = [] # global列表，用于存储UI中获得的起止频率，以控制子线程扫频
startEndFreq2 = [] # global列表，用于存储UI中获得的起止频率，以控制子线程扫频
q1 = Queue.Queue()
q2 = Queue.Queue()
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.label.setText(_fromUtf8("天线效果比对——一体化单元一、二扫频（RF2->RF1）"))
        global q1
        global q2
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)
        global startEndFreq1
        global startEndFreq2
        self.thread1 = Thread_1()
        self.thread1.start()
        self.thread2 = Thread_2()
        self.thread2.start()
        self.q = Queue.Queue()

        # self.rep_address = 'tcp://192.168.0.100:7778'
        self.rep_address = 'tcp://192.168.0.100:6667'
        # self.rep_address = 'tcp://127.0.0.1:6667'

        self.context = zmq.Context()
        self.rep_socket = self.context.socket(zmq.REQ)
        self.rep_socket.bind(self.rep_address)

        self.synchronization()

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
        if self.lineEdit.text() and self.lineEdit_2.text():
            try:
                float(self.lineEdit.text())
                float(self.lineEdit_2.text())
                freq_start = self.lineEdit.text()+'e6'
                freq_end = self.lineEdit_2.text()+'e6'
                startEndFreq1.append(freq_start)
                startEndFreq1.append(freq_end)
                startEndFreq2.append(freq_start)
                startEndFreq2.append(freq_end)
                print freq_start
                print freq_end
                """加上loading之后接收慢了"""
                loading = Message.Loading(q1)
                loading.setWindowModality(Qt.ApplicationModal)
                loading.show()
                gui = QApplication.processEvents
                while q1.empty() or q2.empty():
                    gui()
                else:
                    rturn1 = q1.get()
                    rturn2 = q2.get()
                    if rturn1 == "HeSaidStop":
                        loading.close()
                        # thread1 terminate
                        self.thread1.scan_recv.terminate()
                        # thread2 terminate
                        self.thread2.scan_recv.terminate()
                        # self.scan_recv.terminate()
                    else:
                        loading.close()
                        print rturn1
                        print rturn2
                    # rturn = self.q.get()
                    # print rturn
                    # loading.close()
            except:
                QMessageBox.warning(self,_fromUtf8('错误'),_fromUtf8('请输入正确的参数'))
        else:
            QMessageBox.warning(self, _fromUtf8('错误'), _fromUtf8('请输入参数'))
    def closeEvent(self, event):
        self.thread1.pub_socket.close()
        self.thread1.sub_socket.close()
        self.thread2.pub_socket.close()
        self.thread2.sub_socket.close()
        if self.thread1.pub_socket.closed:
            print 'self.thread1.pub_socket.closed'
        if self.thread1.sub_socket.closed:
            print 'self.thread1.sub_socket.closed'
        if self.thread2.pub_socket.closed:
            print 'self.thread2.pub_socket.closed'
        if self.thread2.sub_socket.closed:
            print 'self.thread2.sub_socket.closed'
        self.thread1.terminate()
        self.thread2.terminate()
        sys.exit()

##############线程一（一体化单元一）###################
class Thread_1(QtCore.QThread):
    def __init__(self, parent=None):
        super(Thread_1, self).__init__(parent)
        global q1
        global startEndFreq1
        self.pub_address = 'tcp://192.168.0.100:6666'
        # self.pub_address = 'tcp://127.0.0.1:6666'
        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_address)
        time.sleep(1)
        self.sub_context = zmq.Context()
        self.sub_socket = self.sub_context.socket(zmq.SUB)
        self.sub_socket.connect('tcp://192.168.0.5:5555')
        # self.sub_socket.connect('tcp://127.0.0.1:5555')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        global startEndFreq1
        while True:
            time.sleep(0.5)
            if len(startEndFreq1) == 2:
                print 'usrp1 worked'
                freq_start = startEndFreq1[0]
                freq_end = startEndFreq1[1]
                self.scan_send = scan_thread_antenna.Send(freq_start, freq_end, '1000000', self.pub_socket)
                self.scan_recv = scan_thread_antenna.Recv(q1, self.sub_socket,
                                                          path=r'D:\postgraduate_program\antenna_recv\mode2_usrp1_%s.txt')
                self.scan_send.start()
                self.scan_recv.start()
                startEndFreq1 = []

##############线程二（一体化单元二）###################
class Thread_2(QtCore.QThread):
    def __init__(self, parent=None):
        super(Thread_2, self).__init__(parent)
        global q2
        global startEndFreq2
        self.pub_address = 'tcp://192.168.0.100:7777'
        # self.pub_address = 'tcp://127.0.0.1:8888'
        self.pub_context = zmq.Context()
        self.pub_socket = self.pub_context.socket(zmq.PUB)
        self.pub_socket.bind(self.pub_address)
        time.sleep(1)
        self.sub_context = zmq.Context()
        self.sub_socket = self.sub_context.socket(zmq.SUB)
        self.sub_socket.connect('tcp://192.168.0.5:9999')
        # self.sub_socket.connect('tcp://127.0.0.1:9999')
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        global startEndFreq2
        while True:
            time.sleep(0.5)
            if len(startEndFreq2) == 2:
                print 'usrp2 worked'
                freq_start = startEndFreq2[0]
                freq_end = startEndFreq2[1]
                self.scan_send = scan_thread_antenna.Send(freq_start, freq_end, '1000000', self.pub_socket)
                self.scan_recv = scan_thread_antenna.Recv(q2, self.sub_socket,
                                                          path=r'D:\postgraduate_program\antenna_recv\mode2_usrp2_%s.txt')
                self.scan_send.start()
                self.scan_recv.start()
                startEndFreq2 = []
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())