#ifndef __EISALFREQUENCY_H
#define __EISALFREQUENCY_H
  
// Frequency domain functions

#ifdef __cplusplus
extern "C" {
#endif

#include "EISAL.h"

// The capabilities defined in this header file will only work on sensors with a server version
// greater than or equal to SAL_TIME_DATA_MIN_VERSION; use salGetServerVersion() to get the version.
#define SAL_FREQ_DATA_MIN_VERSION 0x10002

#define SAL_FFT_POINTS_MIN 8
#define SAL_FFT_POINTS_MAX 16384

// recommended buffer size for FFT segment data
#define SAL_FFT_RECOMMENDED_BYTES (SAL_FFT_POINTS_MAX * sizeof(salFloat32))

/** FFT window type. 
* \enum salWindowType
 * \ingroup FrequencyData
 */
typedef enum _salWindowType {
    salWindow_hann,         /**< Hann/Hanning window ( conversion from RBW to FFT bin spacing: 1.5 ) */
    salWindow_gaussTop,     /**< Gausstop window ( conversion from RBW to FFT bin spacing: ENW 2.215349684 ) */
    salWindow_flatTop,      /**< Flattop window  ( conversion from RBW to FFT bin spacing: ENW 3.6250112 ) */
    salWindow_uniform,      /**< Uniform window  ( conversion from RBW to FFT bin spacing: 1.0 ) */
#ifdef MODEL_3900F
	salWindow_blackMan,             // new added window type (ENW 1.6249856)
	salWindow_custom1,
	salWindow_custom_EB500,
#endif
    salWindow_unknown,
} salWindowType;

/** Power spectrum average type. 
 * \enum salAverageType
 * \ingroup FrequencyData
 */
typedef enum _salAverageType {
    salAverage_off,         /**< No averaging */
    salAverage_rms,         /**< RMS averaging */
    salAverage_peak,        /**< Peak-hold averaging */
    salAverage_unknown
} salAverageType;

/** FFT internal data type type. 
 * \enum salFftDataType
 * \ingroup FrequencyData
 */
typedef enum _salFftDataType {
	salFftData_db,         /**<dBm data from sensor */
	salFftData_mag         /**<v^2 data from sensor */
} salFftDataType;

/** Power speactrum overlap average control. 
* \enum salOverlapType
 * \ingroup FrequencyData
 */
typedef enum _salOverlapType {
    salOverlap_on,          /**< Use overlap averaging. Note that enum value = 0 for backward comapatability. */
    salOverlap_off,         /**< Do not use overlap averaging. */
} salOverlapType;


/** FFT Control type. 
* \enum salMonitorMode
 * \ingroup FrequencyData
 */
typedef enum _salMonitorMode {
   salMonitorMode_off,          /**< Do not use monitor mode */
   salMonitorMode_on       /**< If there is an FFT measurement running on the sensor,
                                    send data in "eavesdrop mode" */
} salMonitorMode;

typedef salUInt32 salFftDataControlMask;  /**< See enum salFFT_DATA_CONTROL */

/** FFT sweep flags bit field  
 * \enum salSWEEP_FLAGS
 * \remark
 * \ingroup FrequencyData
 */
typedef enum _salSWEEP_FLAGS {
  salSWEEP_MEAS_ERROR         = 0x0001, /**< Measurement hardware error */
  salSWEEP_SETUP_NOT_USER     = 0x0002,  /**< setup changed by differnt measurement operation */
  salSWEEP_SEGMENT_TOO_LATE   = 0x0004,  /**< FFT segment too late */
  salSWEEP_END_OF_DATA        = 0x0008,  /**< This is the last block of data for the current measurement, measurement may have terminated early */
  salSWEEP_MONITOR_MODE       = 0x0010,  /**< Monitor mode FFT */
  salSWEEP_REF_OSC_ADJUSTED   = 0x0020,  /**< If set, the sensor clock reference oscillator was adjusted during the measurement  */
  salSWEEP_OVERLOAD_DETECTED  = 0x0040,  /**< Overload detected */
  salSWEEP_FREQ_OUT_OF_BOUNDS = 0x0080, /**< Center frequency out of bounds, value clamped to valid range */
  salSWEEP_CONNECTION_ERROR   = 0x1000,  /**< Connection problem to sensor */
  salSWEEP_LAST_SEGMENT       = 0x4000,  /**< This is the last block of data for the current measurement */
  salSWEEP_STOPPING           = 0x8000,  /**< FFT sweep is stopping */
  salSWEEP_MISSING_DATA       = 0x10000, /**< Gap in FFT data */
  salSWEEP_CPU_OVERLOAD       = 0x20000, /**< If set, the sensor's CPU is compute bound */
  salSWEEP_SYNC_PROBLEM       = 0x40000  /**< If set, the sensor's synchronization is suspect */
} salSWEEP_FLAGS;

/** FFT return data control bit field  
 * \enum salFFT_DATA_CONTROL
 * \remark
 * Most values corrrespond to the salSWEEP_FLAGS return enum.
 * \ingroup FrequencyData
 */
typedef enum _salFFT_DATA_CONTROL {
    salFFT_DATA_SAMPLE_LOSS             = 0x01,    /**< Indicates that this data block is not contiguous with previous block */
    salFFT_DATA_OVER_RANGE              = 0x02,    /**< RF Sensor input overload */
    salFFT_DATA_BLOCK_MEASUREMENT_ERROR = 0x04,    /**< Measurement hardware error */
    salFFT_DATA_SETUP_NOT_USER          = 0x08,    /**< The measurement setup is different than requested */
    salFFT_DATA_LAST_BLOCK              = 0x10,    /**< This is the last block of data for the current measurement */
    salFFT_DATA_OSCILLATOR_ADJUSTED     = 0x20,    /**< If set, the sensor clock reference oscillator was adjusted during the measurement  */
    salFFT_DATA_SEGMENT_TIMEOUT         = 0x40,    /**< If set, synchronized FFT segment was not completed in scheduled time */
	salFFT_DATA_CPU_OVERLOAD            = 0x80,    /**< If set, the sensor's CPU is compute bound */
	salFFT_DATA_SYNC_PROBLEM            = 0x100,   /**< If set, the sensor's synchronization is suspect */
    salSWEEP_IGNORE_SYNC                = 0x1000,  /**< If set, this segment will begin immediately (rather than being time-triggered) */
    salFFT_DATA_SEGMENT_NO_ARRAY        = 0x4000,  /**< If set, the data array will not be transferred (i.e. header info only) */
    salFFT_DATA_SEGMENT_SILENT          = 0x8000,  /**< If set, silent mode (i.e. no transfer) */
} salFFT_DATA_CONTROL;



/** salFrequencySegment specifies parameters for a sigle frequency segment in a frequency sweep.
 * \ingroup FrequencyData
  * \remarks
  * Use the salGetSensorCapabilities() function to get the following capabilities of the sensor:
  *
  * \code 
  *       Parameter         Typical values (3900A sensor)
  *    frequencyData                  1          
  *    maxSampleRate                 28 MHz
  *    sampleRateToSpanRatio         1.28
  *    maxDecimations                15
  *    maxSpan                       20 MHz          
  *    fftMaxBlocksize               16384 
  *    fftMinBlocksize                8 
  * \endcode 
  *
  * sampleRate can be set from maxSampleRate/(2^maxDecimations) to maxSampleRate in multiples of two. For the N6831A, 
  * valid values of sampleRate are 28 MHz, 14 MHz, ... 854 Hz. 
  * Anti-alias filtering is applied to the input data. If you would like to obtain only points that are unaffected by the
  * anti-alias filter, set numPoints as follows:
  *
  * \code
  *     if (sampleRate==maxSampleRate) numPoints = numFftPoints * maxSampleRate/maxSpan
  *     else                           numPoints = numFftPoints * sampleRateToSpanRatio
  * \endcode
  *
  * If you want the sensor to return only the valid data points, set firstPoint as follows:
  *
  * \code
  *     firstPoint = (numFftPoints - numPoints)/2
  * \endcode
  *
  * The frequency spacing between returned data points will be:
  *
  * \code
  *        DeltaF = sampleRate / numFftPoints
  * \endcode
  *
  * The frequency of the first point will be:
  *
  * \code
  *        F0 = centerFrequency - (sampleRate/2.0) + (DeltaF * firstPoint)
  * \endcode
  *
  * 
  * The time it takes to acquire one block of data is:
  *
  * \code
  *        T = 1.0 / DeltaF
  * \endcode
  *
  * If averaging is used, the blocks of data are overlapped by 50 percent. The time it takes
  * to acquire one averaged block of data is:
  *
  * \code
  *        Taverage = T * (numAverages+1)/2 = (numFftPoints/sampleRate)*(numAverages+1)/2
  * \endcode
  *
  * Averaging can be used to limit the amount of data sent over the network. The size in bytes of a 
  * single data message is approximately numPoints*2. As an example, assuming that the FFT calculation
  * time is much shorter than the time it takes to acquire a block of data:
  *
  * \code
  *      numFftPoints = 4096
  *      sampleRate   = 28e6
  *      numPoints    = 4096 * 20e6/28e6 = 2925 points
  *      message size = 2925 * 2 = 5851 bytes
  *      numAverages   = 1
  *      FFTs/sec      = 1/T  = 28e6/4096 = 6835
  *      Network BW    = FFTs/sec*numPoints*2 = 6835*2925*2 = 40 MBytes/sec
  * \endcode
  *
  *  The sensor does not have the network bandwidth to keep up with this rate, so averaging
  *  should be used to limit the bandwidth. For example:
  *
  * \code
  *      numAverages = 250
  *      Taverage    = (4096/28e6)*(250+1)/2 = 0.018
  *      FFTs/sec      = 1/0.018 = 54.4
  *      Network BW    = 54.4 * 2925*2 = 318 kBytes/sec
  * \endcode
  *
  * The overlapMode allows you to turn overlap averaging on and off; the default is salOverlap_on. When
  * overlap is on, each time record used for the FFT overlaps the previous time record by 50%.
  * \n\n
  * The resolution bandwidth of the measurement is a function of the window type, the tuner sample rate, and the 
  * number of FFT points, as follows:
  *
  * \code
  * RBW = EquivalentNoiseBandwidth * DeltaF = EquivalentNoiseBandwidth * sampleRate / numFftPoints
  *
  * where EquivalentNoiseBandwidth =  1.5 for the Hann window
  *                                =  2.2 for the Gausstop window
  *                                =  3.8 for the Flattop window
  * \endcode
  *   
  * The Mixer Level control allows you to trade off between  distortion and signal-to-noise performance. 
  * Increasing Mixer Level increases signal-to-noise (SNR) and distortion. Decreasing Mixer Level decreases distortion and SNR.  
  * Mixer Level control is relative. 0 dB represents the best balance between distortion and SNR. 
  
 **/
typedef struct _salFrequencySegment  {
    salAntennaType  antenna;          /**< Antenna input for this segment */
    salInt32        preamp;           /**< Preamp input state (0=off; otherwise, on) */
    salUInt32       numFftPoints;     /**< FFT points; must be power of 2  */
    salAverageType  averageType;      /**< Average type for this segment */
    salUInt32       numAverages;      /**< Number of averages for this segment */
    salUInt32       firstPoint;       /**< Index of first point to return; must be less than numFftPoints */
    salUInt32       numPoints;        /**< Number of points to return; must be less than or equal to numFftPoints */
    salUInt32       repeatAverage;    /**< If true, repeat the measurement until duration has elapsed (not supported) */
    salFloat64      attenuation;      /**< Input attenuation in dB for this segment */
    salFloat64      centerFrequency;  /**< Center frequency of RF data */
    salFloat64      sampleRate;       /**< Sample rate of RF data */
    salFloat64      duration;         /**< Time interval (sec) between the start of this segment and the start of the next segment */
#ifdef MODEL_3900F
	salUInt64		frequencyTriggerControl; /**< for IQ frequency trigger :高32位表示触发频率Hz；低32位表示触发幅度dBm*/
#else
	salFloat64      mixerLevel;       /**< Mixer level in dB; range is -10 to 10 dB, 0 dB is give best compromise between SNR and distortion. */
#endif
    salOverlapType  overlapMode;      /**< Control overlap for averaging. Default (0) is to use overlap. */
    salFftDataType  fftDataType;      /**< FFT internal data type */
	salInt32        noTunerChange;    /**< In almost all cases, this parameter should be set to 0. Only set this to non-zero value if you do not want the FFT process to modify tuner parameters. */
	salFftDataControlMask  noDataTransfer;   /**< In almost all cases, this parameter should be set to 0. Set this bitfield to non-zero value to limit data return data for this segment */ 
	salUInt64       levelTriggerControl; /**< for IQ level trigger :高32位中的低16位表示幅度触发类型、高16位表示预存储深度；低32位表示触发幅度dBm*/
} salFrequencySegment;

/**  salSweepParms specifies parameters for a spectral measurement over one or more frequency bands.
 * \ingroup FrequencyData
 * \remarks 
 * \ If monitorMode is set to salMonitorMode_on, and another application is currently using
 * \        the sensor for FFTs, the segment table from the other application will be used to control the
 * \         measurement.
 **/
typedef struct _salSweepParms {
    salUInt32        numSweeps;        /**< Number of sweeps to perform; 0 means sweep until a stop command is sent */
    salUInt32        numSegments;      /**< Number of segments in the sweep */
    salWindowType    window;           /**< Window applied to time record before performing FFT  */
    salUInt32        userWorkspace;    /**< User-defined value that will be returned with each data message */
    salDataType      dataType;         /**< Data type for returned power spectrum; (ignored in this release; data is always salREAL_FLOAT32_DBM)*/
	salInt32         reserved1;        /**< reserved */
    salInt32         syncSweepEnable;  /**< Set to non-zero when performing synchronous sweeps. */
    salFloat64       sweepInterval;    /**< Interval between time-triggers for the start of each segment (synchrounous sweep only). */
    salUInt32        syncSweepSec;     /**< "sec" start time for first segment (synchronous sweep only). */
    salUInt32        syncSweepNSec;    /**< "nsec" start time for first segment (synchronous sweep only). */
    salMonitorMode   monitorMode;       /**< Enable/disable monitor mode */
    salFloat64       monitorInterval;   /**< When monitorMode is salMonitorMode_on, send results back at this interval */
	salUInt32        reserved;          /**< Parameter used internally */
}  salSweepParms;

/** salSegmentData describes the data returned by a frequency domain measurement.
 * \ingroup FrequencyData
 * \remarks Anti-alias filtering is applied to the input time record. If you would like to obtain only points that are unaffected by the
 *          anti-alis filter, set numPoints to numFftPoints/1.28 and set first point to (numFftPoints-numPoints)/2. 
 *\par
 *          
 **/
typedef struct _salSegmentData {
	salUInt32      userWorkspace;        /**< User-defined value set in ::salSweepParms */
	salUInt32      segmentIndex;     /**< 0-based index of this segment in the segmentTable  */
	salUInt32      sequenceNumber;   /**< starts at 0; incremented by 1 for each frequency result  */
	salUInt32      sweepIndex;       /**< starts at 0; incremented by 1 at the end of a sweep */

	salUInt32      timestampSec;   /**< Integer seconds part of timestamp of first time point in this segment */
	salUInt32      timestampNSec;  /**< Fractional seconds part of timestamp of first time point in this segment */
	salUInt32      timeQuality;    /**< Measure of time quality of timestamp */
	salLocation    location;       /**< Sensor location when this segment was measured */

	salFloat64     startFrequency; /**< Frequency of first point returned by this measurement */ 
	salFloat64     frequencyStep;  /**< Frequency spacing in Hertz of frequency data */
	salUInt32      numPoints;      /**< Number of frequency points returned by this measurement */
	salUInt32      overload;       /**< If not 0, the sensor input overloaded during this segment */
	salDataType    dataType;       /**< Data type of returned amplitude data */
	salUInt32      lastSegment;    /**< If not zero, this is the last segment before measurement stops */

	salWindowType  window;             /**< Window used for this measurement */
	salAverageType  averageType;   /**< Average type used in this measurement */
	salUInt32      numAverages;        /**< Number of averages used in this measurement */
	salFloat64     fftDuration;        /**< Duration of one FFT result */
	salFloat64     averageDuration;    /**< Duration of this complete measurement (all numAverages)  */

	salUInt32      isMonitor;          /**< If true, the segment table from another request is controlling the measurement */
	salSweepFlagsMask sweepFlags;      /**< Mask of indicators for various conditions (see ::salSWEEP_FLAGS). */
	salUInt32      timeAlarms;                  /**< Indicates status of sensor time sycnh (bit map of ::salTimeAlarm values) */
	double         sampleRate;        /**< Data ample rate (in Hertz) used for this segment */
} salSegmentData;

/** salSweepComputationParms describes parameters to create an optimized set of salFrequencySegments
 * \ingroup FrequencyData
 **/
typedef struct _salSweepComputationParms {
	salFloat64      startFrequency;   /**< Start frequency for the sweep (Hz) */
	salFloat64      stopFrequency;    /**< Stop frequency for the sweep (Hz) */
	salFloat64      rbw;              /**< Resolution band-width (Hz) */
} salSweepComputationParms;

/** salSweepComputationResults information on computed sweep
 * \ingroup FrequencyData
 **/
typedef struct _salSweepComputationResults {
	salFloat64		stepFreq;						/**< Computed desired FFT bin size (converted from rbw and window) */
	salFloat64		fftBinSize;						/**< Actual FFT bin size (some power of 2) */
	salFloat64		actualRbw;						/**< Actual RBW (related to fftBinSize by window type) */
	salFloat64		tunerSampleRate;				/**< Actual tuner sample rate (Hz) */
	salUInt32		fftBlockSize;					/**< FFT size */
	salFloat64		nyquistFactor;					/**< Either 1.4 or 1.28 depending on tunerSampleRate */
	salUInt32		numBinsReturned;				/**< Number of FFT bins returned in each segment */
	salUInt32		numBinsReturnedLastSegment;		/**< Number of FFT bins returned in the last segment */
	salUInt32		firstPointIdx;					/**< Index of first FFT bin returned */
	salUInt32		firstPointIdxLastSegment;		/**< Index of first FFT bin returned in the last segment */
	salUInt32		numSegments;					/**< Number of FFT segments to cover the span */
	salFloat64		centerFrequencyFirstSegment;	/**< Center frequency of the first segment */
	salFloat64		centerFrequencyLastSegment;		/**< Center frequency of the last segment */
} salSweepComputationResults;


/** salComputeFftSegmentTableSize: Compute the number of FFT segments for the sweep.
  * \param computeParms [in] Controls the segment table computation
  * \param sweepParms [in|out] Sweep parameters. The window field must be specified. 
  *   The numSegments field will be update in this function. 
  * \param results [out] Sweep computation results.
  * \return salErrorType error value
  * \remarks This helper function will compute the number of FFT segments required for the sweep.
  *     The result will be returned in the sweepParms->numSegments field. This information is needed
  *     in order to allocate memory before calling salInitializeFftSegmentTable( ).
  *     Caution: be sure to specify the sweepParms->antenna field before calling this function!
  * \ingroup FrequencyData
  */
SAL_API salComputeFftSegmentTableSize(salSweepComputationParms *computeParms, salSweepParms *sweepParms,
	salSweepComputationResults *results);

/** salInitializeFftSegmentTable: Initialize the FFT Segment table.
  * \param computeParms [in] Controls the segment table computation
  * \param sweepParms [in] Sweep parameters. The numSegments field must represent the size of the segmentTable array
  * \param exampleSegment [in] This provides default values for many of the fields that will be initialized in the
  *      segmentTable array
  * \param segmentTable [out] This is a pointer to a salFrequencySegment array
  *       that is initialized by this function. 
  * \param results [out] Sweep computation results.
  * \return salErrorType error value
  * \remarks This helper function will initialize an FFT segment table. The input and sweepParms parameters
  *     control the generation of the segmentTable. 
  *     The salComputeFftSegmentTableSize( ) function should be used to initialize the swepParms->numSegments
  *     field before calling this function.
  *     Sufficient memory for the segmentTable array must be pre-allocated before invocation.
  *     Default values for many of the segmentTable fields should be provided via the exampleSegment parameter.
  * \ingroup FrequencyData
  */
SAL_API salInitializeFftSegmentTable(
	salSweepComputationParms *computeParms, 
	salSweepParms *sweepParms,
	salFrequencySegment *exampleSegment,
	salFrequencySegment *segmentTable,
	salSweepComputationResults *results);


/** salFftTimestampParam describes parameters for the refine FFT timestamp operation.
 * \ingroup FrequencyData
 * \remarks When "Peak-held" FFT averaging is enabled (see salAverage_peak), 
 * the FFT's timestamp is the start time for the first data block being processes. 
 * When measuring bursty RF signals, hardware in the sensor can be used to locating the time in the IQ data 
 * record where RF power appeared. The resulting "refined" is returned and can be used for geo-location purposes.
 *  
 * For rising edge, the lowSignalTime parameter represents the pre-edge time where the signal
 * must be below the triggerLevel threshold.
 *
 * For falling edge, the lowSignalTime parameter represents the post-edge time where the signal
 * must be above the triggerLevel threshold.
 *
 * When an edge is not found using the provided triggerLevel, the sensor will try again using a
 * computed trigger level: new trigger level = firstPoint + (peak-firstPoint)/2.
 * The second attempt will only be attempted when the peak - firstPoint > retrySpan.
 * Consequently, a large value for retrySpan will prevent the sensor from retrying.
 * The minimum value for retrySpan will be automatically clamped to 2 dB 
 * (i.e. the peak must be 2 dB > than the firstPoint)
 **/
typedef struct _salFftTimestampParam {
    salUInt32      timestampSec;    /**< Integer seconds part of FFT timestamp */
    salUInt32      timestampNSec;   /**< Fractional seconds part of FFT timestamp */
	salUInt32      numSamples;      /**< Number of IQ samples */
	salUInt32      edgeSelect;      /**< Edge selection 0==Rising, 1==Falling */
    salFloat64     centerFrequency; /**< IQ Center Frequency [Hz] */ 
    salFloat64     sampleRate;      /**< IQ sample rate [Hz] */ 
    salFloat64     triggerLevel;    /**< IQ trigger level [dBm] */ 
	salFloat64     lowSignalTime;   /**< Time before (or after) the edge where the signal must be low [sec] */
	salFloat64     retrySpan;       /**< If edge not found, try again when peak - first > retrySpan [dB] */
} salFftTimestampParam;

/** salFftTimestampResult describes the data returned by the refine FFT timestamp operation.
 * \ingroup FrequencyData
 * \remarks This structure contains the refined timestamp result.
 * \
 *\par
 *          
 **/
typedef struct _salFftTimestampResult {
    salUInt32      timestampSec;   /**< Integer seconds part of the refined timestamp */
    salUInt32      timestampNSec;  /**< Fractional seconds part of the refined timestamp */
    salUInt8       edgeDetected;   /**< flag indicating edge was detected */ 
	salFloat64     peak;           /**< peak IQ magnitude (dBm) */ 
	salFloat64	   firstPoint;     /**< First Point IQ magnitude (dBm) */ 
	salFloat64	   lastPoint;      /**< Last Point IQ magnitude (dBm) */
} salFftTimestampResult;

/** Frequency segment callback function prototype.
 * \param dataHdr      [out] Description of the data.
 * \param pAmplitude   [out] Pointer (in memory managed by the SAL library) to the amplitude data.
 * \remarks This function is called in a separate thread than the one that called salStartSweep(). Calling
 *          SAL functions (other than salGetErrorString()) from the callback function can result in unpredictable behavior.
 * \ingroup FrequencyData
 **/
#ifdef MATLAB_LOADLIBRARY_COMPILE
// The Matlab loadlibrary.m mechanism does not support functions with callbacks
typedef void *SAL_SEGMENT_CALLBACK;
#else
typedef int(*SAL_SEGMENT_CALLBACK)(salSegmentData *dataHdr, salFloat32 *pAmplitude);
#endif
/** Request frequency data from the sensor
  * \param measHandle      [out] Unique smeasurement handle created by this request.
  * \param sensorHandle    [in] Unique sensor handle returned by salConnectSensor().
  * \param parms           [in] Parameters specifying the measurement request.
  * \param pSegmentTable   [in] Pointer to segment table specifying stepped-sweep parameters
  * \param dataCallback    [in] Pointer to segment data callback function
  * \remarks
  * \par 
  * Older versions of RF sensor firmware do not support the Frequency data interface; if the sensor supports this interface,
  * the frequencyData parameter of ::salSensorCapabilities will be non-zero.
  *
  * \par
  * If dataCallback is NULL, the user is responsible for getting the data by calling salGetSegmentData(). 
  * \par
  * If salSweepParms.monitorMode is 0, a lock will be requested on the tuner and FFT resource. The lock request will 
  * fail if another application has the tuner or FFT locked; in this case the function will return an error. If the lock
  * request does not fail, the tuner and FFT will remain locked until one of the following happens: the measurement 
  * handle is closed; the sensor connection is closed or terminated; or salSweepParms.monitorMode is set to a non-zero value.
  * The tuner and FFT resource are not unlocked when a sweep stop or abort command are sent.
  * \par
  * If you do not want to modify the tuner parameters (center frequency, sample rate, attenuation, and antenna setting),
  * set salSweepParms.noTunerChange to 1. This is useful when the tuner is set for "lookback" mode and you 
  * want to monitor the spectrum without affecting the tuner setup.
  * \par
  * This function utilized default values for pacing: 50 messages backlog or 0.5 seconds backlog (which ever comes first). 
  * When measurements accumulate in the sensor beyond these limits, the sensor will begin discarding new measurements.
  * See salStartSweep2( ) to change this behavior with the salFlowControl parameter.
  * Note that the pacing parameters are ignored when performing time-synchronized FFTs.
  * \par
  * The noDataTransfer bitfield (see salFftReturnDataControl) controls what data is returned. When set to 0, both
  * FFT headers and data arrays are returned. When set to non-zero, you can control what segments get returned.
  * By setting the salFFT_DATA_SEGMENT_NO_ARRAY field, the data array will not be transferred.
  * By setting the salFFT_DATA_SEGMENT_SILENT field, nothing will be returned for this segment.
  * \par
  * \return salErrorType error value
  * \ingroup FrequencyData
  * \see salGetSegmentData() \n
  *           SAL_SEGMENT_CALLBACK \n
  *           salSendSweepCommand() \n
  *           salGetSweepStatus() \n
  *           salGetSensorCapabilities() \n
  *           salClose()
  *   
  */

SAL_API salStartSweep(salHandle *measHandle, salSensorHandle sensorHandle, salSweepParms *parms, 
                      salFrequencySegment *pSegmentTable, SAL_SEGMENT_CALLBACK dataCallback);


/** Request frequency data from the sensor with flow control
  * \param measHandle      [out] Unique smeasurement handle created by this request.
  * \param sensorHandle    [in] Unique sensor handle returned by salConnectSensor().
  * \param parms           [in] Parameters specifying the measurement request.
  * \param pSegmentTable   [in] Pointer to segment table specifying stepped-sweep parameters
  * \param salFlowControl  [in] Pointer to flow control information
  * \param dataCallback    [in] Pointer to segment data callback function
  * \remarks
  * \par 
  * Older versions of RF sensor firmware do not support the Frequency data interface; if the sensor supports this interface,
  * the frequencyData parameter of ::salSensorCapabilities will be non-zero.
  *
  * \par
  * If dataCallback is NULL, the user is responsible for getting the data by calling salGetSegmentData(). 
  * \par
  * If salSweepParms.monitorMode is 0, a lock will be requested on the tuner and FFT resource. The lock request will 
  * fail if another application has the tuner or FFT locked; in this case the function will return an error. If the lock
  * request does not fail, the tuner and FFT will remain locked until one of the following happens: the measurement 
  * handle is closed; the sensor connection is closed or terminated; or salSweepParms.monitorMode is set to a non-zero value.
  * The tuner and FFT resource are not unlocked when a sweep stop or abort command are sent.
  * \par
  * If you do not want to modify the tuner parameters (center frequency, sample rate, attenuation, and antenna setting),
  * set salSweepParms.noTunerChange to 1. This is useful when the tuner is set for "lookback" mode and you 
  * want to monitor the spectrum without affecting the tuner setup.
  * \par
  * The pacing parameters used by the sensor can be changed with the salFlowControl parameter.
  * If all values are zero, default pacing will be used: 50 messages backlog or 0.5 seconds backlog (which ever comes first). 
  * When measurements accumulate in the sensor beyond the pacing limits, the sensor will begin discarding new measurements.
  * Note that the pacing parameters are ignored when performing time-synchronized FFTs.
  * \par
  * The noDataTransfer bitfield (see salFftReturnDataControl) controls what data is returned. When set to 0, both
  * FFT headers and data arrays are returned. When set to non-zero, you can control what segments get returned.
  * By setting the salFFT_DATA_SEGMENT_NO_ARRAY field, the data array will not be transferred.
  * By setting the salFFT_DATA_SEGMENT_SILENT field, nothing will be returned for this segment.
  * \par
  * \return salErrorType error value
  * \ingroup FrequencyData
  * \see salGetSegmentData() \n
  *           SAL_SEGMENT_CALLBACK \n
  *           salSendSweepCommand() \n
  *           salGetSweepStatus() \n
  *           salGetSensorCapabilities() \n
  *           salClose()
  *   
  */

SAL_API salStartSweep2(salHandle *measHandle, salSensorHandle sensorHandle, salSweepParms *parms, 
                      salFrequencySegment *pSegmentTable, 
					  salFlowControl *pFlowControl,
					  SAL_SEGMENT_CALLBACK dataCallback);

/** Request one segment of data from sweep measurement when the dataCallback function in salStartSweep() was set to NULL.
 *  The userDataBuffer must be allocated by the calling application. Use the salRECOMMENDED_DATA_BUFFER_SIZE
 *  macro to allocate the maximum amount of space that will be needed. The calling application must also set
 *  userDataBufferBytes.
 * \param measHandle               [in]  Measurement handle from salStartSweep().
 * \param dataHdr                  [out] User allocated memory which will hold the salSegmentData header.
 * \param pAmplitude               [out] User allocated memory which will hold the amplitude samples.
 * \param userDataBufferBytes      [in] The size in bytes of the memory pointed to by userDataBuffer.
 * \return salErrorType error value. The value will be SAL_ERR_NONE if there is data available,
 *  SAL_ERR_NO_DATA_AVAILABLE if there is no data available. Any other value indicates an
 *  unexpected error. 
 * \ingroup FrequencyData
 * \see salStartSweep()
 */
SAL_API salGetSegmentData(
    salHandle             measHandle,
    salSegmentData        *dataHdr,
    salFloat32            *pAmplitude,
    salUInt32             userDataBufferBytes);

/** Retrieve the backlog status for this FFT stream
 * \param measHandle               [in]  Measurement handle from salStartSweep() or salStartSweep2().
 * \param backlogStatus            [out] Backlog information
 * \ingroup FrequencyData
 * \see salStartSweep()
 */
SAL_API salGetSweepBacklogStatus(
    salHandle             measHandle,
    salBacklogStatus      *backlogStatus);

/** Refine the FFT timestamp to the frequency range of interest. This does not invoke
 * a new FFT. It uses the lookback memory and analyzes the IQ data to refine the FFT's timestamp.
 * \param measHandle               [in]  Measurement handle from salStartSweep().
 * \param input                    [in]  FFT timestamp (starting time) and other params
 * \param result                   [out] Refined timestamp
 * \ingroup FrequencyData
 */
SAL_API salRefineFftTimestamp(
    salHandle             measHandle,
    salFftTimestampParam *input,    
	salFftTimestampResult *result);

/** Sweep commands. 
* \enum salSweepCommand
 * \ingroup FrequencyData
 */
typedef enum _salSweepCommand {
    salSweepCommand_stop,         /**< Stop a sweep when the sweep is finished */
    salSweepCommand_abort,        /**< Stop a sweep as soon as possible*/
    salSweepCommand_flush,        /**< Flush the sweep backlog */
   
} salSweepCommand;

/** Send a command to change the state of a measurement started by salStartSweep().
* \param measHandle               [in]  Measurement handle from salStartSweep().
* \param command                  [in]  Command to send
* \ingroup FrequencyData
* \return salErrorType error value
 */
SAL_API salSendSweepCommand(salHandle measHandle, salSweepCommand command);

/** Sweep status. 
* \enum salSweepStatus
 * \ingroup FrequencyData
 */
typedef enum _salSweepStatus {
    salSweepStatus_stopped,               /**< Sweep is waiting to start  */
    salSweepStatus_running,            /**< Sweep is running */
} salSweepStatus;

/** Get the status of a sweep started by salStartSweep().
* \param measHandle               [in]  Measurement handle from salStartSweep().
* \param status                   [out] Current status of the sweep
* \ingroup FrequencyData
* \return salErrorType error value
 */
SAL_API salGetSweepStatus(salHandle measHandle, salSweepStatus *status);

/** Get the status of a sweep started by salStartSweep2().
* \param measHandle               [in]  Measurement handle from salStartSweep().
* \param fromNow                  [in]  If zero , elapsed last RX time - start time. 
*                                       Id non-zero, current time - start time
* \param status                   [out] Current status of the sweep
* \param elapsed                  [out] elapsed time in seconds from start
* \param fromNow                  [in]  If zero , elapsed last RX time - start time. 
*                                       Id non-zero, current time - start time
* \ingroup FrequencyData
* \return salErrorType error value
 */
SAL_API salGetSweepStatus2(salHandle measHandle, salInt32 fromNow, salSweepStatus *status, salFloat64 *elapsed);

//------------------------------------raw spectrum-------------------------//
#ifdef MODEL_3900F
SAL_API salInitCalibraterParams(salHandle sensorHandle, salFrequencySegment segmentParam, salWindowType winType, double temperature);
//获取扫描频率段的带内校准数据。注意：3900F带内校准数据个数为16384是3900A的两倍
SAL_API salGetBandCalData(salHandle sensorHandle, salFrequencySegment segmentParam, salFloat32* calDataBuf);
SAL_API salCalSegmentRawData(salHandle sensorHandle, salFrequencySegment segmentParam, salFloat32* bandCalData, salUInt32* rawData, salFloat32* amplitude, double temperature);
SAL_API salGetSegmentFRCalData(salHandle sensorHandle, salFrequencySegment segmentParam, float* frCalData, double temperature);
#else
SAL_API salInitInBandCalData(salHandle sensorHandle, salFrequencySegment segmentParam, salFloat32* calDataBuf);
SAL_API salCalSegmentRawData(salHandle sensorHandle, salFrequencySegment segmentParam, salFloat32* bandCalData, salUInt32* rawData, salFloat32* amplitude);
SAL_API salGetSegmentFRCalData(salHandle sensorHandle, salFrequencySegment segmentParam, float* frCalData);
#endif
SAL_API salGetSegmentRawData(salHandle measHandle, salSegmentData* dataHdr, salUInt32* rawData, salUInt32 userDataBufferBytes);

#ifdef __cplusplus
}
#endif

#endif /*__EISALFREQUENCY_H */
