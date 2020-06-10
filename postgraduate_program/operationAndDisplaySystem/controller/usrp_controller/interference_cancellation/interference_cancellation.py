import copy
import numpy as np
import matplotlib.pylab as plt
# from spectrum_v3 import smooth_spectrum_v3

def estimation_bandwith(spectrum):
    center_freq = int(np.argmax(spectrum))
    end = len(spectrum) - 1
    for i in range(center_freq, len(spectrum)):
        if spectrum[i] < 0.1:
            end = i
            break
    start = 0
    i = center_freq
    while i > 0:
        if spectrum[i] < 0.1:
            start = i
            break
        i -= 1
    if center_freq - start > end - center_freq:
        end = 2*center_freq - start if center_freq + (center_freq - start) < len(spectrum)-1 else len(spectrum)-1
    else:
        start = 2*center_freq - end if center_freq - (end - center_freq) > 0 else 0
    return center_freq, start, end

def interference_eliminate(x1, y1, x2, y2):
    """
    
    Args:
        x1: 正对
        y1: 正对
        x2: 背对
        y2: 背对

    Returns:

    """
    target_x = x1
    if len(y1) > len(y2):
        target_x = np.linspace(0, x2[-1], len(x1))
        y2 = np.interp(target_x, x2, y2)
    if len(y2) > len(y1):
        target_x = np.linspace(0, x1[-1], len(x2))
        y1 = np.interp(target_x, x1, y1)
    if max(y1-y2) > max(y2-y1):
        face_spectrum = y1
        back_spectrum = y2
    else:
        face_spectrum = y2
        back_spectrum = y1
    target_y = face_spectrum - back_spectrum
    freq, start, end = estimation_bandwith(target_y)
    power = ((face_spectrum[freq] - face_spectrum[start]) + (face_spectrum[freq] - face_spectrum[end])) / 2
    factor = power / target_y[freq]
    target_y[start:end] = factor * target_y[start:end]
    target_y = target_y - 110
    super_threshold_indices = target_y < -112
    target_y[super_threshold_indices] = -112
    return target_x, target_y



if __name__ == '__main__':
    txt = np.loadtxt(r"E:\chenzhiyun\usrp_test\interference_cancellation\0109\spectrum_950_1050_4.txt", dtype=str, delimiter=' ')
    txt = txt[:, :-1].astype(np.float32)
    x1_background = txt[8, :]
    y1_background = smooth_spectrum_v3(x1_background, copy.deepcopy(txt[9, :]))
    x1_signal = txt[0, :]
    y1_signal = smooth_spectrum_v3(x1_signal, copy.deepcopy(txt[1, :]))
    x2_background = txt[10, :]
    y2_background = smooth_spectrum_v3(x2_background, copy.deepcopy(txt[11, :]))
    x2_signal = txt[4, :]
    y2_signal = smooth_spectrum_v3(x2_signal, copy.deepcopy(txt[5, :]))
    target_x, target_y = interference_eliminate(x1_signal, y1_signal, x2_signal, y2_signal)
    plt.figure()
    plt.subplot(221)
    plt.tight_layout()
    plt.title('Before processing background')
    plt.plot(x1_background, txt[1, :])
    plt.ylim(ymin=-120, ymax=-30)
    plt.subplot(223)
    plt.title('After processing background')
    plt.plot(x1_background, y1_background)
    plt.ylim(ymin=-120, ymax=-30)
    plt.subplot(222)
    plt.title('Face to antenna spectrum')
    plt.plot(x1_signal, y1_signal)
    plt.ylim(ymin=-120, ymax=-30)
    plt.subplot(224)
    plt.title('Face to antenna minus background')
    plt.plot(x1_signal, y1_signal - y1_background - 110)
    plt.ylim(ymin=-120, ymax=-30)
    plt.figure()
    plt.subplot(411)
    plt.tight_layout()
    plt.title('RF1 face to antenna')
    plt.plot(x1_signal, y1_signal)
    plt.ylim(ymin=-120, ymax=-40)
    plt.subplot(412)
    plt.title('RF2 back to antenna')
    plt.plot(x2_signal, y2_signal)
    plt.ylim(ymin=-120, ymax=-40)
    plt.subplot(413)
    plt.title('RF1 minus RF2')
    plt.plot(x1_signal, y1_signal-y2_signal-110)
    plt.ylim(ymin=-120, ymax=-40)
    plt.subplot(414)
    plt.title('Eliminate result')
    plt.plot(target_x, target_y)
    plt.ylim(ymin=-120, ymax=-40)
    plt.show()
