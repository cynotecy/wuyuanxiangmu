import numpy as np
import sys
sys.setrecursionlimit(100000)

def read_dat_hang(file_path,hang):#读取一行的数据

    data = np.loadtxt(file_path, dtype=str, delimiter=' ')[hang, 0:-1]
    data = data.astype(np.float32)
    data = np.asarray(data)
    return data

def read_dat(file_path):
    data = np.loadtxt(file_path, dtype=str, delimiter=' ')
    data = data.astype(np.float32)
    data = np.asarray(data)
    return data


def movingaverage(data,window_size):#滑动平均
    cumsum_vec = np.cumsum(np.insert(data, 0, 0))
    ma_vec = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return ma_vec

def cacu_slope(data_y,data_x,n):
    slope = []
    b = len(data_y) // n
    for i in range(0, (b-1)*n,n):
        d = data_x[i+n] - data_x[i]
        A = (data_y[i+n] - data_y[i])/d
        slope.append(A)
    return slope


def ave_and_slope(sig,step1,step2):#step1滑动平均的步长，step2是计算斜率的步长


    ave_sig1 = movingaverage(sig, step1)
    ave_sig2 = movingaverage(ave_sig1, step1)
    s = slice(0, len(ave_sig2), 10)#滑动平均完做抽样处理
    ave_sig3 = ave_sig2[s]#抽样结果
    list1 = ave_sig3
    x_lable1 = np.arange(0, 5000, 0.05)
    slope_once = cacu_slope(ave_sig2, x_lable1, step2)
    #slope_twice = cacu_slope(slope_once, x_lable1, step2)

    return list1, slope_once

def bodongxing(sig,step4):
    num=0
    l = len(sig)
    n = len(sig) // step4
    for i in range(1,n+1):
        maxx = max(sig[step4*(i-1):i*step4])
        minn = min(sig[step4*(i-1):i*step4])
        if (maxx-minn)>=10:
        #if maxx >= 10:
            num+=1
    return num

def ave(list):
    sum = 0

    for i in list:
        sum = sum + i
    ave_sig = sum / len(list)
    return ave_sig

def classify(online_sig,normal_sig):
    ll = len(normal_sig[0])
    list_above = []
    list_possible = []
    for j in range(0,len(normal_sig)):
        c, c1, flag = lcs(online_sig, normal_sig[j])
        rate = c1/ll
        print(c1)#和特征频段相似点的个数
        print(rate)#相似率
        list_possible.append(rate)
        if rate >= 0.65:
            list_above.append(rate)

    if len(list_above):
        a = ave(list_above)
        print(list_above)
        print(len(list_possible))

        return 1, a
    else:
        a = 0
        return 0, a


def lcs(a, b):
    lena = len(a)
    lenb = len(b)
    c = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
    flag = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
    for i in range(0,lena):
        for j in range(0,lenb):
            if abs(a[i] - b[j]) <= 6:

                c[i + 1][j + 1] = c[i][j] + 1

                flag[i + 1][j + 1] = 'ok'
            elif c[i + 1][j] > c[i][j + 1]:
                c[i + 1][j + 1] = c[i + 1][j]
                flag[i + 1][j + 1] = 'left'
            else:
                c[i + 1][j + 1] = c[i][j + 1]
                flag[i + 1][j + 1] = 'up'
    return c,c[lena][lenb], flag



def printLcs(flag, a, i, j, ziji):
    if i == 0 or j == 0:
        return
    if flag[i][j] == 'ok':

        printLcs(flag, a, i - 1, j - 1,ziji)
        ziji.append(a[i-1])
    elif flag[i][j] == 'left':
        printLcs(flag, a, i, j - 1,ziji)

    else:
        printLcs(flag, a, i - 1, j,ziji)

