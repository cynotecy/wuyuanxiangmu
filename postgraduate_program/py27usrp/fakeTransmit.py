# -*- coding: UTF-8 -*-
"""
@File:fakeTransmit.py
@Author:lcx
@Date:2020/1/1511:10
@Desc:虚拟远端中转，伪装工程机接收消息，回传扫频或采集数据
"""
import zmq
import random
import struct
import matplotlib.pyplot as plt
import crcmod
from functions.spectrum_smooth import spectrum_smooth_v4
from socketTest import socketInit
import os
from threading import Thread


def scanTransmit1():
    subAddress = 'tcp://127.0.0.1:6666'
    pubAddress = 'tcp://127.0.0.1:5555'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    dirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    files = os.listdir(dirPath)  # 得到文件夹下的所有文件名称
    dataList = []
    for file in files:  # 遍历文件夹
        if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
            with open(dirPath + "/" + file, 'rb') as f:  # 打开文件
                content = f.read()
                dataList.append(content)  # 每个文件的文本存到list中
    while True:
        print '转发线程准备就绪'
        msg = subSocket.recv()
        i = int(random.randint(0,15))
        print i
        pubSocket.send(bytes(dataList[i]))

def scanTransmit2():
    subAddress = 'tcp://127.0.0.1:7777'
    pubAddress = 'tcp://127.0.0.1:9999'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    dirPath = r'D:\myPrograms\CASTProgram\fakeData\scan\900-950'
    files = os.listdir(dirPath)  # 得到文件夹下的所有文件名称
    dataList = []
    for file in files:  # 遍历文件夹
        if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
            with open(dirPath + "/" + file, 'rb') as f:  # 打开文件
                content = f.read()
                dataList.append(content)  # 每个文件的文本存到list中
    while True:
        print '转发线程准备就绪'
        msg = subSocket.recv()
        i = int(random.randint(0,15))
        print i
        pubSocket.send(bytes(dataList[i]))

def collectTransmit():
    # subAddress = 'tcp://192.168.0.100:7777'
    # pubAddress = 'tcp://192.168.0.5:9999'
    subAddress = 'tcp://127.0.0.1:7777'
    pubAddress = 'tcp://127.0.0.1:9999'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')
    dirPath = r'D:\myPrograms\CASTProgram\fakeData\collect\940d6_3bd'
    files = os.listdir(dirPath)  # 得到文件夹下的所有文件名称
    dataList = []
    for file in files:  # 遍历文件夹
        if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
            with open(dirPath + "/" + file, 'rb') as f:  # 打开文件
                content = f.read()
                dataList.append(content)  # 每个文件的文本存到list中
    while True:
        print '转发线程准备就绪'
        msg = subSocket.recv()
        i = int(random.randint(0,15))
        print i
        pubSocket.send(bytes(dataList[i]))

def scanTest():
    standard = -11
    subAddress = 'tcp://127.0.0.1:9999'
    pubAddress = 'tcp://127.0.0.1:7777'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')

    msgSend = '1'
    time.sleep(2)
    while 1:
        pubSocket.send(msgSend)
        print '接收线程已发送接受请求'
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        msg = subSocket.recv()
        if len(msg) < 6:
            print 'warning: length of msg is less than 6! Ignore this msg'
            # continue
            break
        LENGTH = struct.unpack('!I', msg[1:5])[0]
        if LENGTH != (len(msg) - 5):
            print "warning0: the length of msg is not equal to LENGTH! Ignore this msg"
            # continue
            break
        HEADER = msg[0]
        CODE = msg[5:6]
        DATA = msg[6:-2]
        CRC16 = struct.unpack('!H', msg[-2:])[0]
        if (HEADER != '\xBB'):
            print 'Do not handle the msg begin with %s! Ignore this msg' % (HEADER,)
            # continue
            break
        if (CODE != '\x06'):
            print 'Do not handle the msg with code %s! Ignore this msg' % (CODE,)
            # continue
            break
        if crc16_ibm(msg[5:-2]) != CRC16:
            print 'CRC check fail!'
            # continue
            break
        if len(DATA) < 12:
            print "warning1: the length of msg is less than 12! Ignore this msg"
            # continue
            break
        freq_resolution = struct.unpack('!d', DATA[0:8])[0]
        n_freq = struct.unpack('!I', DATA[8:12])[0]
        if len(DATA) != n_freq * (4 + 8) + 12:
            print "warning1: the length of msg is not equal to LENGTH! Ignore this msg"
            # continue
            break

        print 'receiving a spectrum msg!'
        bins = struct.unpack('!%s' % ('f' * n_freq,), DATA[12:12 + n_freq * 4])
        freq_list = struct.unpack('!%s' % ('d' * n_freq,), DATA[12 + n_freq * 4:12 + n_freq * (4 + 8)])
        # Do what you want to do, here is a example.
        # 去毛刺
        bins = spectrum_smooth_v4.smoothMain(freq_list, bins)
        bins = list(bins)
        bins = [c + standard for c in bins]  # 定标
        freq_list = list(freq_list)
        plt.plot(freq_list, bins)
        plt.show()
        # break
        
def collectTest():
    # subAddress = 'tcp://192.168.0.5:9999'
    # pubAddress = 'tcp://192.168.0.100:7777'
    subAddress = 'tcp://127.0.0.1:9999'
    pubAddress = 'tcp://127.0.0.1:7777'
    subSocket = socketInit.connect(subAddress, 'SUB')
    pubSocket = socketInit.connect(pubAddress, 'PUB')

    msgSend = '1'
    time.sleep(2)
    while 1:
        pubSocket.send(msgSend)
        print '接收线程已发送接受请求'
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        msg = subSocket.recv()
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
        # q.put(fft_bin)
        # q.put(freq_list)
        # collectInfo = str(freq) + ' '+ str(bandwidth) + ' ' + str(samp_rate)+' '
        # real_part_strlist = map(str, list(real_part))
        # realPartStr = " ".join(real_part_strlist)
        # reslt = collectInfo + realPartStr
        plt.plot(real_part)
        plt.show()

if __name__ == '__main__':
    import time
    t1 = Thread(target=scanTransmit2)
    # t2 = Thread(target=scanTest)
    # t1 = Thread(target=collectTransmit)
    # t2 = Thread(target=collectTest)
    t1.start()
    # t2.start()
    t3 = Thread(target=scanTransmit1)
    t3.start()

    t1.join()
    t3.join()

