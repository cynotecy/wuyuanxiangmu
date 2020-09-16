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
import logging

logger = logging.getLogger("repParaThreadLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

class RepParaThread(Thread):
    def __init__(self, repSocket, pubSocket, subSocket, standar, remoteTimeOut):
        super(RepParaThread, self).__init__()
        self.repSocket = repSocket
        self.pubSocket = pubSocket
        self.subSocket = subSocket
        self.standar = standar
        self.remoteTimeOut = remoteTimeOut
        self.localQueue = Queue.Queue()


    def run(self):
        while True:
            try:
                logger.info("并行本地连接-启动")
                logger.debug('等待本地采集指令')
                localRecv = self.repSocket.recv()
                logger.debug('收到本地采集指令')
                if localRecv == 'close':
                    logger.info("并行本地连接-收到处理端关闭指令")
                    self.repSocket.send('para socket thread closed')
                    self.repSocket.close()
                    break
                else:
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
                            logger.info("并行本地连接-远端超时")
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
                logger.error(e)
            finally:
                time.sleep(0.3)
