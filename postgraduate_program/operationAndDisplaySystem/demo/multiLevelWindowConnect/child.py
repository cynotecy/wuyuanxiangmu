"""
@File:child.py
@Author:lcx
@Date:2020/1/1310:43
@Desc:子窗口
"""
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class DateDialog(QDialog):
    def __init__(self,parent=None):
        super(DateDialog, self).__init__(parent)
        self.setWindowTitle('DateDialog')

        #在布局中添加控件
        layout=QVBoxLayout(self)
        self.datetime=QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        buttons=QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,Qt.Horizontal,self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def dateTime( self ):
        return self.datetime.dateTime()

    @staticmethod
    def getDateTime(parent=None):
        dialog=DateDialog(parent)
        result=dialog.exec_()
        date=dialog.dateTime()
        return (date.date(),date.time(),result==QDialog.Accepted)