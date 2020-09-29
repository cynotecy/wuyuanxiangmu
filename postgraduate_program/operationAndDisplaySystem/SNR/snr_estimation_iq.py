import numpy as np
from SNR.component.dataGet_iq import dataGet_iq
import matplotlib.pyplot as plt
import math
import wave


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
def power(data, Fs):
	Ts = 1/Fs
	#amp_v = 10**(data/20)
	power = (sum((data[:,0]**2)*Ts) + sum((data[:,1]**2)*Ts))/data.shape[0]
	return power

def snr_estimation_iq(data_clean, data_signal):
	pn = power(data_clean, 25e6)
	psn = power(data_signal, 25e6)
	if (psn <= pn):
		return '第一次采集的信号能量大于第二次采集的信号能量，请检查操作是否正确！'
	snr = 10*math.log10((psn - pn)/pn)
	return snr

if __name__ == '__main__':
    #测试用例

    #data_root1 = 'iq.wav'
    #data_root2 = 'OOK.wav'
    #data_clean, fs1 = read_wav_data(data_root1)
    #data_signal, fs2 = read_wav_data(data_root2)
    data_clean = dataGet_iq('single_collect_20200928202649.txt')
    data_signal = dataGet_iq('single_collect_20200928202834.txt')
    print(snr_estimation_iq(data_signal[:,:], data_clean[:,:]))
    