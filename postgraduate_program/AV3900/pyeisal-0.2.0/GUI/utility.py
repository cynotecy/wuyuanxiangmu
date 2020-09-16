import matplotlib.style
import time

def readbleFrequency(x, pos):
        if(x >= 1e9):
            s = '{:1.3f}GHz'.format(x*1e-9)
        elif(x >= 1e6):
            s = '{:1.3f}MHz'.format(x*1e-6)
        elif(x >= 1e3):
            s = '{:1.3f}kHz'.format(x*1e-3)
        else:
            s = '{:1.0f}Hz'.format(x)
        return s

def utcTimeString(utcSec):
    return time.asctime(time.localtime(utcSec))

def useStyle(styleList):
    matplotlib.style.use(styleList)


