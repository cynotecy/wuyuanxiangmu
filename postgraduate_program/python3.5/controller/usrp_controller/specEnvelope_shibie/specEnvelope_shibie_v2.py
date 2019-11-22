import numpy as np
from controller.usrp_controller.specEnvelope_shibie.functions_v2 import *


def baoluoshibie(file_path):
    x_lable = read_dat_hang(file_path, 0)
    L = len(x_lable)
    c = x_lable[-1] - x_lable[0]
    if not (((x_lable[-1] <= 880 + c) & (x_lable[-1] >= 870)) | ((x_lable[-1] <= 960 + c) & (x_lable[-1] >= 935)) | (
            (x_lable[-1] <= 1840 + c) & (x_lable[-1] >= 1805)) | ((x_lable[-1] <= 1875 + c) & (x_lable[-1] >= 1850)) | (
                    (x_lable[-1] <= 2025 + c) & (x_lable[-1] >= 2010)) | (
                    (x_lable[-1] <= 2145 + c) & (x_lable[-1] >= 2130)) | (
                    (x_lable[-1] <= 2483 + c) & (x_lable[-1] >= 2400)) | (
                    (x_lable[-1] <= 2575 + c) & (x_lable[-1] >= 2555))):
        print(x_lable[0], x_lable[-1])
        s = '超出样本库范围'
        ratee = 0
        return s, ratee

    y_lable = read_dat_hang(file_path, 1)
    y_lable = normalization(y_lable, axis=0)

    y_list, y_slope = ave_and_slope(y_lable, 30, 15)
    # bo_numb = bodongxing(y_slope, 30)

    if (x_lable[-1] <= 960 + c) & (x_lable[-1] >= 935):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\GSM900.txt')
        result, ratee = classify(y_list, normal, 0.4)
        if result == 1:
            s = 'GSM900'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]

    elif (x_lable[-1] <= 2145 + c) & (x_lable[-1] >= 2130):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\WCDMA.txt')
        result, ratee = classify(y_list, normal, 0.3)
        if result == 1:
            s = 'WCDMA'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]

    elif (x_lable[-1] <= 2483.5 + c) & (x_lable[-1] >= 2400):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\WLAN.txt')
        result, ratee = classify(y_list, normal, 0.4)
        if result == 1:
            s = 'WLAN(2.4G)'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]
    elif (x_lable[-1] <= 880 + c) & (x_lable[-1] >= 870):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\CDMA800.txt')
        result, ratee = classify(y_list, normal, 0.3)
        if result == 1:
            # print('该信号是CDMA800信号')
            s = 'CDMA800'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]
    elif (x_lable[-1] <= 1840 + c) & (x_lable[-1] >= 1805):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\GSM1800.txt')
        result, ratee = classify(y_list, normal, 0.3)
        if result == 1:
            s = 'GSM1800'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]

    elif (x_lable[-1] <= 1875 + c) & (x_lable[-1] >= 1850):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\FDD-LTE.txt')
        result, ratee = classify(y_list, normal, 0.2)
        if result == 1:
            s = 'FDD_LTE'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]
    elif (x_lable[-1] <= 2025 + c) & (x_lable[-1] >= 2010):
        normal = read_dat(r'..\python3.5\controller\usrp_controller\specEnvelope_shibie\Normal_data\TD_SCDMA.txt')
        result, ratee = classify(y_list, normal, 0.4)
        if result == 1:
            s = 'TD_SCDMA'
            return [s, ratee]
        elif result == 0:
            s = '相似度低,无法识别'
            return [s, ratee]
    else:
        s = '超出样本库范围'
        ratee = 0
        return s, ratee


if __name__ == '__main__':

    ss = baoluoshibie(r"..\baoluoshibie_files\spectrum_2555-2580.txt")

    A = ss
    print(type(A))




