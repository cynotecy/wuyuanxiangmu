"""
数据采集、存储、识别等线程
"""
from multiprocessing import Process
from function import filesOrDirsOperate
import datetime
import time
import os
import queue
from threading import Thread
from communication.zmqLocal import zmqThread
from controller.usrp_controller.usrp_shibie import (oc_list_getting_v2, oc_list_display_v1,usrp_shibie_v7,
                                                    usrp_shibie_v10)
from controller.usrp_controller.specEnvelope_shibie import specEnvelope_shibie_v3
from controller.usrp_controller.steadyStateInterference_shibie import steadyStateInterference_shibie_v3
from controller.Pico_controller import pico_jicheng_online_v3, pico_jicheng_offline_v3
from controller.usrp_controller.interference_cancellation import interferenceCancellationCalling
from SNR import snr_estimation_integration, snr_spectrum
from communication import communicationProxy
from SNR.component import dataGet, dataSave, dataGet_spectrum

import logging
logger = logging.getLogger("Main.algorithmThread")

# py2线程（函数形式）
def py2Thread():
    currentPath = os.path.dirname(__file__)
    fatherPath = os.path.dirname(currentPath)
    grandPath = os.path.dirname(fatherPath)
    scriptPath = os.path.join(grandPath, r'usrpCommunicationMiddlePlatform/demo.py')
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
    def __init__(self, deviceNum, ocRsltDict,
                    ocOverThresholdList, usrpCommu, av3900Commu, ocCollectPathQ):
        super(OcCollectThread, self).__init__()
        self.usrpNum = deviceNum
        self.ocRsltDict = ocRsltDict
        self.ocOverThresholdList = ocOverThresholdList
        self.usrpCommu = usrpCommu
        self.av3900Commu = av3900Commu
        self.ocCollectPathQ = ocCollectPathQ
        self.commuQ = queue.Queue()
    def run(self):
        """
        IQ自动识别线程1，根据表格选中行生成采集参数list，并依次发送lsit中的采集指令
        :return:无返回值，将IQ文件的存储路径存入FIFO队列ocCollectPathQ
        """
        for i in self.ocRsltDict.keys():
            startFreq = float(self.ocOverThresholdList[0][i][0])*1000000
            endFreq = float(self.ocOverThresholdList[0][i][1])*1000000
            centreFreq = float(self.ocOverThresholdList[0][i][2])*1000000
            bdWidth = endFreq - startFreq
            msg = self.usrpNum + ',collect,IQoc,' + str(centreFreq) + ";" + str(bdWidth)
            communicationThread = communicationProxy.CommunicationProxy(msg, self.commuQ, self.usrpCommu, self.av3900Commu)
            # communicationThread.start()
            # while self.commuQ.empty():
            #     pass
            data = communicationThread.dataGetManual(msg)
            self.ocCollectPathQ.put(data)

# 批量识别进程
class OcRecognizeThread(Thread):
    def __init__(self, ocRsltDict, ocCollectPathQ, ocLoadingQ, freqPointList):
        super(OcRecognizeThread, self).__init__()
        self.ocRsltDict = ocRsltDict
        self.ocLoadingQ = ocLoadingQ
        self.ocCollectPathQ = ocCollectPathQ
        self.freqPointList = freqPointList
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
                    recognizeResult = usrp_shibie_v7.play(self.freqPointList, path)
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
        # print(strTime)
        self.q.put(self.path)

# IQ识别线程
class IQSingleProcess(Thread):
    def __init__(self, path, q, freqPointList, harmonicNum, spec1=0, spec2=0):
        super(IQSingleProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
        self.freqPointList = freqPointList
        self.harmonicNum = harmonicNum
        self.spec1 = spec1
        self.spec2 = spec2
    def run(self):
        starttime = datetime.datetime.now()
        # 离线识别时，无法得到频谱数据
        if self.spec1==0 or self.spec2==0:
            # IQSNR算法开启
            snrQ = queue.Queue()
            snrThread = SNREstimationIntegrationThread(self.path, snrQ)
            snrThread.start()
            # IQ识别算法开启
            rslt = usrp_shibie_v10.play(self.freqPointList, self.path, self.harmonicNum)
            endtime = datetime.datetime.now()
            strTime = '识别线程花费:%dms' % (
                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
            logger.debug(strTime)
            while snrQ.empty():
                pass
            strTime = 'SNR线程花费:%dms' % (
                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
            logger.debug(strTime)
            IQSNRResult = snrQ.get()
            rslt.append("%.2f" % IQSNRResult)
            self.q.put(rslt)
        # 在线识别时，能够得到频谱数据
        else:
            # IQSNR算法开启
            snrQ = queue.Queue()
            snrThread = SNREstimationIntegrationThread(self.path, snrQ)
            snrThread.start()
            # SPECSNR算法开启
            specSNRQ = queue.Queue()
            specSNRThread = SpecSNREstimationIntegrationThread(self.spec1, self.spec2, specSNRQ)
            specSNRThread.start()
            # IQ识别算法开启
            rslt = usrp_shibie_v10.play(self.freqPointList, self.path, self.harmonicNum)
            endtime = datetime.datetime.now()
            strTime = '识别线程花费:%dms' % (
                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
            logger.debug(strTime)
            while snrQ.empty() or specSNRQ.empty():
                pass
            strTime = 'SNR线程花费:%dms' % (
                    (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
            logger.debug(strTime)
            IQSNRResult = snrQ.get()
            specSNRResult = specSNRQ.get()
            if type(specSNRResult) == type('str'):
                realSNR = IQSNRResult
                rslt.append("%.2f" % realSNR)
                rslt.append("IQSNR:%.2f, specSNR:不可识别" % IQSNRResult)
            else:
                realSNR = min(IQSNRResult, specSNRResult)
                rslt.append("%.2f" % realSNR)
                rslt.append("IQSNR:%.2f, specSNR:%.2f" % (IQSNRResult, specSNRResult))
            # rslt为一个长度为n的列表，倒数第一个元素表征两种算法信噪比值，倒二表征显示信噪比值
            self.q.put(rslt)

# IQ存储进程
class IQDataSaveProcess(Thread):
    def __init__(self, data, q):
        super(IQDataSaveProcess, self).__init__()
        currentPath = os.path.dirname(__file__)
        fatherPath = os.path.join(os.path.dirname(os.path.dirname(currentPath)), "data")
        dirPath = os.path.join(fatherPath, r'usrp_recvfiles')
        filesOrDirsOperate.makesureDirExist(dirPath)
        local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filePath = os.path.join(dirPath, r'single_collect_{}.txt'.format(local_time))
        self.path = filePath
        self.data = data
        self.q = q
    def run(self):
        # print('saving process start')
        # f = open(self.path, 'w')
        # f.write(self.data)
        # f.close()
        dataList = self.data.split(";")
        dataToWrite = "\n".join(dataList)
        with open(self.path, "w") as f:
            f.writelines(dataToWrite)
        self.q.put(self.path)

# 频谱包络在线识别进程（包括采集、识别、存储）
class specEnvelopeOnlineProcess(Thread):
    def __init__(self, usrpCommu, av3900Commu, msg, dataQ, algorithmProcessQ, savingProcessQ):
        super(specEnvelopeOnlineProcess, self).__init__()
        self.dataQ = dataQ
        self.algorithmProcessQ = algorithmProcessQ
        self.savingProcessQ = savingProcessQ
        self.usrpCommu = usrpCommu
        self.av3900Commu = av3900Commu
        self.msg = msg
        self.zmqQ = queue.Queue()

    # 包络识别
    def recognize(self, data):
        starttime = datetime.datetime.now()
        rslt = specEnvelope_shibie_v3.baoluoshibie(data)
        endtime = datetime.datetime.now()
        strTime = '识别线程耗时:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        # print(strTime)
        self.algorithmProcessQ.put(rslt)

    # 数据存储
    def save(self, data):
        starttime = datetime.datetime.now()
        currentPath = os.path.dirname(__file__)
        fatherPath = os.path.join(os.path.dirname(os.path.dirname(currentPath)), "data")
        dirPath = os.path.join(fatherPath, r'specEnvelope_recvfiles')
        filesOrDirsOperate.makesureDirExist(dirPath)
        local_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filePath = os.path.join(dirPath, r'specEnvelope_data_{}.txt'.format(local_time))
        # print('存储文件名为:', filePath)
        f = open(filePath, 'w')
        f.write(data[0])
        f.write('\n')
        f.write(data[1])
        f.close()
        endtime = datetime.datetime.now()
        strTime = '存储线程耗时:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        # print(strTime)
        self.savingProcessQ.put(filePath)

    def run(self):
        communicationThread = communicationProxy.CommunicationProxy(self.msg, self.zmqQ, self.usrpCommu,
                                                                    self.av3900Commu)
        communicationThread.start()
        while self.zmqQ.empty():
            pass
        else:
            reslt = self.zmqQ.get()
            # print("reslt", reslt)
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
        # print('thread')
        starttime = datetime.datetime.now()
        rslt = specEnvelope_shibie_v3.baoluoshibie(self.path)
        endtime = datetime.datetime.now()
        strTime = '识别线程耗时:%dms' % (
                (endtime - starttime).seconds * 1000 + (endtime - starttime).microseconds / 1000)
        # print(strTime)
        self.q.put(rslt)

# 脉冲在线识别线程
class PulseRecognizeOnlineProcess(Thread):
    def __init__(self, path, q, length, dataRootPath):
        super(PulseRecognizeOnlineProcess, self).__init__()
        self.path = path
        self.q = q
        self.length = length
        self.dataRootPath = dataRootPath
    def run(self):
        reslt, targetFile = pico_jicheng_online_v3.configuration(self.path, self.length, self.dataRootPath)
        self.q.put(reslt)
        self.q.put(targetFile)

# 脉冲离线识别线程
class PulseRecognizeOfflineProcess(Thread):
    def __init__(self, path, q, length, dataRootPath):
        super(PulseRecognizeOfflineProcess, self).__init__()
        self.path = path
        self.q = q
        self.length = length
        self.dataRootPath = dataRootPath
    def run(self):
        reslt= pico_jicheng_offline_v3.configuration(self.path, self.length, self.dataRootPath)
        # print("pulse recognize reslt:", reslt)
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
        reslt = steadyStateInterference_shibie_v3.position(self.x,
                                                           self.y,
                                                           self.standardValue,
                                                           self.outputPath)
        self.q.put(reslt)

# 干扰对消调用线程
class interferenceCancellationProcess(Thread):
    def __init__(self, q, arg):
        super(interferenceCancellationProcess, self).__init__()
        self.arg = arg
        self.q = q

    def run(self):
        targetx, targety = interferenceCancellationCalling.callInterferenceCancellation(self.arg)
        self.q.put([targetx, targety])

# IQ信噪比分析线程
class SNREstimationIntegrationThread(Thread):
    def __init__(self, arg, q):
        super(SNREstimationIntegrationThread, self).__init__()
        self.q = q
        self.arg = arg

    def run(self):
        data = dataGet.dataGet(self.arg)
        result = snr_estimation_integration.snr_estimation(data)
        self.q.put(result)

# 频谱信噪比分析线程
class SpecSNREstimationIntegrationThread(Thread):
    def __init__(self, arg1, arg2, q):
        super(SpecSNREstimationIntegrationThread, self).__init__()
        self.q = q
        self.arg1 = arg1
        self.arg2 = arg2

    def run(self):
        data1 = dataGet_spectrum.dataGet(self.arg1)
        data2 = dataGet_spectrum.dataGet(self.arg2)
        result = snr_spectrum.snr_estimation_spectrum(data1, data2)
        self.q.put(result)

# 信噪比数据存储
class SNRDataSave(Thread):
    def __init__(self, data, dirPath, prefix, q):
        super(SNRDataSave, self).__init__()
        self.q = q
        self.data = data
        self.dirPath = dirPath
        self.prefix = prefix
    def run(self):
        dataList = self.data.split(";")
        dataToSave = "\n".join(dataList)
        savePath = dataSave.dataSave(dataToSave, self.dirPath, "txt", self.prefix)
        self.q.put(savePath)

# 加噪声
class NoiseAdd(Thread):
    def __init__(self, data, original_snr, target_snr, q):
        super(NoiseAdd, self).__init__()
        self.data = data
        self.original_snr = original_snr
        self.target_snr = target_snr
        self.q = q
    def run(self):
        # self.data = dataGet.dataGet(self.data)
        data_noise_added = snr_estimation_integration.add_noise(self.data, self.original_snr, self.target_snr)
        self.q.put(data_noise_added)