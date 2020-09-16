import torch
import numpy as np
# from controller.usrp_controller.usrp_shibie.data_process import smooth, normalization, butter_bandpass_filter
# from controller.usrp_controller.usrp_shibie.component.network import ResNet34
from controller.usrp_controller.usrp_shibie.data_process import smooth, normalization, butter_bandpass_filter
from controller.usrp_controller.usrp_shibie.component.network import ResNet34
import os
from collections import Counter
from collections import OrderedDict
from interval import Interval
import math
# from controller.usrp_controller.usrp_shibie.component.freqPointList import FreqPointList
from controller.usrp_controller.usrp_shibie.component.freqPointList import FreqPointList

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
user_cuda = False
# 模型全局路径，如果想要更换模型，在这里更改路径
currentPath = os.path.dirname(__file__)
# fatherPath = os.path.dirname(currentPath)
# model_path = os.path.join(fatherPath, r'component\model7.path')
model_path = os.path.join(currentPath, 'component\model7.path')

classes = {0: '05pi8PSK', 1: '05piBPSK', 2: '05piQAM16', 3: '05piQPSK', 4: '16FSK', 5: '2FSK',
           6: '32FSK', 7: '4FSK', 8: '8FSK', 9: '8PSK', 10: 'AM', 11: 'BPSK', 12: 'FM',
           13: 'GMSK', 14: 'OOK', 15: 'OQPSK', 16: 'ASK', 17: 'QAM128', 18: 'QAM16',
           19: 'QAM256', 20: 'QAM32', 21: 'QAM512', 22: 'QAM64', 23: 'QPSK', 24: '025piQPSK'}


def gonglv(data):
    """
    功率归一化
    :param data:
    :return: 归一化后的数据
    """
    data_mean = np.mean(pow(abs(data), 2))
    data = data / math.sqrt(data_mean)
    return data


def read_file(dataIn):
    """
    读取文件，并做预处理，或直接预处理数据
    文件格式，第一个数为采样频率，第二个数为带宽，第三个数为采样率
    剩余为信号数据
    :param dataIn: 字符串数组
    :returns test_data:预处理完成的数据
             freq:中心频率
             bandwidth:带宽
             P:原始信号功率
    """
    freq = dataIn[0]
    bandwidth = np.float32(dataIn[1])
    sample_rate = np.float32(dataIn[2])
    data = dataIn[3:]
    data = data.astype(np.float32)
    P = np.mean(pow(data[4096:4096 * 20], 2))
    data = gonglv(data)
    data = smooth(data, 3)
    if sample_rate > 2 * bandwidth:
        data = butter_bandpass_filter(data, 1, bandwidth, sample_rate, 2)
    data = np.expand_dims(normalization(data), axis=0)
    dim1, dim2 = data.shape
    test_data = []
    for j in range(min(int(dim2 / 4096), 100)):
        # test_data存放最多100个4096长度的数据
        # test_data第一维长度是batch_size，多少个4096数据
        # 第二维长度=4096
        test_data.append(data[0][j * 4096:(j + 1) * 4096])
    test_data = np.asarray(test_data)
    test_data = np.expand_dims(test_data, axis=1)
    return torch.from_numpy(test_data).float(), freq, bandwidth, P


def prior_probability(signal_freq, batch_size, P, freq_point_list):
    """
    遍历用户提供的表，返回先验概率矩阵
    :param freq_point_list: 用户提供的表单
    :param signal_freq:信号的频率
    :param batch_size:网络输入batch_size
    :param P:信号功率

    :return:先验概率矩阵
    """
    # lib_list = ["调频广播", "农村无线接入", "数字电视、微波接力", "CDMA800上行", "CDMA800下行", "EGSM900上行", "GSM900上行",
    #             "ISM频段", "EGSM900下行", "GSM900下行", "航空导航", "科研、定位、导航", "空间科学、定位、导航", "航空导航、无线电定位",
    #             "点对点微波通信", "航空、卫星导航", "气象卫星通信", "GSM1800上行", "FDD-LTE上行", "民航", "GSM1800下行",
    #             "FDD-LTE下行", "TD-SCDMA", "CMDA2000上行", "WCDMA上行", "卫星通信", "CDMA2000下行", "WCDMA下行",
    #             "TD-LTE", "WLAN", "卫星广播", "5Ghz无线电波"]
    user_dict = freq_point_list.getPointList()
    prior_p = np.zeros((batch_size, 25))
    u = 0.0
    radio_name = 'null'
    for key in user_dict.keys():
        value = user_dict[key]
        freql = value[0]  # 用户表单里的频率起点
        freqr = value[1]  # 用户表单里的频率终点
        # 如果信号在用户表达的频率范围内，判断标准是否在库中
        if signal_freq in Interval(freql, freqr):
            if (freql in Interval(87, 108)) & (freqr in Interval(87, 108)):
                # radio_name = '调频广播'  # 暂时不管用户表单定义的名字
                u = P / 1.96e-6
                prior_p[:, 12] = 1.5
                return prior_p * u, key

            elif (freql in Interval(450, 470)) & (freqr in Interval(450, 470)):
                # radio_name = '农村无线接入'
                return prior_p * u, key

            elif (freql in Interval(470, 806)) & (freqr in Interval(470, 806)):
                # radio_name = '数字电视、微波接力'
                return prior_p * u, key

            elif (freql in Interval(825, 835)) & (freqr in Interval(825, 835)):
                # radio_name = 'CDMA800上行'
                u = P / 8.49241e-06
                prior_p[:, 11] = 5
                prior_p[:, 23] = 6
                prior_p[:, 15] = 6
                return prior_p * u, key

            elif (freql in Interval(870, 880)) & (freqr in Interval(870, 880)):
                # radio_name = 'CDMA800下行'
                u = P / 0.00284
                prior_p[:, 11] = 3
                prior_p[:, 23] = 3
                prior_p[:, 15] = 2
                return prior_p * u, key

            elif (freql in Interval(885, 890)) & (freqr in Interval(885, 890)):
                # radio_name = 'EGSM900上行'
                u = P / 6.08e-08
                prior_p[:, 13] = 5
                return prior_p * u, key

            elif (freql in Interval(890, 909)) & (freqr in Interval(890, 909)):
                # radio_name = 'GSM900上行'
                u = P / 1.2141e-06
                prior_p[:, 13] = 5
                return prior_p * u, key

            elif (freql in Interval(915, 917)) & (freqr in Interval(915, 917)):
                # radio_name = 'ISM频段'
                return prior_p * u, key

            elif (freql in Interval(930, 935)) & (freqr in Interval(930, 935)):
                # radio_name = 'EGSM900下行'
                u = P / 0.113
                prior_p[:, 13] = 5
                return prior_p * u, key

            elif (freql in Interval(935, 960)) & (freqr in Interval(935, 960)):
                # radio_name = 'GSM900下行'
                u = P / 0.026
                prior_p[:, 13] = 5
                return prior_p * u, key

            elif (freql in Interval(960, 1215)) & (freqr in Interval(960, 1215)):
                # radio_name = '航空导航'
                return prior_p * u, key

            elif (freql in Interval(1215, 1260)) & (freqr in Interval(1215, 1260)):
                # radio_name = '科研、定位、导航'
                return prior_p * u, key

            elif (freql in Interval(1260, 1300)) & (freqr in Interval(1260, 1300)):
                # radio_name = '空间科学、定位、导航'
                return prior_p * u, key

            elif (freql in Interval(1300, 1350)) & (freqr in Interval(1300, 1350)):
                # radio_name = '航空导航、无线电定位'
                return prior_p * u, key

            elif (freql in Interval(1427, 1525)) & (freqr in Interval(1427, 1525)):
                # radio_name = '点对点微波通信'
                return prior_p * u, key

            elif (freql in Interval(1559, 1626)) & (freqr in Interval(1559, 1626)):
                # radio_name = '航空、卫星导航'
                return prior_p * u, key

            elif (freql in Interval(1660, 1710)) & (freqr in Interval(1660, 1710)):
                # radio_name = '气象卫星通信'
                return prior_p * u, key

            elif (freql in Interval(1710, 1745)) & (freqr in Interval(1710, 1745)):
                # radio_name = 'GSM1800上行'
                u = P / 8.2364e-07
                prior_p[:, 13] = 3
                return prior_p * u, key

            elif (freql in Interval(1755, 1780)) & (freqr in Interval(1755, 1780)):
                # radio_name = 'FDD-LTE上行'
                u = P / 2.0031e-06
                prior_p[:, 22] = 5
                prior_p[:, 18] = 5
                prior_p[:, 23] = 5
                return prior_p * u, key

            elif (freql in Interval(1785, 1805)) & (freqr in Interval(1785, 1805)):
                # radio_name = '民航'
                return prior_p * u, key

            elif (freql in Interval(1805, 1840)) & (freqr in Interval(1805, 1840)):
                # radio_name = 'GSM1800下行'
                u = 1
                prior_p[:, 13] = 15
                return prior_p * u, key

            elif (freql in Interval(1850, 1875)) & (freqr in Interval(1850, 1875)):
                # radio_name = 'FDD-LTE下行'
                u = P / 0.0432
                prior_p[:, 22] = 10
                prior_p[:, 18] = 10
                prior_p[:, 23] = 10
                return prior_p * u, key

            elif (freql in Interval(1880, 1900)) & (freqr in Interval(1880, 1900)):
                # radio_name = 'TD-SCDMA'
                u = P / 0.00581
                prior_p[:, 22] = 5
                prior_p[:, 18] = 3
                prior_p[:, 23] = 3
                return prior_p * u, key

            elif (freql in Interval(1920, 1935)) & (freqr in Interval(1920, 1935)):
                # radio_name = 'CDMA2000上行'
                u = P / 3.0310596e-07
                prior_p[:, 11] = 10
                prior_p[:, 23] = 10
                prior_p[:, 15] = 10
                return prior_p * u, key

            elif (freql in Interval(1940, 1955)) & (freqr in Interval(1940, 1955)):
                # radio_name = 'WCDMA上行'
                u = P / 2.066e-06
                prior_p[:, 11] = 3
                prior_p[:, 23] = 3
                return prior_p * u, key

            elif (freql in Interval(1980, 2010)) & (freqr in Interval(1980, 2010)):
                # radio_name = '卫星通信'
                return prior_p * u, key

            elif (freql in Interval(2010, 2025)) & (freqr in Interval(2010, 2025)):
                # radio_name = 'TD-SCDMA'
                u = P / 9.2889e-07
                prior_p[:, 11] = 5
                prior_p[:, 18] = 5
                prior_p[:, 22] = 5
                prior_p[:, 23] = 5
                return prior_p * u, key

            elif (freql in Interval(2110, 2125)) & (freqr in Interval(2110, 2125)):
                # radio_name = 'CDMA2000下行'
                u = P / 0.000236
                prior_p[:, 11] = 3
                prior_p[:, 23] = 3
                prior_p[:, 15] = 3
                return prior_p * u, key

            elif (freql in Interval(2130, 2145)) & (freqr in Interval(2130, 2145)):
                # radio_name = 'WCDMA下行'
                u = P / 0.00214
                prior_p[:, 11] = 1
                prior_p[:, 23] = 3
                return prior_p * u, key

            elif (freql in Interval(2300, 2390)) & (freqr in Interval(2300, 2390)):
                # radio_name = 'TD-LTE'
                u = P / 0.00933
                prior_p[:, 18] = 10
                prior_p[:, 23] = 10
                return prior_p * u, key

            elif (freql in Interval(2400, 2483.5)) & (freqr in Interval(2400, 2483.5)):
                # radio_name = 'WLAN'
                u = P / 1.10046e-05
                prior_p[:, 11] = 3
                prior_p[:, 15] = 6
                prior_p[:, 18] = 5
                prior_p[:, 22:24] = 5
                return prior_p * u, key

            elif (freql in Interval(2500, 2535)) & (freqr in Interval(2500, 2535)):
                # radio_name = '卫星广播'
                return prior_p * u, key

            elif (freql in Interval(2555, 2655)) & (freqr in Interval(2555, 2655)):
                # radio_name = 'TD-LTE'
                u = P / 2.90303e-05
                prior_p[:, 11] = 5
                prior_p[:, 18] = 5
                prior_p[:, 22] = 5
                prior_p[:, 23] = 5
                return prior_p * u, key

            elif (freql in Interval(5725, 5850)) & (freqr in Interval(5725, 5850)):
                # radio_name = '5Ghz无线电波'
                return prior_p * u, key

            else:
                # 不在库中
                # radio_name = 'null'
                u = 0.0
                return prior_p * u, 'null'

    return prior_p * u, 'null'  # 如果信号频率不存在用户表定义的频率中，返回null


def model_test(model, inputs, freq_point_list):
    """

    :param model: 传入模型
    :param inputs: 数据格式：100*4096矩阵，(一个列表，存放100个4096长度向量）
    :param freq_point_list:
    :return:
    """
    test_input, freq, bandwidth, P = inputs
    bandwidth = float(bandwidth)
    batch_size = test_input.size(0)
    signal_frq = float(freq) / 1e6

    with torch.no_grad():
        if user_cuda:
            test_input = test_input.cuda()
        out = model(test_input).cpu().numpy()
        prior_p, radio_name = prior_probability(signal_frq, batch_size, P, freq_point_list)
        out = out + prior_p
        pred = np.argmax(out, axis=1)
        pred_cnt = Counter(pred)
        top_3 = pred_cnt.most_common(3)
        if len(top_3) == 1:
            result_list = []
            result_list.append(str(signal_frq))
            result_list.append(str(bandwidth))
            string = "%s:%s%%" % (str(classes[top_3[0][0]]), str(round(int(top_3[0][1]) / batch_size * 100, 2)))
            result_list.append(string)
            result_list.append(radio_name)
            return result_list

        if len(top_3) == 2:
            result_list = []
            result_list.append(str(signal_frq))
            result_list.append(str(bandwidth))
            string = "%s:%s%%,%s:%s%%" % (
                str(classes[top_3[0][0]]), str(round(int(top_3[0][1]) / batch_size * 100, 2)),
                str(classes[top_3[1][0]]), str(round(int(top_3[1][1]) / batch_size * 100, 2)))
            result_list.append(string)
            result_list.append(radio_name)
            return result_list

        if len(top_3) == 3:
            result_list = []
            result_list.append(str(signal_frq))
            result_list.append(str(bandwidth))
            string = "%s:%s%%,%s:%s%%,%s:%s%%" % (
                str(classes[top_3[0][0]]), str(round(int(top_3[0][1]) / batch_size * 100, 2)),
                str(classes[top_3[1][0]]), str(round(int(top_3[1][1]) / batch_size * 100, 2)),
                str(classes[top_3[2][0]]), str(round(int(top_3[2][1]) / batch_size * 100, 2)))
            result_list.append(string)
            result_list.append(radio_name)
            return result_list


def extract_data_from_txt(first_line, second_line):
    """
    现在两个设备的txt数据都为三行（1-中心频率，带宽，采样率；2-Q路；3-I路）
    提取3900格式的采样数据，转换成usrp格式的数据格式

    3900格式的采样数据:
    txt文件共三行，第一行为空格分隔的中心频点、带宽和采样率，
    第二行为空格分隔的realPart数据，第三行为空格分隔的imagPart数据。

    usrp格式的采样数据格式:
    一行数据，第一个数值为采样中心频率，第二个数值为采样带宽，第三个数值为采样率，剩余数值为信号数据

    输入数据全是字符串数组
    :param first_line: 中心频点、带宽、采样率
    :param second_line: 实部数据
    :return: 符合usrp采样格式的np矩阵，一行
    :param data:
    :return:
    """
    first_line = list(first_line)
    second_line = list(second_line)
    first_line.extend(second_line)

    return np.asarray(first_line)


def extract_data_from_list(data):
    """
    数据列表为一个长字符串，"中心频点 带宽 采样率;realPart（空格分隔）;imagPart（空格分隔）"
    :param data: 3900数据
    :return: 符合usrp采样格式的np矩阵
    """

    dataSplit = data.split(";")
    first_line = dataSplit[0].split(" ")  # 中心频率，带宽，采样率
    second_line = dataSplit[2].split(" ")
    first_line.extend(second_line)

    return np.asarray(first_line)


def play(freq_point_list, file_path):
    """

    :param freq_point_list: 频点列表
    :param file_path: 信号文件路径
    :return:
    """
    net = ResNet34()
    logdir = model_path
    if user_cuda:
        net = net.cuda()
        checkpoint = torch.load(logdir)
    else:
        checkpoint = torch.load(logdir, map_location=lambda storage, loc: storage)
    net.load_state_dict(checkpoint)
    model = net.eval()
    if not ('.txt' in file_path):
        data = file_path  # 输入为数据列表
        data = extract_data_from_list(data)
    else:
        first_line = np.loadtxt(file_path, dtype=str, delimiter=' ', usecols=(0, 1, 2))[0]
        second_line = np.loadtxt(file_path, dtype=str, delimiter=' ', skiprows=2)
        data = extract_data_from_txt(first_line, second_line)
    input_data = read_file(data)
    result = model_test(model=model, inputs=input_data, freq_point_list=freq_point_list)
    return result


if __name__ == '__main__':
    """
    单元测试
    """
    freq_dict = {"调频广播": [87.0, 108.0], '农村无线接入': [450.0, 470.0], "数字电视、微波接力": [470.0, 806.0],
                 "CDMA800上行": [825.0, 835.0], "CDMA800下行": [870.0, 880], "EGSM900上行": [885.0, 890.0],
                 "GSM900上行": [890.0, 909.0], "ISM频段": [915.0, 917.0], "EGSM900下行": [930.0, 935.0],
                 "GSM900下行": [935.0, 960.0], "航空导航": [960.0, 1215.0], "科研、定位、导航": [1215.0, 1260.0],
                 "空间科学、定位、导航": [1260.0, 1300.0], "航空导航、无线电定位": [1300.0, 1350.0], "点对点微波通信": [1427.0, 1525.0],
                 "航空、卫星导航": [1559.0, 1626.0], "气象卫星通信": [1660.0, 1710.0], "GSM1800上行": [1710.0, 1745.0],
                 "FDD-LTE上行": [1755.0, 1780.0], "民航": [1785.0, 1805.0], "GSM1800下行": [1805.0, 1840.0],
                 "FDD-LTE下行": [1850.0, 1875.0], "TD-SCDMA": [1880.0, 1900.0], "CDMA2000上行": [1920.0, 1935.0],
                 "WCDMA上行": [1940.0, 1955.0], "卫星通信": [1980.0, 2010.0], "TD-SCDMA": [2010.0, 2025.0],
                 "CDMA2000下行": [2110.0, 2125.0], "WCDMA下行": [2130.0, 2145.0], "TD-LTE": [2300.0, 2390.0],
                 "WLAN": [2400.0, 2483.5], "卫星广播": [2500.0, 2535.0], "TD-LTE": [2555.0, 2655.0],
                 "5Ghz无线电波": [5725.0, 5850.0]}
    ordered_dict = OrderedDict(freq_dict)
    freq_ordered_dict = FreqPointList(ordered_dict)
    result_test = freq_ordered_dict.getPointList()
    result_test = play(freq_ordered_dict,
                       r"D:\myPrograms\CASTProgram\postgraduate_program\data\usrp_recvfiles\auto_recognize\oc_collect_20200908143134.txt")
    print(result_test)
