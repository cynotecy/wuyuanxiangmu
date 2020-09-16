import sys
import eisal
from GUI import er
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt5.QtGui import QIcon
from GUI.spectrum_chart import SpectrumChart
from GUI.frequency_edit import FreqEdit 
import matplotlib
import time
from PyQt5.QtCore import pyqtSignal

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
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.startAction)
        self.statusBar()
        fileMenu = self.menuBar().addMenu('&Control')
        fileMenu.addAction(self.startAction)

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

        def chartUpdate(header, spectrum):
            self.chart.updateSpectrum(header, spectrum)
            self.chart.redraw()
        self.spectrumGene.connect(chartUpdate)

    def bind(self, snapshot):
        def Gene():
            tick = time.time()
            header, spectrum = snapshot.gene(self.editStartFreq.frequency, self.editStopFreq.frequency, self.editRBW.frequency)
            scanTime = time.time() - tick
            self.chart.setupChart(snapshot)
            self.spectrumGene.emit(header, spectrum)
            format = "扫描结束，扫描耗时 %.3f秒"
            self.statusBar().showMessage(format % scanTime)
        self.startAction.triggered.connect(Gene)  

def test():
    sensorIP = "172.141.74.202"
    if(len(sys.argv) > 1):
        sensorIP = sys.argv[1]
    with eisal.Connection(sensorIP, "spectrumDemo") as connection:
        snapshot = eisal.SpectrumSnapshot(connection.native_handle())
        app = QApplication(sys.argv)
        centerWindow = ApplicationWindow()
        centerWindow.bind(snapshot)
        centerWindow.show()
        app.exec_()
        
if __name__ == '__main__':
    test()       
                
