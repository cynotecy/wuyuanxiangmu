# coding=utf-8
from time import ctime
import struct
import crcmod
import scipy
from PyQt4.QtCore import QThread


class Send(object):
    def __init__(self, centre, samprate, bdwidth, pub_socket):
        super(Send, self).__init__()
        self.centre = centre
        self.socket = pub_socket
        self.samp_rate = samprate
        self.bdwidth = bdwidth
    def run(self):
        print 'start collect_send at:', ctime()
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        fft_size = 2 ** 13
        HEADER = '\xAA'
        CODE = '\x05'
        freq = float(self.centre)
        # freq = 2642.5e6
        samp_rate = float(self.samp_rate)#25e6
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
        self.socket.send(msg)
        print 'end collect_send at:', ctime()

class Recv(QThread):
    def __init__(self, q, sub_socket,path=r'D:\postgraduate_program\usrp_recvfiles\\real3.dat'):
        super(Recv, self).__init__()
        self.q = q
        self.socket = sub_socket
        self.path = path
    def run(self):
        try:
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
                print 'receiving a iq msg'

                freq = struct.unpack("!d", DATA[0:8])[0]
                samp_rate = struct.unpack('!d', DATA[8:16])[0]
                gain = struct.unpack('!d', DATA[16:24])[0]
                bandwidth = struct.unpack('!d', DATA[28:36])[0]
                real_part = struct.unpack('!%s' % ('f' * num_samp,), DATA[36:36 + num_samp * 4])
                imag_part = struct.unpack('!%s' % ('f' * num_samp,), DATA[36 + num_samp * 4:36 + num_samp * 8])
                # Do what you want to do, here is a example.
                # iq = []
                # for x in range(num_samp):
                #     iq.append(real_part[x] + imag_part[x] * 1j)
                # fft_size = 2 ** int(scipy.log2(num_samp))
                # iq_fft = scipy.fft(iq[0:fft_size])
                # fft_bin = [0.0, ] * fft_size
                # freq_list = [0.0, ] * fft_size
                # freq_resolution = samp_rate / fft_size
                # for x in range(fft_size):
                #     fft_bin[(x + fft_size / 2) % fft_size] = 10 * scipy.log10(
                #         max((iq_fft[x].imag) ** 2 + (iq_fft[x].real) ** 2, 1e-12)) - 20 * scipy.log10(fft_size)
                #     freq_list[x] = (freq_resolution * x - samp_rate / 2 + freq) / 1e6
                # self.q.put(fft_bin)
                # self.q.put(freq_list)

                f = open(self.path, 'w+')
                f.write(str(freq) + ' '+ str(bandwidth) + ' ' + str(samp_rate)+' ' )
                for i in range(len(real_part)):
                    f.write(str(real_part[i]) + ' ')
                f.write('\n')
                f.close()
                print len(real_part)
                print 'write worked'
                self.q.put("recvd")
                flag = 1
                if flag == 1:
                    break
        except KeyboardInterrupt:
            pass
        print 'end collect_recv at:', ctime()