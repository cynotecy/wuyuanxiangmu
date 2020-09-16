#ifndef __EISALTIMEDATA_H
#define __EISALTIMEDATA_H
 
// Time domain functions

#ifdef __cplusplus
extern "C" {
#endif

#include "eiSal.h"

// The capabilities defined in this header file will only work on sensors with a server version
// greater than or equal to SAL_TIME_DATA_MIN_VERSION; use salGetServerVersion() to get the version.
#define SAL_TIME_DATA_MIN_VERSION 0x10002

 /** Specifies a demodulation type for time data.
 * \enum salDemodulation
 * \ingroup TimeData
 */
typedef enum _salDemodulation {
    salDemodulation_none = 0,	/**< No Demodulation */
    salDemodulation_AM   = 1,	/**< AM Demodulation */
    salDemodulation_FM   = 2,   /**< FM Demodulation */
	salDemodulation_CW   = 3,
} salDemodulation;

/** Parameters for a time data request
 * \ingroup TimeData
 **/
typedef struct _salAudioParms {
    salFloat64      sampleRate;    /**< Sample rate of returned audio */
    salInt32        squelchState;  /**< 0 = off, 1 = on */
    salFloat64      squelchLevel;  /**< Squelch level (SAL_MIN_SQUELCH to SAL_MAX_SQUELCH); if 0 SAL_MIN_SQUELCH will be used. */
} salAudioParms;

 /** Specifies the slope for IF Magnitude triggering.
 * \enum salTriggerSlope
 * \ingroup TimeData
 */
typedef enum _salTriggerSlope {
    salTrigger_Rising    = 0,  /**< rising edge trigger */
    salTrigger_Falling   = 1,  /**< falling edge trigger */
	salTrigger_Either    = 2   /**< trigger on either edge */
} salTriggerSlope;

/** Parameters for IF Magnitude triggering
 * To start the IQ measurement on an RF burst, set the ifMagTriggerEnable parameter to 1.
 *
 * If useLearnEnv is enabled, the userTriggerLevel is relative to the background environment. The trigger level (dBm) will be computed 
 * as environment (dBm) + userTriggerLevel (dB).
 * 
 * If userLearnEnv is disabled, the trigger level will be set to userTriggerLevel parameter (dBm). 
 *
 * The triggerHoldoff parameter can be used to adjust the trigger time. A positive value will move 
 * the trigger time forward (i.e. later time). A negative value will move the trigger time
 * back in time.
 * \ingroup TimeData
 **/
typedef struct _salIfMagTriggerParms {
	salUInt16       ifMagTriggerEnabled; /**< set to 1 to enable the IF magnitude trigger mechanism */
	salUInt16       useLearnEnv;         /**< set to 1 if using the learn environment as the trigger level */
	salTriggerSlope triggerSlope;        /**< controls slope of IF Magnitude trigger */
	salFloat32      userTriggerLevel;    /**< trigger level (dBm or dB, see useLearnEnv param) */
	salFloat64      ifSearchTimeout;     /**< maximum time to search (seconds) */
	salFloat64      triggerHoldoff;      /**< adjustment to the trigger time (sec) */
} salIfMagTriggerParms;


/** Parameters for IQ pacing
 * To enable pacing between IQ Cut, set the pacingEnabled to non-zero. No pacing is provided within the IQ Cut (see flowControl for that behavior).
 *
 * Specify the number of desired measurements in measCount. A value of 0 implies continuous measurements
 * 
 * Specify the period between measurements using the measIntervalSec and measIntervalNSec fields. 
 * The sensor will advance the trigger time for subsequent IQ Cuts by the specified period.
 * A period of 0.0 implies "as fast as possible". 
 *
 * \ingroup TimeData
 **/
typedef struct _salIqPacingParms {
	salUInt32       pacingEnabled;       /**< set to 1 to enable the IQ Pacing */
	salUInt32       measCount;           /**< number of IQ measurements desired, 0 == continuous */
	salUInt32       measIntervalSec;     /**< secs portion of measurement period */
	salUInt32       measIntervalNSec;    /**< nsecs portion of measurement period */
} salIqPacingParms;

/** Description of data returned by a time data measurement
 * \ingroup TimeData
 **/
typedef struct _salTimeData {
   salUInt64      sequenceNumber;              /**< starts at 0; incremented by 1 for each data block */
   salDataType    dataType;                    /**< Type of data (real or complex) and rewsolution (16 bit, 32 bit, etc) */
   salUInt32      numSamples;                  /**< Number of samples in this data block. A complex pair is considered 1 sample. */
   salFloat64     scaleToVolts;                /**< Multiply data samples by this value to convert to Volts.   */
   salStateEventMask stateEventIndicator;      /**< Mask of indicators for various conditions (see ::salSTATE_EVENT). */
   salUInt32      timestampSeconds;            /**< Integer part of the timestamp (in UTC seconds since January 1, 1970). */
   salUInt32      timestampNSeconds;   
   salLocation	  location;
   salAntennaType antenna;                     /**< Antenna input active for this data block. */
   salFloat64     attenuation;                 /**< Attenuation in dB; negative values indicate gain.  */
   salFloat64     centerFrequency;             /**< RF center frequency in Hertz for this data block. */
   salFloat64     sampleRate;                  /**< Sample rate in Hertz.  */
   salUInt32      timeAlarms;                  /**< Indicates status of sensor time sycn (bit map of ::salTimeAlarm values) */
} salTimeData;

/** IQ cut data callback function prototype.
 * \param iqData [out] IQ Header plus data.
 * \remarks This function is called in a separate thread than the one that called salRequestTimeData(). Calling
 *          SAL functions (other than salGetErrorString()) from the callback function can result in unpredictable behavior.
 * \ingroup TimeData
 **/
#ifdef MATLAB_LOADLIBRARY_COMPILE
// The Matlab loadlibrary.m mechanism does not support functions with callbacks
typedef void *SAL_TIME_DATA_CALLBACK;
#else
typedef int(*SAL_TIME_DATA_CALLBACK)(salTimeData *dataHdr, void *samples);
#endif

//yangqing modified this struct
typedef struct _salTimeDataParms {
	salFloat64      centerFrequency;     /**< The desired center frequency (in Hertz) of the time data. */
	salFloat64      sampleRate;          /**< The desired sample rate (in Hertz) of the time data.*/
	salUInt32       numTransferSamples;  /**< Number of samples to accumulate in sensor before sending over network; must be <= numSamples*/
	salUInt64       numSamples;          /**< Total number of samples to acquire. 0 means to capture until stopped. */
	salDataType		dataType;
} salTimeDataParms;

/** Request time data from the sensor
  * \param measHandle      [out] Unique smeasurement handle created by this request.
  * \param sensorHandle    [in] Unique sensor handle returned by salConnectSensor().
  * \param parms           [in] Parameters specifying the measurement request.
  * \param dataCallback    [in] Pointer to a function to handle returned data; NULL means user will poll for data.
  * \remarks
  *
  * \par 
  * Older versions of RF sensor firmware do not support the time data interface; if the sensor supports this interface,
  * the timeData parameter of ::salSensorCapabilities will be non-zero.
  *
  * \par
  * If dataCallback is not NULL, the data callback function will be called when there is new data available.
  * The data callback function will also be called when an error occurs (the error code is returned in the 
  * error field of the salTimeData structure). 
  * \par
  * If dataCallback is NULL, the user is responsible for getting the data by calling salGetTimeData(). 
  * \par
  * For best performance, you should read the returned data until the ::salSTATE_LAST_BLOCK of the ::stateEventIndicator
  * field is set. If you want to terminate data transfer, it is best use the :salSendTimeDataCommand() function to stop
  * or abort the data stream. If you want to terminate the data stream quickly, call ::salClose() with the measHandle
  * returned by salRequestTimeData().
  * \par
  * To free the resources (memory, socket connections, etc.) used by salRequestTimeData(), call salClose() with the
  * returned measHandle. If you are making multiple successive calls to salRequestTimeData(), however, you do not need 
  * to call salClose() after each call to salRequestTimeData().
  *
  * \return salErrorType error value
  * \deprecated use salRequestTimeData3()
  * \ingroup TimeData
  * \see salGetTimeData()  \n
  *           SAL_TIME_DATA_CALLBACK \n
  *           salSendTimeDataCommand() \n
  *           salGetSensorCapabilities() \n
  *           salClose()
  *
  *       
  */
SAL_API salRequestTimeData(
                     salHandle             *measHandle,
                     salSensorHandle       sensorHandle,
                     salTimeDataParms      *parms);

SAL_API salContinueAcquire(salHandle measHandle);

/** Request data from an IQ cut measurement when the dataCallback function in salRequestTimeData() was set to NULL.
 *  The userDataBuffer must be allocated by the calling application. Use the salRECOMMENDED_DATA_BUFFER_SIZE
 *  macro to allocate the maximum amount of space that will be needed. The calling application must also set
 *  userDataBufferBytes.
 * \param measHandle               [in]  Measurement handle from salRequestTimeData().
 * \param dataHdr                  [out] User allocated memory which will hold the salTimeData header.
 * \param userDataBuffer           [out] User allocated memory which will hold the data samples.
 * \param userDataBufferBytes      [in] The size in bytes of the memory pointed to by userDataBuffer.
 * \return salErrorType error value. The value will be SAL_ERR_NONE if there is data available,
 *  SAL_ERR_NO_DATA_AVAILABLE if there is no data available. Any other value indicates an
 *  unexpected error. 
 * \ingroup TimeData
 * \remarks If demodulated data is requested, the numTransferSamples must be at least ::SAL_MIN_AUDIO_SAMPLES.
 * \see salSetTuner()
 */
SAL_API salGetTimeData(
    salHandle             measHandle,
    salTimeData          *dataHdr,
    void                 *userDataBuffer,
    salUInt32            userDataBufferBytes);


/** Get information about an "time data" stream.
  * \param measHandle   [in]  Measurement handle from salRequestTimeData().
  * \param iqAttribute  [in] A value from the salIqAttribute enumeration.  This
                           value determines which stream characteristic will be returned.
  * \param value        [out] The returned value from the sensor.  This is a pointer to the correct
  *                       size memory for that attribute.  It is the user's responsibility to
  *                       pass the correct pointer and to have allocated the memory.
  * \return salErrorType error value
  * \ingroup MeasurementControl
  * \deprecated use Time Data interface instead (see salRequestTimeData())
  */
SAL_API salTimeDataGetAttribute(salHandle measHandle,
                               salIqAttribute iqAttribute, 
                               void *value);

/** Time data commands. 
* \enum salTimeDataCmd
 * \ingroup TimeData
 */
typedef enum _salTimeDataCmd {
    salTimeDataCmd_stop,         /**< Stop a time data request, but keep sends data acquired so far */
    salTimeDataCmd_abort         /**< Stop a time data request and discard any data not sent */
} salTimeDataCmd;


/** Send a command to stop or abort a time data request.
 * \param measHandle               [in]  Measurement handle from salRequestTimeData().
 * \param command                  [in] The command to send
 * \ingroup TimeData
 * \remarks
 * The salTimeDataCmd_stop tells the sensor to stop acquiring new data, but send any data that has been acquired
 * so far. The salTimeDataCmd_abort tells the sensor to stop sending data immediately. After sending either command,
 * queued data will still be delivered by SAL_TIME_DATA_CALLBACK or returned by calling salGetTimeData(). For best
 * performance, it is usually best to read all queued data until the until the ::salSTATE_LAST_BLOCK 
 * of the ::stateEventIndicator is set.
 * \return salErrorType error value. 
 * \see salGetTimeData()
 * 
 */
SAL_API salSendTimeDataCommand(
     salHandle      measHandle,
     salTimeDataCmd command);
     

/** Send a command to modify the center frequency of a time measurement.
 * \param measHandle               [in]  Measurement handle from salRequestTimeData().
 * \param centerFrequency          [in] The new center frequency.
  * \return salErrorType error value. 
 * \ingroup TimeData
 */
SAL_API salModifyTimeDataFrequency(
     salHandle  measHandle,
     salFloat64 centerFrequency);

#define SAL_MIN_SQUELCH -135.0 
#define SAL_MAX_SQUELCH -20.0 


/** Send a command to modify the squelch setting of a time measurement.
 * \param measHandle               [in]  Measurement handle from salRequestTimeData().
 * \param squelchState             [in] The new squelch state (0=off, 1=on)
 * \param squelchLevel             [in] The new squelch value (::SAL_MIN_SQUELCH to ::SAL_MAX_SQUELCH )
 * \ingroup TimeData
  * \return salErrorType error value. 
 * \remarks If the squelchState is on, the audio samples will be set to 0 if the RF signal power is less than squelchLevel dBm.
 */
SAL_API salModifyTimeDataSquelch(
     salHandle  measHandle,
     salInt32        squelchState,  
     salFloat64      squelchLevel);


/*********************************************************************************
 Tuner functions
 *********************************************************************************/


/** salTunerParms specifies parameters for the the sensor tuner (front-end).
 * \ingroup FrequencyData
  * Use the salGetSensorCapabilities() function to get the following capabilities of the sensor:
  * \remarks
  * \code 
  *     Parameter              Typical values (3900A sensor)
  *    maxSampleRate                28 MHz
  *    maxDecimations                15
  *    minFrequency                  20 MHz
  *    maxFrequency                  6 GHz
  * \endcode
  * The tuner sample rate can be set from maxSampleRate down to maxSampleRate/(2^maxDecimations) in steps of
  * 1/2. For the 3900A tuner, the valid sample rates are 28 MHz, 14 MHz, ..., 854 Hz. The sample rate
  * is rounded up to the next valid sample rate; for example, if you request a sample rate of 10 MHz, the 
  * sensor will round this up to 14 MHz.
  *
  */
typedef struct _salTunerParms {
	salFloat64 centerFrequency;  /**< Tuner center frequency in Hertz */
	salFloat64 sampleRate;       /**< Tuner sample rate in Hertz */
	salFloat64 attenuation;      /**< Front end attenuation in dB (-10 to 30)*/
	salFloat64 mixerLevel;       /**< Mixer level in dB; range is -10 to 10 dB, 0 dB gives best compromise between SNR and distortion. */
	salAntennaType antenna;      /**< Front end input to use */
	salInt32 preamp;             /**< If non-zero, turn preamp on  */
    salInt32 sdramWriting;       /**< non-zero when the FPGA write process is filling capture memory */
} salTunerParms;

#define salTunerStatus salTunerParms /**< for backward compatability */


/** Set the sensor tuner and input parameters.
 * \param sensorHandle      [in] Unique sensor handle returned by salConnectSensor().
 * \param parmsIn           [in] Parameters for the tuner and input setup.
 * \ingroup TimeData
 * \return salErrorType error value. 
 * \remarks
 * This function allows setting a sensor tuner to a desired center frequency and span. It also
 * sets the input antenna port, attenuation, and mixer level. You may need to set the tuner before calling 
 * salRequestTimeData() or before requesting a geolocation measurement. For geolocation measurements,
 * the salSetTunerGroup() is more convenient.
 * \par
 * The valid measurement bandwith for the sensor is a function of the tuner sample rate, the maximum
 * valid span, and the antialias filter shape. To calculate the maximum measurement span for a given
 * tuner set, use the salGetSensorCapabilities() function to get the following capabilities of the sensor:
  *
  * \code 
  *       Parameter         Typical values (3900A sensor)
  *    maxSampleRate                 28 MHz
  *    sampleRateToSpanRatio         1.28
  *    maxDecimations                15
  *    maxSpan                       20 MHz   
  *    rfFifoBytes                   512*1024*1024
  * \endcode 
  * \par
  * sampleRate can be set from maxSampleRate/(2^maxDecimations) to maxSampleRate in multiples of two. For the N6831A, 
  * valid values of sampleRate are 28 MHz, 14 MHz, ... 854 Hz. 
  * Anti-alias filtering is applied to the input data. The maxumum valid span start and stop frequencies cand
  * be calculated as follows:
  *
  * \code
  *     if (tunerStatus.sampleRate==capabilities.maxSampleRate) 
  *         span = maxSpan
  *     else 
  *         span = tunerStatus.sampleRate / capabilities.sampleRateToSpanRatio
  *
  *     fMin = tuner.centerFrequency - span/2
  *     fMax = tuner.centerFrequency + span/2
  * \endcode
  * \par
  * The maximum amount of data in seconds that can be saved in the RF sensor FIFO is a function of the tuner sample rate and
  * the FIFO size. The time in seconds that can be buffered can be calculated as follows:
  *
  * \code
  *    // data in the FIFO is 2 byte complex
  *    bufferSeconds = capabilities.rfFifoBytes / tuner.sampleRate / 4
  * \endcode
  * \par
  * The Mixer Level control allows you to trade off between  distortion and signal-to-noise performance. 
  * Increasing Mixer Level increases signal-to-noise (SNR) and distortion. Decreasing Mixer Level decreases distortion and SNR.  
  * Mixer Level control is relative. 0 dB represents the best balance between distortion and SNR. 
  *
 * \see salSetTunerGroup()  \n
 *       salGetTuner() \n
 */
SAL_API salSetTuner(
     salSensorHandle   sensorHandle,
     salTunerParms    *parmsIn
     );



/** Get the tuner and input parameters.
 * \param sensorHandle      [in] Unique sensor handle returned by salConnectSensor().
 * \param tunerStatus          [out] The current tuner setup.
* \ingroup TimeData
* \return salErrorType error value. 
 */
SAL_API salGetTuner(
     salSensorHandle   sensorHandle,
     salTunerParms    *tunerStatus
     );

/** Set the tuner parameters on a group of sensors.
 * \param sensorGroupHandle [in] Handle to the group of sensors that this function will modify.
 * \param parmsIn           [in] The parameters to set.
 * \return salErrorType error value
 * \ingroup SystemManagement
 * \remarks  This function allows setting the tuners on a group of sensore to a desired center frequency and span. 
 * It also sets the input antenna port, attenuation, and mixer level. You may need to set the tuner before requesting a 
 * geolocation measurement. See salSetTuner() for information about tuner settings.
 *
 * \see salSetTuner() \n
 *           salGetTuner() \n
 *           salMeasureLocation2() \n
 *           salAcquireLocationData()
 */
SAL_API salSetTunerGroup(salHandle sensorGroupHandle, 
     salTunerParms    *parmsIn);

/** Retrieve the backlog status for this IQ stream
 * \param measHandle               [in]  Measurement handle from salRequestTimeData3().
 * \param backlogStatus            [out] Backlog information
 * \ingroup TimeData
 * \see salRequestTimeData3()
 */
SAL_API salGetIqBacklogStatus(
    salHandle             measHandle,
    salBacklogStatus      *backlogStatus);

//yangqing add some struct for demodulation only
typedef struct _salDemodParms {
	salFloat64		tunerCenterFrequency;
	salFloat64		tunerSampleRate;
	salFloat64      demodCenterFrequency;     
	salFloat64      demodSampleRate;
	salUInt64       numSamples;          /**< Total number of samples to acquire. 0 means to capture until stopped. */
	salDemodulation demodulation;        /**< Demodulation type */
} salDemodParms;

typedef struct _salDemodData {
   salUInt64      sequenceNumber;              /**< starts at 0; incremented by 1 for each data block */
   salUInt32      numSamples;                  /**< Number of samples in this data block. A complex pair is considered 1 sample. */
   salStateEventMask stateEventIndicator;      /**< Mask of indicators for various conditions (see ::salSTATE_EVENT). */
   salUInt32      timestampSeconds;            /**< Integer part of the timestamp (in UTC seconds since January 1, 1970). */
   salUInt32      timestampNSeconds;   
   salLocation    location;                    /**< Location of sensor when data was acquired */
   salAntennaType antenna;                     /**< Antenna input active for this data block. */
   salFloat64     attenuation;                 /**< Attenuation in dB; negative values indicate gain.  */
   salFloat64     centerFrequency;             /**< RF center frequency in Hertz for this data block. */
   salFloat64     sampleRate;                  /**< Sample rate in Hertz.  */
   salUInt32      timeAlarms;
} salDemodData;

typedef enum _salDemodCmd {
	salDemodCmd_stop,
	salDemodCmd_abort
} salDemodCmd;

//yangqing add this API for starting demodulation
SAL_API salRequestDemodData(
						   salHandle             *measHandle,
						   salSensorHandle       sensorHandle,
						   salDemodParms		*parms);

SAL_API salGetDemodData(salHandle measHandle, 
							   salDemodData *dataHdr, 
							   void *userDataBuffer, 
							   salUInt32 userDataBufferBytes);

SAL_API salSendDemodCommand(salHandle      measHandle,
							salDemodCmd command);

SAL_API salModifyDemodFrequency(salHandle measHandle, salFloat64 centerFrequency);
SAL_API salChangeDemodChannel(salHandle measHandle, salFloat64 channelFreq, salFloat64 demodSampleRate);

typedef struct _salIQSweepParms 
{
	salUInt32        numSweeps;          /**< 扫描次数，设为0为无限次扫描 */
	salUInt32        numSegments;        /**< 扫描频段个数，至少为1 */
	salUInt32		 numBlocks;			 /**< 每段采集的IQ块个数 */
	salUInt32		 numTransferSamples; /**< 每个块的IQ点数，32位IQ最大可设置为2048,16位IQ最大可设置为4096 */
	salDataType      dataType;           /**< 数据类型，16位或32位复数*/
	salInt32         timeTriggerFlag;    /**<  是否启用时间触发*/
	salUInt32		 sweepInterval;      /**< 每次扫描的时间间隔，单位毫秒，只在syncSweepEnable置一时有效*/
	salUInt32		 segmentInterval;	 /**< 每个段之间的时间间隔，单位毫秒， 只在syncSweepEnable置一时有效*/
	salUInt32        timeTriggerSec;     /**< 首次扫描的起始时刻（秒），只在syncSweepEnable置一时有效. */
	salUInt32        timeTriggerNSec;    /**< 首次扫描的起始时刻（纳秒），只在syncSweepEnable置一时有效. */
} salIQSweepParms;

typedef struct _salIQSegmentData 
{
	salUInt64		sequenceNumber;      /**< 顺序号 */
	salUInt32		segmentIndex;        /**< 频段索引  */
	salUInt32		sweepIndex;          /**< 扫描次数索引 */   
	salDataType		dataType;		     /**< 数据类型 */
	salUInt32		numSamples;			 /**< 采样点数 */
	salUInt32		shlBits;			 /**< 位偏移（16位IQ下有效） */
	salUInt32		timestampSeconds;    /**< 时间戳. */
	salUInt32		timestampNSeconds;
	salUInt32       timeAlarms;			 /**<GPS状态信息*/
	salFloat64      scaleToVolts;        /**< 电压比例尺.   */
	salFloat64		centerFrequency;     /**< 中心频率. */
	salFloat64		sampleRate;          /**< 采样率.  */
	salFloat64		latitude;            /**< 位置信息 */
	salFloat64		longitude;        
	salFloat64		elevation;        
}salIQSegmentData;

#define	TRIG_ABS_TIME (0x1 << 1)	//绝对时间
#define	TRIG_REL_TIME (0x2 << 1)	//相对时间
#define	TRIG_ABS_LEVEL (0x1 << 3)	//绝对幅度
#define	TRIG_RISING (0x2 << 3)		//上升沿
#define	TRIG_FALLING (0x3 << 3)	//下降沿

#ifdef MODEL_3900F
#define TRIG_FREQUENCY (0x2 << 4)  //频率触发
#endif

SAL_API salStartIQSweep(salHandle *measHandle, salSensorHandle sensorHandle, salIQSweepParms *parms, salFrequencySegment *pSegmentTable);
//获取IQ扫描数据
SAL_API salGetIQSweepData(salHandle measHandle, salIQSegmentData *dataHdr, void *userDataBuffer, salUInt32 userDataBufferBytes);
SAL_API salSendIQSweepCommand(salHandle measHandle, salTimeDataCmd command);
#ifdef __cplusplus
}
#endif

#endif /*__EISALTIMEDATA_H */
