import math
import numpy as np

# 这段不是完整的校正算法，只是校正算法核心，真正使用时应置入dataCorrection

def pico_spectrum(x, y):
    a1 = 9.323
    b1 = 0.0575
    c1 = 0.4565
    a2 = 5.342
    b2 = 0.08039
    c2 = 3.073
    a3 = 0.4048
    b3 = 0.1531
    c3 = 7.497
    a4 = 0.4523
    b4 = 5.312
    c4 = -1.506
    s = a1 * math.sin(b1 * x + c1) + a2 * math.sin(b2 * x + c2) + a3 * math.sin(b3 * x + c3) + a4 * math.sin(b4 * x + c4)
    y_correct = y + s
    return y_correct


if __name__ == '__main__':
    x = np.arange(0.5, 30, 0.5)

    # 20dbm测试数据
    y_20 = [-25.43,-24.59,-24.97,-25.05,-24.65,-25.48,-24.54,-25.18,-24.73,-24.83,-25.04,-24.56,\
    -25.58,-24.51,-24.98,-24.66,-24.55,-25,-24.31,-25.19,-24.15,-24.46,-24.33,-24.05,\
    -24.7,-23.86,-24.59,-23.88,-24.03,-24.09,-23.68,-24.53,-23.54,-24.14,-23.61,-23.63,\
    -23.9,-23.34,-24.34,-23.27,-23.74,-23.43,-23.32,-23.83,-23.14,-24.04,-23.18,-23.51,\
    -23.43,-23.2,-23.91,-23.11,-23.88,-23.25,-23.45,-23.6,-23.24,-24.2,-23.26,-23.91,-23.49,-23.57]

    # 10dbm测试数据
    y_10 = [-15.52,-14.8,-15.06,-15.13,-14.75,-15.58,-14.67,-15.32,-14.79,-14.82,-15.09,-14.56,\
    -15.56,-14.5,-14.96,-14.64,-14.52,-14.99,-14.29,-15.16,-14.2,-14.5,-14.37,-14.09,\
    -14.74,-13.89,-14.62,-13.9,-14.05,-14.1,-13.69,-14.55,-13.54,-14.12,-13.61,-13.62,\
    -13.89,-13.33,-14.32,-13.26,-13.71,-13.44,-13.34,-13.85,-13.17,-14.06,-13.22,-13.55,\
    -13.5,-13.26,-14,-13.19,-13.97,-13.35,-13.55,-13.72,-13.36,-14.34,-13.39,-14.05,-13.64,-13.7]

    for i in range(x.shape[0]):
        y_correct = pico_spectrum(x[i], y_20[i])
        print(y_correct)