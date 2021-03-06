# -*- coding: UTF-8 -*-
"""
@File:virtualTransmit.py
@Author:lcx
@Date:2020/1/1511:10
@Desc:虚拟远端中转，伪装工程机接收消息，回传扫频或采集数据
"""
from threading import Thread
import os
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append("..")
from socketTest import socketInit
from virtualUSRP.component import Decoder, VirtualCollecter, VirtualScaner


import logging
logger = logging.getLogger("virtualTransmitLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

# 加载配置文件
# 使用minidom解析器打开 XML 文档
DOMTree = xml.dom.minidom.parse("datapath_properties.xml")
collection = DOMTree.documentElement

scanDataDirPathDic = dict()
collectDataDirPathDic = dict()
if collection.hasAttribute("shelf"):
    USRPS = collection.getElementsByTagName("deviceName")
    # dicIndex = 0
    for USRP in USRPS:
        USRPName = USRP._attrs[u"title"].childNodes[0].nodeValue
        scanDataDirPathDic[USRPName] = USRP.getElementsByTagName("scanDataDirPath")[0].childNodes[0].data
        collectDataDirPathDic[USRPName] = USRP.getElementsByTagName("collectDataDirPath")[0].childNodes[0].data
        # dicIndex += 1

def virtualTransmit1():
    deviceName = "USRP1"
    subAddress = 'tcp://127.0.0.1:6000'
    pubAddress = 'tcp://127.0.0.1:5000'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = scanDataDirPathDic[deviceName]
    collectDataDirPath = collectDataDirPathDic[deviceName]

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner1 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter1 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        logger.debug('transmit thread-1 ready')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        logger.debug(action)
        if action == "scan":
            virtualScaner1.scan(logger, 'transmit thread-1')
        elif action == "collect":
            virtualCollecter1.collect(logger, 'transmit thread-1')

def virtualTransmit2():
    deviceName = "USRP2"
    subAddress = 'tcp://127.0.0.1:6001'
    pubAddress = 'tcp://127.0.0.1:5001'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = scanDataDirPathDic[deviceName]
    collectDataDirPath = collectDataDirPathDic[deviceName]

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner2 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter2 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        logger.debug('transmit thread-2 ready')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        logger.debug(action)
        if action == "scan":
            virtualScaner2.scan(logger, 'transmit thread-2')
        elif action == "collect":
            virtualCollecter2.collect(logger, 'transmit thread-2')

def virtualTransmit3():
    deviceName = "USRP3"
    subAddress = 'tcp://127.0.0.1:6002'
    pubAddress = 'tcp://127.0.0.1:5002'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = scanDataDirPathDic[deviceName]
    collectDataDirPath = collectDataDirPathDic[deviceName]

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner3 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter3 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        logger.debug('transmit thread-3 ready')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        logger.debug(action)
        if action == "scan":
            virtualScaner3.scan(logger, 'transmit thread-3')
        elif action == "collect":
            virtualCollecter3.collect(logger, 'transmit thread-3')

def virtualTransmit4():
    deviceName = "USRP4"
    subAddress = 'tcp://127.0.0.1:6003'
    pubAddress = 'tcp://127.0.0.1:5003'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    scanDataDirPath = scanDataDirPathDic[deviceName]
    collectDataDirPath = collectDataDirPathDic[deviceName]

    # 获得虚拟scaner和虚拟collecter实例
    virtualScaner4 = VirtualScaner.VirtualScaner(pubSocket, scanDataDirPath)
    virtualCollecter4 = VirtualCollecter.VirtualCollecter(pubSocket, collectDataDirPath)

    while True:
        logger.debug('transmit thread-4 ready')
        msg = subSocket.recv()
        action = Decoder.decodeMsg(msg)
        logger.debug(action)
        if action == "scan":
            virtualScaner4.scan(logger, 'transmit thread-4')
        elif action == "collect":
            virtualCollecter4.collect(logger, 'transmit thread-4')

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

