# -*- coding: UTF-8 -*-
import sys
import time
import os

import Queue
import thread
import zmq

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from current_controller import scan_thread, collect_thread
from socketTest import socket
from functions import filesOrDirsOperate
"""
加个远程连接检测
"""

def threadControl():
    localQueue = Queue.Queue()
    remoteQueue = Queue.Queue()
    pubAddress1 = 'tcp://192.168.0.100:6666'
    pubAddress2 = 'tcp://192.168.0.100:7777'
    pubAddress3 = 'tcp://127.0.0.1:6666'

    subAddress1 = 'tcp://192.168.0.5:5555'
    subAddress2 = 'tcp://192.168.0.5:9999'
    subAddress3 = 'tcp://127.0.0.1:5555'
    
    repAddress = 'tcp://127.0.0.1:6667'
    # 定义连接字典
    socketDic = dict()

    try:
        pubSocket1 = socket.connect(pubAddress1, 'PUB')
        subSocket1 = socket.connect(subAddress1, 'SUB')
        socketDic[0] = [pubSocket1, subSocket1]
        print "socket1 连接"
    except:
        pass

    try:
        pubSocket2 = socket.connect(pubAddress2, 'PUB')
        subSocket2 = socket.connect(subAddress2, 'SUB')
        socketDic[1] = [pubSocket2, subSocket2]
        print "socket2 连接"
    except:
        pass

    try:
        pubSocket3 = socket.connect(pubAddress3, 'PUB')
        subSocket3 = socket.connect(subAddress3, 'SUB')
        socketDic[2] = [pubSocket3, subSocket3]
        print "socket3 连接"
    except:
        pass

    repSocket = socket.connect(repAddress, 'REP')

    while 1:
        localRecv = repSocket.recv()
        print '收到信息' + localRecv

        msg = localRecv.split(',')
        print msg
        usrpNum = int(msg[0])

        pubSock = socketDic[usrpNum - 1][0]
        subSock = socketDic[usrpNum - 1][1]
        mode = msg[1]  # scan
        action = msg[2]  # IQ
        instructionInfo = msg[3]
        instructionInfoList = instructionInfo.split(';')
        # 扫频模式
        if mode == 'scan':
            startFreq = instructionInfoList[0]
            endFreq = instructionInfoList[1]
            scanRecv = scan_thread.Recv(localQueue, subSock)
            scanSend = scan_thread.Send(startFreq, endFreq, pubSock)
            scanRecv.start()
            scanSend.run()
            while localQueue.empty():
                pass
            else:
                bins = localQueue.get()
                freqList = list(localQueue.get())
                bins = [c - 11 for c in bins]  # 定标
                # print "freqlist类型", type(freq_list)
                # print type(bins)
                # 将回传的频谱直接发给py3
                freqbinslist = [str(i) for i in freqList+bins]
                freqbins = " ".join(freqbinslist)
                repSocket.send(freqbins)
                # # 将回传的频谱保存成中间文件
                # dirPath = r'..\..\usrp_recvfiles\specfiles'
                # filesOrDirsOperate.makesureDirExist(dirPath)
                # local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                # filePath = dirPath + r'\%s.dat' % local_time
                # f = open(filePath, 'w')
                # for i in range(len(freq_list)):
                #     f.write(str(freq_list[i]) + ' ')
                # f.write('\n')
                # for i in range(len(bins)):
                #     f.write(str(bins[i]) + ' ')
                # f.close()
                # repSocket.send(os.path.abspath(filePath))
        # 采集模式
        elif mode == 'collect':
            if action == 'IQoc':
                centreFreq = float(instructionInfoList[0])
                bdWdith = float(instructionInfoList[1])
                currentPath = os.path.dirname(__file__)
                fatherPath = os.path.dirname(currentPath)
                grandPath = os.path.dirname(fatherPath)
                dirPath = os.path.join(grandPath, r'usrp_recvfiles\auto_recognize')
                filesOrDirsOperate.makesureDirExist(dirPath)
                local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                filePath = os.path.join(dirPath, r'oc_collect_{}.txt'.format(local_time))
                print "oc文件路径", filePath
                localQueue.queue.clear()
                collectRecv = collect_thread.Recv(localQueue, subSock, path=filePath)
                collectRecv.start()
                while 1:
                    if collectRecv.is_alive():
                        collectSend = collect_thread.Send(str(centreFreq), str(bdWdith), '12.5e6', pubSock)
                        collectSend.start()
                        break
                while localQueue.empty():
                    pass
                else:
                    print 'localQueue:'+localQueue.get()
                    repSocket.send(filePath)

if __name__ == '__main__':
    # print "working demo"
    threadControl()