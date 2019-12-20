from multiprocessing import Process
from function import filesOrDirsOperate
import datetime
import time
import os
from threading import Thread
from controller.usrp_controller.usrp_shibie import (oc_list_getting_v2, oc_list_display_v1,
                                                    usrp_shibie_v3)
from controller.usrp_controller.specEnvelope_shibie import specEnvelope_shibie_v3


# 超频点判断线程
class IQOverThreshold(Thread):
    def __init__(self, onlineSpecX, onlineSpecY, thre, overThresholdQ):
        super(self, IQOverThreshold).__init__()
        self.onlineSpecX = onlineSpecX
        self.onlineSpecY = onlineSpecY
        self.thre = thre
        self.overThresholdQ = overThresholdQ
    def run(self):
        ocOverThresholdList = oc_list_getting_v2.position(self.onlineSpecX, self.onlineSpecY,
                                                   self.thre)
        self.overThresholdQ.put(ocOverThresholdList)

# 批量采集进程
class OcCollectThread(Thread):
    def __init__(self, usrpNum, ocRsltDict,
                    ocOverThresholdList, zmqLocal, ocCollectPathQ):
        super(OcCollectThread, self).__init__()
        self.usrpNum = usrpNum
        self.ocRsltDict = ocRsltDict
        self.ocOverThresholdList = ocOverThresholdList
        self.zmqLocal = zmqLocal
        self.ocCollectPathQ = ocCollectPathQ

    def run(self):
        """
        IQ自动识别线程1，根据表格选中行生成采集参数list，并依次发送lsit中的采集指令
        :return:无返回值，将IQ文件的存储路径存入FIFO队列ocCollectPathQ
        """
        for i in self.ocRsltDict:
            startFreq = float(self.ocOverThresholdList[0][i][0])*1000000
            endFreq = float(self.ocOverThresholdList[0][i][1])*1000000
            centreFreq = float(self.ocOverThresholdList[0][i][2])*1000000
            bdWidth = endFreq - startFreq
            msg = self.usrpNum + ',collect,IQoc,' + str(centreFreq) + ";" + str(bdWidth)
            reslt = self.zmqLocal.sendMessege(msg)
            self.ocCollectPathQ.put(reslt)

# 批量识别进程
class OcRecognizeThread(Thread):
    def __init__(self, ocRsltDict, ocCollectPathQ, ocLoadingQ):
        super(OcRecognizeThread, self).__init__()
        self.ocRsltDict = ocRsltDict
        self.ocLoadingQ = ocLoadingQ
        self.ocCollectPathQ = ocCollectPathQ
    def run(self):
        """自动识别线程，共识别len(self.ocRowNumSelectList)次，从self.ocCollectPathQ队列中取文件地址并识别
        将识别结果存在dic中
        :return:
        """
        for num in self.ocRsltDict:
            while 1:
                if self.ocCollectPathQ.empty():
                    continue
                else:
                    path = self.ocCollectPathQ.get()
                    recognizeResult = usrp_shibie_v3.play(path)
                    self.ocRsltDict[int(num)] = recognizeResult
                    break
        self.ocLoadingQ.put(self.ocRsltDict)

# IQ识别线程
class IQSingleProcess(Thread):
    def __init__(self, path, q):
        super(IQSingleProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
    def run(self):
        print('thread')
        starttime = datetime.datetime.now()
        rslt = usrp_shibie_v3.play(self.path)
        endtime = datetime.datetime.now()
        strTime = '识别线程花费:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        print(strTime)
        self.q.put(rslt)

# IQ存储进程
class IQDataSaveProcess(Process):
    def __init__(self, data, q):
        super(IQDataSaveProcess, self).__init__()
        currentPath = os.path.dirname(__file__)
        fatherPath = os.path.dirname(currentPath)
        dirPath = os.path.join(fatherPath, r'usrp_recvfiles')
        filesOrDirsOperate.makesureDirExist(dirPath)
        local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filePath = os.path.join(dirPath, r'single_collect_{}.txt'.format(local_time))
        self.path = filePath
        self.data = data
        self.q = q
    def run(self):
        print('saving process:', self.path)
        f = open(self.path, 'w')
        f.write(self.data)
        f.close()
        self.q.put(self.path)

# 频谱包络识别线程
class specEnvelopeProcess(Thread):
    def __init__(self, path, q):
        super(specEnvelopeProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
    def run(self):
        print('thread')
        starttime = datetime.datetime.now()
        rslt = specEnvelope_shibie_v3.baoluoshibie(self.path)
        endtime = datetime.datetime.now()
        strTime = '识别线程花费:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        print(strTime)
        self.q.put(rslt)

# 频谱包络存储进程
class specEnvelopeDataSaveProcess(Process):
    def __init__(self, data, q):
        super(specEnvelopeDataSaveProcess, self).__init__()
        currentPath = os.path.dirname(__file__)
        fatherPath = os.path.dirname(currentPath)
        dirPath = os.path.join(fatherPath, r'specEnvelope_recvfiles')
        filesOrDirsOperate.makesureDirExist(dirPath)
        local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filePath = os.path.join(dirPath, r'specEnvelope_data_{}.txt'.format(local_time))
        self.path = filePath
        self.data = data
        self.q = q
    def run(self):
        print('saving process:', self.path)
        f = open(self.path, 'w')
        f.write(self.data)
        f.close()
        self.q.put(self.path)