# -*- coding: UTF-8 -*-
"""
@File:repParaThread.py
@Author:lcx
@Date:2020/1/614:11
@Desc:rep多线程类，创建并行socket链接，用来跟主界面进行多路长时间通信，避免阻塞主链接
"""
import Queue
import datetime
import time
from current_controller import scan_thread, collect_thread
from threading import Thread
import threading


class RepParaThread(Thread):
    def __init__(self, repSocket, pubSocket, subSocket, standar, remoteTimeOut):
        super(RepParaThread, self).__init__()
        self.repSocket = repSocket
        self.pubSocket = pubSocket
        self.subSocket = subSocket
        self.standar = standar
        self.remoteTimeOut = remoteTimeOut
        self.localQueue = Queue.Queue()
        self.stopEvent = threading.Event()

    def run(self):
        while True:
            if self.stopEvent.is_set():
                self.repSocket.close()
                print 'from repParaThread: self.repSocket.close()'
                break
            else:
                # 接收界面端消息，发送工程机采集指令，接收工程机采集数据，转发采集数据至界面端
                try:
                    localRecv = self.repSocket.recv()
                    instructionInfoList = localRecv.split(';')
                    startFreq = instructionInfoList[0]
                    endFreq = instructionInfoList[1]
                    scanRecv = scan_thread.Recv(self.localQueue, self.subSocket, self.standar)
                    scanSend = scan_thread.Send(startFreq, endFreq, self.pubSocket)
                    scanRecv.start()
                    scanSend.run()
                    startTime = datetime.datetime.now()
                    while self.localQueue.empty():
                        nowTime = datetime.datetime.now()
                        period = (nowTime - startTime).seconds
                        if period > self.remoteTimeOut:
                            scanRecv.stop()
                            self.repSocket.send('超时')
                            break
                    else:
                        bins = self.localQueue.get()
                        freqList = self.localQueue.get()
                        # 将回传的频谱直接发给py3
                        bins = [str(i) for i in bins]
                        freqlist = [str(i) for i in freqList]
                        binStr = " ".join(bins)
                        freqStr = " ".join(freqlist)
                        freqbinsList = [freqStr, binStr]
                        freqbins = ';'.join(freqbinsList)
                        self.repSocket.send(freqbins)
                except Exception, e:
                    print repr(e), 'repParaThread reply'
                finally:
                    time.sleep(1)

    def terminate(self):
        self.stopEvent.set()
        print 'terminate'
