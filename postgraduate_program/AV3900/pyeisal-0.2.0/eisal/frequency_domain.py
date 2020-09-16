import time

from enum import Enum, IntEnum, auto

from _eisal_cffi import ffi, lib

from .common import *

class AverageType(IntEnum):
    Average_off     = 0  # No averaging
    Average_rms     = 1  # RMS averaging
    Average_peak    = 2  # Peak-hold averaging */
    Average_unknown = 3

class OverlapType(IntEnum):
    Overlap_on  = 0   # Use overlap averaging. Note that enum value = 0 for backward comapatability
    Overlap_off = 1   # Do not use overlap averaging 

class WindowType(IntEnum):
    Window_hann     = 0   #/**< Hann/Hanning window ( conversion from RBW to FFT bin spacing: 1.5 ) */
    Window_gaussTop = 1   #/**< Gausstop window ( conversion from RBW to FFT bin spacing: 2.215349684 ) */
    Window_flatTop  = 2   #/**< Flattop window  ( conversion from RBW to FFT bin spacing: 3.822108760 ) */
    Window_uniform  = 3   #/**< Uniform window  ( conversion from RBW to FFT bin spacing: 1.0 ) */
    Window_unknown  = 4

class FrequencySegment:
    def __init__(self,
                 antenna = AntennaType.Antenna_1,
                 preamp  = 0,
                 numFftPoints = 0,
                 averageType = AverageType.Average_off,
                 numAverages = 0,
                 firstPoint = 0,
                 numPoints = 0,
                 attenuation = 0.0,
                 centerFrequency = 0.0,
                 sampleRate = 0.0,
                 overlapMode = OverlapType.Overlap_on,
                 noTunerChange = 0, 
                 levelTrigger = LevelTrigger()):
        self.antenna         = antenna
        self.preamp          = preamp
        self.numFftPoints    = numFftPoints         
        self.averageType     = averageType              
        self.numAverages     = numAverages
        self.firstPoint      = firstPoint        
        self.numPoints       = numPoints        
        self.attenuation     = attenuation           
        self.centerFrequency = centerFrequency         
        self.sampleRate      = sampleRate         
        self.overlapMode     = overlapMode
        self.noTunerChange   = noTunerChange
        self.levelTrigger    = levelTrigger

    @classmethod
    def from_c_frequencySegment(cls, c_frequencySegment):
        return cls(
            antenna         = AntennaType(c_frequencySegment.antenna),
            preamp          = c_frequencySegment.preamp,
            numFftPoints    = c_frequencySegment.numFftPoints,         
            averageType     = AverageType(c_frequencySegment.averageType),           
            numAverages     = c_frequencySegment.numAverages,
            firstPoint      = c_frequencySegment.firstPoint,        
            numPoints       = c_frequencySegment.numPoints,        
            attenuation     = c_frequencySegment.attenuation,           
            centerFrequency = c_frequencySegment.centerFrequency,         
            sampleRate      = c_frequencySegment.sampleRate,         
            overlapMode     = OverlapType(c_frequencySegment.overlapMode),
            noTunerChange   = c_frequencySegment.noTunerChange,
            levelTrigger    = LevelTrigger.from_trigger_control(c_frequencySegment.levelTriggerControl))
    
def _to_c_frequencySegment(frequencySegment):
    c_frequencySegment = ffi.new("salFrequencySegment*")
    c_frequencySegment.antenna         = int(frequencySegment.antenna)
    c_frequencySegment.preamp          = frequencySegment.preamp
    c_frequencySegment.numFftPoints    = frequencySegment.numFftPoints         
    c_frequencySegment.averageType     = int(frequencySegment.averageType)            
    c_frequencySegment.numAverages     = frequencySegment.numAverages
    c_frequencySegment.firstPoint      = frequencySegment.firstPoint        
    c_frequencySegment.numPoints       = frequencySegment.numPoints        
    c_frequencySegment.attenuation     = frequencySegment.attenuation           
    c_frequencySegment.centerFrequency = frequencySegment.centerFrequency         
    c_frequencySegment.sampleRate      = frequencySegment.sampleRate         
    c_frequencySegment.overlapMode     = int(frequencySegment.overlapMode)
    c_frequencySegment.noTunerChange   = frequencySegment.noTunerChange
    c_frequencySegment.levelTriggerControl = frequencySegment.levelTrigger.level_trigger_control()
    return c_frequencySegment

class SweepParms:
    def __init__(self,
                 numSweeps = 0,   
                 window = WindowType.Window_hann,
                 syncSweepEnable = 0,
                 sweepInterval = 0,  
                 syncSweepSec = 0,   
                 syncSweepNSec = 0):
        self.numSweeps        = numSweeps      # Number of sweeps to perform; 0 means sweep until a stop command is sent */
        self.window           = window         # Window applied to time record before performing FFT  */
        self.syncSweepEnable  = syncSweepEnable# Set to non-zero when performing synchronous sweeps. */
        self.sweepInterval    = sweepInterval  # Interval between time-triggers for the start of each segment (synchrounous sweep only). */
        self.syncSweepSec     = syncSweepSec   # "sec" start time for first segment (synchronous sweep only). */
        self.syncSweepNSec    = syncSweepNSec  # "nsec" start time for first segment (synchronous sweep only). */

def __to_c_sweepParms(sweepParms):
    c_sweepParams = ffi.new('salSweepParms*')
    c_sweepParams.numSweeps       = sweepParms.numSweeps
    c_sweepParams.window          = int(sweepParms.window)
    c_sweepParams.syncSweepEnable = sweepParms.syncSweepEnable
    c_sweepParams.sweepInterval   = sweepParms.sweepInterval
    c_sweepParams.syncSweepSec    = sweepParms.syncSweepSec
    c_sweepParams.syncSweepNSec   = sweepParms.syncSweepNSec
    return c_sweepParams

class SweepComputationResults:
    def __init__(self,
                 stepFreq,                     #/**< Computed desired FFT bin size (converted from rbw and window) */
	             fftBinSize,                   #/**< Actual FFT bin size (some power of 2) */
	             actualRbw,                    #/**< Actual RBW (related to fftBinSize by window type) */
	             tunerSampleRate,              #/**< Actual tuner sample rate (Hz) */
                 fftBlockSize,	               #/**< FFT size */				
	             nyquistFactor,                #/**< Either 1.4 or 1.28 depending on tunerSampleRate */
                 numBinsReturned,              #/**< Number of FFT bins returned in each segment */
                 numBinsReturnedLastSegment,   #/**< Number of FFT bins returned in the last segment */
                 firstPointIdx,                #/**< Index of first FFT bin returned */
                 firstPointIdxLastSegment,     #/**< Index of first FFT bin returned in the last segment */
                 numSegments,                  #/**< Number of FFT segments to cover the span */
	             centerFrequencyFirstSegment,  #/**< Center frequency of the first segment */
	             centerFrequencyLastSegment):  #/**< Center frequency of the last segment */):

        self.stepFreq =                     stepFreq				            			
        self.fftBinSize = 				    fftBinSize				
        self.actualRbw = 				   	actualRbw				
        self.tunerSampleRate = 			    tunerSampleRate			
        self.fftBlockSize = 			    fftBlockSize			
        self.nyquistFactor = 		       	nyquistFactor				
        self.numBinsReturned = 			    numBinsReturned			
        self.numBinsReturnedLastSegment =   numBinsReturnedLastSegment
        self.firstPointIdx =                firstPointIdx			
        self.firstPointIdxLastSegment =     firstPointIdxLastSegment
        self.numSegments = 				    numSegments				
        self.centerFrequencyFirstSegment =  centerFrequencyFirstSegment
        self.centerFrequencyLastSegment =   centerFrequencyLastSegment

class SweepComputationParms:
    def __init__(self, startFrequency, stopFrequency, rbw):
        self.startFrequency =  startFrequency  #/**< Start frequency for the sweep (Hz) */
        self.stopFrequency  =  stopFrequency   #/**< Stop frequency for the sweep (Hz) */
        self.rbw            =  rbw             #/**< Resolution band-width (Hz) */

class SegmentData:
    def __init__(self,
                 segmentIndex = 0,  
                 sequenceNumber = 0,
                 sweepIndex = 0,   
                 timestampSec = 0,  
                 timestampNSec = 0, 
                 location = None, 
                 startFrequency = 0.0,
                 frequencyStep = 0.0,
                 numPoints = 0,     
                 lastSegment = 0,   
                 timeAlarms = 0):
        self.segmentIndex   = segmentIndex    #/**< 0-based index of this segment in the segmentTable  */
        self.sequenceNumber = sequenceNumber  #/**< starts at 0; incremented by 1 for each frequency result  */
        self.sweepIndex     = sweepIndex      #/**< starts at 0; incremented by 1 at the end of a sweep */

        self.timestampSec   = timestampSec    #/**< Integer seconds part of timestamp of first time point in this segment */
        self.timestampNSec  = timestampNSec   #/**< Fractional seconds part of timestamp of first time point in this segment */
        self.location       = location        #/**< Sensor location when this segment was measured */

        self.startFrequency = startFrequency  #/**< Frequency of first point returned by this measurement */ 
        self.frequencyStep  = frequencyStep   #/**< Frequency spacing in Hertz of frequency data */
        self.numPoints      = numPoints       #/**< Number of frequency points returned by this measurement */
        self.lastSegment    = lastSegment     #/**< If not zero, this is the last segment before measurement stops */

        self.timeAlarms     = timeAlarms      #/**< Indicates status of sensor time sycnh (bit map of ::salTimeAlarm values) */

    @classmethod
    def from_c_segmentData(cls, c_segmentData):
        return cls(
            segmentIndex   = c_segmentData.segmentIndex,   
            sequenceNumber = c_segmentData.sequenceNumber, 
            sweepIndex     = c_segmentData.sweepIndex,    
            timestampSec   = c_segmentData.timestampSec,  
            timestampNSec  = c_segmentData.timestampNSec,    
            location       = Location.from_c_location(c_segmentData.location),
            startFrequency = c_segmentData.startFrequency,
            frequencyStep  = c_segmentData.frequencyStep, 
            numPoints      = c_segmentData.numPoints,     
            lastSegment    = c_segmentData.lastSegment,
            timeAlarms     = c_segmentData.timeAlarms)


def InitializeFftSegmentTable(computationParms, 
                              sweepParms = SweepParms(), 
                              exampleSegment = FrequencySegment()):
        
    c_computationParms = ffi.new('salSweepComputationParms*')
    c_computationParms.startFrequency = computationParms.startFrequency
    c_computationParms.stopFrequency = computationParms.stopFrequency
    c_computationParms.rbw = computationParms.rbw

    c_sweepParams = ffi.new('salSweepParms*')
    c_sweepParams.window = int(sweepParms.window)

    c_sweepComputationResults = ffi.new('salSweepComputationResults*')
    err = lib.salComputeFftSegmentTableSize(c_computationParms, c_sweepParams, c_sweepComputationResults)
    if(err != lib.SAL_ERR_NONE):
        raise ValueError("salComputeFftSegmentTableSize", err)

    numSegments = c_sweepParams.numSegments
    assert(numSegments == c_sweepComputationResults.numSegments)
    c_segmentTable = ffi.new('salFrequencySegment[]', numSegments)

    c_exampleSegments = _to_c_frequencySegment(exampleSegment)
    err = lib.salInitializeFftSegmentTable(c_computationParms, c_sweepParams, c_exampleSegments, c_segmentTable, c_sweepComputationResults)
    if(err != lib.SAL_ERR_NONE):
        raise ValueError("salInitializeFftSegmentTable error", err)
    return c_segmentTable

class SpectrumBase(object):
    '''频谱扫描基类'''
    def __init__(self, sensorHandle):
        '构造时传入由eisal.Connection()返回的传感器连接句柄'
        self._sensorHandle = sensorHandle
        self._measHandle = 0
    
    @property    
    def startFrequency(self):
        firstSeg = self._segmentTable[0]
        step = firstSeg.sampleRate / firstSeg.numFftPoints
        return firstSeg.centerFrequency - step * (firstSeg.numFftPoints / 2 - firstSeg.firstPoint) + step / 2

    @property
    def stopFrequency(self):
        lastSeg = self._segmentTable[len(self._segmentTable) - 1]
        step = lastSeg.sampleRate / lastSeg.numFftPoints
        return lastSeg.centerFrequency + step * (lastSeg.numPoints / 2)

    @property
    def totalPoints(self):
        return self._totalPoints

    @property
    def totalSegments(self):
        return len(self._segmentTable)
    
    def _config(self, **kwargs):
        """配置扫描参数
        start/stop 20MHz-6/18/26.5/40GHz
        stop > start
        att 衰减 0-30dB
        gain True前放开 False前放关
        avg 平均次数 0-64
        """
        computationParms = SweepComputationParms(kwargs["start"], kwargs["stop"], kwargs["rbw"])
        exampleSegment = FrequencySegment()
        exampleSegment.antenna = AntennaType.Antenna_1
        exampleSegment.overlapMode = OverlapType.Overlap_off
        exampleSegment.attenuation = kwargs["att"]
        exampleSegment.preamp = kwargs["gain"]
        if kwargs["avg"] != 0:
            exampleSegment.averageType = AverageType.Average_rms
            exampleSegment.averaging = avg
        else:
            exampleSegment.averageType = AverageType.Average_off
        self._segmentTable = InitializeFftSegmentTable(computationParms, SweepParms(), exampleSegment)
        self._totalPoints = 0
        for seg in self._segmentTable:
           self._totalPoints += seg.numPoints

class SpectrumSnapshot(SpectrumBase):
    '频谱快照：只采集一次的频谱类'
    def __init__(self, sensorHandle):
        super().__init__(sensorHandle)
        
    def gene(self, start = 88e6, stop = 108e6, rbw = 10e3, **kwargs):
        "根据起始、终止、分辨率等参数启动扫描，并获取扫描结果"
        param = {'start':start, 'stop':stop, 'rbw':rbw, 'avg':0, 'gain':False, 'att':0}
        for k in kwargs: param[k] = kwargs[k]
        self._config(**param)    #配置扫描参数
        sweepParams = ffi.new('salSweepParms*')
        sweepParams.numSweeps = 1 #只采一次
        sweepParams.numSegments = len(self._segmentTable)
        measHandle = ffi.new('salHandle*', 0)
        #启动扫描
        err = lib.salStartSweep(measHandle, self._sensorHandle, sweepParams, self._segmentTable, ffi.cast('SAL_SEGMENT_CALLBACK', 0))
        if err != lib.SAL_ERR_NONE:
            raise IOError("start spectrum sweep error")
        self._measHandle = measHandle[0]
        resultHeader = ffi.new('salSegmentData*')
        amplitudeBuffer = ffi.new('salFloat32[]', self._segmentTable[0].numFftPoints)
        bufferSize = self._segmentTable[0].numFftPoints * 4 #每个频点幅度为float型，占4字节       
        try:
            spectrum = []
            for i in range(len(self._segmentTable)): #获取每个frequency segment的频谱
                err = lib.salGetSegmentData(self._measHandle, resultHeader, amplitudeBuffer, bufferSize)
                if(err != lib.SAL_ERR_NONE):
                    raise IOError("get result error")
                spectrum.extend(amplitudeBuffer[0:resultHeader.numPoints])
        except IOError as ioe:
            print(ioe)
            lib.salClose(self._measHandle)
        else:
            lib.salClose(self._measHandle)
            header = SegmentData.from_c_segmentData(resultHeader)
            return header, spectrum
        
class SpectrumScaner(SpectrumBase):
    '连续扫描的频谱类，可作为迭代器使用'
    def __init__(self, sensorHandle):
        super().__init__(sensorHandle)

    def config(self, start, stop, rbw, avg = 0, gainSwitch = False, attenuation = 0):
        '''通过起始终止频率和分辨率计算频段参数
        频段参数默认使用天线1，平均次数0次，增益0dB, 衰减0dB'''
        param = {'start':start, 'stop':stop, 'rbw':rbw, 'avg':avg, 'gain':gainSwitch, 'att':attenuation}
        super()._config(**param)

    def start(self, sweepCount = 0, sweepInterval = 100):
        '启动扫描，扫描次数默认为0，为无限次，扫描间隔默认100 ms'
        self.reset()    #清理上次的连接
        c_sweepParams = ffi.new('salSweepParms*')
        c_sweepParams.numSweeps = sweepCount
        c_sweepParams.numSegments = len(self._segmentTable)
        c_sweepParams.sweepInterval = sweepInterval
        c_measHandle = ffi.new('salHandle*', 0)
        err = lib.salStartSweep(c_measHandle, self._sensorHandle, c_sweepParams, self._segmentTable, ffi.cast('SAL_SEGMENT_CALLBACK', 0))
        if err == lib.SAL_ERR_NONE:
            self._measHandle = c_measHandle[0]
            self._resultHeader = ffi.new('salSegmentData*')
            self._bufferSize = self._segmentTable[0].numFftPoints * 4 #每个频点幅度为float型，占4字节
            self._amplitudeBuffer = ffi.new('salFloat32[]', self._segmentTable[0].numFftPoints)
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
            raise IOError("扫描尚未启动")
        if self._resultHeader.lastSegment != 0: #该字段非0意味着结束扫描
            raise StopIteration
        spectrum = []
        for i in range(self.totalSegments):
            err = lib.salGetSegmentData(self._measHandle, self._resultHeader, self._amplitudeBuffer, self._bufferSize)
            if(err != lib.SAL_ERR_NONE):
                raise StopIteration
            spectrum.extend(self._amplitudeBuffer[0:self._resultHeader.numPoints])
        header = SegmentData.from_c_segmentData(self._resultHeader)
        return header, spectrum

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()

    def __del__(self):
        self.reset()

__all__ = ['SegmentData', 'SpectrumSnapshot', 'SpectrumScaner']