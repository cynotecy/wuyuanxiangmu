import numpy as np
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from .utility import readbleFrequency, utcTimeString, useStyle
import threading

class SpectrumChart(FigureCanvas):
    def __init__(self):
        useStyle(["fast", "dark_background"])
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        self.ax.figure.suptitle('Spectrum')
        self.ax.set_xlabel('Frequency')
        self.ax.set_ylabel('Amplitude')
        self.background = None
        super().__init__(self.fig)
        
    def setupChart(self, controller):
        self.ax.clear()
        self.ax.grid(True)
        x_data = np.linspace(controller.startFrequency, controller.stopFrequency, controller.totalPoints)
        y_data = np.zeros(controller.totalPoints)
        self.spectrumLine, = self.ax.plot(x_data, y_data, linestyle="-", color="y", animated = True)
        self.ax.set_xlim(controller.startFrequency, controller.stopFrequency)
        self.ax.set_ylim(-120.0, -30.0)
        self.ax.xaxis.set_major_formatter(FuncFormatter(readbleFrequency))
        self.timestamp = self.ax.text(self.ax.get_xlim()[0] + 100, -48, "", animated = True)
        self.draw() #first draw
        self.background = self.copy_from_bbox(self.ax.bbox)  #grab the background for blit

    def updateSpectrum(self, header, spectrum):
        self.spectrumLine.set_ydata(spectrum)
        self.timestamp.set_text(utcTimeString(header.timestampSec))
        
    def redraw(self):
        self.restore_region(self.background)
        self.ax.draw_artist(self.spectrumLine)
        self.ax.draw_artist(self.timestamp)
        self.blit(self.ax.bbox)
        
__all__ = ["SpectrumChart"]