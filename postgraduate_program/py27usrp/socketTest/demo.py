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
            # IQ扫频
            if action == 'IQ':
                startFreq = instructionInfoList[0]
                endFreq = instructionInfoList[1]
                scanRecv = scan_thread.Recv(localQueue, subSock, '-11')
                scanSend = scan_thread.Send(startFreq, endFreq, pubSock)
                scanRecv.start()
                scanSend.run()
                while localQueue.empty():
                    pass
                else:
                    bins = localQueue.get()
                    freqList = localQueue.get()
                    # 将回传的频谱直接发给py3
                    freqbinslist = [str(i) for i in freqList+bins]
                    freqbins = " ".join(freqbinslist)
                    repSocket.send(freqbins)
            # 频谱包络识别扫频
            elif action == 'specEnvelope':
                pass
            # 稳态干扰识别扫频
            elif action == 'steadyStateInterference':
                pass
            # 48H监测扫频（连续）（1-4线程）
            elif action == 'specMonitor':
                pass
            # 实时频谱仪扫频（连续）
            elif action == 'realtimeSpecMonitor':
                pass
            # 天线（每个usrp的两个天线串行采集，不同usrp并行采集）（1或2线程）
            elif action == 'antenna':
                pass
        # 采集模式
        elif mode == 'collect':
            # 批量采集
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
            # # 单个采集（串行，返回存储地址）
            # elif action == 'IQsingle':
            #     centreFreq = float(instructionInfoList[0])
            #     bdWdith = float(instructionInfoList[1])
            #     samprate = float(instructionInfoList[2])
            #     currentPath = os.path.dirname(__file__)
            #     fatherPath = os.path.dirname(currentPath)
            #     grandPath = os.path.dirname(fatherPath)
            #     dirPath = os.path.join(grandPath, r'usrp_recvfiles')
            #     filesOrDirsOperate.makesureDirExist(dirPath)
            #     local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            #     filePath = os.path.join(dirPath, r'single_collect_{}.txt'.format(local_time))
            #     print "single collect文件路径", filePath
            #     localQueue.queue.clear()
            #     collectRecv = collect_thread.Recv(localQueue, subSock, path=filePath)
            #     collectRecv.start()
            #     while 1:
            #         if collectRecv.is_alive():
            #             collectSend = collect_thread.Send(str(centreFreq), str(bdWdith), samprate, pubSock)
            #             collectSend.start()
            #             break
            #     while localQueue.empty():
            #         pass
            #     else:
            #         print 'localQueue:' + localQueue.get()
            #         repSocket.send(filePath)

            # 单个采集（并行，返回采集数据）
            elif action == 'IQsingle':
                centreFreq = float(instructionInfoList[0])
                bdWdith = float(instructionInfoList[1])
                samprate = float(instructionInfoList[2])
                localQueue.queue.clear()
                collectRecv = collect_thread.Recv(localQueue, subSock)
                collectRecv.start()
                while 1:
                    if collectRecv.is_alive():
                        collectSend = collect_thread.Send(str(centreFreq), str(bdWdith), samprate, pubSock)
                        collectSend.start()
                        break
                while localQueue.empty():
                    pass
                else:
                    data = localQueue.get()
                    print 'localQueue:' + str(type(data))
                    repSocket.send(data)

if __name__ == '__main__':
    # print "working demo"
    threadControl()