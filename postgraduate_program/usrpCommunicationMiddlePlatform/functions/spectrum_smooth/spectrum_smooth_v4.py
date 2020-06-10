#!/usr/bin/python
#-*-coding:utf-8-*-
"""
集成版本
"""
import os
import numpy as np

def binary_search(arr, item):
    low = 0
    height = len(arr)-1
    deta = 0.0015
    mid = 0
    while low <= height:
        mid = (height + low) // 2
        if arr[mid] > item + deta: # 往左边缩小
            height = mid - 1
        elif arr[mid] < item - deta: # 往右边缩小
            low = mid + 1
        else:
            return mid
    return mid

def smooth(dat, WSZ):
    # dat:原始数据，NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    out0 = np.convolve(dat, np.ones(WSZ, dtype=int), 'valid') / WSZ
    r = np.arange(1, WSZ-1, 2)
    start = np.cumsum(dat[:WSZ-1])[::2]/r
    stop = (np.cumsum(dat[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((start, out0, stop))

def smooth_spectrum(spectrum_x, spectrum_y, base_x, base_y, dirPath):
    '''30-100M减底噪'''
    if spectrum_x[0] < 86.5:
        start = binary_search(base_x, spectrum_x[0])
        print "start:", start
        if spectrum_x[-1] < 86.5:
            spectrum_y = spectrum_y - base_y[start: start + len(spectrum_y)] - 102
        else:
            stop = binary_search(base_x, 86.5)
            print "stop:", stop
            print "len_spectrum_y:", len(spectrum_y[0: stop]), "len_base_y:", len(base_y[start: stop])
            
            spectrum_y[0: (stop - start)] = spectrum_y[0: (stop - start)] - base_y[start: stop] - 102

    '''去毛刺'''
    index = 3073
    d = np.load(os.path.join(dirPath, r'd1.npy'))
    d2= np.load(os.path.join(dirPath, r'd_128.npy'))
    t = 128
    while index < (len(spectrum_x) - t/2):
        tmp = index - 7 + np.argmax(spectrum_y[index - 7: index + 7])
        '''平滑'''
        if spectrum_x[tmp]<2500:
            deta = spectrum_y[tmp] - spectrum_y[index - 20]
            spectrum_y[tmp-32:tmp+32] = spectrum_y[tmp-32:tmp+32] - 1.2*deta*d
            for i in range(64):
                spectrum_y[tmp - 32 + i] = sum(spectrum_y[tmp - 32 + i - 32:tmp - 32 + i + 32]) / 64
        else:
            deta = spectrum_y[tmp] - spectrum_y[index - 30]
            spectrum_y[tmp - int(t/2):tmp + int(t/2)] = spectrum_y[tmp - int(t/2):tmp + int(t/2)] - 1.1 * deta * d2
            for i in range(t):
                spectrum_y[tmp - int(t/2) + i] = sum(spectrum_y[tmp - int(t/2) + i - 32:tmp - int(t/2) + i + 32]) / 64

        index = tmp + 6146

    super_threshold_indices = spectrum_y < -112
    spectrum_y[super_threshold_indices] = -112
    y_smooth = smooth(spectrum_y, 5)
    return y_smooth
    
def smoothMain(x, y):
    dirPath = os.path.dirname(__file__)
    print dirPath
    base = np.load(os.path.join(dirPath, 'base_30_86.npy'))
    base_x = base[0, :]
    base_y = base[1, :]
    npX = np.array(x)
    npY = np.array(y)
    y1_smooth = smooth_spectrum(npX, npY, base_x, base_y, dirPath)
    return y1_smooth


if __name__ == '__main__':
    pass