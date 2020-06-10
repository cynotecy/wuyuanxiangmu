# -*- coding: UTF-8 -*-
"""
@File:VirtualCollecter.py
@Author:lcx
@Date:2020/6/923:38
@Desc:
"""
import random
import os
class VirtualCollecter():
    def __init__(self, pub_socket, collectDataDirPath):
        self.socket = pub_socket
        files = os.listdir(collectDataDirPath)  # 得到文件夹下的所有文件名称
        self.collectDataList = []
        for file in files:  # 遍历文件夹
            if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
                with open(collectDataDirPath + "/" + file, 'rb') as f:  # 打开文件
                    content = f.read()
                    self.collectDataList.append(content)  # 每个文件的文本存到list中

    def collect(self):
        i = int(random.randint(0, 15))
        print i
        self.socket.send(bytes(self.collectDataList[i]))