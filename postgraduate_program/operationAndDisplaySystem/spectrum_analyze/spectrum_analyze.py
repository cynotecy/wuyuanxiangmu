'''
实时频谱分析程序说明：
(1)该程序需给定文件夹，文件夹内存储频谱数据，格式为txt
(2)该程序会自动寻找文件夹内最新的txt文件作为数据来源
(3)该程序输出的频谱颜色代表该频点出现的频次或概率
'''


import numpy as np
import os
import matplotlib.pyplot as plt
import collections
import time
import tkinter



start = time.clock()

class SpectrumAnalyze:
    num = 0

    # data_path为存储频谱数据的文件夹路径
    def __init__(self, data_path):
        self.data_path = data_path
        self.warning_report = ['Error:文件夹中无频谱数据!']
        self.plot_report = ['分析频谱中……']
        self.file_int = []
        self.file = []
        self.frequency_raw = []
        self.amplitude_raw = []
        self.frequency_int_raw = []
        self.amplitude_int_raw = []
        self.spectrum = []

        sc = 0

    # 获取文件夹内最新的文件
    def get_latest_file(self):
        lists = os.listdir(self.data_path)
        txt_list = []
        for path in lists:
            if '.txt' in path:
                txt_list.append(path)
            else:
                pass
        if txt_list:
            txt_list.sort()
            file_latest = os.path.join(self.data_path, txt_list[self.num])
            print(file_latest)
            return file_latest
        else:
            return self.warning_report

    # 频谱数据处理，得到各个频点的出现频次
    def spectrum_deal(self,):
        flag = self.get_latest_file()
        if flag[0] == self.warning_report[0]:
            return self.warning_report
        else:
            spectrum_file = flag

            #  存储整数作为统计频点的标准，所有整数部分相同的坐标判为同一个坐标
            self.file_int = np.loadtxt(spectrum_file).astype(np.int)

            #  存储实际频点和幅度用作画图
            self.file = np.loadtxt(spectrum_file).astype(np.float32)

            for i in range(len(self.file)):
                if i % 2 == 0:
                    self.frequency_raw.append(self.file[i])
                else:
                    self.amplitude_raw.append(self.file[i])

            for i in range(len(self.file_int)):
                if i % 2 == 0:
                    self.frequency_int_raw.append(self.file_int[i])
                else:
                    self.amplitude_int_raw.append(self.file_int[i])

            # 将txt中的频点和幅值的整数部分分别存储为1*N维数组，作为判别值
            frequency_int = np.array(self.frequency_int_raw).flatten()
            amplitude_int = np.array(self.amplitude_int_raw).flatten()

            # 将频点和幅值数组合并，维数为N*2
            array_num_int = np.column_stack((frequency_int, amplitude_int))

            # 将频点和幅值存成坐标，放到列表中

            for i in array_num_int:
                self.spectrum.append(tuple(i))

            # 统计频次，coordinate存放坐标，dot_count存放频次
            spectrum_dict = collections.Counter(self.spectrum)
            coordinate_standard = list(spectrum_dict.keys())
            dot_count_standard = list(spectrum_dict.values())

            # 创建坐标对应频次的字典
            spectrum_probability_dict = dict(zip(coordinate_standard, dot_count_standard))

            frequency = np.array(self.frequency_raw)
            amplitude = np.array(self.amplitude_raw)

            dot_num_raw = []
            for i in range(frequency.shape[0]):
                array_num = np.column_stack((frequency[i], amplitude[i]))
                num_each_rows = []
                for j in array_num:
                    j = tuple(j.astype(np.int))
                    num_each_rows.append(spectrum_probability_dict.get(j))
                    array_num_each_rows = num_each_rows
                array_num_each_rows = np.array(array_num_each_rows)
                dot_num_raw.append(array_num_each_rows)
            dot_num = np.array(dot_num_raw)
            return dot_num

    def on_key_press(self, event):
        raise tkinter.TclError



    # 画频谱图
    def spectrum_plot(self):

        # fig, ax = plt.subplots()
        # fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        data_result = self.spectrum_deal()
        plt.ion()
        fre = []
        amp = []
        dot = []
        if str(data_result[0]) == self.warning_report[0]:
            return self.warning_report
        else:
            for i in range(len(self.frequency_raw)):
                plt.clf()
                fre.append(self.frequency_raw[i])
                amp.append(self.amplitude_raw[i])
                dot.append(data_result[i])
                # fig = plt.figure()
                # fig.canvas.mpl_connect('key_press_event', self.on_key_press)
                # ax1 = fig.add_subplot(111)
                sc = plt.scatter(fre, amp, c=dot, cmap=plt.cm.rainbow, marker='d', linewidths=0)
                plt.grid()
                bar_label = plt.colorbar(sc)
                bar_label.set_label(u'频点出现频次')
                plt.xlabel(u'频率（KHz）')
                plt.ylabel(u'功率幅度（dB）')
                plt.pause(0.1)
            elapsed = (time.clock() - start)
            print("Time used:", elapsed)

if __name__ == '__main__':

    a1 = SpectrumAnalyze(r'..\realtime_recv')
    while a1.num <= 2000:
        try:
            result = a1.spectrum_plot()
            print(result)
            a1.num += 1
            a1.__init__(r'..\realtime_recv')
        except IndexError:
            break
        except tkinter.TclError:
            break
        # except:
        #     break


