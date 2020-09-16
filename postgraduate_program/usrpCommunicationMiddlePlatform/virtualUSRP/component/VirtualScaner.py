# -*- coding: UTF-8 -*-
"""
@File:VirtualScaner.py
@Author:lcx
@Date:2020/6/923:38
@Desc:
"""
import random
import os

import logging
logger = logging.getLogger("virtualScanerLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)
class VirtualScaner():
    def __init__(self, pub_socket, scanDataDirPath):
        self.socket = pub_socket
        files = os.listdir(scanDataDirPath)  # 得到文件夹下的所有文件名称
        self.scanDataList = []
        for file in files:  # 遍历文件夹
            if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
                with open(scanDataDirPath + "/" + file, 'rb') as f:  # 打开文件
                    content = f.read()
                    self.scanDataList.append(content)  # 每个文件的文本存到list中

    def scan(self, logger, source):
        i = int(random.randint(0, 15))
        msg = "{}扫频转发，第{}个文件".format(source, str(i))
        logger.debug(msg)
        self.socket.send(bytes(self.scanDataList[i]))