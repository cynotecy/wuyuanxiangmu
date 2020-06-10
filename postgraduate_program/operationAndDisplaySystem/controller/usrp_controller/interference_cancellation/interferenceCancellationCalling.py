"""
@File:interferenceCancellationCalling.py
@Author:lcx
@Date:2020/1/1610:14
@Desc:
"""
from controller.usrp_controller.interference_cancellation import interference_cancellation
import numpy as np

def callInterferenceCancellation(arg):
    print(type(arg))
    print(len(arg))
    # if '/' in arg or '\\' in arg:
    if len(arg) == 2:
        x1, y1, x2, y2 = getdata(arg)
    else:
        x1, y1, x2, y2 = arg
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