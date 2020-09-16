import sys
import eisal
from GUI import er
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt5.QtGui import QIcon
from GUI.spectrum_chart import SpectrumChart
from GUI.frequency_edit import FreqEdit 
import matplotlib
from matplotlib.animation import FuncAnimation
import time
import threading
from PyQt5.QtCore import pyqtSignal, QTimer

class ApplicationWindow(QMainWindow):
    spectrumGene = pyqtSignal(eisal.SegmentData, list)
    def __init__(self):
        super().__init__()
        self.createChild()
        self.createBars()

    def createBars(self):
        self.startAction = QAction(QIcon(":/start.png"), "&Start", self)
        self.startAction.setShortcut('Ctrl+S')
        self.startAction.setStatusTip('Start')
        self.stopAction = QAction(QIcon(":/stop.png"), "&Stop", self)
        self.stopAction.setShortcut('Ctrl+T')
        self.stopAction.setStatusTip('Stop')
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.stopAction)
        self.statusBar()
        fileMenu = self.menuBar().addMenu('&Control')
        fileMenu.addAction(self.startAction)
        fileMenu.addAction(self.stopAction)

    def createChild(self):
        self.mainWindow = QWidget()
        self.setCentralWidget(self.mainWindow)
        self.editStartFreq = FreqEdit("起始频率", 20e6)
        self.editStopFreq = FreqEdit("终止频率", 1e9)
        self.editRBW = FreqEdit("分辨率", 100e3)
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.editStartFreq)
        leftLayout.addWidget(self.editStopFreq)
        leftLayout.addWidget(self.editRBW)
        leftLayout.addStretch()
        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        self.chart = SpectrumChart()
        layout.addWidget(self.chart)
        self.mainWindow.setLayout(layout)
        self.spectrumGene.connect(self.chart.updateSpectrum)
        self.acqireThread = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.chart.redraw)

    def bind(self, scaner):
        def startSweep():
            if self.acqireThread is not None:
                return
            scaner.config(self.editStartFreq.frequency, self.editStopFreq.frequency, self.editRBW.frequency)
            if not scaner.start():
                return
            self.chart.setupChart(scaner)
            self.timer.start(200)
            def acquireThreadFunc():
                for header, spectrum in scaner:
                    self.spectrumGene.emit(header, spectrum)
                self.statusBar().showMessage("采集线程退出")

            self.acqireThread = threading.Thread(target=acquireThreadFunc)
            self.acqireThread.start()

        def stopSweep():
            if self.acqireThread is None:
                return
            self.timer.stop()
            scaner.abort()  #发送停止扫描的指令
            self.acqireThread.join()    #等待线程退出
            scaner.reset()  #关闭采集句柄
            self.acqireThread = None

        self.startAction.triggered.connect(startSweep)  
        self.stopAction.triggered.connect(stopSweep)

        def closeEvent(self, event):
            if self.acqireThread is not None:
                scaner.abort()
                self.acqireThread.join()
                scaner.reset()
                self.acqireThread = None

def test():
    sensorIP = "192.168.1.88"
    if(len(sys.argv) > 1):
        sensorIP = sys.argv[1]
    with eisal.Connection(sensorIP, "spectrumDemo") as connection:
        scaner = eisal.SpectrumScaner(connection.native_handle())
        app = QApplication(sys.argv)
        centerWindow = ApplicationWindow()
        centerWindow.bind(scaner)
        centerWindow.show()
        app.exec_()
        
if __name__ == '__main__':
    test()       