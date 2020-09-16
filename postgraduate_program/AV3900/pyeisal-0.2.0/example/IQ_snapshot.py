import sys
import eisal
import GUI
import GUI.er
from GUI.iq_chart import IQChart
from GUI.frequency_edit import FreqEdit
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QToolBar, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5 import Qt
import time

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.createChild()
        self.createBars()

    def createBars(self):
        self.startAction = QAction(QIcon(":/start.png"), "&Start", self)
        self.startAction.setShortcut('Ctrl+S')
        self.startAction.setStatusTip('Start')
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.startAction)
        self.statusBar()
        fileMenu = self.menuBar().addMenu('&Control')
        fileMenu.addAction(self.startAction)

    def createChild(self):
        self.mainWindow = QWidget()
        self.setCentralWidget(self.mainWindow)
        self.editCenterFreq = FreqEdit("中心频率", 92.6e6)
        self.editSpan = FreqEdit("带宽", 1e6)
        self.checkBox = QCheckBox("电压值")
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.editCenterFreq)
        leftLayout.addWidget(self.editSpan)
        leftLayout.addWidget(self.checkBox)
        leftLayout.addStretch()
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        self.chart = IQChart()
        layout.addWidget(self.chart)
        self.mainWindow.setLayout(layout)

    def bind(self, snapshot):
        def Gene():
            tick = time.time()
            header, IQ = snapshot.gene(self.editCenterFreq.frequency, self.editSpan.frequency)
            scanTime = time.time() - tick
            tick = time.time()
            self.chart.updateIQ(header, IQ, self.checkBox.checkState() == Qt.Qt.Checked)
            renderTime = time.time() - tick
            format = "扫描结束，扫描耗时 %.3f秒，绘图耗时%.3f秒"
            self.statusBar().showMessage(format % (scanTime, renderTime))
        self.startAction.triggered.connect(Gene)  

def test():
    sensorIP = "172.141.74.202"
    if(len(sys.argv) > 1):
        sensorIP = sys.argv[1]
    with eisal.Connection(sensorIP, "IQDemo") as connection:
        snapshot = eisal.IQSnapshot(connection.native_handle())
        app = QApplication(sys.argv)
        centerWindow = ApplicationWindow()
        centerWindow.bind(snapshot)
        centerWindow.show()
        app.exec_()
        
if __name__ == '__main__':
    test()       