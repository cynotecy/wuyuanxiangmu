import sys
import eisal
from GUI.demod_chart import DemodChart
from GUI import er
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
import matplotlib
from time import time
import threading

class ApplicationWindow(QMainWindow):
    spectrumGene = pyqtSignal(list)
    audioGene = pyqtSignal(list)
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
        self.recordAction = QAction(QIcon(":/record.png"), "&Record", self)
        self.recordAction.setShortcut('Ctrl+R')
        self.recordAction.setStatusTip('Record')
        self.recordAction.setCheckable(True)
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.stopAction)
        toolbar.addAction(self.recordAction)
        self.statusBar()
        fileMenu = self.menuBar().addMenu('&Control')
        fileMenu.addAction(self.startAction)
        fileMenu.addAction(self.stopAction)
        fileMenu.addAction(self.recordAction)

    def createChild(self):
        self.mainWindow = QWidget()
        self.setCentralWidget(self.mainWindow)
        layout = QVBoxLayout()
        self.chart = DemodChart()
        layout.addWidget(self.chart)
        self.mainWindow.setLayout(layout)
        self.audioPlayThread = None
        self.spectrumAcquireThread = None

    def bind(self, demodulator):
        def onTuner(center, span):
            if self.audioPlayThread is None:
                return
            demodulator.changeTuner(center, span)
            self.statusBar().showMessage("解调于%.3fMHz, 解调带宽%.3fkHz" % (center / 1e6, span / 1e3))
        
        demodulator.config(center = 92.6e6, analyseBw=40e6, gainSwitch = False, attenuation = 0)
        scaner = eisal.AnalogDemodulatorSpectrumScaner(demodulator)

        self.chart.freqChange.connect(onTuner)
        self.audioGene.connect(self.chart.on_pcm_block)
        self.spectrumGene.connect(self.chart.on_spectrum)
        self.recordAction.toggled.connect(self.chart.on_record_switch)
        
        def startDemod():
            if self.audioPlayThread is not None: #already started
                return
            if not demodulator.start():
                return
            if not scaner.start():
                return
            self.chart.setupChart(demodulator, scaner)
            
            def audioPlayFunc():
                for header, pcmBlock in demodulator:
                    self.audioGene.emit(pcmBlock)
                self.statusBar().showMessage("线程退出")

            def spectrumAcquireFunc():
                for header, spectrum in scaner:
                    self.spectrumGene.emit(spectrum)
                
            self.audioPlayThread = threading.Thread(target=audioPlayFunc)
            self.audioPlayThread.start()

            self.spectrumAcquireThread = threading.Thread(target=spectrumAcquireFunc)
            self.spectrumAcquireThread.start()

        def stopDemod():
            if self.audioPlayThread is None: #already stopped
                return
            self.recordAction.setChecked(False)
            scaner.abort()
            self.spectrumAcquireThread.join()
            demodulator.abort()
            self.audioPlayThread.join()
            scaner.reset()
            demodulator.reset()
            self.spectrumAcquireThread = None
            self.audioPlayThread = None

            
        self.startAction.triggered.connect(startDemod)  
        self.stopAction.triggered.connect(stopDemod)

    def closeEvent(self, event):
        self.stopAction.trigger()

def test():
    sensorIP = "192.168.1.88"
    if(len(sys.argv) > 1):
        sensorIP = sys.argv[1]
    with eisal.Connection(sensorIP, "demodDemo") as connection:
        demodulator = eisal.AnalogDemodulator(connection.native_handle())
        app = QApplication(sys.argv)
        centerWindow = ApplicationWindow()
        centerWindow.bind(demodulator)
        centerWindow.show()
        app.exec_()

if __name__ == '__main__':
    test()       