# -*- coding: UTF-8 -*-
"""
@File:antennaProxy.py
@Author:lcx
@Date:2020/9/1520:02
@Desc:
"""
import Queue
import time
from current_controller import antennaChangeThread, scan_thread
def antennaCommandParseProxy(subSock, pubSock, standar, startFreq, endFreq):
    # dataQ = queue.Queue()
    # 发送天线切换指令后发送采集指令后发送天线切换指令
    antennaChangeT = antennaChangeThread.AntennaChangeSend(startFreq, endFreq, pubSock, "1")
    antennaChangeT.start()
    time.sleep(3)
    RF1dataQ = Queue.Queue()
    recvT = scan_thread.Recv(RF1dataQ, subSock, standar)
    sendT = scan_thread.Send(startFreq, endFreq, pubSock)
    recvT.start()
    sendT.run()
    while RF1dataQ.empty():
        pass
    antennaChangeT = antennaChangeThread.AntennaChangeSend(startFreq, endFreq, pubSock, "2")
    antennaChangeT.start()
    time.sleep(3)
    RF2dataQ = Queue.Queue()
    recvT = scan_thread.Recv(RF2dataQ, subSock, standar)
    sendT = scan_thread.Send(startFreq, endFreq, pubSock)
    recvT.start()
    sendT.run()
    while RF2dataQ.empty():
        pass
    RF1bins = [str(i) for i in RF1dataQ.get()]
    RF1freq = [str(i) for i in RF1dataQ.get()]
    RF2bins = [str(i) for i in RF2dataQ.get()]
    RF2freq = [str(i) for i in RF2dataQ.get()]


    # dataQ.put("|".join(["RF1:"+RF1dataQ.get(), "RF2:"+RF2dataQ.get()]))
    return "|".join(["RF1:"+";".join([" ".join(RF1freq), " ".join(RF1bins)]),
                     "RF2:"+";".join([" ".join(RF2freq), " ".join(RF2bins)])])