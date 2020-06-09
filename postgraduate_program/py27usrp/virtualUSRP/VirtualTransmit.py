# -*- coding: UTF-8 -*-
"""
@File:fakeTransmit.py
@Author:lcx
@Date:2020/1/1511:10
@Desc:虚拟远端中转，伪装工程机接收消息，回传扫频或采集数据
"""
import random
import struct
import matplotlib.pyplot as plt
import crcmod
from functions.spectrum_smooth import spectrum_smooth_v4
from virtualUSRP.component import Decoder, VirtualCollecter, VirtualScaner
from socketTest import socketInit
import os
from threading import Thread


def virtualTransmit1():
    subAddress = 'tcp://127.0.0.1:6666'
    pubAddress = 'tcp://127.0.0.1:5555'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner1 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter1 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        print '转发线程准备就绪'
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner1.scan()
        elif action == "collect":
            virtualCollecter1.collect()

def virtualTransmit2():
    subAddress = 'tcp://127.0.0.1:7777'
    pubAddress = 'tcp://127.0.0.1:9999'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner2 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter2 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        print '转发线程准备就绪'
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner2.scan()
        elif action == "collect":
            virtualCollecter2.collect()

if __name__ == '__main__':
    import time
    t1 = Thread(target=virtualTransmit1)
    t1.start()
    t2 = Thread(target=virtualTransmit2)
    t2.start()

    t1.join()
    t2.join()

