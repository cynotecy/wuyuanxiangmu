import numpy as np
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from .utility import utcTimeString, useStyle
import math

class IQChart(FigureCanvas):
    def __init__(self):
        useStyle(["fast", "dark_background"])
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        
    def updateIQ(self, header, IQ, displayInVolt):
        self.ax.clear()
        self.ax.figure.suptitle('IQ')
        self.ax.grid(True)
        self.ax.set_xlabel('samples')
        x_data = np.arange(len(IQ) // 2)
        i_data = np.zeros(len(IQ) // 2, dtype=np.float)
        q_data = np.zeros(len(IQ) // 2, dtype=np.float)
        if displayInVolt:
            ratio = math.sqrt(200.0) * header.scaleToVolts / 1000
            self.ax.set_ylabel('mV')
        else:
            ratio = 1
        for i in range(len(i_data)):
            i_data[i] = IQ[i * 2] / ratio
            q_data[i] = IQ[i * 2 + 1] / ratio
        I_line, = self.ax.plot(x_data, i_data, linestyle="-", color="y", linewidth = 1, label = "I")
        Q_line, = self.ax.plot(x_data, q_data, linestyle="-", color="b", linewidth = 1, label = "Q")
        self.timestamp = self.ax.text(0, 0, utcTimeString(header.timestampSeconds))
        self.ax.legend()
        self.draw()


__all__ = ["IQChart"]