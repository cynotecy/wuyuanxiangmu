from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel)
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore


class Example(QWidget):

    def __init__(self):
        super().__init__()

        # self.my_UI()

    def my_UI(self):
        hbox = QHBoxLayout(self)
        pixmap = QPixmap("D:/postgraduate_program/python3.5/Ui/file_ui/ESMD辐射.bmp")
        # 创建QPixmap对象。该对象构造方法传入一个文件的名字作为参数

        lbl = QLabel(self)
        lbl.setPixmap(pixmap)  # 我们把像素图对象设置给标签，从而通过标签来显示像素图

        hbox.addWidget(lbl)
        self.setLayout(hbox)

        self.move(300, 300)
        self.setWindowTitle('连接示意图')
        self.show()
        q = QtCore.QEventLoop()
        q.exec_()
