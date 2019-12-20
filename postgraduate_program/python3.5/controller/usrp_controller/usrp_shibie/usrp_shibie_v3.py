import torch
import torch.nn as nn
import torch.optim as optim
from controller.usrp_controller.usrp_shibie.resnet import ResNet, Bottleneck
import numpy as np
from controller.usrp_controller.usrp_shibie.data_process import smooth, normalization, butter_bandpass_filter
import os
from collections import Counter
from interval import Interval
import math

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
use_cuda = False
# if torch.cuda.is_available():
#     print('cuda is available')
#     use_cuda = True

classes = {0 : '05pi8PSK',  1 : '05piBPSK',  2 : '05piQAM16',  3 : '05piQPSK',  4 : '16FSK',  5 : '2FSK',  6 : '32FSK',  7 : '4FSK',  8 : '8FSK',
           9 : '8PSK', 10 : 'AM', 11 : 'BPSK', 12 : 'FM',  13 : 'GMSK', 14 : 'OOK',  15 : 'OQPSK', 16 : 'ASK',  17 : 'QAM128',  18 : 'QAM16',
           19 : 'QAM256',  20 : 'QAM32',  21 : 'QAM512', 22 : 'QAM64', 23 : 'QPSK', 24 : '025piQPSK'}



def gonglv(data):
    data_mean = np.mean(pow(abs(data), 2))
    data = data / math.sqrt(data_mean)
    return data

def read_file(file_path):
    txt = np.loadtxt(file_path, dtype=str, delimiter=' ')[0:-1]
    freq = txt[0]
    bandwidth = np.float32(txt[1])
    sample_rate = np.float32(txt[2])
    data = txt[3:]
    data = data.astype(np.float32)
    P = np.mean(pow(data[4096:8192], 2))
    data = gonglv(data)
    data = smooth(data, 3)
    data = butter_bandpass_filter(data, 1, bandwidth, sample_rate, 2)
    data = np.expand_dims(normalization(data), axis=0)
    dim1, dim2 = data.shape
    test_data = []
    data_freq = []
    for i in range(dim1):
        for j in range(min(int(dim2 / 4096), 100)):
            test_data.append(data[i][j * 4096:(j + 1) * 4096])
            data_freq.append(freq)
    test_data = np.asarray(test_data)
    data_freq = np.asarray(data_freq)
    test_data = np.expand_dims(test_data, axis=1)
    return torch.from_numpy(test_data).float(), data_freq, bandwidth, P

def model_test(model, logdir, inputs):
    # print('Evaluating model...')

    test_input, freq, bandwidth, P = inputs
    bandwidth = float(bandwidth)
    batch_size = test_input.size(0)
    signal_freq = float(freq[0]) / 1e6
    if use_cuda:
        checkpoint = torch.load(logdir)
        test_input = test_input.cuda()
    else:
        checkpoint = torch.load(logdir, map_location=lambda storage, loc:storage)

    model.load_state_dict(checkpoint)
    model.eval()
    with torch.no_grad():

        out = model(test_input).cpu().numpy()
        prior_p = np.zeros((batch_size, 25))
        u = 0.0
        if signal_freq in Interval(87, 108):  # 广播
            radio_name = '调频广播'
            u = P / 4.96e-6  # 已修改
            prior_p[:, 12] = 1.5

        elif signal_freq in Interval(450, 470):  # 农村无线接入
            radio_name = '农村无线接入'

        elif signal_freq in Interval(470, 806):  # 数字电视、微波接力
            radio_name = '数字电视、微波接力'

        elif signal_freq in Interval(825, 835):  # CDMA800上行  f=832.8, s=25M, B=1M
            radio_name = 'CDMA800上行'
            u = P / 8.49241e-06  # 已修改
            prior_p[:, 11] = 5
            prior_p[:, 23] = 6
            prior_p[:, 15] = 6

        elif signal_freq in Interval(870, 880):  # CDMA800下行  f=871, s=25M, B=1M
            radio_name = 'CDMA800下行'
            u = P / 0.00284  # 已修改
            prior_p[:, 11] = 3
            prior_p[:, 23] = 3
            prior_p[:, 15] = 2

        elif signal_freq in Interval(885, 890):  # EGSM900上行  f=887.6, s=2M, B=0.3M
            radio_name = 'EGSM900上行'
            u = P / 6.08e-08  # 已修改
            prior_p[:, 13] = 5

        elif signal_freq in Interval(890, 909):  # GSM900上行   f=890M, s=25M, B=0.2M
            radio_name = 'GSM900上行'
            u = P / 1.2141e-06  # 已修改
            prior_p[:, 13] = 5

        elif signal_freq in Interval(915, 917):  # ISM
            radio_name = 'ISM频段'

        elif signal_freq in Interval(930, 935):  # EGSM900下行   f=932, s=25M, B=0.2M
            radio_name = 'EGSM900下行'
            u = P / 0.113  # 已修改
            prior_p[:, 13] = 5

        elif signal_freq in Interval(935, 960):  # GSM900下行
            radio_name = 'GSM900下行'
            u = P / 0.166
            prior_p[:, 13] = 5

        elif signal_freq in Interval(960, 1215):  # 航空导航
            radio_name = '航空导航'

        elif signal_freq in Interval(1215, 1260):  # 科研、定位、导航
            radio_name = '科研、定位、导航'

        elif signal_freq in Interval(1260, 1300):  # 空间科学、定位、导航
            radio_name = '空间科学、定位、导航'

        elif signal_freq in Interval(1300, 1350):  # 航空导航、无线电定位
            radio_name = '航空导航、无线电定位'

        elif signal_freq in Interval(1427, 1525):  # 点对点微波通信
            radio_name = '点对点微波通信'

        elif signal_freq in Interval(1559, 1626):  # 航空、卫星导航
            radio_name = '航空、卫星导航'

        elif signal_freq in Interval(1660, 1710):  # 气象卫星通信
            radio_name = '航空、卫星导航'

        elif signal_freq in Interval(1710, 1745):  # 移动GSM1800    f=1738.4, s=25M, B=0.2M
            radio_name = 'GSM1800上行'
            u = P / 8.2364e-07
            prior_p[:, 13] = 3

        elif signal_freq in Interval(1755, 1780):  # FDD-LTE上行    f=1755.6, s=25M, B=0.3M
            radio_name = 'FDD-LTE上行'
            u = P / 2.0031e-06
            prior_p[:, 22] = 5
            prior_p[:, 18] = 5
            prior_p[:, 23] = 5

        elif signal_freq in Interval(1785, 1805):  # 民航
            radio_name = '民航'

        elif signal_freq in Interval(1805, 1840):  # 移动GSM1800      f=1835,s=25M,b=0.2e6
            radio_name = 'GSM1800下行'
            u = 1 # P / 0.035093 待修改！！！
            prior_p[:, 13] = 15

        elif signal_freq in Interval(1850, 1875):  # 联通FDD下行       f=1856,s=25M,b=2e6
            radio_name = 'FDD-LTE下行'
            u = P / 0.0432
            prior_p[:, 22] = 10
            prior_p[:, 18] = 10
            prior_p[:, 23] = 10

        elif signal_freq in Interval(1880, 1900):  # TD-SCDMA         f=1890,s=25M,b=2e6
            radio_name = 'TD-SCDMA'
            u = P / 0.000581
            prior_p[:, 22] = 5
            prior_p[:, 18] = 3
            prior_p[:, 23] = 3

        elif signal_freq in Interval(1920, 1935):  # 电信CDMA2000      f=1921,s=2M,b=0.2e6
            radio_name = 'CDMA2000上行'
            u = P / 3.0310596e-07  # !!!待修改
            prior_p[:, 11] = 10
            prior_p[:, 23] = 10
            prior_p[:, 15] = 10

        elif signal_freq in Interval(1940, 1955):  # 联通WCDMA    f=1944,s=25M,b=1e6
            radio_name = 'WCDMA上行'
            u = P / 2.0066e-06
            prior_p[:, 11] = 3
            prior_p[:, 23] = 3

        elif signal_freq in Interval(1980, 2010):  # 卫星通信
            radio_name = '卫星通信'

        elif signal_freq in Interval(2010, 2025):  # 移动TD      f=2023.6,s=25M,b=1e6
            radio_name = 'TD-SCDMA'
            u = P / 9.2889e-07
            prior_p[:, 11] = 5
            prior_p[:, 18] = 5
            prior_p[:, 22] = 5
            prior_p[:, 23] = 5

        elif signal_freq in Interval(2110, 2125):  # 电信CDMA2000    f=2120,s=25M,b=2e6
            radio_name = 'CDMA2000下行'
            u = P / 0.000236
            prior_p[:, 11] = 3
            prior_p[:, 23] = 3
            prior_p[:, 15] = 3

        elif signal_freq in Interval(2130, 2145):  # 联通WCDMA     f=2137.6,s=25M,b=2e6
            radio_name = 'WCDMA下行'
            u = P / 0.00214  # 已修改

            prior_p[:, 11] = 1  # 已修改
            prior_p[:, 23] = 3

        elif signal_freq in Interval(2300, 2390):  # TD-LTE        f=2347,s=25M,b=2e6
            radio_name = 'TD-LTE'
            u = P / 0.00933
            prior_p[:, 18] = 10
            prior_p[:, 23] = 10

        elif signal_freq in Interval(2400, 2483.5):  # WLAN        f=2442,s=25M,b=1e6
            radio_name = 'WLAN'
            u = P / 1.10046e-05
            prior_p[:, 11] = 3
            prior_p[:, 15] = 6
            prior_p[:, 18] = 5
            prior_p[:, 22:24] = 5

        elif signal_freq in Interval(2500, 2535):  # 卫星广播
            radio_name = '卫星广播'

        elif signal_freq in Interval(2555, 2655):  # TD-LTE      f=2645,s=25M,b=2e6
            radio_name = 'TD-LTE'
            u = P / 2.90303e-05
            prior_p[:, 11] = 5
            prior_p[:, 18] = 5
            prior_p[:, 22] = 5
            prior_p[:, 23] = 5

        elif signal_freq in Interval(5725, 5850):  # TD-LTE
            radio_name = '5Ghz无线电波'

        else:
            radio_name = 'null'
            u = 0.0
        # print('u=',end='')
        # print(u)
        out = out + u * prior_p
        pred = np.argmax(out, axis=1)
        pred_cunt = Counter(pred)
        top_3 = pred_cunt.most_common(3)
        if len(top_3) == 1:
            reslt_list = []
            reslt_list.append(str(signal_freq))
            reslt_list.append(str(bandwidth))
            string = "%s:%s%%" % (str(classes[top_3[0][0]]), str(int(top_3[0][1]) / batch_size * 100))
            reslt_list.append(string)
            reslt_list.append(radio_name)
            # str(classes[top_3[0][0]]) + ':'+ str(int(top_3[0][1]) / batch_size * 100))+'%'
            return reslt_list
            # return ('freq:{:.4f} MHz : {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100))
            # print('freq:{:.4f} MHz : {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100))
        if len(top_3) == 2:
            reslt_list = []
            reslt_list.append(str(signal_freq))
            reslt_list.append(str(bandwidth))
            string = "%s:%s%%,%s:%s%%" % (str(classes[top_3[0][0]]), str(int(top_3[0][1]) / batch_size * 100),
                                          str(classes[top_3[1][0]]), str(int(top_3[1][1]) / batch_size * 100))
            reslt_list.append(string)
            reslt_list.append(radio_name)
            return reslt_list
            # return ('freq:{:.4f} MHz : {}:{:.2f}%, {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100,
            #       classes[top_3[1][0]], int(top_3[1][1]) / batch_size * 100))
            # print('freq:{:.4f} MHz : {}:{:.2f}%, {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100,
            #       classes[top_3[1][0]], int(top_3[1][1]) / batch_size * 100))
        if len(top_3) == 3:
            reslt_list = []
            reslt_list.append(str(signal_freq))
            reslt_list.append(str(bandwidth))
            string = "%s:%s%%,%s:%s%%,%s:%s%%" %(str(classes[top_3[0][0]]), str(int(top_3[0][1]) / batch_size * 100),
                                              str(classes[top_3[1][0]]), str(int(top_3[1][1]) / batch_size * 100),
                                              str(classes[top_3[2][0]]), str(int(top_3[2][1]) / batch_size * 100))
            reslt_list.append(string)
            reslt_list.append(radio_name)
            return reslt_list
            # return ('freq:{:.4f} MHz : {}:{:.2f}%, {}:{:.2f}%, {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100,
            #       classes[top_3[1][0]], int(top_3[1][1]) / batch_size * 100, classes[top_3[2][0]], int(top_3[2][1]) / batch_size * 100))
            # print('freq:{:.4f} MHz : {}:{:.2f}%, {}:{:.2f}%, {}:{:.2f}%'.format(signal_freq, classes[top_3[0][0]], int(top_3[0][1]) / batch_size * 100,
            #       classes[top_3[1][0]], int(top_3[1][1]) / batch_size * 100, classes[top_3[2][0]], int(top_3[2][1]) / batch_size * 100))

def play(file_path):

    net = ResNet(Bottleneck,
                 [[(16, 32, 2), (32, 64, 1)] * 1,
                  [(32, 64, 2), (64, 64, 1)] * 5,
                  ])
    if use_cuda:
        net = net.cuda()
    currentPath = os.path.dirname(__file__)
    fatherPath = os.path.dirname(currentPath)
    # logdir = r'..\..\python3.5\controller\usrp_controller\logs\0709_5p.pkl'
    logdir = os.path.join(fatherPath, r'logs\0709_5p.pkl')
    if not ('\\' in file_path or '/' in file_path):
        dataList = file_path.split(' ')
        txt = np.array(dataList)
        freq = txt[0]
        bandwidth = np.float32(txt[1])
        sample_rate = np.float32(txt[2])
        data = txt[3:]
        data = data.astype(np.float32)
        P = np.mean(pow(data[4096:8192], 2))
        data = gonglv(data)
        data = smooth(data, 3)
        data = butter_bandpass_filter(data, 1, bandwidth, sample_rate, 2)
        data = np.expand_dims(normalization(data), axis=0)
        dim1, dim2 = data.shape
        test_data = []
        data_freq = []
        for i in range(dim1):
            for j in range(min(int(dim2 / 4096), 100)):
                test_data.append(data[i][j * 4096:(j + 1) * 4096])
                data_freq.append(freq)
        test_data = np.asarray(test_data)
        data_freq = np.asarray(data_freq)
        test_data = np.expand_dims(test_data, axis=1)
        input_data = (torch.from_numpy(test_data).float(), data_freq, bandwidth, P)
    else:
        input_data = read_file(file_path)
    reslt = model_test(net, logdir, inputs=input_data)
    print(reslt)
    return reslt



if __name__ == '__main__':
    file_path = r"D:\myPrograms\CASTProgram\postgraduate_program\usrp_recvfiles\single_collect_20191219104125.txt"
    a = play(file_path)
    print(a)