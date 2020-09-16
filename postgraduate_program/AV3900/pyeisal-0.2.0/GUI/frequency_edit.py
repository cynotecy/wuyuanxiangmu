import numpy as np
import time
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QApplication, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject, QRegExp
from PyQt5.QtGui import QRegExpValidator

FreqRatio = (1, 1e3, 1e6, 1e9)
FreqUnit = ("Hz", "kHz", "MHz", "GHz")

class FreqEdit(QWidget):
    newVal = pyqtSignal(float)
    def __init__(self, label="", val=0):
        super().__init__()
        self.initUI(label, val)
        self._freqVal = val
    
    @classmethod
    def parse(cls, val):
        try:
            for i, r in enumerate(FreqRatio):
                if val < r:
                    return str(val / FreqRatio[i - 1]), FreqUnit[i - 1]
            return str(val / FreqRatio[-1]), FreqUnit[-1]
        except:
            return str(val), "Hz"

    def geneFreq(self):
        unit = self.combo.currentText()
        val = float(self.edit.displayText())
        for r, u in zip(FreqRatio, FreqUnit):
            if(u == unit):
                self._freqVal = val * r
                self.newVal.emit(self._freqVal)
                break

    @property
    def frequency(self):
        return self._freqVal 

    def initUI(self, label, val):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        edit = QLineEdit()
        combo = QComboBox()
        layout.addWidget(edit)
        layout.addWidget(combo)
        layout.addStretch()
        for unit in FreqUnit:
            combo.addItem(unit)
        vstr, vunit = FreqEdit.parse(val)
        edit.setValidator(QRegExpValidator(QRegExp("^[0-9]+([.]{1}[0-9]+){0,1}$")))
        edit.setText(vstr)
        combo.setCurrentText(vunit)
        edit.textChanged.connect(self.geneFreq)
        combo.currentIndexChanged.connect(self.geneFreq)
        self.combo = combo
        self.edit = edit
        self.setLayout(layout)

def test():
    import sys
    app = QApplication(sys.argv)
    fe = FreqEdit("起始频率", 1e9)
    lb = QLabel()      

    def onFreqGene(freq):
        val, unit = FreqEdit.parse(freq)
        lb.setText(val + " " + unit)
        lb.adjustSize()
    
    fe.newVal.connect(onFreqGene)

    w = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(fe)
    layout.addWidget(lb)
    w.setLayout(layout)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    test()
    
__all__ = ["FreqEdit"]
