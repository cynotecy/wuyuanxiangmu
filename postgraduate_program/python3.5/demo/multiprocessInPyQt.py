from multiprocessing import Process, Queue
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication
from time import sleep


class communicate_Thread(QThread):
    communicate_singal = pyqtSignal(str)
    exit_signal = pyqtSignal()

    def __init__(self, q, parent=None, ):
        QThread.__init__(self, parent)
        self.q = q

    def run(self):
        global running
        running = 1
        while running:
            text = self.q.get(True)
            self.communicate_singal.emit(text)

        self.exit_signal.emit()


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__(parent=None)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.pushButton_1 = QtWidgets.QPushButton()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_1.sizePolicy().hasHeightForWidth())
        self.pushButton_1.setSizePolicy(sizePolicy)
        self.pushButton_1.setMinimumSize(QtCore.QSize(125, 35))
        self.pushButton_1.setObjectName("pushButton_1")
        self.verticalLayout_6.addWidget(self.pushButton_1)

        self.q = Queue()
        self.xxx = communicate_Thread(self.q)
        self.xxx.communicate_singal.connect(self.do_something)
        self.xxx.start()
        self.pushButton_1.clicked.connect(self.runProcess)

    def runProcess(self):
        # self.yyy_process = Process(target=self.yyyprocess, args=(self.q,))
        # self.yyy_process.start()
        yp = YYYProcess(self.q)
        yp.start()

    def do_something(self):
        self.close()

class YYYProcess(Process):
    def __init__(self, q):
        super(YYYProcess, self).__init__()
        self.q = q
    def run(self):
        print("1")
        sleep(5)
        print("2")
        self.q.put("s")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ui = App()
    ui.show()
    sys.exit(app.exec_())