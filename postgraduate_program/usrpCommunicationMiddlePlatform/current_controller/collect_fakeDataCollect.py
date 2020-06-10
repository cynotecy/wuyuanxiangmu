# coding=utf-8
"""
@File:collect_fakeDataCollect.py
@Author:lcx
@Date:2020/1/1514:57
@Desc:
"""

import os
from time import ctime
import time
import datetime
import struct
# from future_builtins import map
import crcmod
import scipy
from PyQt4.QtCore import QThread
from threading import Thread
saveFlag = 1


class Send(Thread):
    def __init__(self, centre, bdwidth, samprate, pub_socket):
        super(Send, self).__init__()
        self.centre = centre
        self.socket = pub_socket
        self.samp_rate = samprate
        self.bdwidth = bdwidth
    def run(self):
        global saveFlag
        # print 'start collect_send at:', ctime()
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        fft_size = 2 ** 13
        HEADER = '\xAA'
        CODE = '\x05'
        freq = float(self.centre)
        # freq = 2642.5e6
        samp_rate = float(self.samp_rate)#25e6
        # samp_rate = 25e6
        gain = 20.
        num_samps_per_freq = 4096*80
        bandwidth = float(self.bdwidth)
        # bandwidth = 1.  # any value you like,
        DATA = struct.pack('!d', freq) \
               + struct.pack('!d', samp_rate) \
               + struct.pack('!d', gain) \
               + struct.pack('!l', num_samps_per_freq & 0xffffffff) \
               + struct.pack('!d', bandwidth)
        CRC16 = struct.pack('!H', crc16_ibm(CODE + DATA) & 0xffff)
        LENGTH = struct.pack('!I', (len(CODE) + len(DATA) + len(CRC16)) & 0xffffffff)
        msg = HEADER + LENGTH + CODE + DATA + CRC16
        while True:
            if saveFlag:
                self.socket.send(msg)
                print 'end scan_send at:', ctime()
                saveFlag = 0
            time.sleep(0.1)

class Recv(Thread):
    def __init__(self, sub_socket):
        super(Recv, self).__init__()
        self.socket = sub_socket
        self.savePath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'
        # self.runningFlag = 1
    def run(self):
        i = 0
        global saveFlag
        try:
            while True:
                crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
                msg = self.socket.recv()
                fileName = str(i)
                path = os.path.join(self.savePath, fileName)
                with open(path, 'wb') as f:
                    f.write(msg)
                i += 1
                saveFlag = 1
                print 'recved'
        except KeyboardInterrupt:
            pass
        print 'end collect_recv at:', ctime()

if __name__ == '__main__':
    from socketTest import socketInit

    pubAddress = 'tcp://192.168.0.100:7777'
    subAddress = 'tcp://192.168.0.5:9999'
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    subSocket = socketInit.connect(subAddress, 'SUB')

    time.sleep(5)
    centre = '940.6e6'
    bdwidth = '3e6'
    samprate = '12.5e6'
    scanRecv = Recv(subSocket)
    scanSend = Send(centre, bdwidth, samprate, pubSocket)
    scanRecv.start()
    scanSend.start()