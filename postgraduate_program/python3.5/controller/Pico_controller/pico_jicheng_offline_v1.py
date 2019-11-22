'''
程序说明：
(1)该程序是用于离线识别数据库下载的脉冲
(2)界面只需调用 configuration(txt_path,length,test_path)函数进行配置
'''

from sklearn.externals import joblib
import numpy as np
import scipy.stats as sp
import pywt
from scipy.signal import argrelextrema
import pandas as pd
import math
import os
import warnings
# from mat_to_txt import mat_to_txt
warnings.filterwarnings("ignore", category=DeprecationWarning)


# 读取数据
def data_read(data_path):
    '''
    :param data_path: 一个txt
    :return: 一个txt数据，为浮点型
    '''
    read_data = []
    with open(data_path, 'r') as f:
        data = f.readlines()  # txt中所有字符串读入data
        for line in data:
            # print(line)
            odom = line.strip('\n')  # 将单个数据分隔开存好
            odom = float(odom)
            read_data.append(odom)
    return read_data


# 数据截取
def var_adap_start(data):
    '''
    函数功能：通过方差自适应的方法进行信号有效段截取
    :param data: 一个原始信号
    :return: 有效段截取之后的信号
    '''
    window = 100  # 窗长
    step = 20  # 步移，重叠（window-step）的长度

    y = (data - np.min(data))/(np.max(data)-np.min(data))#归一化
    noise_var = np.var(data[0:299]) #环境中的方差
    circle = math.floor((len(y) - (window - step)) / step)
    vars = []
    for i in range(circle - 1):
        subHead = np.int(1 + step * (i))  # 起始点
        subEnd = np.int(subHead + window - 1)  # 终点
        vars.append(np.var(y[subHead:subEnd]))

    var_mean = np.mean(vars)
    # start_var_threshold = noise_var + var_mean
    # end_var_threshold = 2 * noise_var + 0.1 * var_mean

    start_var_threshold = noise_var + var_mean
    end_var_threshold = noise_var  # 通过调节该参数值确定起始点位置
    # + 0.01 * var_mean
    for i in range(circle - 1):
        if vars[i] > start_var_threshold: break

    start_point = step * i

    for j in range(i, circle - 1):
        if vars[j] < end_var_threshold: break
    end_point = step * j
    y_output = y[start_point:end_point]  # 截取之后
    return y_output


def normalization(data, axis=0):
    m = np.mean(data, axis=axis)
    s = np.std(data, axis=axis)
    data_temp = data - m
    data = data_temp / s
    return data


# [hjorth, wrapper1, wrapper2, wavelet_features, wrapper3]
# 特征提取共38个特征
def hjorth(input):
    '''
    :param input: [batch signal]
    :return:
    '''
    realinput = input
    lenth = len(realinput)
    hjorth_activity = np.zeros(len(realinput))
    hjorth_mobility = np.zeros(len(realinput))
    hjorth_diffmobility = np.zeros(len(realinput))
    hjorth_complexity = np.zeros(len(realinput))
    diff_input = np.diff(realinput)
    diff_diffinput = np.diff(diff_input)
    k = 0
    for signal in realinput:
        hjorth_activity[k] = np.var(signal)
        hjorth_mobility[k] = np.sqrt(np.var(diff_input[k]) / hjorth_activity[k])
        hjorth_diffmobility[k] = np.sqrt(np.var(diff_diffinput[k]) / np.var(diff_input[k]))
        hjorth_complexity[k] = hjorth_diffmobility[k] / hjorth_mobility[k]
        k = k + 1

    # returning hjorth activity, hjorth mobility , hjorth complexity
    return np.sum(hjorth_activity) / lenth, np.sum(hjorth_mobility) / lenth, np.sum(
        hjorth_complexity) / lenth


# Kurtosis, 2nd Diff Mean, 2nd Diff Max
def my_kurtosis(inputs):
    b = inputs
    lenth = len(b)
    output = np.zeros(len(b))
    k = 0
    for i in b:
        mean_i = np.mean(i)
        std_i = np.std(i)
        t = 0.0
        for j in i:
            # Formula: (1/N)*(summation(x_i-mean)/standard_deviation)^4-3
            t += (pow((j - mean_i) / std_i, 4) - 3)
        kurtosis_i = t / len(i)
        # Saving the kurtosis in the array created
        output[k] = kurtosis_i
        # Updating the current row no.
        k += 1
    return np.sum(output) / lenth


def secDiffMean(inputs):
    b = inputs
    lenth = len(b)

    output = np.zeros(len(b))
    temp1 = np.zeros(len(b[0]) - 1)
    k = 0
    for i in b:
        t = 0.0
        for j in range(len(i) - 1):
            temp1[j] = abs(i[j + 1] - i[j])
        for j in range(len(i) - 2):
            t += abs(temp1[j + 1] - temp1[j])
        output[k] = t / (len(i) - 2)
        k += 1
    return np.sum(output) / lenth


def secDiffMax(inputs):
    b = inputs
    lenth = len(b)
    output = np.zeros(len(b))
    temp1 = np.zeros(len(b[0]) - 1)
    k = 0
    for i in b:
        for j in range(len(i) - 1):
            temp1[j] = abs(i[j + 1] - i[j])
        t = temp1[1] - temp1[0]
        for j in range(len(i) - 2):
            if abs(temp1[j + 1] - temp1[j]) > t:
                t = temp1[j + 1] - temp1[j]

        output[k] = t
        k += 1
    return np.sum(output) / lenth


def wrapper1(inputs):
    kurtosis = my_kurtosis(inputs)
    sec_diff_mean = secDiffMean(inputs)
    sec_diff_max = secDiffMax(inputs)
    return kurtosis, sec_diff_mean, sec_diff_max


def skewness(inputs):
    data = inputs
    lenth = len(data)
    skew_array = np.zeros(len(data))
    index = 0
    for i in data:
        skew_array[index] = sp.stats.skew(i, axis=0, bias=True)
        index += 1
    return np.sum(skew_array) / lenth


def first_diff_mean(inputs):
    data = inputs
    lenth = len(data)
    diff_mean_array = np.zeros(len(data))
    index = 0
    for i in data:
        sum = 0.0
        for j in range(len(i) - 1):
            sum += abs(i[j + 1] - i[j])
        diff_mean_array[index] = sum / (len(i) - 1)
        index += 1
    return np.sum(diff_mean_array) / lenth


def first_diff_max(inputs):
    data = inputs
    lenth = len(data)
    diff_max_array = np.zeros(len(data))
    first_diff = np.zeros(len(data[0]) - 1)
    index = 0
    for i in data:
        max = 0.0
        for j in range(len(i) - 1):
            first_diff[j] = abs(i[j + 1] - i[j])
            if first_diff[j] > max:
                max = first_diff[j]
        diff_max_array[index] = max
        index += 1
    return np.sum(diff_max_array) / lenth


def wrapper2(inputs):
    # coeff = coeff_var(inputs)
    slew = skewness(inputs)
    fdmeam = first_diff_mean(inputs)
    fdmax = first_diff_max(inputs)
    return slew, fdmeam, fdmax
    #coeff,


# Wavelet transform features
def wavelet_features(epoch):
    lenth = len(epoch)
    cA_values = []
    cD_values = []
    cA_mean = []
    cA_std = []
    cA_Energy = []
    cD_mean = []
    cD_std = []
    cD_Energy = []
    Entropy_D = []
    Entropy_A = []
    for i in range(lenth):
        cA, cD = pywt.dwt(epoch[i, :], 'coif1')
        cA_values.append(cA)
        cD_values.append(cD)
    # calculating the coefficients of wavelet transform.
    for x in range(lenth):
        cA_mean.append(np.mean(cA_values[x]))
        cA_std.append(np.std(cA_values[x]))
        cA_Energy.append(np.sum(np.square(cA_values[x])))
        cD_mean.append(np.mean(cD_values[x]))
        cD_std.append(np.std(cD_values[x]))
        cD_Energy.append(np.sum(np.square(cD_values[x])))
        Entropy_D.append(np.sum(np.square(cD_values[x]) * np.log(np.square(cD_values[x]))))
        Entropy_A.append(np.sum(np.square(cA_values[x]) * np.log(np.square(cA_values[x]))))
        Entropy_DD = np .sum(Entropy_D) / lenth
        # print(Entropy_DD)
    return np.sum(cA_mean) / lenth, np.sum(cA_std) / lenth, np.sum(cD_mean) / lenth, np.sum(cD_std) / lenth, np.sum(
        cA_Energy) / lenth, np.sum(cD_Energy) / lenth, np.sum(Entropy_A) / lenth,np.sum(Entropy_D) / lenth


# Variance and Mean of Vertex to Vertex Slope
def first_diff(inputs):
    b = inputs
    c = np.diff(b)
    return c


def slope_mean(inputs):
    b = inputs
    lenth = len(inputs)
    output = np.zeros(len(b))
    k = 0
    for i in b:
        x = i
        # amp_max = i[argrelextrema(x, np.greater)[0]]  # storing maxima value
        t_max = argrelextrema(x, np.greater)[0]
        # amp_min = i[argrelextrema(x, np.less)[0]]  # storing minima value
        t_min = argrelextrema(x, np.less)[0]
        t = np.concatenate((t_max, t_min), axis=0)
        t.sort()  # sort on the basis of time

        amp = np.zeros(len(t))
        res = np.zeros(len(t) - 1)
        for l in range(len(t)):
            amp[l] = i[t[l]]
        amp_diff = first_diff(amp)

        t_diff = first_diff(t)

        for q in range(len(amp_diff)):
            res[q] = amp_diff[q] / t_diff[q]
        output[k] = np.mean(res)
        k = k + 1
    return np.sum(output) / lenth


def slope_var(inputs):
    b = inputs
    lenth = len(b)
    output = np.zeros(len(b))
    k = 0
    for i in b:
        x = i
        # amp_max = i[argrelextrema(x, np.greater)[0]]  # storing maxima value
        t_max = argrelextrema(x, np.greater)[0]  # storing time for maxima
        # amp_min = i[argrelextrema(x, np.less)[0]]  # storing minima value
        t_min = argrelextrema(x, np.less)[0]  # storing time for minima value
        t = np.concatenate((t_max, t_min), axis=0)  # making a single matrix of all matrix
        t.sort()  # sorting according to time

        amp = np.zeros(len(t))
        res = np.zeros(len(t) - 1)
        for l in range(len(t)):
            amp[l] = i[t[l]]

        amp_diff = first_diff(amp)

        t_diff = first_diff(t)

        for q in range(len(amp_diff)):
            res[q] = amp_diff[q] / t_diff[q]  # calculating slope

        output[k] = np.var(res)
        k = k + 1
    return np.sum(output) / lenth


def wrapper3(inputs):
    smean = slope_mean(inputs)
    svar = slope_var(inputs)
    return smean, svar



'''
基于直方图的信号纹理特征
'''


def signal_to_values(num_values, signal):
    '''
    #将数据划分成 num_values 等份
    :param num_values:  划分等份数目
    :param signal:       一维信号,array类型
    :return:
    '''

    signal = np.array(signal, dtype=np.float32)
    sig_min = signal.min()
    sig_max = signal.max()

    signal_vol = num_values * (signal - sig_min) / (sig_max - sig_min)
    signal_vol = np.floor(signal_vol) + 1

    signal_vol[signal_vol == num_values + 1] = num_values
    return signal_vol


'''
 基于GLCM的信号纹理特征
'''
def sig_glcm(signal_vol, kernal_size=1, stride=1):
    '''
    计算信号的灰度共生矩阵
    :param signal_vol: 信号
    :param kernal_size: 和当前位置的距离
    :param stride: 每次移动步长
    :return:
    '''
    signal_len = signal_vol.shape[1]
    width = signal_vol.max()
    width = int(width)
    glcm = np.zeros((width, width))
    i = 0
    while(True):
        if i + kernal_size < signal_len:
            l = signal_vol[0, i]
            k = signal_vol[0, i + kernal_size]
            # print(int(l), int(k))
            glcm[int(l-1), int(k-1)] += 1
            i += stride
        else:
            break

    return glcm


def compute_glcm_distributions(glcm):
    N_g = glcm.shape[0]
    p = glcm / np.sum(glcm)
    p_x = np.sum(p, axis=1)
    p_y = np.sum(p, axis=0)

    p_x = p_x[:, np.newaxis]
    p_y = p_y[:, np.newaxis]

    #p_{x+y}
    p_xpy = np.zeros((2*N_g, 1))
    for this_row in range(N_g):
        for this_col in range(N_g):
            p_xpy[this_row + this_col] = p_xpy[this_row + this_col] + p[this_row, this_col]

    #p_{x-y}
    p_xmy = np.zeros((N_g, 1))
    for this_row in range(N_g):
        for this_col in range(N_g):
            p_xmy[np.abs(this_row - this_col)] = p_xmy[np.abs(this_row - this_col)] + p[this_row, this_col]
    return p, p_x,  p_y, p_xpy, p_xmy, N_g


def compute_glcm_metrics(p, p_x,  p_y, p_xpy, p_xmy, N_g):
    metrics_vect ={
        'Angular Second Moment': None,
        # 'Contrast': None,
        'Correlation': None,
        'Sum of squares variance': None,
        'Inverse Difference moment': None,
        'Sum average': None,
        'Sum variance': None,
        'Sum Entropy': None,
        'Entropy': None,
        'Difference Variance': None,
        'Difference Entropy': None,
        'Information Correlation 1': None,
        'Information Correlation 2': None,
        'Autocorrelation': None,
        'Dissimilarity': None,
        'Cluster Shade': None,
        'Cluster Prominence': None,
        'Maximum Probability': None,
        'Inverse Difference': None}

    #SE Entropy
    SE = - np.sum(p_xpy[p_xpy > 0] * np.log(p_xpy[p_xpy > 0]))

    #Entropy This is also HXY used later
    HXY = - np.sum(p[p > 0] * np.log(p[p > 0]))

    # Needed for later
    pp_xy = p_x * p_y.T

    HXY1 = - np.sum(p[pp_xy > 0] * np.log(pp_xy[pp_xy > 0]))
    HXY2 = - np.sum(pp_xy[pp_xy > 0] * np.log(pp_xy[pp_xy > 0]) )
    HX = - np.sum(p_x[p_x > 0] * np.log(p_x[p_x > 0]))
    HY = - np.sum(p_y[p_y > 0] * np.log(p_y[p_y > 0]))


    n = [num for num in np.arange(N_g)]
    n = np.array(n, np.float32)
    n = n[:, np.newaxis]

    ndr, ndc = np.mgrid[0:N_g, 0:N_g]

    #(1)Angular Second Moment
    metrics_vect['Angular Second Moment'] = np.sum(p**2)

    # (2)Contrast
    temp = (n**2)*p_xmy
    # print('temp:', temp.shape)
    metrics_vect['Contrast'] = np.sum(temp)

    #(3)Correlation
    nn = n+1
    mu_x = np.sum(nn * p_x)
    mu_y = np.sum(nn * p_y)
    sg_x = np.sqrt(np.sum((nn - mu_x)**2 * p_x))
    sg_y = np.sqrt(np.sum((nn - mu_y)**2 * p_y))

    if sg_x*sg_y == 0:
        metrics_vect['Correlation'] = 0
    else:
        metrics_vect['Correlation'] = (np.sum(ndr.reshape([-1, ]) * ndc.reshape([-1, ]) *
                                              p.reshape([-1, ])) - (mu_x * mu_y)) / (sg_x * sg_y)

    #(4)Sum of squares variance
    metrics_vect['Sum of squares variance'] = np.sum(((ndr.reshape([-1, ]) - np.mean(p.reshape([-1, ])))**2) *
                                                     p.reshape([-1, ]))
    #(5)Inverse Difference moment
    '''
    因分母为0导致结果出现inf，替换成均值
    '''
    metrics_vect['Inverse Difference moment'] = np.sum((1. / (1+((ndr.reshape([-1, ]) - ndc.reshape([-1, ])) * p.reshape([-1, ])))))
    if math.isinf(metrics_vect['Inverse Difference moment']):
        data, mean_values = data_deal()
        metrics_vect['Inverse Difference moment'] = mean_values
    else:
        pass
    #(6)Sum average
    metrics_vect['Sum average'] = np.sum(np.arange(1, 2*N_g+1) * p_xpy.reshape([-1, ]))
    #(7)Sum variance
    metrics_vect['Sum variance'] = np.sum(((np.arange(1, 2 * N_g+1) - metrics_vect['Sum average'])**2) *
                                          p_xpy.reshape([-1, ]))

    #(8)Sum Entropy
    metrics_vect['Sum Entropy'] = SE
    #(9)Entropy
    metrics_vect['Entropy'] = HXY
    #(10)Difference Variance
    mu_xmy = np.sum(np.arange(0, N_g) * p_xmy.reshape([-1, ]))
    metrics_vect['Difference Variance'] = np.sum(((np.arange(0, N_g) - mu_xmy)**2) * p_xmy.reshape([-1, ]))
    #(11)Difference Entropy
    metrics_vect['Difference Entropy'] = - np.sum(p_xmy[p_xmy > 0] * np.log(p_xmy[p_xmy > 0]))
    #(12) and (13) Information Correlation
    if (np.max([HX, HY]) == 0):
        metrics_vect['Information Correlation 1'] = 0
    else:
        metrics_vect['Information Correlation 1'] = (HXY - HXY1) / np.max([HX, HY])

    metrics_vect['Information Correlation 2'] = np.sqrt((1 - np.exp(-2 * (HXY2 - HXY))))

    # (14)Autocorrelation
    metrics_vect['Autocorrelation'] = np.sum((ndr.reshape([-1, ]) * ndc.reshape([-1, ])) * p.reshape([-1, ]))
    # (15)Dissimilarity
    metrics_vect['Dissimilarity'] = np.sum(np.abs((ndr.reshape([-1, ]) - ndc.reshape([-1, ]))) * p.reshape([-1, ]))
    # (16)Cluster Shade
    metrics_vect['Cluster Shade'] = np.sum(((ndr.reshape([-1, ]) + ndc.reshape([-1, ]) - mu_x - mu_y)**3) *
                                           p.reshape([-1, ]))
    # (17)Cluster Prominence
    metrics_vect['Cluster Prominence'] = np.sum(((ndr.reshape([-1, ]) + ndc.reshape([-1, ]) - mu_x - mu_y)**4) *
                                                p.reshape([-1, ]))
    # (18)Maximum Probability
    metrics_vect['Maximum Probability'] = np.max(p)

    # (19)Inverse Difference
    metrics_vect['Inverse Difference'] = np.sum((1. / (1 + np.abs(ndr.reshape([-1, ]) - ndc.reshape([-1, ])))) * p.reshape([-1, ]))

    result=[value for (key, value) in sorted(metrics_vect.items())]
    # print(result)
    return result


def texture_feature_extraction(data):
# def texture_feature_extraction(each_path,label):
    one_signal_feature = []
    all_features = []
    all_labels = []

    # data = np.loadtxt(each_path).astype(np.float32)
    data=np.array(data)
    data = data.reshape(1, len(data))
    signal = signal_to_values(128, data)
    glcm = sig_glcm(signal, 1, 1)
    p, p_x, p_y, p_xpy, p_xmy, N_g = compute_glcm_distributions(glcm)
    met = compute_glcm_metrics(p, p_x, p_y, p_xpy, p_xmy, N_g)
    one_signal_feature.extend(met)


    # all_labels.append([label])
    # all_features.append(one_signal_feature)
    #all_labels.extend([label])
    all_features.extend(one_signal_feature)
    return all_features  #all_labels


#def general_feature_extraction(each_path,label):
def general_feature_extraction(data):
    one_signal_feature = []
    all_features = []
    all_labels = []
    func = [hjorth, wrapper1, wrapper2, wavelet_features, wrapper3]

    #data = np.loadtxt(each_path).astype(np.float32)
    data=np.array(data)
    data1 = data.reshape(len(data), 1)
    data = data1.T
    # 归一化，之前进行了功率归一化
    data = normalization(data, axis=1)
    for f in func:
        feature = f(data)
        one_signal_feature.extend(feature)
    # all_labels.append([label])
    #all_labels.extend([label])
    all_features.extend(one_signal_feature)

    return all_features #all_labels


def get_index():
    general_index =['hjorth_activity','hjorth_mobility','hjorth complexity','kurtosis','secDiffMean','secDiffMax',
        'slew', 'fdmeam', 'fdmax','cA_mean','cA_std', 'cD_mean', 'cD_std','cA_Energy', 'cD_Energy',
        'Entropy_A','Entropy_D','smean', 'svar']
    # 'coeff',

    metrics_vect = {
        'Angular Second Moment': None,
        'Contrast': None,
        'Correlation': None,
        'Sum of squares variance': None,
        'Inverse Difference moment': None,
        'Sum average': None,
        'Sum variance': None,
        'Sum Entropy': None,
        'Entropy': None,
        'Difference Variance': None,
        'Difference Entropy': None,
        'Information Correlation 1': None,
        'Information Correlation 2': None,
        'Autocorrelation': None,
        'Dissimilarity': None,
        'Cluster Shade': None,
        'Cluster Prominence': None,
        'Maximum Probability': None,
        'Inverse Difference': None}
    texture_index = [key for(key,value)in sorted(metrics_vect.items())]
    all_index =general_index+ texture_index+['label']
    return all_index

def data_deal():
    index = np.arange(0, 38, 1)
    data_path = r'..\python3.5\controller\Pico_controller\history_feature_data\new_pico_feature.csv'
    data = pd.read_csv(data_path, usecols=index)
    data[np.isnan(data)] = 0
    data_numpy = data.values
    data_column_sum = 0
    num = 0
    for i in data_numpy[:, 32]:
        if math.isinf(i):
            pass
        else:
            data_column_sum = data_column_sum + i
            num = num + 1
    mean_values = float(data_column_sum / num)
    data[np.isinf(data)] = mean_values
    return data, mean_values


def get_normalized_data_oneSignal(input_data):
    data, mean_values = data_deal()
    m = np.mean(data, axis=0)
    s = np.std(data, axis=0)
    data_temp = input_data - m
    normal_input_data = data_temp / s
    return normal_input_data


def get_testdata(root_path, test_path, length):
    '''
    函数功能：将测试文件夹中的数据存到一个txt中，并设置读取数量
    :param: root_path: 测试文件夹路径，length:读取文件数量
    :return: 测试所用的正确设备名称
    '''
    test_files = []

    for root, dirs, files in os.walk(root_path):
        for i in files:
            #数据读取路径
            data_path = os.path.join(root,i)
            test_files.append(data_path)

        test_files = test_files[:length]

    if len(test_files):
        with open(test_path, 'w') as f:
            for test_file in test_files:
                f.write('{}\n'.format(test_file))
    else:
        pass




def max_voter(pre_result):
    '''
    函数功能：返回数组中重复次数最多的元素
    :param : 测试数组
    :return: 重复次数最多的元素
    '''
    temp = 0
    for i in pre_result:
        if pre_result.count(i) > temp:
            max_str = i
            temp = pre_result.count(i)
    return max_str



def recongnize(test_path):
    '''
    :param input_path: 一个采集txt数据的路径
    :return: 识别结果
    '''
    key_value = {0: "fan", 1: "power", 2: "shipeiqi", 3: "WD_200"} #根据实际情况进行修改

    input = np.loadtxt(test_path, str)
    pre_result = []
    if input.shape is ():
        try:
            data = data_read(input)
            data_cut = var_adap_start(data)  # 信号截取
            texture_feature = texture_feature_extraction(data_cut)
            general_feature = general_feature_extraction(data_cut)
            sum_features = general_feature + texture_feature  # 特征提取，此时的两种特征提取函数和训练时不同，仅仅提取一个信号的特征
            sum_features = np.array(sum_features, np.float32)
            normal_feature_oneSignal = get_normalized_data_oneSignal(sum_features)            # print("特征归一化之后：", normal_feature_oneSignal)
            normal_feature_oneSignal = normal_feature_oneSignal.values.reshape(1, 38)
            father_path = os.path.abspath('.')
            model_path = r'..\python3.5\controller\Pico_controller\model_saved\AdaBoost_GBDT.py'  # 获取模型所在目录

            clf = joblib.load(model_path)  # 模型加载
            result = clf.predict(normal_feature_oneSignal)
            np.dtype(np.uint8, result)
            result = np.uint8(result)
            result = key_value[result[0]]  # 由于返回的result是一个list，且只有一个元素，因此只取其中一个元素
            pre_result.append(result)
            return pre_result
        except:
            pass
    else:
        for each_path in input:
            try:
                data = data_read(each_path)
                data_cut = var_adap_start(data)  # 信号截取
                texture_feature = texture_feature_extraction(data_cut)
                general_feature = general_feature_extraction(data_cut)
                sum_features = general_feature + texture_feature  # 特征提取，此时的两种特征提取函数和训练时不同，仅仅提取一个信号的特征
                # print(np.shape(sum_features))
                # sum_features.append(general_feature[1])
                # sum_features.append(general_feature[2])
                # sum_features.append(general_feature[9])
                sum_features = np.array(sum_features, np.float32)
                # print("提取完特征：sum_features", sum_features)
                normal_feature_oneSignal = get_normalized_data_oneSignal(sum_features)
                # print("特征归一化之后：", normal_feature_oneSignal)
                normal_feature_oneSignal = normal_feature_oneSignal.values.reshape(1, 38)
                # normal_feature_oneSignal = normal_feature_oneSignal.values.reshape(1, 3)
                # print("改变数据维度归一化后的特征：", normal_feature_oneSignal)
                father_path = os.path.abspath('.')
                model_path = r'..\python3.5\controller\Pico_controller\model_saved\AdaBoost_GBDT.py'  # 获取模型所在目录

                clf = joblib.load(model_path)  # 模型加载
                result = clf.predict(normal_feature_oneSignal)
                np.dtype(np.uint8, result)
                result = np.uint8(result)
                result = key_value[result[0]]  # 由于返回的result是一个list，且只有一个元素，因此只取其中一个元素
                pre_result.append(result)
            except:
                pass
        return pre_result

def remove_files(test_path):
    '''
    函数功能：删除test_path以及其txt内容里面对应的文件路径
    :param: test_path: 在txt_path中选取lenth个文件，并把路径存成一个txt，此路径需要指定到txt，如r'H:\data\test_path.txt'
    :return:
    '''
    input = np.loadtxt(test_path, str)
    for each_path in input:
        os.remove(each_path)
    os.remove(test_path)


# 检查文件夹内是否有txt
def dectect_folder(data_path):
    lists = os.listdir(data_path)
    txt_list = []
    for path in lists:
        if '.txt' in path:
            txt_list.append(path)
    if txt_list:
        return 1
    else:
        return 0


def remove_files(txt_path):
    '''
    函数功能：删除txt_path文件夹里的所有文件
    :param:
    :return:
    '''
    for root, dirs, files in os.walk(txt_path):
        for i in files:
            # 数据读取路径
            data_path = os.path.join(root, i)
            os.remove(data_path)


def configuration(txt_path,length):
    '''
    函数功能：配置pico开关脉冲的数据文件路径
    :param:
            txt_path: 存txt文件路径（文件夹）,程序执行后清空文件
            length: 读取txt文件夹的数据文件数量
            test_path: 在txt_path中选取lenth个文件，并把路径存成一个txt，此路径需要指定到txt，如r'H:\data\test_path.txt'
    :return: 测试所用的正确设备名称
    '''

    warnings.filterwarnings("ignore")
    test_path = r'..\interference_file\txtpath\test_path.txt'
    flag = dectect_folder(txt_path)
    if flag == 1:
        get_testdata(txt_path, test_path, length)
        pre_result = recongnize(test_path)
        pre_result = max_voter(pre_result)
        # remove_files(txt_path)
        os.remove(test_path)
        return pre_result
    else:
        print("测试文件夹为空")
        return '0'



if __name__ == '__main__':
    txt_path = r'..\interference_file\txt\power\20190626171347'  # mat存txt文件路径,存入数据库后清空
    # test_path = r'..\interference_file\txtpath\test_path.txt'  # txt_path中选取lenth个文件，并把路径存成一个txt
    length = 100  # 读取文件夹的数据文件数量，可在界面手动更改
    pre_result = configuration(txt_path, length)
    print(pre_result)




