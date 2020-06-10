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

def test_model(model, logdir, inputs):
    # print('Evaluating model...')
    model.load_state_dict(torch.load(logdir))
    model.eval()
    test_input, freq, bandwidth, P = inputs
    bandwidth = float(bandwidth)
    batch_size = test_input.size(0)
    signal_freq = float(freq[0]) / 1e6

    with torch.no_grad():
        test_input = test_input.cuda()
        out = model(test_input).cpu().numpy()

        prior_p = np.zeros((batch_size, 25))
        if signal_freq in Interval(85, 108):  # 广播
            radio_name = 'FM广播'
            u = P / 1.92e-6    #!!!待修改
            prior_p[:, 12] = 0.5

        elif signal_freq in Interval(870, 880):  # 电信CDMA800
            radio_name = 'CDMA800'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 30
            prior_p[:, 23] = 30
            prior_p[:, 15] = 10

        elif signal_freq in Interval(935, 960):  # GSM900
            radio_name = 'GSM900'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 13] = 5

        elif signal_freq in Interval(1805, 1840):  # 移动GSM1800
            radio_name = 'GSM1800'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 13] = 5

        elif signal_freq in Interval(1850, 1875):  # 联通FDD下行
            radio_name = 'FDD-LTE'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 22] = 30
            prior_p[:, 18] = 30
            prior_p[:, 23] = 30

        elif signal_freq in (Interval(1880, 1920) or Interval(2010, 2025)):  # 移动TD
            radio_name = 'TD-SCDMA'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 30
            prior_p[:, 18] = 30
            prior_p[:, 22] = 20
            prior_p[:, 23] = 30

        elif signal_freq in Interval(2110, 2125):  # 电信CDMA2000
            radio_name = 'CDMA2000'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 30
            prior_p[:, 23] = 30
            prior_p[:, 15] = 10

        elif signal_freq in Interval(2130, 2145):  # 联通WCDMA
            radio_name = 'WCDMA'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 50
            prior_p[:, 23] = 50

        elif signal_freq in (Interval(2320, 2370) or Interval(2575, 2635)):  # 移动TD-LTE
            radio_name = 'TD-LTE'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 18] = 30
            prior_p[:, 23] = 30

        elif signal_freq in Interval(2400, 2440):  # WLAN
            radio_name = 'WLAN'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 30
            prior_p[:, 15] = 40
            prior_p[:, 18] = 30
            prior_p[:, 22:24] = 30

        elif signal_freq in (Interval(2635, 2655) or Interval(3400, 3600)):  # 电信TD-LTE
            radio_name = 'TD-LTE'
            u = P / 1.92e-6  # !!!待修改
            prior_p[:, 11] = 30
            prior_p[:, 18] = 30
            prior_p[:, 22] = 30
            prior_p[:, 23] = 30

        else:
            radio_name = 'null'
            u = 0.0

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

def test_(file_path):
    net = ResNet(Bottleneck,
                 [[(16, 32, 2), (32, 64, 1)] * 1,
                  [(32, 64, 2), (64, 64, 1)] * 5,
                  ]).cuda()

    logdir = r'..\python3.5\controller\usrp_controller\logs\0709_5p.pkl'

    input_data = read_file(file_path)
    reslt = test_model(net, logdir, inputs=input_data)
    print(reslt)
    return reslt



if __name__ == '__main__':
    file_path = r"..\usrp_recvfiles\未命名_20190717151459.dat"
    a = test_(file_path)
    print(a)