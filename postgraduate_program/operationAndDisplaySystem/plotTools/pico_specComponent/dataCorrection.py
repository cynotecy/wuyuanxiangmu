import math
import numpy as np


def single_correct(x, y):
    p1 = 6.52e-06
    p2 = 4.66e-05
    p3 = -0.01069
    p4 = 0.02853
    p5 = 4.96
    s = p1*math.pow(x, 4) + p2*math.pow(x, 3) + p3*math.pow(x, 2) + p4*x + p5
    y_correct = y + s
    # y_correct = np.asarray(y_correct)
    # x = list(x)
    return y_correct

def correct(x, y):
    y_correct = []
    for i in range(x.shape[0]):
        y_correct.append(single_correct(x[i], y[i]))
    # y_correct = np.asarray(y_correct)
    x = list(x)
    return x, y_correct


if __name__ == '__main__':
    x = np.arange(0.5, 30, 0.5)

    # 20dbm测试数据
    y_20 = [-24.76, -24.83, -25.47, -25.42, -24.91, -24.58, -24.49, -24.58, -24.88, \
         -25.37, -25.25, -24.76, -24.47, -24.35, -24.4, -24.65, -25.07, -24.86, \
         -24.38, -24.03, -23.78, -23.83, -24.08, -24.47, -24.18, -23.7, -23.41, \
         -23.25, -23.3, -23.54, -23.95, -23.62, -23.1, -22.8, -22.71, -22.77, \
         -23.01, -23.43, -23.05, -22.57, -22.29, -22.21, -22.3, -22.59, -23.06, \
         -22.64, -22.22, -21.99, -21.95, -22.1, -22.42, -22.95, -22.52, -22.15, \
         -21.97, -21.99, -22.19, -22.59, -23.15, -22.72]
    y_20 = np.array(y_20)

    # 10dbm测试数据
    y_10 = [-14.85, -15.08, -15.57, -15.51, -15.04, -14.74, -14.66, -14.75, -14.98, \
            -15.4, -15.27, -14.79, -14.5, -14.38, -14.44, -14.68, -15.09, -14.9, \
            -14.39, -14.08, -13.89, -13.95, -14.17, -14.58, -14.3, -13.8, -13.47, \
            -13.34, -13.38, -13.62, -14.03, -13.67, -13.18, -12.87, -12.74, -12.8, \
            -13.05, -13.48, -13.08, -12.6, -12.34, -12.25, -12.36, -12.67, -13.13, \
            -12.71, -12.31, -12.08, -12.05, -12.2, -12.53, -13.07, -12.65, -12.28, \
            -12.12, -12.14, -12.36, -12.76, -13.32, -12.9]

    for i in range(x.shape[0]):
        y_correct = correct(x[i], y_10[i])
        print(y_correct)