import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np


"""在当前鼠标位置出现一条横线和一个点，当前鼠标位置随意"""
class SnaptoCursor(object):
    def __init__(self, ax, x, y):
        self.ax = ax
        self.lx = ax.axhline(color='g', alpha=1)  # the vert line
        # self.marker, = ax.plot([0],[0],'b--', linewidth = 2, markersize = 12)
        self.marker, = ax.plot([0],[0], marker="H", color="green", zorder=2)
        self.x = x # 成员是一个时间格式
        self.y = y
        self.txt = ax.text(self.x[0], 0.9, '')

    def mouse_move(self, event):
        if not event.inaxes: return
        x, y = event.xdata, event.ydata
        # indx = np.searchsorted(self.x, [x])[0]
        # x = self.x[indx]
        # y = self.y[indx]
        self.lx.set_ydata(y)
        self.marker.set_data([x],[y])
        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        self.txt.set_position((x,y))
        self.ax.figure.canvas.draw_idle()
if __name__ == '__main__':

    t = np.arange(0.0, 4.0, 0.01)
    s = np.sin(2*2*np.pi*t)
    fig, ax = plt.subplots()

    #cursor = Cursor(ax)
    cursor = SnaptoCursor(ax, t, s)
    cid = plt.connect('motion_notify_event', cursor.mouse_move)

    ax.plot(t, s,)
    plt.axis([0, 3.99, -1, 1])
    plt.show()