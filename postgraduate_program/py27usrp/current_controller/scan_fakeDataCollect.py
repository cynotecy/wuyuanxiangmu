# coding=utf-8
from PyQt4.QtCore import QThread
from time import ctime
import struct
import crcmod
import os
import time
import threading
from functions.spectrum_smooth import spectrum_smooth_v4

saveFlag = 1
class Send(threading.Thread):
    def __init__(self, starts, end, pub_socket):
        super(Send, self).__init__()
        self.starts = starts
        self.end = end
        self.socket = pub_socket
        self.pointnum = 10000000
    def run(self):
        global saveFlag
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
        num_scan = 1
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
        # print len(msg)
        while True:
            if saveFlag:
                self.socket.send(msg)
                print 'end scan_send at:', ctime()
                saveFlag = 0
            time.sleep(0.1)


class Recv(threading.Thread):
    def __init__(self, sub_socket, standard='-11'):
        super(Recv, self).__init__()
        self.socket = sub_socket
        self.standard = float(standard)
        self.savePath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-1000'
        self.runningFlag = 1

    def stop(self):
        self.runningFlag = 0

    def run(self):
        global saveFlag
        print 'start scan_recv at:', ctime()
        try:
            i = 0
            while self.runningFlag:
                crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
                print 'before socket.recv'
                msg = self.socket.recv()
                fileName = str(i)
                path = os.path.join(self.savePath, fileName)
                with open(path, 'wb') as f:
                    f.write(msg)
                i += 1
                print 'recved'
                # print msg
                saveFlag = 1
        except KeyboardInterrupt:
            pass
        print 'end scan_recv at:', ctime()

if __name__ == '__main__':
    from socketTest import socketInit
    pubAddress = 'tcp://192.168.0.100:7777'
    subAddress = 'tcp://192.168.0.5:9999'
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    subSocket = socketInit.connect(subAddress, 'SUB')

    time.sleep(5)
    startFreq = '900e6'
    endFreq = '1000e6'
    scanRecv = Recv(subSocket)
    scanSend = Send(startFreq, endFreq, pubSocket)
    scanRecv.start()
    scanSend.start()
