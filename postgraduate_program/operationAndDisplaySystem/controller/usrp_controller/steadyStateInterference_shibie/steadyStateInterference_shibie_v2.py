import sys

import matplotlib
import numpy as np
import logging
from matplotlib.backends.qt_compat import QtWidgets

# from controller.usrp_controller.steadyStateInterference_shibie import steadyResult_draw
import time
matplotlib.use('Qt5Agg')

logger = logging.getLogger("steadyStateInterfaceLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)
def position(fres, amps, standard_vaule, path_output_filename):
    # save_filename = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    user_amps = float(standard_vaule)
    list_range_lable = []
    list_maxpoint_lable=[]
    outputlist_range_list=[]
    outputlist_fre_amp_list=[]
    flag = 1   #1判断起点
    for i in range(len(amps)):
        if flag and amps[i] > user_amps :
            list_range_lable.append(i)
            flag = 0

        if flag == 0 and amps[i] < user_amps:
            list_range_lable.append(i)
            flag = 1

    if len(list_range_lable) % 2 != 0:
          list_range_lable.append(len(amps)-1)


    for j in range(0,len(list_range_lable)-1,2):
        try:
            list_maxpoint_lable.append(list_range_lable[j] + np.argmax(amps[list_range_lable[j] : list_range_lable[j+1]]))
        except Exception:
            logger.debug("wrong data at {}".format(j))

    for m in range(int(len(list_range_lable)/2)):
        outputlist_range_list.append("("+str(fres[list_range_lable[m*2]])+","
                                     +str(fres[list_range_lable[2*m+1]])+")")

    for k in list_maxpoint_lable:
        outputlist_fre_amp_list.append("("+str(fres[k])+","+str(amps[k])+")")

    # path_output_filename='D:\\postgraduate_program\\steadyInterference\\Output_file\\%s' % save_filename    #输出文件路径

    with open(path_output_filename+'.txt','w') as file_object:
        for n in range(len(outputlist_range_list)):
            file_object.write("\n"+str(outputlist_range_list[n])+":"+str(outputlist_fre_amp_list[n]))

    c = []
    d = []
    for i in range(len(outputlist_fre_amp_list)):
        c.append(str(outputlist_range_list[i].replace("(", '').replace(")", '')) + ',' + str(outputlist_fre_amp_list[i]).replace("(", '').replace(")", ''))
        cc = c[i].split(',')
        ccc = float(cc[0]), float(cc[1]), float(cc[2]), float(cc[3])-11
        d.append(ccc)
    # print(d)

    return d

if __name__ == '__main__':
    path = r"C:\Users\gouhu\Desktop\0916联调问题\问题1频谱数据.txt"
    x = np.loadtxt(path, dtype=str, delimiter=' ')[0, 0:-1]  # 输出频率的一维数组
    y = np.loadtxt(path, dtype=str, delimiter=' ')[1, 0:-1]  # 输出幅度的一维数组
    x = np.asarray(np.float32(x))
    y = np.asarray(np.float32(y))
    threshold = -100
    import queue

    q = queue.Queue()
    d = position(x, y, threshold, r"steadyOutput.txt")
    print(d)
    print(len(d[0]))