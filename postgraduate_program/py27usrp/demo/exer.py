# -*- coding: UTF-8 -*-
import sys
import time
import os
import datetime
import Queue
import thread
import zmq

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from current_controller import scan_thread, collect_thread
from socketTest import socketInit, repParaThread
from demo import exer2
from functions import filesOrDirsOperate

"""
加个远程连接检测
"""


def threadControl():
    standar = '-11'  # USRP定标
    # standar = '0'  # USRP定标
    remoteTimeOut = 10  # 远端socket超时时限
    localQueue = Queue.Queue()
    remoteQueue = Queue.Queue()
    pubAddress1 = 'tcp://127.0.0.1:6666'
    pubAddress2 = 'tcp://127.0.0.1:7777'
    # pubAddress3 = 'tcp://127.0.0.1:6666'

    subAddress1 = 'tcp://127.0.0.1:5555'
    subAddress2 = 'tcp://127.0.0.1:9999'
    # subAddress3 = 'tcp://127.0.0.1:5555'

    # pubAddress1 = 'tcp://192.168.0.100:6666'
    # pubAddress2 = 'tcp://192.168.0.100:7777'
    # pubAddress3 = 'tcp://127.0.0.1:6666'
    #
    # subAddress1 = 'tcp://192.168.0.5:5555'
    # subAddress2 = 'tcp://192.168.0.5:9999'
    # subAddress3 = 'tcp://127.0.0.1:5555'

    repAddress = 'tcp://127.0.0.1:6667'
    # 并行本地连接，当多路usrp同时使用时，repAddress地址绑定的socket不可以一直被占用则启用并行连接
    repAddressPara1 = 'tcp://127.0.0.1:6668'
    repAddressPara2 = 'tcp://127.0.0.1:6669'
    repAddressPara3 = 'tcp://127.0.0.1:6670'
    repAddressPara4 = 'tcp://127.0.0.1:6671'
    repParaAddressList = [repAddressPara1, repAddressPara2, repAddressPara3, repAddressPara4]
    # 定义连接字典
    socketDic = dict()

    try:
        pubSocket1 = socketInit.connect(pubAddress1, 'PUB')
        subSocket1 = socketInit.connect(subAddress1, 'SUB')
        socketDic[0] = [pubSocket1, subSocket1]
        print "socket1 连接"
    except:
        pass

    try:
        pubSocket2 = socketInit.connect(pubAddress2, 'PUB')
        subSocket2 = socketInit.connect(subAddress2, 'SUB')
        socketDic[1] = [pubSocket2, subSocket2]
        print "socket2 连接"
    except:
        pass

    repSocket = socketInit.connect(repAddress, 'REP')

    while 1:
        print 'py2 waiting msg'
        localRecv = repSocket.recv()
        print '收到信息' + localRecv

        msg = localRecv.split(',')
        print msg

        usrpNum = int(msg[0])
        pubSock = socketDic[usrpNum - 1][0]
        subSock = socketDic[usrpNum - 1][1]
        mode = msg[1]  # e.g. scan
        action = msg[2]  # e.g. IQ
        instructionInfo = msg[3]
        instructionInfoList = instructionInfo.split(';')
        # 扫频模式
        if mode == 'scan':
            # 48H监测扫频（连续）（1-4线程）
            if action == 'specMonitor':
                if not instructionInfoList[0] == '0':
                    try:
                        repParaSocket = socketInit.connect(repParaAddressList[usrpNum - 1], 'REP')
                        repParaT = exer2.RepParaThread(repParaSocket, pubSock, subSock, standar, remoteTimeOut)
                        repParaT.start()

                        repSocket.send(repParaAddressList[usrpNum - 1])
                    except Exception, e:
                        print repr(e)
                        # 虽然我不知道为啥有时候terminate会不好使，但是通过这句话让terminate失灵时本该关闭的socket连接关闭了
                        # repParaSocketDic[int(usrpNum)].close()
                        repSocket.send("paraSocket {} build failed".format(str(usrpNum)))
                else:
                    repParaT.terminate()
                    repParaT.join()
                    print "paraSocket {} closed".format(str(usrpNum))
                    repSocket.send("paraSocket {} closed".format(str(usrpNum)))



if __name__ == '__main__':
    # print "working demo"
    threadControl()