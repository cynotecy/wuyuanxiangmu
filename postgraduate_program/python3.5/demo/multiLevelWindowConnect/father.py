"""
@File:father.py
@Author:lcx
@Date:2020/1/1310:43
@Desc:父窗口
"""
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from demo.multiLevelWindowConnect.child import DateDialog

class WinForm(QWidget):
    def __init__(self,parent=None):
        super(WinForm, self).__init__(parent)
        self.resize(400,90)
        self.setWindowTitle('对话框关闭时返回值给主窗口的例子')

        self.lineEdit=QLineEdit(self)
        self.button1=QPushButton('弹出对话框1')
        self.button1.clicked.connect(self.onButton1Clicked)

        self.button2=QPushButton('弹出对话框2')
        self.button2.clicked.connect(self.onButton2Clicked)

        gridLayout=QGridLayout(self)
        gridLayout.addWidget(self.lineEdit)
        gridLayout.addWidget(self.button1)
        gridLayout.addWidget(self.button2)

    def onButton1Clicked( self ):
        dialog=DateDialog(self)
        result=dialog.exec_()
        date=dialog.dateTime()
        self.lineEdit.setText(date.date().toString())
        print('\n日期对话框的返回值')
        print('date=%s'%str(date.date))
        print('time=%s'%str(date.time()))
        print('result=%s'%result)
    def onButton2Clicked( self ):
        date,time,result=DateDialog.getDateTime()
        self.lineEdit.setText(date.toString())
        print('\n 日期对话框的返回值')
        print('date=%s' %str(date))
        print('time=%s' %str(time))
        print('result=%s' %result)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    form=WinForm()
    form.show()
    sys.exit(app.exec_())