import numpy as np
from SNR.component.dataGet_spectrum import dataGet
import matplotlib.pyplot as plt
import math

def power(data, Fs):
	Ts = 1/Fs
	T = len(data)*Ts
	amp_v = 10**(data/20)
	power = sum(amp_v**2/T)
	return power

# def snr_estimation_spectrum(data_clean, data_signal):
# 	pn = power(data_clean, 25e6)
# 	psn = power(data_signal, 25e6)
# 	snr = 10*math.log10((psn - pn)/pn)
# 	return snr
def snr_estimation_spectrum(data_clean, data_signal):
	pn = power(data_clean, 25e6)
	psn = power(data_signal, 25e6)
	if (psn <= pn):
		return '第一次采集的信号能量大于第二次采集的信号能量，请检查操作是否正确！'
	snr = 10*math.log10((psn - pn)/pn)
	return snr

if __name__ == '__main__':
	noise = dataGet(r"D:\myPrograms\CASTProgram\postgraduate_program\data\SNR_data\SNRSpecPro_20200927162748.txt")
	data = dataGet(r"D:\myPrograms\CASTProgram\postgraduate_program\data\SNR_data\SNRSpecCurrent_20200927162751.txt")
	snr = snr_estimation_spectrum(noise, data)
	print(snr)
