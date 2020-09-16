import numpy as np
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from .utility import readbleFrequency, utcTimeString, useStyle
from CeyearAudioPlayer import *
import time

class DemodChart(FigureCanvas):
    lock = None
    freqChange = pyqtSignal(float, float)
    def __init__(self):
        useStyle(["fast", "dark_background"])
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.figure.suptitle('FM-band spectrum')
        self.ax.set_xlabel('Frequency')
        self.ax.set_ylabel('Amplitude')
        self.press = None
        self.background = None
        self.audioWriter = None
        self.recordAudio = False
        super().__init__(self.fig)
        
    def setupChart(self, demodulator, scaner):
        self.ax.clear()
        self.ax.grid(True)
        startFreq = scaner.center - scaner.span / 2
        stopFreq = scaner.center + scaner.span / 2
        x_data = np.linspace(startFreq, stopFreq, scaner.points)
        y_data = np.zeros(scaner.points)
        self.audioSampleRate = demodulator.audioSampleRate
        self.audioPlayer = AudioPlayer(self.audioSampleRate)
        self.spectrumLine, = self.ax.plot(x_data, y_data, linestyle="-", color="y")
        self.ax.set_xlim(startFreq, stopFreq)
        self.ax.set_ylim(-120.0, -30.0)
        self.ax.xaxis.set_major_formatter(FuncFormatter(readbleFrequency))
        self.rect, = self.ax.bar(scaner.center, -120, 450e3)
        self.spectrumLine.set_animated(True)
        self.rect.set_animated(True)
        self.recordTime = self.ax.text(stopFreq - scaner.span / 9, -35, "", animated = True)
        self.recordStart = 0
        self.draw() #first draw
        self.background = self.copy_from_bbox(self.ax.bbox)  #grab the background for blit
        self.connectEvent()
        
    def connectEvent(self):
        'connect to all the events we need'
        self.cidpress = self.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.mpl_connect(
            'motion_notify_event', self.on_motion)

    def disconnectEvent(self):
        'disconnect all the stored connection ids'
        self.mpl_disconnect(self.cidpress)
        self.mpl_disconnect(self.cidrelease)
        self.mpl_disconnect(self.cidmotion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return
        if DemodChart.lock is not None: return
        contains, attrd = self.rect.contains(event)
        if not contains: return
        print('event contains', self.rect.xy)
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata
        DemodChart.lock = self

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if DemodChart.lock is not self:
            return
        if event.inaxes != self.ax: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.rect.set_x(x0+dx)
        #self.rect.set_y(y0+dy)
        self.redraw()

    def on_release(self, event):
        'on release we reset the press data'
        if DemodChart.lock is not self:
            return
        x,y = self.rect.xy
        self.press = None
        DemodChart.lock = None
        self.freqChange.emit(x + self.rect.get_width() / 2, self.rect.get_width() / 3)
        
    def on_pcm_block(self, pcmBlock):
        self.audioPlayer.play(pcmBlock)
        if(self.recordAudio):
            self.audioWriter.record(pcmBlock)
    
    def on_spectrum(self, spectrum):
        self.spectrumLine.set_ydata(spectrum)
        self.redraw()

    def on_record_switch(self, toggle):
        if toggle:
            self.audioWriter = WAVFileWriter("record.wav", self.audioSampleRate)
            self.recordStart = time.time()
            self.recordAudio = True
        else:
            self.recordAudio = False
            self.recordStart = 0
            if self.audioWriter is not None:
                self.audioWriter.close()
                self.audioWriter = None
        
    def redraw(self):
        self.restore_region(self.background)
        #redraw just the current rectangle
        self.ax.draw_artist(self.rect)
        self.ax.draw_artist(self.spectrumLine)
        if self.recordStart != 0:
            self.recordTime.set_text("record %.0f s"%(time.time() - self.recordStart))
            self.ax.draw_artist(self.recordTime)
        # blit just the redrawn area
        self.blit(self.ax.bbox)
