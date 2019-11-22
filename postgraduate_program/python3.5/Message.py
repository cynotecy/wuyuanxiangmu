# -*- coding: utf-8 -*-
import ziyuan_rc
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


class Loading(QDialog):
    def __init__(self, parent = None):
        super(Loading, self).__init__(parent)
        print("loading start")
        self.setObjectName("Form")
        self.setFixedSize(275, 175)
        self.setWindowFlags(QtCore.Qt.ToolTip)
        # self.setWindowFlags(QtCore.Qt.WindowDoesNotAcceptFocus)
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/图标/ooopic_1521110980.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # Loading.setWindowIcon(icon)
        self.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.setWindowTitle("识别中")
        self.label.setText("正在识别，请稍候……")
        self.movie = QtGui.QMovie(":/图标/loading2.gif")
        # self.pushButton = QtWidgets.QPushButton(self)
        # self.pushButton.setMinimumSize(QtCore.QSize(0, 50))
        # self.pushButton.setObjectName("pushButton")
        # self.pushButton.setText("停止识别")
        # self.pushButton.setFont(font)
        # self.verticalLayout.addWidget(self.pushButton)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setMovie(self.movie)
        self.movie.start()

    def on_pushButton_clicked_1(self):
        pass

# if __name__ == '__main__':
#     import sys
#
#     app = QApplication(sys.argv)
#     # ui = Loading()
#     ui = Usrp_scan()
#     # ui = Usrp_collect()
#     # styleFile = 'white_style.qss'
#     # style = CommonHelper.readQss(styleFile)
#     # ui.setStyleSheet(style)
#     ui.show()
#     sys.exit(app.exec_())
