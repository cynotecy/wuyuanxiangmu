# -*- coding: utf-8 -*-
import ziyuan_rc
from PyQt4 import QtGui
from PyQt4.QtGui import *
# from PyQt4.QtCore import *
from PyQt4 import QtCore

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
class Loading(QDialog):
    def __init__(self, q, parent = None):
        super(Loading, self).__init__(parent)
        self.q = q
        self.setObjectName("Form")
        self.setFixedSize(275, 200)
        self.setWindowFlags(QtCore.Qt.ToolTip)
        # self.setWindowFlags(QtCore.Qt.WindowDoesNotAcceptFocus)
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/图标/ooopic_1521110980.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # Loading.setWindowIcon(icon)
        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setText("")
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.setWindowTitle("1")
        self.label.setText(_translate("label_2", "正在操作，请稍候……",None))
        self.movie = QtGui.QMovie(_fromUtf8(":/图标/loading2.gif"))
        self.movie.start()
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setMovie(self.movie)
        self.pushButton_1 = QtGui.QPushButton()
        self.pushButton_1.setMinimumSize(QtCore.QSize(0, 31))
        self.pushButton_1.setMaximumSize(QtCore.QSize(16777215, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_1.setFont(font)
        self.pushButton_1.setObjectName(_fromUtf8("pushButton_1"))
        self.verticalLayout.addWidget(self.pushButton_1)
        self.pushButton_1.setText(_translate("Loading", "停止", None))
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)

    def on_pushButton_clicked_1(self):
        if self.q.empty():
            self.q.put("HeSaidStop")
            self.close()
        else:
            self.q.get()
            self.q.put("HeSaidStop")
            self.close()



if __name__ == '__main__':
    import sys
    import Queue
    from PyQt4.QtCore import Qt
    q = Queue.Queue()
    app = QApplication(sys.argv)
    ui = Loading(q)
    # while q.empty():
    #     ui.show()
    # else:
    #     ui.close()
    # # print q.get()
    # sys.exit(app.exec_())
    # print q.get()
    loading = Loading(q)
    loading.setWindowModality(Qt.ApplicationModal)
    loading.show()
    gui = QApplication.processEvents
    # self.loading.setWindowModality(Qt.ApplicationModal)
    while q.empty():
        gui()
    else:
        loading.close()
        rturn = q.get()
        print rturn
