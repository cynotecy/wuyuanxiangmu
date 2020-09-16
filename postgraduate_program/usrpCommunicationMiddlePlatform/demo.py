# -*- coding: UTF-8 -*-
import sys
import time
import os
import datetime
import Queue
import logging
import thread
import threading
import zmq
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from current_controller import scan_thread, collect_thread
from socketTest import socketInit, repParaThread
from functions import filesOrDirsOperate
import keyboard
"""
数据中台
"""

logger = logging.getLogger("transmitPlatformLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

def threadControl():
    logger.debug("shell path:"+ os.getcwd())
    stopFlag = 0
    keyboardListerThread = threading.Thread(target=keyboardListener, args=(stopFlag,))
    keyboardListerThread.start()
    standar = '-11'  # USRP定标
    # standar = '0'  # USRP定标
    remoteTimeOut = 10  # 远程连接超时时限
    localQueue = Queue.Queue()
    remoteQueue = Queue.Queue()
    # 向4路usrp的远程连接地址
    # 发送地址
    pubAddressDic = dict()
    pubAddressDic[0] = 'tcp://127.0.0.1:6000'
    pubAddressDic[1] = 'tcp://127.0.0.1:6001'
    pubAddressDic[2] = 'tcp://127.0.0.1:6002'
    pubAddressDic[3] = 'tcp://127.0.0.1:6003'
    # 接收地址
    subAddressDic = dict()
    subAddressDic[0] = 'tcp://127.0.0.1:5000'
    subAddressDic[1] = 'tcp://127.0.0.1:5001'
    subAddressDic[2] = 'tcp://127.0.0.1:5002'
    subAddressDic[3] = 'tcp://127.0.0.1:5003'
    
    # 本地连接地址，本地连接采用rep/req模式
    repAddress = 'tcp://127.0.0.1:5678'
    # 并行本地连接，当多路usrp同时使用时，repAddress地址绑定的socket不可以一直被占用则启用并行连接
    repAddressPara1 = 'tcp://127.0.0.1:6668'
    repAddressPara2 = 'tcp://127.0.0.1:6669'
    repAddressPara3 = 'tcp://127.0.0.1:6670'
    repAddressPara4 = 'tcp://127.0.0.1:6671'
    repParaAddressList = [repAddressPara1, repAddressPara2, repAddressPara3, repAddressPara4]
    # 定义连接字典
    socketDic = dict()


    for i in range(0,4):
        socketDic[i] = [socketInit.connect(pubAddressDic[i], 'PUB'),
                        socketInit.connect(subAddressDic[i], 'SUB')]
        logger.info("连接" + str(i)+"创建成功")

    repSocket = socketInit.connect(repAddress, 'REP')
    repParaSocketDic = {}
    repParaThreadDic = {}

    while not stopFlag:
        logger.info('py2 waiting msg')
        localRecv = repSocket.recv()
        logger.info('收到信息' + localRecv)

        if localRecv == "StopAll":
            repSocket.send("StopAllOk")
            stopFlag = 1
            continue

        msg = localRecv.split(',')
        logger.info(msg)
        if ';' in msg[0]:
            pubSockList = []
            subSockList = []
            if not ":" in msg[0]:
                usrpNumList = msg[0].split(';')
                for usrpNumStr in usrpNumList:
                    usrpNum = int(usrpNumStr)
                    pubSock = socketDic[usrpNum - 1][0]
                    subSock = socketDic[usrpNum - 1][1]
                    pubSockList.append(pubSock)
                    subSockList.append(subSock)
            elif "." in msg[0]:
                # 设备名解析
                deviceAntennaList = msg[0].split(".")
                compareReqDic = dict()
                for record in deviceAntennaList:
                    recordList = record.split(":")
                    compareReqDic[recordList[0]] = recordList[1:]
                    usrpNum = int(recordList[0].strip("USRP"))
                    pubSock = socketDic[usrpNum - 1][0]
                    subSock = socketDic[usrpNum - 1][1]
                    pubSockList.append(pubSock)
                    subSockList.append(subSock)

        else:
            if "USRP" in msg[0]:
                usrpNum = int(msg[0].strip("USRP"))
                pubSock = socketDic[usrpNum - 1][0]
                subSock = socketDic[usrpNum - 1][1]
            else:
                usrpNum = int(msg[0])
                pubSock = socketDic[usrpNum - 1][0]
                subSock = socketDic[usrpNum - 1][1]
                # logger.error("错误的设备名称")
        mode = msg[1]  # e.g. scan
        action = msg[2]  # e.g. IQ
        instructionInfo = msg[3]
        instructionInfoList = instructionInfo.split(';')
        # 扫频模式
        if mode == 'scan':
            # IQ&频谱包络&稳态干扰识别扫频
            if action == 'IQ' or action == 'specEnvelope' or action == 'steadyStateInterference':

                startFreq = instructionInfoList[0]
                endFreq = instructionInfoList[1]
                scanRecv = scan_thread.Recv(localQueue, subSock, standar)
                scanSend = scan_thread.Send(startFreq, endFreq, pubSock)
                scanRecv.start()
                scanSend.run()
                startTime = datetime.datetime.now()
                while localQueue.empty():
                    nowTime = datetime.datetime.now()
                    period = (nowTime - startTime).seconds
                    if period > remoteTimeOut:
                        scanRecv.stop()
                        repSocket.send('超时')
                        break
                else:
                    bins = localQueue.get()
                    freqList = localQueue.get()
                    # 将回传的频谱直接发给py3
                    bins = [str(i) for i in bins]
                    freqlist = [str(i) for i in freqList]
                    binStr = " ".join(bins)
                    freqStr = " ".join(freqlist)
                    freqbinsList = [freqStr, binStr]
                    freqbins = ';'.join(freqbinsList)
                    repSocket.send(freqbins)

            # 48H监测扫频（连续）（1-4线程）
            elif action == 'specMonitor':
                # if not instructionInfoList[0] == '0':
                try:
                    repParaSocketDic[usrpNum] = socketInit.connect(repParaAddressList[usrpNum-1], 'REP')
                    repParaThreadDic[usrpNum] = repParaThread.RepParaThread(repParaSocketDic[usrpNum], pubSock, subSock,
                                                           standar, remoteTimeOut)
                    repParaThreadDic[usrpNum].start()
                    repSocket.send(repParaAddressList[usrpNum-1])
                except Exception, e:
                    logger.error(e)
                    # 虽然我不知道为啥有时候terminate会不好使，但是通过这句话让terminate失灵时本该关闭的socket连接关闭了
                    # repSocket.send("paraSocket {} build failed".format(str(usrpNum)))

            # 多设备扫频(同频段)
            elif action == 'plural':
                startFreq = instructionInfoList[0]
                endFreq = instructionInfoList[1]
                scanRecvList = []
                scanSendList = []
                i = 0
                j = 0
                dataQList = []
                for usrpN in usrpNumList:
                    q = Queue.Queue()
                    dataQList.append(q)
                for subSock in subSockList:
                    scanRecvList.append(scan_thread.Recv(dataQList[i], subSock, standar))
                    scanRecvList[i].start()
                    i += 1
                for pubSock in pubSockList:
                    scanSendList.append(scan_thread.Send(startFreq, endFreq, pubSock))
                    scanSendList[j].run()
                    j += 1
                startTime = datetime.datetime.now()
                # 查询直至所有的dataQ都有两个元素
                dataReadyFlag = False
                while not dataReadyFlag:
                    nowTime = datetime.datetime.now()
                    period = (nowTime - startTime).seconds
                    if period > remoteTimeOut:
                        for scanRecv in scanRecvList:
                            scanRecv.stop()
                        repSocket.send('超时')
                        break
                    else:
                        for q in dataQList:
                            dataReadyFlag = dataReadyFlag and (~(q.qsize == 2))
                        if not dataReadyFlag:
                            dataReadyFlag = True
                else:
                    reportDataList = []
                    for k in range(len(dataQList)):
                        deviceNum = "USRP"+usrpNumList[k]
                        bins = dataQList[k].get()
                        freqList = dataQList[k].get()
                        # 将回传的频谱直接发给py3
                        bins = [str(i) for i in bins]
                        freqlist = [str(i) for i in freqList]
                        binStr = " ".join(bins)
                        freqStr = " ".join(freqlist)
                        freqbins = ';'.join([freqStr, binStr])
                        reportData = ":".join([deviceNum, freqbins])
                        reportDataList.append(reportData)
                    reportDataMsg = "|".join(reportDataList)
                    repSocket.send(reportDataMsg)

            # 天线（每个usrp的两个天线串行采集，不同usrp并行采集）（1或2线程）
            elif action == 'compare':
                startFreq = instructionInfoList[0]
                endFreq = instructionInfoList[1]
                scanRecvList = []
                scanSendList = []
                i = 0
                j = 0
                dataQDic = dict()
                # 在dataQDic中创建应有数量的Q
                for device in compareReqDic:
                    for antenna in compareReqDic[device]:
                        q = Queue.Queue()
                        dataQDic[":".join([device, antenna])] = q
                for subSock in subSockList:
                    scanRecvList.append(scan_thread.Recv(dataQList[i], subSock, standar))
                    scanRecvList[i].start()
                    i += 1
                for pubSock in pubSockList:
                    scanSendList.append(scan_thread.Send(startFreq, endFreq, pubSock))
                    scanSendList[j].run()
                    j += 1
                startTime = datetime.datetime.now()
                # 查询直至所有的dataQ都有两个元素
                dataReadyFlag = False
                while not dataReadyFlag:
                    nowTime = datetime.datetime.now()
                    period = (nowTime - startTime).seconds
                    if period > remoteTimeOut:
                        for scanRecv in scanRecvList:
                            scanRecv.stop()
                        repSocket.send('超时')
                        break
                    else:
                        for q in dataQList:
                            dataReadyFlag = dataReadyFlag and (~(q.qsize == 2))
                        if not dataReadyFlag:
                            dataReadyFlag = True
                else:
                    reportDataList = []
                    for k in range(len(dataQList)):
                        deviceNum = "USRP" + usrpNumList[k]
                        bins = dataQList[k].get()
                        freqList = dataQList[k].get()
                        # 将回传的频谱直接发给py3
                        bins = [str(i) for i in bins]
                        freqlist = [str(i) for i in freqList]
                        binStr = " ".join(bins)
                        freqStr = " ".join(freqlist)
                        freqbins = ';'.join([freqStr, binStr])
                        reportData = ":".join([deviceNum, freqbins])
                        reportDataList.append(reportData)
                    reportDataMsg = "|".join(reportDataList)
                    repSocket.send(reportDataMsg)

        # 采集模式
        elif mode == 'collect':
            # 批量采集，数据直接写入文件
            if action == 'IQoc':
                centreFreq = float(instructionInfoList[0])
                bdWdith = float(instructionInfoList[1])
                # currentPath = os.path.abspath(os.path.dirname(__file__))
                currentPath = os.getcwd()
                logger.debug("self path: "+currentPath)
                fatherPath = os.path.join(os.path.dirname(currentPath), "data")
                dirPath = os.path.join(fatherPath, r'usrp_recvfiles\auto_recognize')
                filesOrDirsOperate.makesureDirExist(dirPath)
                local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                filePath = os.path.join(dirPath, r'oc_collect_{}.txt'.format(local_time))
                logger.info("oc file path: "+filePath)
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
                    logger.info('localQueue:'+localQueue.get())
                    repSocket.send(filePath)

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
                    logger.info('localQueue:' + str(type(data)))
                    repSocket.send(data)

            # 两路IQ采集
            elif action == '2way':
                centreFreq = float(instructionInfoList[0])
                bdWdith = float(instructionInfoList[1])
                samprate = float(instructionInfoList[2])
                localQueue.queue.clear()
                collectRecv = collect_thread.Recv(localQueue, subSock, way=2)
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
                    logger.info('localQueue:' + str(type(data)))
                    repSocket.send(data)

def getSockerLink(pubAddr, subAddr):
    pubSocket = socketInit.connect(pubAddr, 'PUB')
    subSocket = socketInit.connect(subAddr, 'SUB')
    return pubSocket, subSocket

def keyboardListener(stopFlag):
    keyboard.wait("q")
    stopFlag = 1

if __name__ == '__main__':
    threadControl()