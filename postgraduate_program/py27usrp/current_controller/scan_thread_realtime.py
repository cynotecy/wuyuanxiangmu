# coding=utf-8
from PyQt4.QtCore import QThread
from time import ctime
import time
import struct
import crcmod
flag = 1
class Send(QThread):
    def __init__(self, starts, end, pointnum, pub_socket):
        super(Send, self).__init__()
        self.starts = starts
        self.end = end
        self.pointnum = pointnum
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
        num_scan = 10#扫频次数
        n_fft = 1
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
        global flag
        # a = 0
        # while a < 3:
        #     self.socket.send(msg)
        #     print 'send at:', ctime()
        #     a += 1
        #     time.sleep(7)
        while True:
            time.sleep(1)
            if flag == 1:
                self.socket.send(msg)
                flag = 0
                print 'end scan_send at:', ctime()

class Recv(QThread):
    def __init__(self, q, sub_socket):
    # def __init__(self, sub_socket):
        super(Recv, self).__init__()
        self.socket = sub_socket
        self.q = q
        self.localtime = time.strftime("%Y%m%d%H%M%S", time.localtime( time.time() ))
    def run(self):
        print 'start scan_recv at:', ctime()
        # try:
        num = 1
        global flag
        while True:
            # 接收10次
            for time in range(10):
                crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
                # print 'before socket.recv'
                msg = self.socket.recv()
                print 'receive at:', ctime()
                if len(msg) < 6:
                    print 'warning: length of msg is less than 6! Ignore this msg'
                    continue
                LENGTH = struct.unpack('!I', msg[1:5])[0]
                if LENGTH != (len(msg) - 5):
                    print "warning0: the length of msg is not equal to LENGTH! Ignore this msg"
                    continue
                HEADER = msg[0]
                CODE = msg[5:6]
                DATA = msg[6:-2]
                CRC16 = struct.unpack('!H', msg[-2:])[0]
                if (HEADER != '\xBB'):
                    print 'Do not handle the msg begin with %s! Ignore this msg' % (HEADER,)
                    continue
                if (CODE != '\x06'):
                    print 'Do not handle the msg with code %s! Ignore this msg' % (CODE,)
                    continue
                if crc16_ibm(msg[5:-2]) != CRC16:
                    print 'CRC check fail!'
                    continue
                if len(DATA) < 12:
                    print "warning1: the length of msg is less than 12! Ignore this msg"
                    continue
                freq_resolution = struct.unpack('!d', DATA[0:8])[0]
                n_freq = struct.unpack('!I', DATA[8:12])[0]
                if len(DATA) != n_freq * (4 + 8) + 12:
                    print "warning1: the length of msg is not equal to LENGTH! Ignore this msg"
                    continue

                # print 'receiving a spectrum msg!'
                bins = struct.unpack('!%s' % ('f' * n_freq,), DATA[12:12 + n_freq * 4])
                freq_list = struct.unpack('!%s' % ('d' * n_freq,), DATA[12 + n_freq * 4:12 + n_freq * (4 + 8)])
                # Do what you want to do, here is a example.
                bins = [c - 7 for c in bins]
                f = open(r'D:\postgraduate_program\realtime_recv\%s.txt' % num, 'a+')
                for i in range(len(freq_list)):
                    f.write(str(freq_list[i]) + ' ')
                f.write('\n')
                for i in range(len(bins)):
                    f.write(str(bins[i]) + ' ')
                f.write('\n')
                f.close()
                print 'finish writing at:', ctime()
                print time
            num += 1
            flag = 1
        # except KeyboardInterrupt:
        #         #     pass
        # print 'end scan_recv at:', ctime()

