# -*- coding: UTF-8 -*-
"""
@File:fakeTransmit.py
@Author:lcx
@Date:2020/1/1511:10
@Desc:虚拟远端中转，伪装工程机接收消息，回传扫频或采集数据
"""
from threading import Thread
import logging

from socketTest import socketInit
from virtualUSRP.component import Decoder, VirtualCollecter, VirtualScaner


logger = logging.getLogger("transmitLogger")
logger.setLevel(logging.DEBUG)
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

def virtualTransmit1():
    subAddress = 'tcp://127.0.0.1:6000'
    pubAddress = 'tcp://127.0.0.1:5000'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner1 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter1 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        # print '转发线程1准备就绪'
        logger.debug('转发线程1准备就绪')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner1.scan(logger, '转发线程1')
        elif action == "collect":
            virtualCollecter1.collect(logger, '转发线程1')

def virtualTransmit2():
    subAddress = 'tcp://127.0.0.1:6001'
    pubAddress = 'tcp://127.0.0.1:5001'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner2 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter2 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        # print '转发线程2准备就绪'
        logger.debug('转发线程2准备就绪')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner2.scan(logger, '转发线程2')
        elif action == "collect":
            virtualCollecter2.collect(logger, '转发线程2')

def virtualTransmit3():
    subAddress = 'tcp://127.0.0.1:6002'
    pubAddress = 'tcp://127.0.0.1:5002'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner3 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter3 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        # print '转发线程3准备就绪'
        logger.debug('转发线程3准备就绪')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner3.scan(logger, '转发线程3')
        elif action == "collect":
            virtualCollecter3.collect(logger, '转发线程3')

def virtualTransmit4():
    subAddress = 'tcp://127.0.0.1:6003'
    pubAddress = 'tcp://127.0.0.1:5003'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    collectDataDirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner4 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter4 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        # print '转发线程4准备就绪'
        logger.debug('转发线程4准备就绪')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        print action
        if action == "scan":
            virtualScaner4.scan(logger, '转发线程4')
        elif action == "collect":
            virtualCollecter4.collect(logger, '转发线程4')

if __name__ == '__main__':
    t1 = Thread(target=virtualTransmit1, name="transmitThread1")
    t1.start()
    t2 = Thread(target=virtualTransmit2, name="transmitThread2")
    t2.start()
    t3 = Thread(target=virtualTransmit3, name="transmitThread3")
    t3.start()
    t4 = Thread(target=virtualTransmit4, name="transmitThread4")
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

