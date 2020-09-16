from SNR.network import ResNet18
import torch
import torch.nn as nn
import numpy as np
import wave
import math
import os

#设置使用cpu或gpu
device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
#print(torch.cuda.is_available())


def normalization(data, axis = 1):
    #数据标准化

    m = np.mean(data, axis = axis)
    mean = m.reshape(2, -1)
    s = np.std(data, axis = axis)#计算标准差
    st = s.reshape(2, -1)
    data = (data - mean) / st
    return data

def gonglv(data, axis = 0):
    #功率归一化

    data0 = data[:, 0]
    data1 = data[:, 1]
    data_mean0 = np.mean(pow(abs(data), 2))
    data_mean1 = np.mean(pow(abs(data), 2))
    data0 = data0 / math.sqrt(data_mean0)
    data1 = data1 / math.sqrt(data_mean1)
    out = np.vstack((data0, data1))
    return out.T


def awgn(x, pnp):
    #高斯白

    pn1 = pnp/2#pnp/(1+ratio2)
    pn0 = pn1#ratio2*pn1
    x0 = x[:, 0]
    x1 = x[:, 1]
    x0 = x0 + np.random.randn(len(x0)) * np.sqrt(pn0)
    x1 = x1 + np.random.randn(len(x1)) * np.sqrt(pn1)
    y = np.vstack((x0, x1))
    return y.T


def read_wav_data(filename):
    #读取wav文件

    wav = wave.open(filename, "r") # 打开一个wav格式的声音文件流
    num_frame = wav.getnframes() # 获取帧数
    num_channel = wav.getnchannels() # 获取声道数
    framerate = wav.getframerate() # 获取帧速率
    num_sample_width = wav.getsampwidth() # 获取实例的比特宽度，即每一帧的字节数
    str_data = wav.readframes(num_frame) # 读取全部的帧
    wav.close() # 关闭流
    wave_data = np.fromstring(str_data, dtype = np.short) # 将声音文件数据转换为数组矩阵形式,两个字节一个取样值，因此是short
    
    wave_data.shape = -1, num_channel # 按照声道数将数组整形，单声道时候是一列数组，双声道时候是两列的矩阵
    wave_data = wave_data.astype(np.float32)
    #wave_data = wave_data.T # 将矩阵转置
    wave_data = wave_data
    return wave_data, framerate

def snr_estimation(data):
    #信噪比估计
    #输入：两路iq数据 samples*2
    #输出：估计出的信噪比

    currentPath = os.path.dirname(__file__)
    model_file = os.path.join(currentPath, 'model11.pth')
    model = ResNet18()
    model.to(device)                                        # 送入GPU，利用GPU计算
    model.load_state_dict(torch.load(model_file, map_location = device))#"cuda:0"
    start = 500#10000000
    data = data[start:start+10000, :]
    model.eval()
    with torch.no_grad():
        data = gonglv(data)
        data = data.T
        data = normalization(data)
        data = torch.from_numpy(data)
        data = data.float()
        data = np.expand_dims(data, axis=0)
        data = torch.from_numpy(data)
        data = data.to(device)
        output = model(data)
        #print('output: '+str(output))
        out_cpu = output.cpu()
    return str(out_cpu.numpy()[0,0])

def add_noise(data, original_snr, target_snr):
    #添加噪声
    #输入:
    #   data: 两路iq数据 samples*2
    #   original_snr: data的信噪比
    #   target_snr: 目标信噪比，单位dB
    #输出:
    #   加噪声后的数据 samples*2

    ratio1 = 10**(original_snr/10)
    x0 = data[:,0]
    x1 = data[:,1]
    x0_power = np.sum(x0**2)/len(x0)
    x1_power = np.sum(x1**2)/len(x1)
    power = x0_power + x1_power
    pno = power/(1+ratio1)
    ps = ratio1*pno

    pnp = ps/(10**(target_snr/10))-pno

    data_noise_added = awgn(data, pnp)

    return data_noise_added

if __name__ == '__main__':
    #测试用例

    data_root = 'GMSK.wav'
    wave_data, fs = read_wav_data(data_root)
    original = snr_estimation(wave_data)
    print(original)
    data_with_noise = add_noise(wave_data, original, 3)
    snr_after = snr_estimation(data_with_noise)
    print(snr_after)