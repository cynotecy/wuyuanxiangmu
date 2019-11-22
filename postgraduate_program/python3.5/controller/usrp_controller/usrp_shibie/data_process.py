import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from scipy.fftpack import fft

def smooth(dat,WSZ):
    # dat:原始数据，NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    out0 = np.convolve(dat, np.ones(WSZ,dtype=int), 'valid')/WSZ
    r = np.arange(1, WSZ-1,2)
    start = np.cumsum(dat[:WSZ-1])[::2]/r
    stop = (np.cumsum(dat[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((start, out0, stop))

def normalization(data, axis=0):
    m = np.mean(data, axis=axis)
    s = np.std(data, axis=axis)
    data = (data - m) / s
    return data

def awgn(x, snr):
    snr = 10**(snr/10.0)
    xpower = np.sum(x**2)/len(x)
    npower = xpower / snr
    return x + np.random.randn(len(x)) * np.sqrt(npower)

def butter_bandpass_filter(data, lowcut, highcut, fs, order=2): #data�����룬lowcut:��ͨ��ֹƵ�ʣ�highcut:��ͨ��ֹƵ�ʣ�fs:�����ʣ�order:�˲�������
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandpass')
    return b, a

def FFT(data):
    Fs = 10e6  # sampling rate采样率
    Ts = 1.0 / Fs  # sampling interval 采样区间


    n = len(data)  # length of the signal
    k = np.arange(n)
    T = n / Fs

    Y = fft(data).real / n  # fft computing and normalization 归一化
    return abs(Y)



if __name__ == '__main__':
    data = np.loadtxt(r'/data/data1/data/chenzhy/0310/4/QAM32/QAM32_1010M_1.txt')[:, 0]
    data = smooth(data, 3)
    data_noise = awgn(data, 10)
    #data_noise = smooth(data_noise, 3)
    plt.figure()
    plt.plot(data)
    plt.figure()
    plt.plot(data_noise)
    plt.show()
