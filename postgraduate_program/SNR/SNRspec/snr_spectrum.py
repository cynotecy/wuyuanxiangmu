import numpy as np
from dataGet_spectrum import dataGet
import matplotlib.pyplot as plt
import math

def power(data, Fs):
	Ts = 1/Fs
	T = len(data)*Ts
	amp_v = 10**(data/20)
	power = sum(amp_v**2/T)
	return power

def snr_estimation_spectrum(data_clean, data_signal):
	pn = power(data_clean, 25e6)
	psn = power(data_signal, 25e6)
	snr = 10*math.log10((psn - pn)/pn)
	return snr

if __name__ == '__main__':
	noise = dataGet(r"test_clean.txt")
	data = dataGet(r"test_800.txt")
	snr = snr_estimation_spectrum(noise, data)
	print(snr)
