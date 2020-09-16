/* Basic types */

typedef unsigned char salUInt8;
typedef short salInt16;
typedef unsigned short salUInt16;
typedef long salInt32;
typedef unsigned long salUInt32;
typedef unsigned long long salUInt64;
typedef float salFloat32;
typedef double salFloat64;
/* MASKS */
typedef salUInt32 salChangeMask;
typedef salUInt32 salStateEventMask;
typedef salUInt32 salSweepFlagsMask; 
typedef salUInt32 salValidGpsMask;
typedef salUInt32 salChangeGpsMask;
typedef salUInt32 salRFStatusMask;

/** Maximum length of arrays used in SAL. 
* \enum salArrayMaximums
 * \ingroup SystemManagement
 */
enum salArrayMaximums{
 
 SAL_MAX_GEOGRAPHIC_DATUM = 64, /**< Maximum string length for geographic datum */
 SAL_MAX_SENSOR_NAME      = 64, /**< Maximum string length for sensor name */
 SAL_MAX_SENSOR_HOSTNAME  = 64, /**< Maximum string length for sensor hostname  */
 SAL_MAX_APPLICATION_NAME = 64,  /**< Maximum string length for application name */
 SAL_MAX_ERROR_STRING     = 64,  /**< Maximum string length for error strings */
 SAL_MAX_SENSORS          = 512,  /**< Maximum number of sensors that will be returned by salOpenSensorList  */
 SAL_MAX_EVENT_MSG_LEN    = 81,   /**< Maximum string length for salEvent message */
 SAL_MAX_UNIT             = 32,   /**< Maximum string length for measurement units (e.g., "meters" and "degrees") */
 
 SAL_MAX_FILENAME         = 256, /**< Maximum string length for file names */
 SAL_MAX_SESSION_ID       = 256, /**< Maximum string length for sessionId */
 SAL_MAX_COMMENT          = 256, /**< Maximum string length for comment */
 SAL_MAX_SENSORS_PER_GROUP = 100,  /**< Maximum number of sensors that can be added to a sensor group */
 SAL_MAX_GEOLOCATION_SAMPLES = 32768, /**< Maximum number of samples for geolocation measurements */
 SAL_MIN_GEOLOCATION_SAMPLES = 256, /**< Minimum number of samples for geolocation measurements */
 SAL_MAX_SAMPLES_PER_TRANSFER = 32768, /**< Maximum number of samples that can be read at one time */
 
};

/** Time sync status (bitmap) for the sensor time alarms
 * \enum salTimeAlarm
 * \ingroup Session
 */
typedef enum _salTimeAlarm {
   salTimeAlarm_clockNotSet      = 0x01,       /**< The sensor clock has not been set */
   salTimeAlarm_timeQuestionable = 0x02,       /**< The sensor time may not be accurate (for example, GPS may not be locked) */
} salTimeAlarm;

/** Sensor Handle 
 * \ingroup Session */
typedef size_t salHandleType;
typedef salHandleType salSensorHandle;

/** Sensor Group Handle
 * \ingroup Geolocation */
typedef salHandleType salHandle;


/** IQ Data resolution
  * \enum salDataType
  * \ingroup MeasurementData 
*/
typedef enum _salDataType {
    salDATA_TYPE_NONE = -1, /**< Indicates no data / unknown type */
    salCOMPLEX_32,        /**< 32 bit integer complex pairs (real and imaginary parts are interleaved)*/
    salCOMPLEX_16,        /**< 16 bit integer complex pairs (real and imaginary parts are interleaved)*/
    salCOMPLEX_FLOAT32,   /**< 32 bit float complex pairs (real and imaginary parts are interleaved)*/
    salREAL_INT8,         /**< 8 bit integer real data */
    salREAL_INT8_ALAW,    /**< 8 bit integer real data with A-law encoding*/
    salREAL_INT8_ULAW,    /**< 8 bit integer real data with A-law encoding*/
    salREAL_INT16,        /**< 16 bit integer real data */
    salREAL_FLOAT32,       /**< 32 bit float real data */
    salREAL_FLOAT32_DBM,   /**< 32 bit float real data in units of dBm */
} salDataType; 

/** Antenna type
  * \enum salAntennaType
  * \ingroup MeasurementControl 
*/
typedef enum _salAntennaType { 
    salAntenna_TestSignal  = -4,  /**< Connect input to internal comb generator (NOTE: due to the high signal level of the internal signal,
                                      the comb generator may cause detectable radiation from an antenna connected to a sensor input) */
    salAntenna_Auto        = -3,  /**< Select antenna as configured by the SMS */
    salAntenna_Unknown     = -2,  /**< Unknown antenna type */
    salAntenna_Terminated  = -1,  /**< Sensor internal 50 ohm termination */
 
    salAntenna_1           = 0,   /**< Sensor Antenna 1 input */
    salAntenna_2           = 1,   /**< Sensor Antenna 2 input */

    salAntenna_TestSignal2 = 2,  /**< Connect input to internal comb generator */
    salAntenna_Terminated2 = 3,  /**< Sensor internal 50 ohm termination */
    salAntenna_Auto2       = 4   /**< Select antenna as configured by the SMS */
} salAntennaType;

/** Error Codes
  * \enum salErrorType
  * \ingroup Error
  */
typedef enum  _salErrorType {
    SAL_ERR_NONE = 0,                       /**< No Error */
    SAL_ERR_NOTIMPLEMENTED = -1,            /**< This functionality is not implemented yet. */
    SAL_ERR_UNKNOWN = -2,                   /**< Error of unspecified type */
    SAL_ERR_BUSY = -3,                      /**< The system is busy */
    SAL_ERR_TRUNCATED = -4,                 /**< Unspecified error */
    SAL_ERR_ABORTED = -5,                   /**< The measurement was aborted */
    SAL_ERR_RPC_NORESULT = -6,              /**< The server accepted the call but returned no result */
    SAL_ERR_RPC_FAIL = -7,                  /**< The RPC call to the server failed completely */
    SAL_ERR_PARAM = -8,                     /**< Incorrect parameter in call. */
    SAL_ERR_MEAS_IN_PROGRESS = -9,          /**< Another measurement is currently in progress */
    SAL_ERR_NO_RESULT = -10,                /**< No result was returned */
    SAL_ERR_SENSOR_NAME_EXISTS = -11,       /**< The sensor name specified already exists */
    SAL_ERR_INVALID_CAL_FILE = -12,         /**< The calibration file has an invalid format */
    SAL_ERR_NO_SUCH_ANTENNAPATH = -13,      /**< The antenna path specified does not exist */
    SAL_ERR_INVALID_SENSOR_NAME = -14,      /**< The sensor name specified does not exist */
    SAL_ERR_INVALID_MEASUREMENT_ID = -15,   /**< The given measurement ID is not valid */
    SAL_ERR_INVALID_REQUEST = -16,          /**< Internal system error */
    SAL_ERR_MISSING_MAP_PARAMETERS = -17,   /**< You need to specify map coordinates */
    SAL_ERR_TOO_LATE = -18,                 /**< The measurement arrived at the sensor too late */
    SAL_ERR_HTTP_TRANSPORT = -19,           /**< An HTTP error occurred when trying to talk to the sensors */
    SAL_ERR_NO_SENSORS = -20,               /**< No sensors available for measurement */
    SAL_ERR_NOT_ENOUGH_TIMESERIES = -21,    /**< Not enough timeseries in measurement */
    SAL_ERR_NATIVE = -22,                   /**< Error in native code */
    SAL_ERR_BAD_SENSOR_LOCATION = -23,      /**< Invalid sensor location */
    SAL_ERR_DATA_CHANNEL_OPEN = -24,        /**< Data Channel already open */
    SAL_ERR_DATA_CHANNEL_NOT_OPEN = -25,    /**< Data Channel not open */
    SAL_ERR_SOCKET_ERROR = -26,             /**< Socket error */
    SAL_ERR_SENSOR_NOT_CONNECTED = -27,     /**< Sensor not connected */
    SAL_ERR_NO_DATA_AVAILABLE = -28,        /**< No data available */
    SAL_ERR_NO_SMS = -29,                   /**< No SMS Available */
    SAL_ERR_BUFFER_TOO_SMALL = -30,         /**< User data buffer too small for data > */
    SAL_ERR_DIAGNOSTIC = -31,               /**< A diagnostic error occurred*/
    SAL_ERR_QUEUE_EMPTY = -32,              /**< No more msgs in the Error Queue */
    SAL_ERR_WRONG_SERVICE = -33,            /**< Sensor set to the wrong service (see salSetService()) */
    SAL_ERR_MEMORY = -34,                   /**< Could not allocate memory */
    SAL_ERR_INVALID_HANDLE = -35,           /**< User supplied handle was invalid */
    SAL_ERR_SENSOR_CONNECT = -36,           /**< Attempt to connect to sensor failed */
    SAL_ERR_SMS_NO_TOKEN = -37,             /**< SMS refused to issue token */
    SAL_ERR_COMMAND_FAILED = -38,           /**< Sensor command failed */
    SAL_ERR_NO_LOCATE_HISTORY = -39,        /**< Could not get locate result history */
    SAL_ERR_TIMEOUT = -40,                  /**< Measurement timed out */
    SAL_ERR_IMAGE_SIZE = -41,               /**< Requested location image size too big */
    SAL_ERR_INVALID_ANTENNA = -42,          /**< Requested antenna type not valid */
    SAL_ERR_STRING_TOO_LONG = -43,          /**< Input string too long */
    SAL_ERR_INVALID_TIMEOUT = -44,          /**< Requested timeout value not valid */
    SAL_ERR_INVALID_SENSOR_INDEX = -45,     /**< Sensor index not valid */
    SAL_ERR_INVALID_TRIGGER_TYPE = -46,     /**< Requested trigger type not valid */
    SAL_ERR_INVALID_DOPPLER_COMP = -47,     /**< Requested Doppler compensation not valid */ 
    SAL_ERR_NUM_SENSORS = -48,              /**< Maximum number of sensors already added to group */ 
    SAL_ERR_EMPTY_GROUP = -49,              /**< Operation not valid on empty sensor group */ 
    SAL_ERR_HANDLE_IN_USE = -50,            /**< Handle can not be closed because it is in use */
    SAL_ERR_DATA_TYPE     = -52,            /**< Requested salDataType not valid for measurement */
    SAL_ERR_SENSOR_SERVER = -53,            /**< Sensor measurement server communications error */ 
    SAL_ERR_TIME_NOT_IN_STREAM = -54,       /**< Request for time data that is not in sensor memory */ 
    SAL_ERR_FREQ_NOT_IN_STREAM = -55,       /**< Requested frequency is outside of current tuner range */ 
    SAL_ERR_NOT_IN_LOOKBACK = -56,          /**< Measurement requires sensor in lookback mode */    
    SAL_ERR_AUTHORIZATION = -57,            /**< Error authorizing current application and user on the sensor */    
    SAL_ERR_TUNER_LOCK = -58,               /**< Could not obtain a lock on tuner resource */
    SAL_ERR_FFT_LOCK = -59,                 /**< Could not obtain a lock on FFT resource */
    SAL_ERR_LOCK_FAILED = -60,              /**< Could not obtain a lock on requested resource */
    SAL_ERR_SENSOR_DATA_END = -61,          /**< RF Sensor data stream terminated unexpectedly */
    SAL_ERR_INVALID_SPAN = -62,             /**< Requested measurement span is not valid */
    SAL_ERR_INVALID_ALGORITHM = -63,        /**< Requested geolocation algorithm is not available */
    SAL_ERR_LICENSE = -64,                  /**< License error */
    SAL_ERR_LIST_END       = -65,           /**< End of list reached */
    SAL_ERR_MEAS_FAILED = -66,              /**< The measurement failed of timed out with no results */
    SAL_ERR_EMBEDDED = -67,                 /**< Function not supported in embedded apps. */
	SAL_ERR_SMS_EXCEPTION = -68,            /**< Exception in SMS processing */
	SAL_SDRAM_OVERFLOW = -69,               /**< SDRAM overflow in sensor */
	SAL_NO_DMA_BUFFER = -70,				/**< NO free DMA Buffers in sensor */
	SAL_DMA_FIFO_UNDERFLOW = -71,           /**< DMA FIFO Underflow in sensor */
	SAL_FFT_SETUP_ERROR = -72,              /**< FFT Setup Error */
	SAL_TRIGGER_TIMEOUT = -73,				/**< Measurement trigger timeout in sensor */
	SAL_NO_STREAM_DATA = -74,				/**< Measurement stream problem in sensor */
	SAL_DATA_AVAIL_TIMEOUT = -75,			/**< Measurement data available timeout in sensor */
	SAL_TUNER_NOT_STREAMING = -76,		    /**< Tuner not streaming in sensor */
    SAL_ERR_NUM = -76                       /** this should ALWAYS EQUAL the last valid error message */
} salErrorType;

/** Trigger type
* \enum salTriggerType
 * \ingroup MeasurementControl
 */
typedef enum _salTriggerType {
    salTrigger_absoluteTime =  3,
    salTrigger_relativeTime =  0,      /**< trigger after a specified time has elapsed */
    salTrigger_relativeLevel = 1,      /**< trigger when signal exceeds a threshold by a specified amount */
    salTrigger_absoluteLevel = 2,      /**< trigger when signal exceeds specified level */
} salTriggerType;

/* ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Structs ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ */


/** A Location describes the location of a receiver
 * \ingroup SystemManagement 
 **/
typedef struct _salLocation {
    salFloat64 latitude;         /**< In fractional degrees, southern latitudes are negative numbers */
    salFloat64 longitude;        /**< In fractional degrees, western longitudes are negative numbers */
    salFloat64 elevation;        /**< In meters  */
    char geographicDatum[SAL_MAX_GEOGRAPHIC_DATUM]; /**<  read-only, always set to "WGS-84" */
    salFloat64 eastVel;         /**< velocity toward east, less than 0 means west*/
    salFloat64 northVel;         /**< velocity toward north, less than 0 means south*/
    salFloat64 upVel;         /**< velocity up  */
    char velocity_unit[SAL_MAX_UNIT]; /**< mobile velocity in PVT mode; read-only, always set to "meters_per_second" */
    salUInt32 latitudeType;        /**< latitude type  - reserved for future use*/
    salUInt32 longitudeType;       /**< longitude type - reserved for future use */
    salFloat64 rotation;         /**< In degrees, counter-clockwise from Longitude */
} salLocation;

/** Capabilities of of sensor. See ::salGetSensorCapabilities().
 * \ingroup Session
**/
typedef struct _salSensorCapabilities {
   salInt32 frequencyData;         /**< if non-zero, sensor supports the frequency data interface */
   salInt32 timeData;              /**< if non-zero, sensor supports the time data interface */
   salInt32 fftMinBlocksize;       /**< the minimum FFT blocksize for this sensor */
   salInt32 fftMaxBlocksize;       /**< the maximum FFT blocksize for this sensor */
   salInt32 maxDecimations;        /**< maximum number of sample rate decimations */
   salInt32 hasDmaHardware;         /**< if non-zero, this sensor has DMA hardware, which allows higher data transfer rates */
   salUInt64 rfFifoBytes;           /**< size in bytes of sensor high speed FIFO (gets filled at the tuner sample rate)*/
   salUInt64 dmaBufferBytes;         /**< size in bytes of sensor DMA buffer (for time data, gets filed at the time data sample rate) */
   salInt32 reserved1;              /**< reserved for future use */
   salInt32 reserved2;              /**< reserved for future use */
   salInt32 reserved3;              /**< reserved for future use */
   salFloat64 maxSampleRate;        /**< the maximum FFT blocksize for this sensor */
   salFloat64 maxSpan;              /**< the maximum valid measurement span for this sensor */
   salFloat64 sampleRateToSpanRatio; /**< the ratio of sample rate to valid frequency span */ 
   salFloat64 minFrequency;         /**< the minimum measurable frequency */ 
   salFloat64 maxFrequency;         /**< the maximum measurable frequency */ 
   salFloat64 fReserved1;           /**< reserved for future use */
   salFloat64 fReserved2;           /**< reserved for future use */
   salFloat64 fReserved3;           /**< reserved for future use */
   salFloat64 fReserved4;           /**< reserved for future use */
   salFloat64 fReserved5;           /**< reserved for future use */
   salFloat64 fReserved6;           /**< reserved for future use */
   salFloat64 fReserved7;           /**< reserved for future use */

} salSensorCapabilities; 


/***************************** ^^^^^^^^^^^^^^^^^^^^^^^^^^ ******************************/
/*********************************************************************************
 System functions
 *********************************************************************************/
salErrorType salGetVersion(salUInt32 *version);
salErrorType salGetVersionString(char *version, salUInt32 versionLength);

/***************************** ^^^^^^^^^^^^^^^^^^^^^^^^^^ ******************************/
/*********************************************************************************
 Session functions
 *********************************************************************************/
salErrorType salConnectSensor2(salSensorHandle *sensorHandle, salHandle smsHandle, char *sensorName, char *applicationName, salInt32 options);
salErrorType salGetSensorLocation(salSensorHandle sensorHandle, salLocation *location);
salErrorType salGetSensorCapabilities(salSensorHandle sensorHandle, salSensorCapabilities *capabilities);     
salErrorType salClose(salHandle handle);

/** Lockable sensor resources 
* \enum salResource
 * \ingroup Session
 */
typedef enum _salResource {
  salResource_sensor       = 0x1, /**< Lock all sensor resources */
  salResource_tuner        = 0x2, /**< Lock the tuner (center frequency, sample rate, antenna, attenuation) */
  salResource_fft          = 0x4, /**< Lock the FFT measurement engine */
  salResource_timeData     = 0x8  /**< Lock the time data engine (DDC) */
} salResource;

/** Lock types
* \enum salLock
 * \ingroup Session
 */
typedef enum _salLock {
  salLock_none      = 0,
  salLock_exclusive = 1
} salLock;

/** Information about a resource lock.
 * \ingroup Session */
typedef struct _salLockInfo {
    salLock  type;                          /**< The type of lock */
    char     sessionId[SAL_MAX_SESSION_ID]; /**< String identifying the owner of the lock */
    salUInt32      timestampSeconds;      /**< Integer part of the time the lock was set (in UTC seconds since January 1, 1970). */
    salUInt32      timestampNSeconds;     /**< Fractional part of the the lock was set. */
} salLockInfo;

salErrorType salLockResource(salHandle sensorHandle, salResource resource);
salErrorType salUnlockResource(salHandle sensorHandle, salResource resource);
salErrorType salAbortAll(salHandle sensorHandle);
salErrorType salBreakResourceLock(salHandle sensorHandle, salResource resource);
salErrorType salQueryResource(salHandle sensorHandle, salResource resource, salLockInfo *lockInfo);
salErrorType salReleaseAllResource();




/////////////////////////////////////////////////////////////////////////////////////////////////
//  salFrequency.h
/////////////////////////////////////////////////////////////////////////////////////////////////

typedef enum _salWindowType {
    salWindow_hann,         /**< Hann/Hanning window ( conversion from RBW to FFT bin spacing: 1.5 ) */
    salWindow_gaussTop,     /**< Gausstop window ( conversion from RBW to FFT bin spacing: 2.215349684 ) */
    salWindow_flatTop,      /**< Flattop window  ( conversion from RBW to FFT bin spacing: 3.822108760 ) */
    salWindow_uniform,      /**< Uniform window  ( conversion from RBW to FFT bin spacing: 1.0 ) */
    salWindow_unknown,
} salWindowType;

typedef enum _salAverageType {
    salAverage_off,         /**< No averaging */
    salAverage_rms,         /**< RMS averaging */
    salAverage_peak,        /**< Peak-hold averaging */
    salAverage_unknown
} salAverageType;

typedef enum _salFftDataType {
	salFftData_db,         /**<dBm data from sensor */
	salFftData_mag         /**<v^2 data from sensor */
} salFftDataType;

typedef enum _salOverlapType {
    salOverlap_on,          /**< Use overlap averaging. Note that enum value = 0 for backward comapatability. */
    salOverlap_off,         /**< Do not use overlap averaging. */
} salOverlapType;

typedef enum _salMonitorMode {
   salMonitorMode_off,          /**< Do not use monitor mode */
   salMonitorMode_on       /**< If there is an FFT measurement running on the sensor,
                                    send data in "eavesdrop mode" */
} salMonitorMode;

typedef salUInt32 salFftDataControlMask;  /**< See enum salFFT_DATA_CONTROL */

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
    salFloat64      mixerLevel;       /**< Mixer level in dB; range is -10 to 10 dB, 0 dB is give best compromise between SNR and distortion. */
    salOverlapType  overlapMode;      /**< Control overlap for averaging. Default (0) is to use overlap. */
    salFftDataType  fftDataType;      /**< FFT internal data type */
	salInt32        noTunerChange;    /**< In almost all cases, this parameter should be set to 0. Only set this to non-zero value if you do not want the FFT process to modify tuner parameters. */
	salFftDataControlMask  noDataTransfer;   /**< In almost all cases, this parameter should be set to 0. Set this bitfield to non-zero value to limit data return data for this segment */ 
    salUInt64       levelTriggerControl; /**< for IQ level trigger */
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

typedef struct _salSegmentData {
	salUInt32      userWorkspace;    /**< User-defined value set in ::salSweepParms */
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

typedef struct _salSweepComputationParms {
	salFloat64      startFrequency;   /**< Start frequency for the sweep (Hz) */
	salFloat64      stopFrequency;    /**< Stop frequency for the sweep (Hz) */
	salFloat64      rbw;              /**< Resolution band-width (Hz) */
} salSweepComputationParms;

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

salErrorType salComputeFftSegmentTableSize(salSweepComputationParms *computeParms, salSweepParms *sweepParms,
	salSweepComputationResults *results);

salErrorType salInitializeFftSegmentTable(
	salSweepComputationParms *computeParms, 
	salSweepParms *sweepParms,
	salFrequencySegment *exampleSegment,
	salFrequencySegment *segmentTable,
	salSweepComputationResults *results);

typedef int(*SAL_SEGMENT_CALLBACK)(salSegmentData *dataHdr, salFloat32 *pAmplitude);

salErrorType salStartSweep(salHandle *measHandle, salSensorHandle sensorHandle, salSweepParms *parms, 
                      salFrequencySegment *pSegmentTable, SAL_SEGMENT_CALLBACK dataCallback);

salErrorType salGetSegmentData(
    salHandle             measHandle,
    salSegmentData        *dataHdr,
    salFloat32            *pAmplitude,
    salUInt32             userDataBufferBytes);

typedef enum _salSweepCommand {
    salSweepCommand_stop,         /**< Stop a sweep when the sweep is finished */
    salSweepCommand_abort,        /**< Stop a sweep as soon as possible*/
    salSweepCommand_flush,        /**< Flush the sweep backlog */
   
} salSweepCommand;

salErrorType salSendSweepCommand(salHandle measHandle, salSweepCommand command);



/////////////////////////////////////////////////////////////////////////////////////////////////
//  salTimeData.h
/////////////////////////////////////////////////////////////////////////////////////////////////

/** Time data commands. 
* \enum salTimeDataCmd
 * \ingroup TimeData
 */
typedef enum _salTimeDataCmd {
    salTimeDataCmd_stop,         /**< Stop a time data request, but keep sends data acquired so far */
    salTimeDataCmd_abort         /**< Stop a time data request and discard any data not sent */
} salTimeDataCmd;


typedef struct _salIQSweepParms 
{
	salUInt32        numSweeps;          
	salUInt32        numSegments;        
	salUInt32		 numBlocks;			 
	salUInt32		 numTransferSamples; 
	salDataType      dataType;           
	salInt32         timeTriggerFlag;   
	salUInt32		 sweepInterval;     
	salUInt32		 segmentInterval;	 
	salUInt32        timeTriggerSec;     
	salUInt32        timeTriggerNSec;   
} salIQSweepParms;

typedef struct _salIQSegmentData 
{
	salUInt64		sequenceNumber;      
	salUInt32		segmentIndex;        
	salUInt32		sweepIndex;          
	salDataType		dataType;		     
	salUInt32		numSamples;			 
	salUInt32		shlBits;			 
	salUInt32		timestampSeconds;    
	salUInt32		timestampNSeconds;
	salUInt32       timeAlarms;			 
	salFloat64      scaleToVolts;        
	salFloat64		centerFrequency;     
	salFloat64		sampleRate;          
	salFloat64		latitude;            
	salFloat64		longitude;        
	salFloat64		elevation;        
}salIQSegmentData;

typedef struct _salTunerParms 
{
	salFloat64 centerFrequency;  /**< Tuner center frequency in Hertz */
	salFloat64 sampleRate;       /**< Tuner sample rate in Hertz */
	salFloat64 attenuation;      /**< Front end attenuation in dB (-10 to 30)*/
	salFloat64 mixerLevel;       /**< Mixer level in dB; range is -10 to 10 dB, 0 dB gives best compromise between SNR and distortion. */
	salAntennaType antenna;      /**< Front end input to use */
	salInt32 preamp;             /**< If non-zero, turn preamp on  */
    salInt32 sdramWriting;       /**< non-zero when the FPGA write process is filling capture memory */
} salTunerParms;

typedef enum _salDemodulation {
    salDemodulation_none = 0,	/**< No Demodulation */
    salDemodulation_AM   = 1,	/**< AM Demodulation */
    salDemodulation_FM   = 2,   /**< FM Demodulation */
	salDemodulation_CW   = 3,
} salDemodulation;

typedef struct _salDemodParms 
{
	salFloat64		tunerCenterFrequency;
	salFloat64		tunerSampleRate;
	salFloat64      demodCenterFrequency;     
	salFloat64      demodSampleRate;
	salUInt64       numSamples;          /**< Total number of samples to acquire. 0 means to capture until stopped. */
	salDemodulation demodulation;        /**< Demodulation type */
} salDemodParms;

typedef struct _salDemodData 
{
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

typedef enum _salDemodCmd 
{
	salDemodCmd_stop,
	salDemodCmd_abort
} salDemodCmd;


salErrorType salStartIQSweep(salHandle *measHandle, salSensorHandle sensorHandle, salIQSweepParms *parms, salFrequencySegment *pSegmentTable);
salErrorType salGetIQSweepData(salHandle measHandle, salIQSegmentData *dataHdr, void *userDataBuffer, salUInt32 userDataBufferBytes);
salErrorType salSendIQSweepCommand(salHandle measHandle, salTimeDataCmd command);

salErrorType salSetTuner(salSensorHandle sensorHandle, salTunerParms *parmsIn);
salErrorType salRequestDemodData(salHandle *measHandle, salSensorHandle sensorHandle, salDemodParms *parms);
salErrorType salGetDemodData(salHandle measHandle, salDemodData *dataHdr, void *userDataBuffer, salUInt32 userDataBufferBytes);
salErrorType salSendDemodCommand(salHandle measHandle, salDemodCmd command);
salErrorType salModifyDemodFrequency(salHandle measHandle, salFloat64 centerFrequency);
salErrorType salChangeDemodChannel(salHandle measHandle, salFloat64 channelFreq, salFloat64 demodSampleRate);