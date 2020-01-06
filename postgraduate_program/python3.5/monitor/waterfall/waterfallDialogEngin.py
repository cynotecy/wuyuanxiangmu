"""
@File:waterfallDialogEngin.py
@Author:lcx
@Date:2020/1/615:23
@Desc:瀑布图子窗口
"""
from Ui.UitoPy.SpecMonitorDialog import Ui_Dialog
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
from monitor.waterfall import WaterFall
import threading
import queue
from socketDemo import zmqLocal


class WaterfallDialog(QDialog, Ui_Dialog):
    def __init__(self, usrpNum, socket, startfreq, endfreq, parent=None):
    # def __init__(self, parent=None):
        super(WaterfallDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("一体化单元{}频谱监测视图".format(usrpNum))
        self.label_3.setText("监测频段{}~{}MHz".format(str(startfreq), str(endfreq)))
        self.socket = socket
        self.startfreq = startfreq
        self.endfreq = endfreq
        self.zmqLocalQ = queue.Queue()

    def messegeSend(self):
        while True:
            msg = (str(self.startfreq) + ";" + str(self.endfreq))
            zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                         args=(self.socket, msg, self.zmqLocalQ))
            zmqThread.start()
            while self.zmqLocalQ.empty():
                pass
            else:
                reslt = self.zmqLocalQ.get()
                if reslt == "超时":
                    pass
                else:
                    print(type(reslt))
                    resltList = reslt.split(';')
                    self.scanRslt = resltList
                    freqList = resltList[0].split(' ')
                    binsList = resltList[1].split(" ")
                    self.onlineSpecX = [float(i) for i in freqList]
                    self.onlineSpecY = [float(i) for i in binsList]

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ui = WaterfallDialog()
    ui.show()
    sys.exit(app.exec_())