from enum import Enum, IntEnum, auto

from _eisal_cffi import ffi, lib
from .common import *
from .frequency_domain import FrequencySegment, _to_c_frequencySegment

def calcSampleRate(bandwidth):
    sampleRate = 28e6
    while bandwidth * 1.4 < sampleRate / 2:
        sampleRate /= 2
        if(sampleRate < 10e3):
            break
    return sampleRate

class IQSweepParms:
    def __init__(self,
                 numSweeps = 0,
                 numSegments = 1,
                 numBlocks = 1,
                 numTransferSamples = 2048,
                 dataType = DataType.COMPLEX_32,
                 timeTriggerFlag = 0,
                 sweepInterval = 0,
                 segmentInterval = 0,
                 timeTriggerSec = 0,   
                 timeTriggerNSec = 0):
        self.numSweeps          = numSweeps           # Number of sweeps to perform; 0 means sweep until a stop command is sent */
        self.numSegments        = numSegments
        self.numBlocks          = numBlocks	          # Number of IQ blocks in a segment */
        self.numTransferSamples = numTransferSamples  # Number of samples in a block */
        self.dataType           = dataType            # Data type for returned 
        self.timeTriggerFlag    = timeTriggerFlag
        self.sweepInterval      = sweepInterval       # Interval between time-triggers for the start of each segment (synchrounous sweep only). */
        self.segmentInterval    = segmentInterval     #Interval between time-triggers for the start of each segment (synchrounous sweep only)(in msec unit). */
        self.timeTriggerSec       = timeTriggerSec        # "sec" start time for first segment (synchronous sweep only). */
        self.timeTriggerNSec      = timeTriggerNSec       # "nsec" start time for first segment (synchronous sweep only). */

def _to_c_iqsweepParms(iqSweepParms):
    c_iqSweepParams = ffi.new('salIQSweepParms*')
    c_iqSweepParams.numSweeps           =  iqSweepParms.numSweeps
    c_iqSweepParams.numSegments         =  iqSweepParms.numSegments       
    c_iqSweepParams.numBlocks           =  iqSweepParms.numBlocks          
    c_iqSweepParams.numTransferSamples  =  iqSweepParms.numTransferSamples
    c_iqSweepParams.dataType            =  int(iqSweepParms.dataType)           
    c_iqSweepParams.timeTriggerFlag     =  iqSweepParms.timeTriggerFlag   
    c_iqSweepParams.sweepInterval       =  iqSweepParms.sweepInterval     
    c_iqSweepParams.segmentInterval     =  iqSweepParms.segmentInterval    
    c_iqSweepParams.timeTriggerSec        =  iqSweepParms.timeTriggerSec      
    c_iqSweepParams.timeTriggerNSec       =  iqSweepParms.timeTriggerNSec     
    return c_iqSweepParams


class IQSegmentData:
    def __init__(self,
                 sequenceNumber = 0,  
                 segmentIndex = 0,     
                 sweepIndex = 0,       
                 dataType = 0,
                 numSamples = 0,
                 shlBits = 0,
                 timestampSeconds = 0, 
                 timestampNSeconds = 0,
                 timeAlarms = 0,
                 scaleToVolts = 0.0,     
                 centerFrequency = 0.0, 
                 sampleRate = 0.0,       
                 latitude  = 0.0,   
                 longitude = 0.0,       
                 elevation = 0.0):
        self.sequenceNumber    = sequenceNumber     # starts at 0; incremented by 1 for each data block */
        self.segmentIndex      = segmentIndex       # 0-based index of this segment in the segmentTable  */      
        self.sweepIndex        = sweepIndex         # starts at 0; incremented by 1 at the end of a sweep */       
        self.dataType          = dataType         
        self.numSamples        = numSamples        
        self.shlBits           = shlBits          
        self.timestampSeconds  = timestampSeconds         
        self.timestampNSeconds = timestampNSeconds        
        self.timeAlarms        = timeAlarms        
        self.scaleToVolts      = scaleToVolts       # Multiply data samples by this value to convert to Volts.   */      
        self.centerFrequency   = centerFrequency    # RF center frequency in Hertz for this data block. */      
        self.sampleRate        = sampleRate         # Sample rate in Hertz.  */      
        self.latitude          = latitude           # In fractional degrees, southern latitudes are negative numbers */      
        self.longitude         = longitude          # In fractional degrees, western longitudes are negative numbers */      
        self.elevation         = elevation          # In meters  */
    
    @classmethod
    def from_c_IQSegmentData(cls, c_iqSegmentData):
        return cls(
            sequenceNumber    = c_iqSegmentData.sequenceNumber,
            segmentIndex      = c_iqSegmentData.segmentIndex,
            sweepIndex        = c_iqSegmentData.sweepIndex,
            dataType          = DataType(c_iqSegmentData.dataType),
            numSamples        = c_iqSegmentData.numSamples,
            shlBits           = c_iqSegmentData.shlBits,
            timestampSeconds  = c_iqSegmentData.timestampSeconds ,
            timestampNSeconds = c_iqSegmentData.timestampNSeconds,
            timeAlarms        = c_iqSegmentData.timeAlarms,
            scaleToVolts      = c_iqSegmentData.scaleToVolts,
            centerFrequency   = c_iqSegmentData.centerFrequency,
            sampleRate        = c_iqSegmentData.sampleRate,
            latitude          = c_iqSegmentData.latitude,
            longitude         = c_iqSegmentData.longitude,
            elevation         = c_iqSegmentData.elevation)

class IQSnapshot(object):
    '''
    获取IQ数据的快照
    '''
    def __init__(self, sensorHandle):
        self._sensorHandle = sensorHandle

    def gene(self, center, span, **kwargs):
        #配置参数
        param = {'center':center, 'sampleRate':calcSampleRate(span), 'numSweeps':1, 
        'numBlocks':1, 'numTransferSamples':2048, 'gain':False, 'att':0}
        for k in kwargs: param[k] = kwargs[k]
        iqParam = IQSweepParms(numSweeps = param["numSweeps"], 
                                numTransferSamples = param["numTransferSamples"], 
                                numBlocks = param["numBlocks"])
        segParam = FrequencySegment(centerFrequency = param["center"], sampleRate = param["sampleRate"])
        #启动IQ采集
        try:
            measHandle = ffi.new('salHandle*', 0)
            c_iqParam = _to_c_iqsweepParms(iqParam)
            c_segParam = _to_c_frequencySegment(segParam)
        except Exception as e:
            print(e)
        err = lib.salStartIQSweep(measHandle, self._sensorHandle, c_iqParam, c_segParam)
        if err != lib.SAL_ERR_NONE:
            raise IOError("start IQ sweep error")
        self._measHandle = measHandle[0]
        c_header = ffi.new('salIQSegmentData*')
        c_amplitudeBuffer = ffi.new('salInt32[]', iqParam.numTransferSamples * 2)
        bufferSize = iqParam.numTransferSamples * 8 #每个IQ点包括I Q两个有符号整数，占8字节       
        try:
            IQ = []
            while(True):
                err = lib.salGetIQSweepData(self._measHandle, c_header, c_amplitudeBuffer, bufferSize)
                if(err != lib.SAL_ERR_NONE):
                    raise IOError("get result error")
                IQ.extend(c_amplitudeBuffer[0:iqParam.numTransferSamples * 2])
                if c_header.sweepIndex + 1 == iqParam.numSweeps:
                    break
        except IOError as ioe:
            print(ioe)
            lib.salClose(self._measHandle)
        else:
            lib.salClose(self._measHandle)
            header = IQSegmentData.from_c_IQSegmentData(c_header)
            return header, IQ
        
__all__ = ["IQSegmentData", "IQSnapshot"]