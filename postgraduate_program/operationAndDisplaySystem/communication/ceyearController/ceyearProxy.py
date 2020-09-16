"""
@File:ceyearProxy.py
@Author:lcx
@Date:2020/9/311:49
@Desc:用来进一步解析采集指令，根据scan/collect来判断调用哪个数据获取接口
"""
import os
import time
from communication.ceyearController import spectrum_snapshot, IQ_snapshot
import logging
class CeyearProxy():
    def __init__(self, ip, fatherPath):
        self.ip = ip
        self.fatherPath = fatherPath
        self.logger = logging.getLogger("UILogger")
        LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
        DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
        logging.basicConfig(level=logging.INFO,
                            format=LOG_FORMAT, datefmt=DATE_FORMAT)
    def getCeyearData(self, msg):
        msgList = msg.split(",")
        dataMode = msgList[1]
        dataAction = msgList[2]
        dataInstructionInfoList = msgList[3].split(";")
        if dataMode == "scan":
            if dataAction == 'IQ' or dataAction == 'specEnvelope' or dataAction == 'steadyStateInterference' or "plural":
                startFreq = float(dataInstructionInfoList[0])
                endFreq = float(dataInstructionInfoList[1])
                data = spectrum_snapshot.getSpecData(self.ip, startFreq, endFreq)
                return data
        elif dataMode == "collect":
            if dataAction == 'IQsingle':
                centreFreq = float(dataInstructionInfoList[0])
                bdWidth = float(dataInstructionInfoList[1])
                data = IQ_snapshot.getIQData(self.ip, centreFreq, bdWidth)
                return data
            elif dataAction == "IQoc":
                centreFreq = round(float(dataInstructionInfoList[0]), 1)
                bdWidth = round(float(dataInstructionInfoList[1]), 1)
                self.logger.debug("3900采集开始")
                data = IQ_snapshot.getIQData(self.ip, centreFreq, bdWidth)
                dirPath = os.path.join(self.fatherPath, r"usrp_recvfiles\auto_recognize")
                local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                filePath = os.path.join(dirPath, r'oc_collect_{}.txt'.format(local_time))
                self.logger.debug("3900oc file path:"+filePath)
                dataList = data.split(";")
                dataToWrite = "\n".join(dataList)
                with open(filePath, "w") as f:
                    # f.writelines(data)
                    f.writelines(dataToWrite)
                return filePath