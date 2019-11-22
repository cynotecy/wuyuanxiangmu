import numpy as np
from controller.usrp_controller.specEnvelope_shibie.functions_v1 import*


def baoluoshibie(file_path):

    x_lable = read_dat_hang(file_path,0)

    if not (((x_lable[0]<=930) & (x_lable[-1]>=950)) | ((x_lable[0]<=2130) & (x_lable[-1]>=2149.9)) |((x_lable[0]<=2426) & (x_lable[-1]>=2445)) |((x_lable[0]<=2555) & (x_lable[-1]>=2570))):
        print(x_lable[0],x_lable[-1])
        s = '超出识别范围'
        return s


    y_lable = read_dat_hang(file_path,1)
    y_list,y_slope = ave_and_slope(y_lable,30,15)
    bo_numb = bodongxing(y_slope,30)

    if ((x_lable[0]<=930) & (x_lable[-1]>=950) & (bo_numb>=7) & (bo_numb<=18)):
        normal = read_dat(
            r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\GSM.txt')
        result, ratee = classify(y_list, normal)
        if result==1:
            #print('该信号是GSM信号')
            s = 'GSM'
            return s
        elif result == 0:
            s = '信号出现较大失真'
            return s
            #print('该信号bu是GSM信号')
    elif ((x_lable[0]<=2130) & (x_lable[-1]>=2149.9) & (bo_numb>=0) & (bo_numb<=4)):
        normal = read_dat(
            r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\WCDMA.txt')
        result, ratee = classify(y_list, normal)
        if result==1:
            print('该信号是WCDMA信号')
            s = 'WCDMA'
            return s
        elif result == 0:
            s = '信号出现较大失真'
            return s

    elif (x_lable[0]<=2426) & (x_lable[-1]>=2445) & (bo_numb>=0) & (bo_numb<=3):
        normal = read_dat(
            r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\WLAN.txt')
        result, ratee = classify(y_list, normal)
        if result==1:
            #print('该信号是WLAN信号')
            s = 'WLAN'
            return s
        elif result == 0:
            s = '信号出现较大失真'
            return s

    elif (x_lable[0]<=2555) & (x_lable[-1]>=2570) & (bo_numb>=0) & (bo_numb<=1):
        normal = read_dat(
            r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\LTE.txt')
        result, ratee = classify(y_list, normal)
        if result==1:
            #print('该信号是LTE信号')
            s = 'LTE'
            return s
        elif result == 0:
            s = '信号出现较大失真'
            return s

if __name__ == '__main__':
    s = baoluoshibie(r'..\specEnvelope_recvfiles\20190712213518.txt')
    print(s)

    # from matplotlib import pyplot as plt
    # plt.plot(x_lable, y_lable)
    #
    # plt.show()
