# coding=utf-8
"""
@File:antennaChangeThread.py
@Author:lcx
@Date:2020/9/1520:46
@Desc:
"""
from PyQt4.QtCore import QThread
from time import ctime
import time
import struct
import crcmod

class AntennaChangeSend(QThread):
    def __init__(self, starts, end, pub_socket):
        super(AntennaChangeSend, self).__init__()
        self.starts = starts
        self.end = end
        self.pointnum = 10000000
        self.socket = pub_socket
    def run(self):
        print 'start scan_send at:', ctime()
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        # fft_size = 2 ** 13
        HEADER = '\xAA'
        CODE = '\x01'
        start_freq = float(self.starts)
        stop_freq = float(self.end)
        # start_freq = 100e6
        # stop_freq = 800e6
        samp_rate = 25e6
        freq_step = samp_rate * 6 / 8
        gain = 20.0
        num_scan = 1#扫频次数
        n_fft = 100
        num_samps_per_freq = int(self.pointnum)
        # num_samps_per_freq = fft_size * (n_fft + 1)
        # print num_samps_per_freq
        bandwidth = freq_step / samp_rate
        num_samps_per_signal = 8192
        DATA = struct.pack('!5d3ldl', start_freq, stop_freq, freq_step, samp_rate, gain, num_scan & 0xffffffff,
                           num_samps_per_freq & 0xffffffff, n_fft & 0xffffffff, bandwidth,
                           num_samps_per_signal & 0xffffffff)
        CRC16 = struct.pack('!H', crc16_ibm(CODE + DATA) & 0xffff)
        LENGTH = struct.pack('!I', (len(CODE) + len(DATA) + len(CRC16)) & 0xffffffff)
        msg = HEADER + LENGTH + CODE + DATA + CRC16

        #############切换天线至RF1#########################
        antenna_CODE = '\x07'
        antenna_DATA = struct.pack('!B', 1)  # 0 -> RX2 (RF2); 1 -> TX/RX (RF1)
        antenna_CRC16 = struct.pack('!H', crc16_ibm(antenna_CODE + antenna_DATA) & 0xffff)
        antenna_LENGTH = struct.pack('!I', (len(antenna_CODE) + len(antenna_DATA) + len(antenna_CRC16)) & 0xffffffff)
        antenna_msg = HEADER + antenna_LENGTH + antenna_CODE + antenna_DATA + antenna_CRC16
        self.socket.send(antenna_msg)
        print "天线切换至RF1"
        print 'end antenna_exchange at:', ctime()

        #############切换天线至RF2#########################
        antenna_CODE = '\x07'
        antenna_DATA = struct.pack('!B', 0)  # 0 -> RX2 (RF2); 1 -> TX/RX (RF1)
        antenna_CRC16 = struct.pack('!H', crc16_ibm(antenna_CODE + antenna_DATA) & 0xffff)
        antenna_LENGTH = struct.pack('!I', (len(antenna_CODE) + len(antenna_DATA) + len(antenna_CRC16)) & 0xffffffff)
        antenna_msg = HEADER + antenna_LENGTH + antenna_CODE + antenna_DATA + antenna_CRC16
        self.socket.send(antenna_msg)
        print "天线切换至RF2"
        print 'end antenna_exchange at:', ctime()