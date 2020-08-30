import matplotlib.pyplot as plt

import numpy as np
import sys
import math
import matplotlib.pyplot as plt
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

def normalization(data, axis = 0):
    m = np.mean(data, axis=axis)
    s = np.std(data, axis=axis)
    data = (data - m) / s
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


def ave_and_slope(sig, step1, step2):#对一条数据取抽样值和斜率，step1滑动平均的步长，step2是计算斜率的步长


    ave_sig1 = movingaverage(sig, step1)
    ave_sig2 = movingaverage(ave_sig1, step1)
    s = slice(0, len(ave_sig2), 10)#滑动平均完做抽样处理
    ave_sig3 = ave_sig2[s]#抽样结果
    list1 = ave_sig3
    x_lable1 = np.arange(0, 5000, 0.05)
    #slope_once = cacu_slope(ave_sig2, x_lable1, step2)
    #slope_twice = cacu_slope(slope_once, x_lable1, step2)

    return list1

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

def classify(xinhao_name, online_sig, normal_data, bound): #
    ll = len(normal_data[0])
    list_above = []
    list_possible = []
    index_for_above = []

    rate_for_f = []  # 基于frenchet距离的相似度

    for j in range(0,len(normal_data)):
        '''
        plt.figure()
        plt.plot(online_sig,'g',normal_data[j], 'r')
        plt.show()
        '''
        c, c1, flag = lcs(online_sig, normal_data[j], bound)
        sil = c1 / ll
        list_possible.append(sil)
        if sil >= 0.6:
                list_above.append(sil)
                index_for_above.append(j)#存贮相似度对应的信号编码

    if len(list_above): #如果frencht判断出相似度高，继续用lcs找出最相似的样本
        for j in index_for_above:
            mid_list = normal_data[j].tolist()
            max_point = max(mid_list)
            min_point = min(mid_list)
            h_point = (max_point - min_point)
            f_dis = frechet_distance(online_sig, normal_data[j])
            rate = 1 - f_dis / h_point  #相似度计算
            rate_for_f.append(rate)
        add_two = [a/2 + b/2 for a, b in zip(list_above, rate_for_f)]
        a = max(add_two)
        location = add_two.index(a)
        num_for_yangben = index_for_above[location]#最相似的模板的编号
        # print('基于LCS的相似度大于0.6：', list_above)
        # print('对应的模板坐标：', index_for_above)
        # print('备选项中基于frenchet的相似度：', rate_for_f)
        # print('总的相似度', add_two)
        # print('基于LCS对所有模板的相似度：', list_possible)
        # print('最相似的模板编号：', num_for_yangben)
        return 1, a ,num_for_yangben
    else:
        #a = ave(list_possible)
        return 0,list_possible, 'NaN'


def lcs(a, b, bound):
    lena = len(a)
    lenb = len(b)
    c = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
    flag = [[0 for i in range(lenb + 1)] for j in range(lena + 1)]
    for i in range(0,lena):
        for j in range(0,lenb):
            if abs(a[i] - b[j]) <= bound:

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

def euc_dist(pt1, pt2):

    #return math.sqrt((pt2[0]-pt1[0])*(pt2[0]-pt1[0])+(pt2[1]-pt1[1])*(pt2[1]-pt1[1]))
    return math.sqrt((pt2-pt1)*(pt2-pt1))

def dis(ca,x1,y1,P,Q):
    for i in range(x1):
        for j in range(y1):
            if ca[i, j] > -1:
                return ca[i, j]
            elif i == 0 and j == 0:
                ca[i, j] = euc_dist(P[0], Q[0])
            elif i > 0 and j == 0:
                ca[i, j] = max(ca[i-1,0], euc_dist(P[i], Q[0]))
            elif i == 0 and j > 0:
                ca[i, j] = max(ca[0,j-1], euc_dist(P[0], Q[j]))
            elif i > 0 and j > 0:
                A = ca[i-1,j]
                B = ca[i-1,j-1]
                C = ca[i,j-1]
                ca[i, j] = max(min(A, B, C), euc_dist(P[i], Q[j]))
            else:
                ca[i, j] = float("inf")
    return ca[i,j]


def frechet_distance(P,Q):
    ca = np.ones((len(P),len(Q)))
    ca = np.multiply(ca,-1)
    return dis(ca, len(P) - 1, len(Q) - 1, P, Q)