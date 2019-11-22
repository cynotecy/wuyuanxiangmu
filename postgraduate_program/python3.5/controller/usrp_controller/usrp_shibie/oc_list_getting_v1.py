"""
本脚本输入门限频谱文件的地址，返回超频列表。
输入文件的存储格式为：
第一行是门限值，
第二行是频点，
第三行是幅值。
"""

import matplotlib
import numpy as np
import queue
import sys
from controller.usrp_controller.usrp_shibie import oc_list_display_v1

matplotlib.use('Qt5Agg')


def position(input_filename):
    # save_filename = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    # print(save_filename)
    path_input_filename = input_filename      #输入文件路径

    file_object = open(path_input_filename, 'r')
    filelist = []
    try:
        for line in file_object:
            line_ = line.replace("\n", "")  # 去掉换行
            filelist.append(line_.split(" "))
    finally:
        file_object.close()
    standard_vaule = filelist[0][0]
    # fres = np.array(filelist[1])
    # amps = np.array(filelist[2])

    # fres = np.loadtxt(path_input_filename,dtype=str,delimiter=' ')[0, 0:-1]  #输出频率的一维数组
    # amps=np.loadtxt(path_input_filename,dtype=str,delimiter=' ')[1, 0:-1]  #输出幅度的一维数组
    user_amps = float(standard_vaule)+11
    # print('user_amps=', end='')
    print(user_amps)
    fres = np.asarray(np.float32(filelist[1][0:-2]))
    amps = np.asarray(np.float32(filelist[2][0:-2]))

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

    # # 输出文件
    for m in range(int(len(list_range_lable)/2)):
        outputlist_range_list.append("("+str(fres[list_range_lable[m*2]])+","
                                     +str(fres[list_range_lable[2*m+1]])+")")

    for k in list_maxpoint_lable:
        outputlist_fre_amp_list.append("("+str(fres[k])+","+str(amps[k])+")")

    # path_output_filename='D:\\postgraduate_program\\steadyInterference\\Output_file\\%s' % save_filename    #输出文件路径
    #
    # with open(path_output_filename+'.txt','w+') as file_object:
    #     for n in range(len(outputlist_range_list)):
    #         file_object.write("\n"+str(outputlist_range_list[n])+":"+str(outputlist_fre_amp_list[n]))

    c = []
    d = []
    e = []
    for i in range(len(outputlist_fre_amp_list)):
        c.append(str(outputlist_range_list[i].replace("(", '').replace(")", '')) + ',' + str(outputlist_fre_amp_list[i]).replace("(", '').replace(")", ''))
        cc = c[i].split(',')
        ccc = float(cc[0]), float(cc[1]), float(cc[2]), float(cc[3])-11
        d.append(ccc)
        e.append(d)

    return e

if __name__ == '__main__':
    d = position(r"..\usrp_recvfiles\threshold\198707ae-d6c2-11e9-837d-a088699cd42e.txt")
    print(d)
    print(len(d))

    # # 获取行号
    # oc_rowNum_select = range(len(d[0]))
    # # 将中心频率和带宽存入辅助文件供py2脚本读取
    # fw = open(r"..\usrp_recvfiles\oc_selected_rows\collectList.txt", 'w')  # 将要输出保存的文件地址
    # for i in range(len(oc_rowNum_select)):
    #     rowName_ = oc_rowNum_select[i]
    #     centreWrite = float(d[0][rowName_][2])
    #     start = float(d[0][rowName_][0])
    #     end = float(d[0][rowName_][1])
    #     bdwidthWrite = int((end - start)*1000000)
    #     fw.write(str(centreWrite) + ' ')
    #     fw.write(str(bdwidthWrite) + '\n')
    # fw.close()
    # ###################辅助文件写入完毕#################

    # from PyQt5.QtWidgets import QApplication
    # arowNum = queue.Queue()
    # app = QApplication(sys.argv)
    # win = oc_list_display_v1.WindowClass()
    # win.pushButton(d)
    # win.show()
    # sys.exit(app.exec_())