import datetime
# from PyQt5.QtCore import QThread
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Cursor

"""


"""
class MaxminRealpart():
    def __init__(self, currenttime):
        super(MaxminRealpart, self).__init__()
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.currenttime = currenttime
    def run(self, file_path):
        txt = np.loadtxt(file_path, dtype=str)[:]
        max_group = []
        min_group = []
        for i in range(len(txt)):
            data = txt[i, 2:].astype(np.float32)
            max_group.append(np.max(data))
            min_group.append(np.min(data))
        print(len(max_group))
        # start_time = self.currenttime.strftime("%H:%M:%S")
        # print(start_time)

        #生成一个matplotli认得的days序列
        delay = datetime.timedelta(seconds=2)
        end_time_ = self.currenttime+delay*(len(max_group)-1)
        import matplotlib
        time_range_2 = matplotlib.dates.drange(self.currenttime,end_time_,delay)
        # 为了解决薛定谔的drange，根据drange尺寸决定要不要丢掉一个y
        if not len(time_range_2)==len(max_group):
            max_group = max_group[:len(time_range_2)]
            min_group = min_group[:len(time_range_2)]
        fig, ax = plt.subplots()
        plt.xlabel('时间')
        plt.ylabel('电压/v')
        ax.plot_date(time_range_2, max_group,linestyle = '-',marker = '')
        ax.plot_date(time_range_2, min_group, linestyle = '-',marker = '')
        date_format = matplotlib.dates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_formatter(date_format, )
        # 生成游标
        cursor = Cursor(ax, useblit=True, color='red', linewidth=2)
        plt.show()

    def get_latest_file(self, data_path):
        lists = os.listdir(data_path)
        txt_list = []
        for path in lists:
            if '.txt' in path:
                txt_list.append(path)
        if txt_list:
            txt_list.sort(key=lambda fn: os.path.getmtime(data_path + "\\" + fn))
            file_latest = os.path.join(data_path, txt_list[-1])
            return file_latest
        else:
            return "noFile"


if __name__ == '__main__':
    currenttime = datetime.datetime.now()
    a = MaxminRealpart(currenttime)
    # currenttime = time.strftime('%H:%M:%S',time.localtime(time.time()))

    path = a.get_latest_file("..\\realpart_files")
    if not path=="noFile":
        a.run(path)
    else:
        pass
