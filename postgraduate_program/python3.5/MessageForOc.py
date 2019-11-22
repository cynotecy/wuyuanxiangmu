import Message
import ziyuan_rc
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
class OcLoading(Message.Loading):
    def __init__(self, q, parent = None):
        super(OcLoading, self).__init__(parent)
        # 重载loading，改变显示的操作名字和加入停止按键
        self.q = q
        self.setWindowTitle("采集中")
        self.label.setText("正在采集，请稍候……")
        self.pushButton_1 = QtWidgets.QPushButton(self)
        self.pushButton_1.setMinimumSize(QtCore.QSize(0, 31))
        self.pushButton_1.setMaximumSize(QtCore.QSize(16777215, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_1.setFont(font)
        self.pushButton_1.setObjectName("pushButton_1")
        self.verticalLayout.addWidget(self.pushButton_1)
        self.pushButton_1.setText("停止")
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
    import queue
    q = queue.Queue()
    app = QApplication(sys.argv)
    ui = OcLoading(q)
    # ui = Usrp_scan()
    # ui = Usrp_collect()
    # styleFile = 'white_style.qss'
    # style = CommonHelper.readQss(styleFile)
    # ui.setStyleSheet(style)
    ui.show()
    sys.exit(app.exec_())