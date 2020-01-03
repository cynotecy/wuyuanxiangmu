from multiprocessing import Process
from function import filesOrDirsOperate
import datetime
import time
import os
import queue
from threading import Thread
from socketDemo.zmqLocal import zmqThread
from controller.usrp_controller.usrp_shibie import (oc_list_getting_v2, oc_list_display_v1,
                                                    usrp_shibie_v3)
from controller.usrp_controller.specEnvelope_shibie import specEnvelope_shibie_v3
from controller.usrp_controller.steadyStateInterference_shibie import steadyStateInterference_shibie_v2
from controller.Pico_controller import pico_jicheng_online_pack_v2, pico_jicheng_offline_v2

# py2线程（函数形式）
def py2Thread():
    currentPath = os.path.dirname(__file__)
    fatherPath = os.path.dirname(currentPath)
    scriptPath = os.path.join(fatherPath, r'py27usrp/socketTest/demo.py')
    os.system('python2 {}'.format(scriptPath))

# 超频点判断线程
class IQOverThreshold(Thread):
    def __init__(self, onlineSpecX, onlineSpecY, thre, overThresholdQ):
        super(IQOverThreshold, self).__init__()
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

# 频谱保存线程
class SaveSpectrumThread(Thread):
    def __init__(self, path, data, q):
        super(SaveSpectrumThread, self).__init__()
        self.path = path
        self.data = data
        self.q = q
    def run(self):
        starttime = datetime.datetime.now()
        with open(self.path, 'w') as f:
            f.write(self.data[0])
            f.write('\n')
            f.write(self.data[1])
        endtime = datetime.datetime.now()
        strTime = '存储线程花费:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        print(strTime)
        self.q.put(self.path)

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

# 频谱包络在线识别进程（包括采集、识别、存储）
class specEnvelopeOnlineProcess(Thread):
    def __init__(self, zmq, msg, dataQ, algorithmProcessQ, savingProcessQ):
        super(specEnvelopeOnlineProcess, self).__init__()
        self.dataQ = dataQ
        self.algorithmProcessQ = algorithmProcessQ
        self.savingProcessQ = savingProcessQ
        self.zmq = zmq
        self.msg = msg
        self.zmqQ = queue.Queue()

    # 包络识别
    def recognize(self, data):
        starttime = datetime.datetime.now()
        rslt = specEnvelope_shibie_v3.baoluoshibie(data)
        endtime = datetime.datetime.now()
        strTime = '识别线程花费:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        print(strTime)
        self.algorithmProcessQ.put(rslt)

    # 数据存储
    def save(self, data):
        starttime = datetime.datetime.now()
        currentPath = os.path.dirname(__file__)
        fatherPath = os.path.dirname(currentPath)
        dirPath = os.path.join(fatherPath, r'specEnvelope_recvfiles')
        filesOrDirsOperate.makesureDirExist(dirPath)
        local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filePath = os.path.join(dirPath, r'specEnvelope_data_{}.txt'.format(local_time))
        print('存储文件名为:', filePath)
        f = open(filePath, 'w')
        f.write(data[0])
        f.write('\n')
        f.write(data[1])
        f.close()
        endtime = datetime.datetime.now()
        strTime = '存储线程花费:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        print(strTime)
        self.savingProcessQ.put(filePath)

    def run(self):
        zmqT = Thread(target=zmqThread, args=(self.zmq, self.msg, self.zmqQ))
        zmqT.start()
        while self.zmqQ.empty():
            pass
        else:
            reslt = self.zmqQ.get()
            print("reslt", reslt)
            if reslt == "超时":
                self.dataQ.put('超时')
                self.algorithmProcessQ.put("超时")
                self.savingProcessQ.put("超时")
            else:
                # 当zmq返回值为数据时，对数据进行切分，得到x和y
                data = reslt
                dataList = data.split(r';')
                xList = dataList[0].split(' ')
                yList = dataList[1].split(' ')
                # 将x和y塞入数据队列
                self.dataQ.put([xList, yList])
                # 开启识别进程/线程
                recognizeProcess = Thread(target=self.recognize, args=([xList, yList],))
                recognizeProcess.start()
                # 开启存储进程/线程
                savingProcess = Thread(target=self.save, args=(dataList,))
                savingProcess.start()

# 频谱包络离线识别线程
class specEnvelopeOfflineProcess(Thread):
    def __init__(self, path, q):
        super(specEnvelopeOfflineProcess, self).__init__()
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

# 脉冲在线识别线程
class PulseRecognizeOnlineProcess(Thread):
    def __init__(self, path, q, length):
        super(PulseRecognizeOnlineProcess, self).__init__()
        self.path = path
        self.q = q
        self.length = length
    def run(self):
        reslt, targetFile = pico_jicheng_online_pack_v2.configuration(self.path, self.length)
        print("pulse recognize reslt, target file path:", reslt, targetFile)
        self.q.put(reslt)
        self.q.put(targetFile)

# 脉冲离线识别线程
class PulseRecognizeOfflineProcess(Thread):
    def __init__(self, path, q, length):
        super(PulseRecognizeOfflineProcess, self).__init__()
        self.path = path
        self.q = q
        self.length = length
    def run(self):
        reslt= pico_jicheng_offline_v2.configuration(self.path, self.length)
        print("pulse recognize reslt:", reslt)
        self.q.put(reslt)

# 稳态干扰判断线程
class steadyStateRecognizeProcess(Thread):
    def __init__(self, q, x, y, standardVaule, outputPath):
        super(steadyStateRecognizeProcess, self).__init__()
        self.q = q
        self.x = x
        self.y = y
        self.standardValue = standardVaule
        self.outputPath = outputPath
    def run(self):
        reslt = steadyStateInterference_shibie_v2.position(self.x,
                                                           self.y,
                                                           self.standardValue,
                                                           self.outputPath)
        self.q.put(reslt)