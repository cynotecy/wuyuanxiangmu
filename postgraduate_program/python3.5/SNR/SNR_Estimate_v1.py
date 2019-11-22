# 该版本为追钟版本，其中使用了功率归一化和分布归一化，
# 使采集的数据在matlab上和python读出来的数据一样。

import numpy as np
import wave
import cmath
import math
from threading import Thread
import queue
import scipy.io.wavfile as wavfile


class SNR_finally(Thread):
    # trigger = pyqtSignal(int)

    def __init__(self, path, q):
        super(SNR_finally, self).__init__()
        self.path = path
        self.q = q

    def run(self):
        data = self.read_dat(self.path)
        self.snr_calculate(data, 1, 2)

    def gonglv(self, data):
        data1 = np.mean(pow(abs(data), 2))
        data = data / math.sqrt(data1)
        return data

    def normalization(self, data):
        m = np.mean(data)
        s = np.std(data)
        data_temp = data - m
        data = data_temp / s
        return data

    # def read_wave_data(self, file_path):
    #     # open a wave file, and return a Wave_read object
    #     f = wave.open(file_path, "rb")
    #     # read the wave's format infomation,and return a tuple
    #     params = f.getparams()
    #     # get the info
    #     nchannels, sampwidth, framerate, nframes = params[:4]
    #     # Reads and returns nframes of audio, as a string of bytes.
    #     str_data = f.readframes(50000)
    #     # close the stream
    #     f.close()
    #     # turn the wave's data to array
    #     wave_data = np.fromstring(str_data, dtype=np.short)
    #
    #     # for the data is stereo,and format is LRLRLR...
    #     # shape the array to n*2(-1 means fit the y coordinate)
    #     # wave_data.shape = -1, 2
    #     # # transpose the data
    #     # wave_data = wave_data.T
    #     # wave_data = wave_data.astype(np.int32)
    #
    #     wave_data = self.normalization(self.gonglv(wave_data))
    #     wave_data = wave_data[:500]
    #     return wave_data

    '''只可用于不同调制方式的信噪比估计，使用M2M4算法进行估计
           inputs:输入信号
           Ka:信号峰值
           Kv:噪声类型，取值为2时，代表复噪声，取值为3时，代表实噪声
    '''

    def snr_calculate(self, data, Ka, Kn):
        m2 = np.mean(data * data).astype(np.float32)
        m4 = np.mean(data * data * data * data).astype(np.float32)

        # print(m2)
        # print(m4)

        Py1 = (m2 * (Kn - 2) + cmath.sqrt(abs((4 - Ka * Kn) * m2 * m2 + m4 * (Ka + Kn - 4))))
        Py2 = (m2 * (Kn - 2) - cmath.sqrt(abs((4 - Ka * Kn) * m2 * m2 + m4 * (Ka + Kn - 4))))
        # print(Py1)
        # print(Py2)

        Pn = abs(m2 - Py1)
        snr = abs(10 * math.log10((abs(Py1) / Pn)))
        self.q.put(str(round(snr, 2)) + 'db')

        return str(round(snr, 2)) + 'db'  # round():结果保留两位小数

    def read_dat(self, file_path, data_len = 20000):
        txt = np.loadtxt(file_path, dtype=str, delimiter=' ')[3:data_len]
        data = txt[3:]
        data = data.astype(np.float32)
        data = self.normalization(self.gonglv(data))
        test_data = np.asarray(data)
        return test_data


if __name__ == '__main__':

    file_path = r"..\usrp_recvfiles\未命名_20190717151533.dat"
    # 示例程序
    q = queue.Queue()
    snr = SNR_finally(file_path, q)
    data = snr.read_dat(file_path, data_len=200000)
    snr = snr.snr_calculate(data, 1, 2)
    print(snr)

    # print(str(snr)+'db')
