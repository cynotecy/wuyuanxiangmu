import sys

import matplotlib
import numpy as np
from matplotlib.backends.qt_compat import QtWidgets

from controller.usrp_controller.steadyStateInterference_shibie import steadyResult_draw
import time
matplotlib.use('Qt5Agg')


def position(input_filename,standard_vaule):
    save_filename = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    print(save_filename)
    # path_input_filename = input_filename  #输入文件路径
    # input_file = np.loadtxt(path_input_filename,dtype=str,delimiter=' ')
    fres=np.loadtxt(path_input_filename,dtype=str,delimiter=' ')[0, 0:-1]  #输出频率的一维数组
    amps=np.loadtxt(path_input_filename,dtype=str,delimiter=' ')[1, 0:-1]  #输出幅度的一维数组
    user_amps=float(standard_vaule)+11
    amps = np.asarray(np.float32(amps))                                    #
    fres = np.asarray(np.float32(fres))                                    #

    list_range_lable = []
    list_maxpoint_lable=[]
    outputlist_range_list=[]
    outputlist_fre_amp_list=[]
    flag = 1   #1判断起点
    # print(amps)
    # print(fres)
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
        list_maxpoint_lable.append(list_range_lable[j] + np.argmax(amps[list_range_lable[j] : list_range_lable[j+1]]))

    for m in range(int(len(list_range_lable)/2)):
        outputlist_range_list.append("("+str(fres[list_range_lable[m*2]])+","
                                     +str(fres[list_range_lable[2*m+1]])+")")

    for k in list_maxpoint_lable:
        outputlist_fre_amp_list.append("("+str(fres[k])+","+str(amps[k])+")")

    path_output_filename='D:\\postgraduate_program\\steadyInterference\\Output_file\\%s' % save_filename    #输出文件路径

    with open(path_output_filename+'.txt','w+') as file_object:
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
    # d = position(r"..\steadyStateInterference_recvfiles\20190821170048.txt", '-100')
    d = position(r"..\steadyStateInterference_recvfiles\error1.txt", '-85')
    lists = []
    lists.append(d)
    time.sleep(1)
    # print(lists)
    # d = position(r"..\steadyStateInterference_recvfiles\20190821170157.txt", '-120')
    d = position(r"..\steadyStateInterference_recvfiles\error2.txt", '-85')
    lists.append(d)
    print(lists)
    import queue
    from controller.usrp_controller.steadyStateInterference_shibie import display_v4
    from PyQt5.QtWidgets import QApplication
    arowNum = queue.Queue()
    app = QApplication(sys.argv)
    win = display_v4.WindowClass(arowNum)
    win.pushButton(lists)
    win.show()
    sys.exit(app.exec_())