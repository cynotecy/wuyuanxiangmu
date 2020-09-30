"""
@File:circulationZmqThread.py
@Author:lcx
@Date:2020/8/3020:02
@Desc:
"""
from threading import Thread
import datetime
import time
from communication import communicationProxy
class CircultaionZmqThread(Thread):
    def __init__(self, usrpCommu, av3900Commu, msg, dataCach, condition, waitNum, dataNumPerCell = 1):
        super(CircultaionZmqThread, self).__init__()
        self.usrpCommu = usrpCommu
        self.av3900Commu = av3900Commu
        self.msg = msg
        self.dataCach = dataCach
        self.condition = condition
        self.waitNum = waitNum
        self.stopFlag = 0
        self.recvNum = 0
        self.dataNumPerCell = dataNumPerCell
        self.setDaemon(True)
        self.q = ''
        self.comunicationThread = communicationProxy.CommunicationProxy(self.msg, self.q, usrpCommu, av3900Commu)
    def run(self):
        self.condition.acquire()
        while not self.stopFlag:
            while self.dataCach.qsize() < self.waitNum:
                dataList = []
                while self.recvNum < self.dataNumPerCell:
                    startTime = datetime.datetime.now()
                    dataList.append([self.comunicationThread.dataGetManual(self.msg)])
                    self.recvNum += 1
                    endTime = datetime.datetime.now()
                    if (endTime - startTime).seconds.numerator < 1:
                        time.sleep(1)
                self.dataCach.put(dataList)
                self.recvNum = 0
            self.condition.wait()
        self.condition.release()

    def reset(self):
        self.dataCach.queue.clear()
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()

    def stop(self):
        self.stopFlag = 1
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()

if __name__ == '__main__':
    from communication import zmqLocal
    import queue
    import threading
    import logging
    from communication.ceyearController import ceyearProxy

    logger = logging.getLogger("循环采集测试日志")

    LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(level=logging.DEBUG,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)
    usrpCommu = zmqLocal.localZMQ()
    av3900Commu = ceyearProxy.CeyearProxy("172.141.11.202","")
    startfreq = 900*1000000
    endfreq = 950*1000000
    usrpNum = "USRP2"
    msg = (usrpNum + ',scan,IQ,' + str(startfreq) + ";" +str(endfreq))
    dataCach = queue.Queue()
    condition = threading.Condition()
    waitNum = 4
    circultaionZmqThread = CircultaionZmqThread(usrpCommu, av3900Commu, msg, dataCach, condition, waitNum, dataNumPerCell=10)
    circultaionZmqThread.start()
    while 1:
        ipt = input()
        if ipt == "q":
            logger.debug("input q")
            circultaionZmqThread.stop()

            break
        elif ipt == "r":
            logger.debug("input r")
            circultaionZmqThread.reset()
    print("end")