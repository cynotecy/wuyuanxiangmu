"""
@File:pluralCommunicationProxy.py
@Author:lcx
@Date:2020/9/514:22
@Desc:适用于多设备同频段采集，是否同时采集取决于usrp数据中台的写法
需输入设备号列表、采集指令（除去设备号之外的部分）、结果队列、usrp采集代理、3900采集代理
采集运行结束后结果队列中将存放全部的采集结果，格式待定
"""
from threading import Thread
import queue
from communication import communicationProxy
class PluralCommunicationProxy(Thread):
    def __init__(self, deviceList, requestMsg, resultQueue, usrpProxy, ceyearProxy):
        super(PluralCommunicationProxy, self).__init__()
        self.deviceList = deviceList
        self.device = ""
        self.data = ""
        self.requestMsg = requestMsg
        self.resultQueue = resultQueue
        self.usrpProxy = usrpProxy
        self.ceyearProxy = ceyearProxy
    def msgCombine(self, deviceNum):
        return deviceNum + self.requestMsg
    def dataGet(self):
        usrpList = []
        msgList = []
        for deviceNum in self.deviceList:
            if "USRP" in deviceNum:
                usrpList.append(deviceNum.strip("USRP"))
            else:
                msgList.append(self.msgCombine(deviceNum))
        usrpListStr = ""
        if len(usrpList)>1:
            usrpListStr = ";".join(usrpList)
        elif len(usrpList) == 1:
            usrpListStr = usrpList[0]+";"
        if usrpListStr:
            msgList.append(self.msgCombine(usrpListStr))
        dataQList = []
        for msg in msgList:
            q = queue.Queue()
            dataQList.append(q)
            communicationThread = communicationProxy.CommunicationProxy(msg, q, self.usrpProxy, self.ceyearProxy)
            communicationThread.start()
        # 查询直至所有的dataQ都有内容
        dataReadyFlag = False
        while not dataReadyFlag:
            for q in dataQList:
                dataReadyFlag = dataReadyFlag and (~(q.qsize == 2))
            if not dataReadyFlag:
                dataReadyFlag = True
        dataRsltList = []
        for q in dataQList:
            dataRsltList.append(q.get())
        reportMsg = "|".join(dataRsltList)
        self.resultQueue.put(reportMsg)

    def run(self):
        self.dataGet()

if __name__ == '__main__':
    from communication import zmqLocal
    from communication.ceyearController import ceyearProxy
    import queue
    import time

    usrpCommu = zmqLocal.localZMQ()
    av3900Commu = ceyearProxy.CeyearProxy("172.141.11.202")
    rsltQ = queue.Queue()
    reqMsg = ',scan,plural,' + str(900e6) + ";" +str(950e6)
    deviceList = ["USRP1", "USRP2", "3900"]
    # usrpMsg = "USRP1" + ',scan,IQ,' + str(900e6) + ";" +str(950e6)
    # usrpMsg = ("USRP1" + ',collect,IQoc,' + str(960e6) + ";" + str(1e6) + ";" + str(12.5e6))
    # # av3900Msg = "3900" + ',scan,IQ,' + str(900e6) + ";" +str(950e6)
    # av3900Msg = "3900" + ',collect,IQsingle,' + str(900e6) + ";" + str(950e6)

    # i = 0
    # while i < 100:
    dataGetT = PluralCommunicationProxy(deviceList,reqMsg, rsltQ, usrpCommu, av3900Commu)
    dataGetT.start()
    while rsltQ.empty():
        pass
    data = rsltQ.get()
    dataList = data.split("|")
    print("finish dataget")