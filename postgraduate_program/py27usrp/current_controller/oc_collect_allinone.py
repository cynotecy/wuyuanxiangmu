# coding=utf-8
from time import ctime
import struct
import crcmod
import scipy
from PyQt4.QtCore import QThread
import thread
import zmq
import time
import numpy as np
import Queue
recvFlag = 1
class Send(object):
    def __init__(self, centre, samprate, bdwidth, pub_socket):
        super(Send, self).__init__()
        self.centreList = centre
        self.socket = pub_socket
        self.samp_rate = samprate
        self.bdwidthList = bdwidth
        self.length = len(centre)
    def run(self):
        print 'start collect_send at:', ctime()
        global recvFlag
        for ii in range(self.length):
            self.centre = self.centreList[ii]
            self.bdwidth = self.bdwidthList[ii]
            crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
            fft_size = 2 ** 13
            HEADER = '\xAA'
            CODE = '\x05'
            freq = float(self.centre)
            # freq = 2642.5e6
            samp_rate = float(self.samp_rate)  # 25e6
            gain = 20.
            num_samps_per_freq = 4096 * 25
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
                if recvFlag:
                    self.socket.send(msg)
                    recvFlag = 0
                    print 'end collect_send at:', ctime()
                    break


class Recv(QThread):
    def __init__(self, sub_socket):
        super(Recv, self).__init__()
        # self.q = q
        self.socket = sub_socket
    def run(self):
        try:
            global recvFlag
            while True:
                crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
                print 'start recv'
                msg = self.socket.recv()
                print 'finish recv'
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
                if (CODE != '\x08'):
                    print 'Do not handle the msg with code %s! Ignore this msg' % (CODE,)
                    continue
                if crc16_ibm(msg[5:-2]) != CRC16:
                    print 'CRC check fail!'
                    continue
                if len(DATA) < 36:
                    print "warning: the length of msg is less than 36! Ignore this msg"
                    continue
                num_samp = struct.unpack('!l', DATA[24:28])[0]
                if len(DATA) != num_samp * 8 + 36:
                    print "warning1: the length of msg is not equal to LENGTH! Ignore this msg"
                    continue
                print 'writing a iq msg'

                freq = struct.unpack("!d", DATA[0:8])[0]
                samp_rate = struct.unpack('!d', DATA[8:16])[0]
                gain = struct.unpack('!d', DATA[16:24])[0]
                bandwidth = struct.unpack('!d', DATA[28:36])[0]
                real_part = struct.unpack('!%s' % ('f' * num_samp,), DATA[36:36 + num_samp * 4])
                imag_part = struct.unpack('!%s' % ('f' * num_samp,), DATA[36 + num_samp * 4:36 + num_samp * 8])
                # self.q.put("recvd")

                local_time1 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                self.path = r'D:\postgraduate_program\usrp_recvfiles\auto_recognize\oc_%s.dat' % (local_time1)
                f = open(self.path, 'w+')
                f.write(str(freq) + ' '+ str(bandwidth) + ' ' + str(samp_rate)+' ' )
                for i in range(len(real_part)):
                    f.write(str(real_part[i]) + ' ')
                f.write('\n')
                f.close()
                print len(real_part)
                print 'write worked'
                recvFlag = 1
        except KeyboardInterrupt:
            pass
        print 'end collect_recv at:', ctime()

if __name__ == '__main__':

    path_input_filename = r"D:\postgraduate_program\usrp_recvfiles\oc_selected_rows\rowNumList.txt"  # 输入文件路径
    file_object = open(path_input_filename, 'r')
    try:
        for line in file_object:
            line_ = line.replace("\n", "")
            filelist = line_.split(" ")[0:-1]
    finally:
        file_object.close()
    time.sleep(2)
    # pub_address = 'tcp://192.168.0.100:7777'
    pub_address = 'tcp://192.168.0.100:6666'
    # self.pub_address = 'tcp://127.0.0.1:6666'

    # sub_address = 'tcp://192.168.0.5:9999'
    sub_address = 'tcp://192.168.0.5:5555'
    # sub_address = 'tcp://127.0.0.1:5555'

    # rep_address = 'tcp://192.168.0.100:7778'
    rep_address = 'tcp://192.168.0.100:6667'
    # self.rep_address = 'tcp://127.0.0.1:6667'

    pub_context = zmq.Context()
    pub_socket = pub_context.socket(zmq.PUB)
    pub_socket.bind(pub_address)

    rep_socket = pub_context.socket(zmq.REQ)
    rep_socket.bind(rep_address)

    sub_context = zmq.Context()
    sub_socket = sub_context.socket(zmq.SUB)
    sub_socket.connect(sub_address)
    sub_socket.setsockopt(zmq.SUBSCRIBE, '')
    # time.sleep(25)
    # q = Queue.Queue()

    recv = ''
    while 1:
        rep_socket.send('hello client')
        recv = rep_socket.recv()
        if recv == 'hello server':
            # 同步完成
            rep_socket.close()
            break
        else:
            # self.rep_socket.send('nothing')
            time.sleep(1)

    b = np.loadtxt("D:\postgraduate_program\usrp_recvfiles\oc_selected_rows\collectList.txt", dtype=np.float32)
    print "维度：", b.ndim
    centreList = []
    bdwidthList = []
    if b.ndim == 1:
        b = np.expand_dims(b, axis=0)# 单条数据时扩展维度
    for i in range(len(b)):
        centre_ = b[i][0]*1e6
        bdwidth_ = b[i][1]
        centreList.append(centre_)
        bdwidthList.append(bdwidth_)

    collect_recv = Recv(sub_socket)
    collect_send = Send(centreList, 25e6, bdwidthList, pub_socket)
    collect_recv.start()
    collect_send.run()
    time.sleep(5)
    if recvFlag:
        pub_socket.close()
        sub_socket.close()