"""
本脚本输入门限频谱文件的地址，返回超频列表。
输入文件的存储格式为：
第一行是门限值，
第二行是频点，
第三行是幅值。
"""

import matplotlib
import numpy as np
import logging
import queue
import sys
from controller.usrp_controller.usrp_shibie import oc_list_display_v1

matplotlib.use('Qt5Agg')

logger = logging.getLogger("Main.ocListGetting")
def position(x, y, threshold):
    user_amps = float(threshold)
    fres = np.array(x)
    amps = np.array(y)

    list_range_lable = []
    list_maxpoint_lable=[]
    outputlist_range_list=[]
    outputlist_fre_amp_list=[]
    flag = 1   #1判断起点
    for i in range(len(amps)):
        if flag and amps[i] > user_amps:
            list_range_lable.append(i)
            flag = 0

        if flag == 0 and amps[i] < user_amps:
            list_range_lable.append(i)
            flag = 1

    if len(list_range_lable) % 2 != 0:
          list_range_lable.append(len(amps)-1)

    for j in range(0, len(list_range_lable) - 1, 2):
        try:
            list_maxpoint_lable.append(
                list_range_lable[j] + np.argmax(amps[list_range_lable[j]: list_range_lable[j + 1]]))
        except Exception:
            logger.debug("wrong data at {}".format(j))

    # # 输出文件
    #范围
    for m in range(int(len(list_range_lable)/2)):
        outputlist_range_list.append("("+str(fres[list_range_lable[m*2]])+","
                                     +str(fres[list_range_lable[2*m+1]])+")")

    # 中心频率，幅值
    for k in list_maxpoint_lable:
        outputlist_fre_amp_list.append("("+str(fres[k])+","+str(amps[k])+")")
    c = []
    d = []
    e = []
    # print("len(outputlist_fre_amp_list)=", str(len(outputlist_fre_amp_list)))
    for i in range(len(outputlist_fre_amp_list)):
        c.append(str(outputlist_range_list[i].replace("(", '').replace(")", '')) + ',' + str(outputlist_fre_amp_list[i]).replace("(", '').replace(")", ''))
        cc = c[i].split(',')
        ccc = float(cc[0]), float(cc[1]), float(cc[2]), float(cc[3])
        d.append(ccc)
    e.append(d)
    # if not q.empty():
    #     q.get()
    # q.put('超频点判断完毕')
    return e

if __name__ == '__main__':
    # with open(r"C:\Users\gouhu\Desktop\0916联调问题\问题1频谱数据.txt", "r") as f:
    path = r"D:\myPrograms\CASTProgram\postgraduate_program\data\usrp_recvfiles\usrp_scan\scan_spectrum_20200916172530.txt"
    # lines = f.readlines()
    # x = lines[0].split(" ")
    # y = lines[1].split(" ")
    x = np.loadtxt(path, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
    y = np.loadtxt(path, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
    x = np.asarray(np.float32(x))
    y = np.asarray(np.float32(y))
    threshold = -100
    import queue
    q = queue.Queue()
    d = position(x, y, threshold)
    print(d)
    print(len(d[0]))

