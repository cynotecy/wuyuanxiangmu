"""
@File:interferenceCancellationCalling.py
@Author:lcx
@Date:2020/1/1610:14
@Desc:
"""
from controller.usrp_controller.interference_cancellation import interference_cancellation
import numpy as np

def callInterferenceCancellation(arg):
    # if '/' in arg or '\\' in arg:
    if len(arg) == 2 and ".txt" in arg[0]:
        x1, y1, x2, y2 = getdata(arg)
    else:
        data1, data2 = arg
        if ":" in data1:
            data1 = data1.split(":")[1]
        if ":" in data2:
            data2 = data2.split(":")[1]
        data1List = data1.split(';')
        freq1List = data1List[0].split(' ')
        bins1List = data1List[1].split(" ")
        x1 = [float(i) for i in freq1List]
        y1 = [float(i) for i in bins1List]
        data2List = data2.split(';')
        freq2List = data2List[0].split(' ')
        bins2List = data2List[1].split(" ")
        x2 = [float(i) for i in freq2List]
        y2 = [float(i) for i in bins2List]
        x1 = np.asarray(np.float32(x1))
        y1 = np.asarray(np.float32(y1))
        x2 = np.asarray(np.float32(x2))
        y2 = np.asarray(np.float32(y2))
    targetx, targety = interference_cancellation.interference_eliminate(x1, y1, x2, y2)
    return targetx, targety

def getdata(paths):
    path1 = paths[0]
    path2 = paths[1]
    x1 = np.loadtxt(path1, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
    y1 = np.loadtxt(path1, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
    x1 = np.asarray(np.float32(x1))
    y1 = np.asarray(np.float32(y1))

    x2 = np.loadtxt(path2, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
    y2 = np.loadtxt(path2, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
    x2 = np.asarray(np.float32(x2))
    y2 = np.asarray(np.float32(y2))

    return x1, y1, x2, y2