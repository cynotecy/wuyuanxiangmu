"""
@File:communicationProxy.py
@Author:lcx
@Date:2020/9/39:38
@Desc:面向界面的设备调度代理模块，向界面屏蔽设备通信的具体过程，接收界面传入的数据请求消息（有固定格式，需以设备名为开头）和
数据接收队列，根据数据请求消息执行数据请求操作后将收到的数据置入数据接收队列
"""
from threading import Thread
class CommunicationProxy(Thread):
    def __init__(self, requestMsg, resultQueue, usrpProxy, ceyearProxy, fatherPath = ''):
        super(CommunicationProxy, self).__init__()
        self.device = ""
        self.data = ""
        self.requestMsg = requestMsg
        self.resultQueue = resultQueue
        self.dataProxy = ''
        self.usrpProxy = usrpProxy
        self.ceyearProxy = ceyearProxy
        self.fatherPath = fatherPath
    def deviceResolve(self):
        self.device = self.requestMsg.split(",")[0]
    def dataGet(self):
        if "USRP" in self.device or ";" in self.device:
            self.dataProxy = self.usrpProxy
            self.data = self.dataProxy.sendMessage(self.requestMsg)
            self.dataEnqueue()
        elif "3900" in self.device:
            self.dataProxy = self.ceyearProxy
            self.data = self.dataProxy.getCeyearData(self.requestMsg)
            self.dataEnqueue()
        else:
            # 抛出异常
            pass
    def dataGetManual(self, msg):
        self.requestMsg = msg
        self.deviceResolve()
        if "USRP" in self.device:
            self.dataProxy = self.usrpProxy
            self.data = self.dataProxy.sendMessage(self.requestMsg)
        elif "3900" in self.device:
            self.dataProxy = self.ceyearProxy
            self.data = self.dataProxy.getCeyearData(self.requestMsg)
        return self.data
    def dataEnqueue(self):
        self.resultQueue.put(self.data)
    def run(self):
        self.deviceResolve()
        self.dataGet()

if __name__ == '__main__':
    from communication import zmqLocal
    from communication.ceyearController import ceyearProxy
    import queue
    import time
    usrpCommu = zmqLocal.localZMQ()
    av3900Commu = ceyearProxy.CeyearProxy("172.141.11.202")
    rsltQ = queue.Queue()
    # usrpMsg = "USRP1" + ',scan,IQ,' + str(900e6) + ";" +str(950e6)
    # usrpMsg = ("USRP1" + ',collect,IQoc,'+ str(960e6) + ";" + str(1e6) + ";" + str(12.5e6))
    usrpMsg = ("USRP1" + ',collect,IQsingle,'+ str(960e6) + ";" + str(1e6) + ";" + str(12.5e6))
    # av3900Msg = "3900" + ',scan,IQ,' + str(900e6) + ";" +str(950e6)
    av3900Msg = "3900" + ',collect,IQsingle,' + str(900e6) + ";" +str(950e6)

    # i = 0
    # while i < 100:
    dataGetT = CommunicationProxy(av3900Msg, rsltQ, usrpCommu, av3900Commu)
    dataGetT.start()
    while rsltQ.empty():
        pass
    print("finish dataget")
    # ##############
    # communicationThread = communicationProxy.CommunicationProxy(msg, self.zmqLocalQ, self.usrpCommu, self.av3900Commu)
    # communicationThread.start()
