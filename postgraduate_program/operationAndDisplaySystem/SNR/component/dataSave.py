"""
@File:dataSave.py
@Author:lcx
@Date:2020/8/309:21
@Desc:数据存储函数，输入数据、存储文件夹路径、文件类型、命名前缀，返回存储地址
"""
import time
import os
def dataSave(data, path, type, prefix):
    localTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    fileName = "{}_{}.{}".format(prefix, localTime, type)
    savePath = os.path.join(path, fileName)
    with open(savePath, "w+") as file:
        file.write(data)
    return savePath