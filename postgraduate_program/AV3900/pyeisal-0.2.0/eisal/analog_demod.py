from _eisal_cffi import ffi, lib
from .common import *
import math
from .frequency_domain import SegmentData

def _calcTunerSampleRate(analyseBw):
        sampleRate = 28e6
        while analyseBw * 1.4 < sampleRate / 2:
            sampleRate /= 2
            if(sampleRate < 1e6):
                break
        return sampleRate

def _calcDDCSampleRate(input, maxSampleRate):
    sampleRateInput = input * 2.56
    sampleRateToSet = maxSampleRate
    while sampleRateToSet / 2 > sampleRateInput or math.fabs(sampleRateToSet / 2 - sampleRateInput) < 100:
	    sampleRateToSet /= 2
	    if(sampleRateToSet < 10e3):
		    sampleRateToSet = 6835.9375
		    break
    return sampleRateToSet

class DemodResultHeader(object):
    def __init__(self, c_header):
        self.sequenceNumber = c_header.sequenceNumber
        self.numSamples = c_header.numSamples
        self.timestampSeconds = c_header.timestampSeconds
        self.timestampNSeconds = c_header.timestampNSeconds
        self.location = Location.from_c_location(c_header.location)
        self.attenuation = c_header.attenuation
        self.centerFrequency = c_header.centerFrequency
        self.sampleRate = c_header.sampleRate

class AnalogDemodulator(object):
    def __init__(self, sensorHandle):
        'sensorHandle 由connection传入的连接句柄'
        self._sensorHandle = sensorHandle
        self._measHandle = 0
        self._tunerParms = ffi.new("salTunerParms*")
        self._demodParam = ffi.new("salDemodParms*")
        self._resultHeader = ffi.new('salDemodData*')
        self._buffer = ffi.new('salInt32[]', 1024)
        self._bufferSize = 1024 * 4 #每次固定回传1024个样点
        self._pcmBlock = [int(0)] * 1024
        
    def config(self, center, analyseBw, gainSwitch = False, attenuation = 0):
        '配置解调参数'
        self._tunerParms.centerFrequency = center
        self._tunerParms.sampleRate = _calcTunerSampleRate(analyseBw)
        self._tunerParms.preamp = gainSwitch
        self._tunerParms.attenuation = attenuation
        self._demodParam.demodulation = 2
        self._demodParam.tunerCenterFrequency = center
        self._demodParam.tunerSampleRate = self._tunerParms.sampleRate
        self._demodParam.demodCenterFrequency = center
        self._demodParam.demodSampleRate = _calcDDCSampleRate(120e3, self._tunerParms.sampleRate)
    
    @property
    def audioSampleRate(self):
        '音频采样率，单位Hz'
        demodSampleRate = self._demodParam.demodSampleRate
        if (demodSampleRate > 54687):
            return 10937
        elif (demodSampleRate > 27343):
            return 27343
        elif (demodSampleRate > 13671):
            return 13671
        else:
            return 6835

    def start(self):
        '启动解调'
        self.reset()
        err = lib.salSetTuner(self._sensorHandle, self._tunerParms)
        if err != lib.SAL_ERR_NONE:
            print("salSetTuner failed")
            return False
        c_measHandle = ffi.new('salHandle*', 0)
        err = lib.salRequestDemodData(c_measHandle, self._sensorHandle, self._demodParam)
        if err != lib.SAL_ERR_NONE:
            print("salRequestDemodData failed")
            return False
        self._measHandle = c_measHandle[0]
        return True

    def changeTuner(self, center, bw):
        '改变解调频道，center解调频点, bw解调带宽'
        if self._measHandle == 0:
            raise IOError("解调尚未启动")
        ddcSampleRate = _calcDDCSampleRate(bw, self._tunerParms.sampleRate)
        err = lib.salChangeDemodChannel(self._measHandle, center, ddcSampleRate)
        return err == lib.SAL_ERR_NONE

    def __iter__(self):
        return self

    def __next__(self):
        if self._measHandle == 0:
            raise IOError("解调尚未启动")
        err = lib.salGetDemodData(self._measHandle, self._resultHeader, self._buffer, self._bufferSize)
        if(err != lib.SAL_ERR_NONE):
            print("error = %d" % err)
            raise StopIteration
        for i in range(len(self._pcmBlock)):
            self._pcmBlock[i] = self._buffer[i] >> 16
        header = DemodResultHeader(self._resultHeader)
        return header, self._pcmBlock

    def abort(self):
        '向设备发送终止解调的指令，稍后迭代会退出'
        if(self._measHandle != 0):
            lib.salSendDemodCommand(self._measHandle, 1)
    
    def reset(self):
        '关闭测量句柄，释放连接资源'
        if self._measHandle != 0:
            lib.salClose(self._measHandle)
            self._measHandle = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()

    def __del__(self):
        self.reset()

class AnalogDemodulatorSpectrumScaner(object):
    '伴随解调的频谱扫描，用于在解调的同时获取频谱数据'
    def __init__(self, demodulator):
        self._demodulator = demodulator
        self._sensorHandle = demodulator._sensorHandle
        self._measHandle = 0
        self._initSpectrumParms()
        self._resultHeader = ffi.new('salSegmentData*')
        self._bufferSize = self._segment.numFftPoints * 4 #每个频点幅度为float型，占4字节
        self._buffer = ffi.new('salFloat32[]', self._segment.numFftPoints)
        self._spectrum = [0] * self._segment.numFftPoints

    def _initSpectrumParms(self):
        self._segment = ffi.new('salFrequencySegment*')
        self._segment.centerFrequency = self._demodulator._tunerParms.centerFrequency
        self._segment.sampleRate      = self._demodulator._tunerParms.sampleRate
        self._segment.numFftPoints    = 2048       
        self._segment.averageType     = 1 #rms    
        self._segment.numAverages     = 8
        self._segment.overlapMode     = 1
        self._segment.numPoints       = int(float(self._segment.numFftPoints) / 1.4)      
        self._segment.firstPoint      = (self._segment.numFftPoints - self._segment.numPoints) // 2    
        self._segment.noTunerChange   = True # demod requires no turner change
    
    @property
    def center(self):
        '频谱中心频率'
        return self._demodulator._tunerParms.centerFrequency

    @property
    def span(self):
        '频谱带宽 一般等于解调器的分析带宽'
        return self._demodulator._tunerParms.sampleRate / 1.4

    @property
    def points(self):
        '频谱的总点数'
        return self._segment.numPoints

    def start(self):
        c_measHandle = ffi.new('salHandle*', 0)
        c_sweepParams = ffi.new('salSweepParms*')
        c_sweepParams.sweepInterval = 500
        c_sweepParams.numSegments = 1 #only one segment
        err = lib.salStartSweep(c_measHandle, self._sensorHandle, c_sweepParams, self._segment, ffi.cast('SAL_SEGMENT_CALLBACK', 0))
        if err == lib.SAL_ERR_NONE:
            self._measHandle = c_measHandle[0]
        return err == lib.SAL_ERR_NONE

    def abort(self):
        '终止本次扫描'
        if(self._measHandle != 0):
            lib.salSendSweepCommand(self._measHandle, 1)
    
    def reset(self):
        if self._measHandle != 0:
            lib.salClose(self._measHandle)
            self._measHandle = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._measHandle == 0:
            raise IOError("频谱扫描尚未启动")
        err = lib.salGetSegmentData(self._measHandle, self._resultHeader, self._buffer, self._bufferSize)
        if(err != lib.SAL_ERR_NONE):
            raise StopIteration
        
        self._spectrum[:] = self._buffer[0:self._resultHeader.numPoints]
        header = SegmentData.from_c_segmentData(self._resultHeader)
        return header, self._spectrum

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()

    def __del__(self):
        self.reset()

        
__all__ = ['DemodResultHeader', 'AnalogDemodulator', 'AnalogDemodulatorSpectrumScaner']