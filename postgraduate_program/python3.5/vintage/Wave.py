# -*- coding: utf-8 -*-
"""
上一代识别算法调用合集，已不再使用，作为参考留存
"""
import wave
import random
import math
import numpy as np
from controller.usrp_controller.usrp_shibie import usrp_shibie_v3
# from controller.esmd_controller import esmd_shibie
from controller.Pico_controller import pico_jicheng_online_pack_v2, pico_jicheng_offline_v2
from controller.usrp_controller.specEnvelope_shibie import specEnvelope_shibie_v3
from controller.usrp_controller.usrp_shibie import oc_shibie_v2
from controller.usrp_controller.steadyStateInterference_shibie import steadyStateInterference_shibie
from threading import Thread

import matplotlib.pyplot as plt
class WavePaint():
    def __init__(self, path):
        super().__init__()
        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.path = path
        self.wa = wave.open(self.path, "rb")
        self.n = 0  # 设置起始点
        self.j = 0
        self.i = 100
        self.z = 100
        self.x = 0

    # 静态图绘制函数
    def start_static_plot(self, start):
        fig1, ax1 = plt.subplots()
        self.wa.setpos(start)
        # 读取50000个点并处理矩阵
        datawav = self.wa.readframes(50000)
        datause = np.fromstring(datawav, dtype=np.short)
        datause.shape = -1, 2
        datause = datause.T
        fig1.hold(False)  # 每次绘图的时候不保留上一次绘图的结果
        ax1.set_title('静态图')
        ax1.set_ylabel('幅值')
        ax1.set_xlabel('点数')
        ax1.grid(True)
        ax1.plot(np.arange(50000), datause[0])
        fig1.show()
        self.wa.close()

    # 动态图绘制函数
    def start_dynamic_plot(self):

        def close_Event(event):
            WavePaint.wa.close()

        def on_button_press(event):

            if self.x==0:
                plt.pause(0)
                self.x=1
            else:
                plt.pause(1)
                self.x=0

        plt.figure(1).canvas.mpl_connect("button_release_event", on_button_press)
        plt.figure(1).canvas.mpl_connect("close_event", close_Event)
        plt.figure(1)
        plt.axes().set_xlim(0, 1500)
        plt.ion()
        plt.xlabel('点数')
        plt.ylabel("数值")
        plt.title("动态信号")
        plt.grid(True)
        end = []
        while True:
            # 首先绘制前i个点
            if self.j == 0:
                t = np.arange(self.i)
                self.wa.setpos(self.n)
                # 读取i个点并处理矩阵
                datawav = self.wa.readframes(self.i)
                datause = np.fromstring(datawav, dtype=np.short)
                datause.shape = -1, 2
                datause = datause.T
                # 画图，设置颜色为黑色
                plt.plot(t, datause[0], color='blue')
                end.append(datause[0][self.i-1])
                self.j += 1
                plt.pause(0.01)
            else:
                # 读取i个点并处理矩阵
                datawav = self.wa.readframes(self.i)
                datause = np.fromstring(datawav, dtype=np.short)
                datause.shape = -1, 2
                datause = datause.T
                # 前i个点的最后一个点加入
                a = np.insert(datause[0], 0, values=end, axis=0)
                # 更新end数组
                end.pop()
                end.append(a[self.i])
                self.j += 1
                t = np.arange(self.z-1, self.z+self.i)
                plt.plot(t, a, color='blue')
                self.z += self.i
                # 获取x轴的最大值与最小值
                xmin, xmax = plt.subplot().get_xlim()
                # 设置x轴移动
                if self.z >= xmax-500:
                    plt.subplot().set_xlim(xmin + 50, xmax + 50)
                plt.pause(0.01)


class UsrpProcess(Thread):
    def __init__(self, path, q):
        super(UsrpProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
    def run(self):
        a = usrp_shibie_v3.play(self.path)
        print(a)
        self.q.put(a)

class OcUsrpProcess(Thread):
    def __init__(self, q):
        super(OcUsrpProcess, self).__init__()
        self.q = q
    def run(self):
        a = oc_shibie_v2.play()
        print(a)
        self.q.put(a)



class PicoProcess_online(Thread):
    def __init__(self, path, q, length, class_name='test_device'):
        super(PicoProcess_online, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
        self.length = int(length)
    def run(self):
        a,b = pico_jicheng_online_pack_v2.configuration(self.path, self.length)
        print("a,b",a,b)
        self.q.put(a)
        self.q.put(b)


class PicoProcess_offline(Thread):
    def __init__(self, path, q, length):
        super(PicoProcess_offline, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
        self.length = int(length)
    def run(self):
        a = pico_jicheng_offline_v2.configuration(self.path, self.length)
        self.q.put(a)

class specEnvelopeProcess(Thread):
    def __init__(self, path, q):
        super(specEnvelopeProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
    def run(self):
        a = specEnvelope_shibie_v3.baoluoshibie(self.path)
        self.q.put(a)

class steadyStateInterference(Thread):
    def __init__(self, path, inner, q):
        super(steadyStateInterference, self).__init__()
        self.path = path
        self.inner = inner
        self.q = q
    def run(self):
        a = steadyStateInterference_shibie.position(self.path, self.inner)
        self.q.put(a)

if __name__ == '__main__':
    import queue
    q = queue.Queue()
    usrp = OcUsrpProcess(q)
    usrp.start()
    rslt = q.get()
    p1 = rslt[0][2]
    p2 = rslt[0][3]
    print(type(p1))
    print(type(p2))
    print(range(len(rslt)))
