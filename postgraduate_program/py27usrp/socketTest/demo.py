# -*- coding: UTF-8 -*-
import sys
import time
import os

import Queue
import thread
import zmq
sys.path.append("..\..\py27usrp")
from current_controller import scan_thread
from socketTest import socket
from functions import filesOrDirsOperate


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
    # try:
    # pubSocket1 = socket.connect(pubAddress1, 'PUB')
    pubSocket2 = socket.connect(pubAddress2, 'PUB')
    # pubSocket3 = socket.connect(pubAddress3, 'PUB')

    # subSocket1 = socket.connect(subAddress1, 'SUB')
    subSocket2 = socket.connect(subAddress2, 'SUB')
    # subSocket3 = socket.connect(subAddress3, 'SUB')

    socketDic = dict()
    # socketDic[0] = [pubSocket1, subSocket1]
    socketDic[1] = [pubSocket2, subSocket2]
    # socketDic[2] = [pubSocket3, subSocket3]
    # except:
    #     pass
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
        action = localRecv[2]  # IQ
        instructionInfo = msg[3]
        print instructionInfo
        instructionInfoList = instructionInfo.split(';')
        print instructionInfoList
        if mode == 'scan':
            startFreq = instructionInfoList[0]
            endFreq = instructionInfoList[1]
            scan_recv = scan_thread.Recv(localQueue, subSock)
            scan_send = scan_thread.Send(startFreq, endFreq, pubSock)
            scan_recv.start()
            scan_send.run()
            while localQueue.empty():
                pass
            else:
                bins = localQueue.get()
                freq_list = localQueue.get()
                bins = [c - 11 for c in bins]
                # 将回传的频谱保存成中间文件
                dirPath = r'..\..\usrp_recvfiles\specfiles'
                filesOrDirsOperate.makesureDirExist(dirPath)
                local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                filePath = dirPath + r'\%s.dat' % local_time
                f = open(filePath, 'w')
                for i in range(len(freq_list)):
                    f.write(str(freq_list[i]) + ' ')
                f.write('\n')
                for i in range(len(bins)):
                    f.write(str(bins[i]) + ' ')
                f.close()
        repSocket.send(os.path.abspath(filePath))

if __name__ == '__main__':
    # print "working demo"
    threadControl()