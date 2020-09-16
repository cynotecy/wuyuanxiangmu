// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the EISAL_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
#ifndef __EISAL_H
#define __EISAL_H

#ifdef __cplusplus
	extern "C" {
#endif

#ifdef SAL_API_CALL_TYPE
#else 
#ifdef _WIN32
#define SAL_API_CALL_TYPE __stdcall
#else 
#define SAL_API_CALL_TYPE
#endif
#endif


#ifdef EISAL_EXPORTS
	#define SAL_API __declspec(dllexport) salErrorType SAL_API_CALL_TYPE
#else
	#define SAL_API __declspec(dllimport) salErrorType SAL_API_CALL_TYPE
#endif

/* the maximum data buffer size per read is 32768 4-byte complex samples */
#define salRECOMMENDED_DATA_BUFFER_SIZE (32768*2*4)
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

/** Miscellaneous constants used in SAL. 
* \enum salMiscellaneousConstants
 * \ingroup SystemManagement
 */
enum salMiscellaneousConstants {
    SAL_DEFAULT_QUEUED_MSGS  = 10, /**< Default number of data messages that will be queued */
    SAL_MIN_LOCATION_IMAGE_PIXELS = 20, /**< Minimum number of pixels for the height or width of the location image */
    SAL_MAX_LOCATION_IMAGE_PIXELS = 1000, /**< Maximum number of pixels for the height or width of the location image */
    SAL_LOCATION_SPECTRUM_POINTS = 401,  /**< Number of points in the location measurement spectra */
    SAL_LOCATION_CORRELATION_POINTS = 401, /**< Number of points in the location measurement correlation */

    SAL_MIN_AUDIO_SAMPLES = 64,  /**< Minimum blocksize when using demodulation */

};

/** Sensor modes in the ::salSensorStatus structure. 
* \enum salSensorMode
 * \ingroup SystemManagement
 */
typedef enum _salSensorMode {
     salSENSOR_MODE_NONE = 0,          /**< No Measurement             */
     salSENSOR_MODE_TDOA = 3,          /**< TDOA measurement           */
     salSENSOR_MODE_LOOKBACK = 4,      /**< TDOA measurement           */
     salSENSOR_MODE_DEFAULT = 100,     /**< E3238s or IQ measurement   */
     ERR_MODE     = -1                 /**< Error mode                 */  
} salSensorMode;

/** IQ Streaming Data State/Event (bitmap) for the salStateEventMask  
 * \enum salSTATE_EVENT
 * \ingroup MeasurementData
 */
typedef enum _salSTATE_EVENT {
    salSTATE_SAMPLE_LOSS             = 0x01,    /**< Indicates that this data block is not contiguous with previous block */
    salSTATE_OVER_RANGE              = 0x02,    /**< RF Sensor input overload */
    salSTATE_MEASUREMENT_ERROR       = 0x04,    /**< Measurement hardware error */
   	salSTATE_SETUP_NOT_USER          = 0x08,    /**< The measurement setup is different than requested */
    salSTATE_LAST_BLOCK              = 0x10,    /**< This is the last block of data for the current measurement */
	salSTATE_OSCILLATOR_ADJUSTED     = 0x20,    /**< If set, the sensor clock reference oscillator was adjusted during the measurement  */
	salSTATE_CPU_OVERLOAD            = 0x100,   /**< If set, the sensor's CPU is compute bound */
	salSTATE_SYNC_PROBLEM            = 0x200    /**< If set, the sensor's synchronization is suspect */
} salSTATE_EVENT;

/** IQ Streaming Data change indicators (bitmap) for the salChangeMask 
 * \enum salCHANGE
 * \ingroup MeasurementData
 */
typedef enum _salCHANGE {
    salCHANGE_BANDWIDTH       = 0x01,    /**< Data bandwidth changed */
    salCHANGE_RF_REF_FREQ     = 0x02,    /**< Data center frequency changed */
    salCHANGE_SCALE_TO_VOLTS  = 0x04,    /**< Data scale changed */
    salCHANGE_DATA_FULL_SCALE = 0x08,    /**< Data full scale changed */
    salCHANGE_ATTENUATION     = 0x10,    /**< RF sensor attenuation changed */
    salCHANGE_SAMPLE_RATE     = 0x20,    /**< Data sample rate changed */
    salCHANGE_TEMPERATURE     = 0x40,    /**< Sensor RF board temperature changed */
    salCHANGE_ANTENNA         = 0x80     /**< Sensor RF antenna input changed */
} salCHANGE;

/** IQ change indicators (bitmap) for the salChangeGpsMask and salValidGpsMask 
 * \enum salGPS_INDICATOR
 * \ingroup MeasurementData
 */
typedef enum _salGPS_INDICATOR {
    salGPS_INDICATOR_LATITUDE    = 0x01,   /**< Latitude is valid or has changed  */
    salGPS_INDICATOR_LONGITUDE   = 0x02,   /**< Longitude is valid or has changed  */
    salGPS_INDICATOR_ALTITUDE    = 0x04,   /**< Altitude is valid or has changed  */
    salGPS_INDICATOR_SPEED       = 0x08,   /**< Speed is valid or has changed  */
    salGPS_INDICATOR_HEADING     = 0x10,   /**< Heading is valid or has changed  */
    salGPS_INDICATOR_TRACK_ANGLE = 0x20,   /**< Track angle is valid or has changed  */
    salGPS_INDICATOR_MAGNETIC_VARIATION = 0x40 /**< Magnetic variation is valid or has changed  */
} salGPS_INDICATOR;

/** RF Status (bitmap) for the salRFStatusMask 
 * \enum salRfStatusBits
 * \ingroup MeasurementData
 */
typedef enum _salRfStatusBits {
    salLO_UNLOCK            = 0x01,  /**< Local oscillator became unlocked */
    salRF_TEMP_HIGH         = 0x2,   /**< RF board temperature is high */
    salRF_SETUP_ERROR       = 0x4,   /**< error setting up RF hardware */
    salCORRECTIONS_DISABLED = 0x8,   /**< corrections are disabled     */
} salRfStatusBits;

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

/** Data Channel Handle
 * \ingroup Session */
typedef salHandleType salDataStreamHandle;
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

/** Configuration for salAntenna_Auto
 * \ingroup Session
 */
typedef struct _salAntennaAuto {
	salFloat64 startFreq;     /**< Start frequency for this frequency band */
	salFloat64 stopFreq;      /**< Stop frequency for this frequency band */
	salFloat64 attenuation;   /**< attenuation for this frequency band */
	salFloat64 mixerLevel;    /**< mixerLevel for this frequency band */
	salInt32 preamp;          /**< preamp for this frequency band */
	salAntennaType antenna;   /**< antenna for this frequency band */
} salAntennaAuto;

/** IQ  Mode 
  * \enum salIqMode
  * \ingroup MeasurementData
*/
typedef enum _salIqMode {
    salIQ_MODE_STREAM,  /**< Stream continuous data at specified sample rate */
    salIQ_MODE_BLOCK    /**< Capture specified number of samples */
} salIqMode;

/** Data Protocols 
  * \enum salDataProtocol
  * \ingroup MeasurementData 
  */
typedef enum _salDataProtocol {
    salDATA_PROTOCOL_UDP, /**< Use User Datagram Protocol (stream mode only, packets may be lost or delivered out-of-sequence) */   
    salDATA_PROTOCOL_TCP  /**< Use Transmission Control Protocol (stream or block mode) */ 
}salDataProtocol;

/** Services
  * \enum salService
  * \ingroup MeasurementControl 
  */
typedef enum _salService {
    salSERVICE_NONE,        /**< Undefined mode */
    salSERVICE_IQ,          /**< IQ data (may be streaming or block mode, see ::salIqMode) */
    salSERVICE_DIAGNOSTICS  /**< Run diagnostic tests */
} salService;

/** For localization.
  * \enum salLocalization
  * \ingroup Error
  */
typedef enum _salLocalization {
    salEnglish           /**< English language */
} salLocalization;

/** IQ Measurement Command 
  * \enum salIqCommand
 * \ingroup MeasurementControl
 **/
typedef enum _salIqCommand {
    salIQ_COMMAND_FLUSH_FIFO,  /**<  Clear all data from the sensor FIFO; valid only when streaming real-time data. */
    salIQ_COMMAND_STOP_ACQUISITION, /**< Stop acquiring data, but send what has been acquired so far; valid only when streaming real-time data.
                                     * The measurement state will be salIQ_STATE_STREAMING_TRANSFER while there is data in the FIFO. 
                                     * The measurement state will change to salIQ_STATE_STOPPED when the FIFO is empty. */
} salIqCommand;

/** Decimation type
 * \enum salDecimation
 * \ingroup Session
 */
typedef enum _salDecimation {
    salDECIMATION_NONE,     /**< No decimation supported */
    salDECIMATION_BY_2,     /**< Decimation by two supported */
    salDECIMATION_BY_5,     /**< Decimation by five supported */
    salDECIMATION_VARIABLE, /**< Arbitrary decimation supported */
    salDECIMATION_UNKNOWN   /**< Decimation capability unknown */
} salDecimation;

/** IEEE1588_STATE
 * \enum salIeee1588State
 * Caution: only valid when 1588 is in operation
 * \ingroup Session
 */
typedef enum _salIeee1588State {
	SAL_PTP_POWERUP=0,	
	SAL_PTP_INITIALIZING=1,	
	SAL_PTP_FAULTY=2,
	SAL_PTP_DISABLED=3,
	SAL_PTP_LISTENING=4,
	SAL_PTP_PRE_MASTER=5,
	SAL_PTP_MASTER=6,
	SAL_PTP_PASSIVE=7,
	SAL_PTP_UNCALIBRATED=8,
	SAL_PTP_SLAVE=9
} salIeee1588State;

/** Time Alarm bitfield
 * \enum salTimeAlarms
 * \ingroup Session
 */
typedef enum _salTimeAlarms {
	TIME_INIT_PROBLEM		= 0x01,
	TIME_QUESTIONABLE		= 0x02,
	TIME_GPS_ANTENNA		= 0x04,
	TIME_GPS_SATELLITE		= 0x08,
	TIME_DAC_CAL_ERROR		= 0x10,
	TIME_GPS_DRIFT			= 0x20,
	TIME_DAC_QUESTIONABLE	= 0x40
} salTimeAlarms;

/** Spectrum Analyzer Alarm bitfield
 * \enum salSpectrumAnalyzerAlarms
 * (future)
 * \ingroup Session
 */
typedef enum _salSpectrumAnalyzerAlarms {
	SA_INIT_PROBLEM		= 0x01
} salSpectrumAnalyzerAlarms;

/** System Alarm bitfield
 * \enum salSystemAlarms
 * \ingroup Session
 */
typedef enum _salSystemAlarms {
	SYSTEM_INIT_PROBLEM					= 0x001,
	SYSTEM_LEARN_ENV_IN_OPERATION		= 0x002,
	SYSTEM_LEARN_ENV_RESULTS_READY		= 0x004,
	SYSTEM_PORTAL_COMMUNICATION_PROBLEM = 0x008,
	SYSTEM_FPGA_IMAGE_PROBLEM			= 0x010,
	SYSTEM_INCOMPATIBLE_SMS				= 0x020,
	SYSTEM_DAC_CAL_IN_OPERATION         = 0x040,
	SYSTEM_ADC_DCM_UNLOCK_PROBLEM		= 0x080,
	SYSTEM_SDRAM_DCM_UNLOCK_PROBLEM		= 0x100,
	SYSTEM_1588_DCM_UNLOCK_PROBLEM		= 0x200
} salSystemAlarms;

/** System Alarm bitfield
 * \enum salSystemAlarms
 * \ingroup Session
 */
typedef enum _salIntegrityAlarms {
	INTEGRITY_FREQ_QUESTIONABLE    = 0x001,
	INTEGRITY_TEMP_QUESTIONABLE    = 0x002,
	INTEGRITY_TEMPERATURE_SHUTOFF  = 0x004,
	INTEGRITY_POWER_DOWN_CONDITION = 0x008,
	INTEGRITY_CALIBRATION_PROBLEM  = 0x010,
	INTEGRITY_TAMPER_SWITCH        = 0x020,
	INTEGRITY_WATCHDOG_SWITCH      = 0x040,
	INTEGRITY_GPS_TX_SWITCH        = 0x080,
	INTEGRITY_CPU_OVERLOAD         = 0x100
} salIntegrityAlarms;

/** Sensor Capability Attributes
  * Used in the salGetSensorAttribute() function
  * \enum salSensorAttribute
  * \ingroup Session
  */
typedef enum _salSensorAttribute {

    salATTRIBUTE_COMPLEX_SAMPLE_RATE_MAX,     /**< returns salFloat64; value is the maximum sample rate in complex samples per second */

    salATTRIBUTE_DECIMATION_MAX,              /**< returns salInt32; value is the maximum number of times the maximum complex sample rate can be divided by two */
    salATTRIBUTE_DECIMATION_TYPE,             /**< returns salInt32; value is one of the ::salDecimation enumerated values indicating the type of decimation supported */

    salATTRIBUTE_FREQ_SPAN_FULL,             /**< returns salFloat64; value is valid analog frequency span in Hertz at maximum sample rate */
    salATTRIBUTE_FREQ_SPAN_DECIMATING,       /**< returns salFloat64; value is ratio of (sample rate)/(valid freq span) when decimating; muliply the sample rate by this value to get the valid bandwidth */

    salATTRIBUTE_MEASURABLE_FREQ_MIN,        /**< returns salFloat64; value is the lowest valid frequency in Hertz that can be measured by the sensor */
    salATTRIBUTE_MEASURABLE_FREQ_MAX,        /**< returns salFloat64; value is the highest valid frequency in Hertz that can be measured by the sensor */

    salATTRIBUTE_CENTER_FREQ_MIN,            /**< returns salFloat64; value is the lowest value in Hertz to which the center frequency can be set */
    salATTRIBUTE_CENTER_FREQ_MAX,            /**< returns salFloat64; value is the highest value in Hertz to which the center frequency can be set */
    salATTRIBUTE_CENTER_FREQ_RESOLUTION,     /**< returns salFloat64; value is the resolution in Hertz of the center frequency setting */
        
    salATTRIBUTE_RESAMPLER_CAPABILITY,       /**< returns salInt32; value is 1 if resampling is supported, 0 if not */
            
    salATTRIBUTE_ATTENUATION_MIN,            /**< returns salFloat64; value is the minimum attenuation in dB supported by the sensor (negative attenuation means gain) */
    salATTRIBUTE_ATTENUATION_MAX,            /**< returns salFloat64; value is the maximum attenuation in dB supported by the sensor */
    salATTRIBUTE_ATTENUATION_STEP,           /**< returns salFloat64;  value is the attenuation step size in dB supported by the sensor  */

    salATTRIBUTE_PREAMPLIFIER_CAPABILITY,    /**< returns salInt32; returns 1 if the sensor supports a preamplifier and 0 if it does not */
    
    salATTRIBUTE_IQ_CHANNELS_MAX,           /**< returns salInt32; returns the number of narrowband channels supported by the sensor */

    salATTRIBUTE_IQ_SAMPLES_MIN,            /**< returns salInt32; value is the minimum blocksize supported by block and streaming modes */
    salATTRIBUTE_IQ_SAMPLES_MAX_16BIT,      /**< returns salInt32; value is the maximum number of samples that can be captured in block mode using 16 bit samples */
    salATTRIBUTE_IQ_SAMPLES_MAX_32BIT,      /**< returns salInt32; value is the maximum number of samples that can be captured in block mode using 32 bit samples*/

    salATTRIBUTE_SAMPLES_PER_XFER_MAX_TCP, /**< returns salInt32; value is the maximum number of samples that can be transferred to the user application in one function call in
                                                 block or streaming mode */
    salATTRIBUTE_SAMPLES_PER_XFER_MAX_UDP, /**< returns salInt32; value is the maximum number of samples that can be transferred to the user application in one function call in
                                                 streaming mode when using the UDP protocol */
     
    salATTRIBUTE_MODEL_NUMBER,               /**< returns character array terminated by NULL */
    salATTRIBUTE_SERIAL_NUMBER,              /**< returns character array terminated by NULL */

    salATTRIBUTE_SENSOR_NAME,                /**< returns character array terminated by NULL; value is the SMS name of the sensor */
    salATTRIBUTE_HOSTNAME,                   /**< returns character array terminated by NULL; value is the hostname of the sensor */

    salATTRIBUTE_DATE,                      /**< returns character array terminated by NULL; value is sensor time and date (e.g. Wed Jul 15 16:14:20 UTC 2009) */

    salATTRIBUTE_FFT_POINTS_MIN,           /**< returns salInt32; returns the minimum size of FFT that can be requested from the sensor */
    salATTRIBUTE_FFT_POINTS_MAX,            /**< returns salInt32; returns the maximum size of FFT that can be requested from the sensor */

    salATTRIBUTE_DMA_HW,                   /**< returns salInt32; if non-zero, this sensor has DMA hardware, which allows higher data transfer rates */

    salATTRIBUTE_LO_ADJ_MODE,              /**< [in|out] sets/gets current sensor LO adjustment mode */
    salATTRIBUTE_TIME_SYNC_MODE,           /**< [in|out] salInt32  sets/gets the time sync mode. See ::salTimeSync enumerated values */

    salATTRIBUTE_TUNER_FIFO_BYTES,          /**< [out] salUInt64; gets the size in bytes of the high speed sensor FIFO*/
    salATTRIBUTE_DMA_BUFFER_BYTES,          /**< [out] salUInt64; gets the size in bytes of the sensor DMA buffer */

	salATTRIBUTE_IEEE1588_STATE,            /**< [out] gets current IEEE1588 state (int32, see salIeee1588State) */
	salATTRIBUTE_IEEE1588_DOMAIN,           /**< [in|out] sets/gets current IEEE1588 domain (uint32) */
	salATTRIBUTE_IEEE1588_PRIORITY1,        /**< [in|out] sets/gets current IEEE1588 priority1 (uint32) */
	salATTRIBUTE_IEEE1588_PRIORITY2,        /**< [in|out] sets/gets current IEEE1588 priority2 (uint32) */

	salSENSOR_VARIANCE,                     /**< [out] gets current "overall" sensor time-sync variance (double, sec^2) */
	salSENSOR_OFFSET,                       /**< [out] gets current "overall" sensor time-sync "offset from master" (double, sec) */
	salIEEE1588_VARIANCE,                   /**< [out] gets current sensor IEEE1588 variance (double, sec^2) */
	salIEEE1588_OFFSET,                     /**< [out] gets current sensor IEEE1588 "offset from master" (double, sec) */
	salGPS_VARIANCE,                        /**< [out] gets current sensor GPS variance (double, sec^2) */
	salGPS_OFFSET,                          /**< [out] gets current sensor GPS "offset from GPS module" (double, sec) */
	salFPGA_VARIANCE,                       /**< [out] gets current sensor FPGA variance (double, sec^2) */
	salFPGA_OFFSET,                         /**< [out] gets current sensor FPGA "offset from PHY or GPS module" (double, sec) */

	salCPU_1MIN,                            /**< [out] gets 1 minute exp averaged run-queue length, an estimate of CPU load (float) */
	salCPU_5MIN,                            /**< [out] gets 5 minute exp averaged run-queue length, an estimate of CPU load (float) */
	salCPU_10MIN,                           /**< [out] gets 10 minute exp averaged run-queue length, an estimate of CPU load (float) */

	salVARIANCE_ALARM_THRESHOLD,            /**< [in|out] sets/gets current variance alarm threshold (double, sec^2) */
	salOFFSET_ALARM_THRESHOLD,              /**< [in|out] sets/gets current time offset alarm threshold (double, sec) */
	salCPU_ALARM_THRESHOLD,                 /**< [in|out] sets/gets run-queue length alarm threshold (float, 0 to N) */

	salRF_TEMPERATURE,						/**< [out] RF Board temperature (double, deg C) */
	salDIG_TEMPERATURE,						/**< [out] Digital Board temperature (double, deg C) */

	salUP_TIME,								/**< [out] Up-time (float, sec) */
	salIDLE_TIME,							/**< [out] Idle-time (float, sec) */

	salTIME_ALARMS,							/**< [out] Time alarm bitfield (unit32, see salTimeAlarms) */
	salSA_ALARMS,							/**< [out] Spectrum Analyzer alarm bitfield (unit32, see salSpectrumAnalyzerAlarms) */
	salSYS_ALARMS,							/**< [out] System alarm bitfield (unit32, see salSystemAlarms) */
	salINTEG_ALARMS,						/**< [out] Integrity alarm bitfield (unit32, see salIntegrityAlarms) */

	salATTRIBUTE_NUM                        /**< Number of enums in this type */
} salSensorAttribute;

/** IQ specific Attributes
  * \enum salIqAttribute
  * \ingroup MeasurementControl
  */
typedef enum _salIqAttribute {
    salIQ_ATTRIBUTE_DELAY_MAX_SECONDS,      /**< returns salFloat64; value is maximum amount of data (in seconds) that will be buffered in the sensor before the data is discarded */
    salIQ_ATTRIBUTE_DELAY_SECONDS,          /**< returns salFloat64; value is amount of data (in seconds) currently buffered in the sensor */
    salIQ_ATTRIBUTE_LAST_SEQUENCE_NUMBER,   /**< returns salInt32; value is the sequence number of the last data message that was successfully sent by the sensor  */
    salIQ_ATTRIBUTE_STATE,                  /**< returns salInt32; value is one of the ::salIqState enumerated values */
    salIQ_ATTRIBUTE_USER_STREAM_ID,         /**< returns salInt32; value is salIqArg.id set by user when salIqStart() was called */

    salIQ_ATTRIBUTE_XFER_SAMPLES_MAX,       /**< returns salInt32; value is the maximum number of samples that will be returned at one time (either by callback or salIqGetData) with current parameters*/
    salIQ_ATTRIBUTE_XFER_BYTES_MAX,         /**< returns salInt32; value is the maximum number of bytes that will be returned at one time (either by callback or salIqGetData) with current parameters*/

    salIQ_ATTRIBUTE_NUM_SAMPLES,             /**< returns salInt32; when streaming, the number of samples per callback. In block mode, the total number of samples that will be captured.  */  
    salIQ_ATTRIBUTE_SAMPLE_RATE,             /**< returns salFloat64; value is the current sample rate in samples/sec */
    salIQ_ATTRIBUTE_CENTER_FREQUENCY,        /**< returns salFloat64; value is the current center frequency in Hertz */
    salIQ_ATTRIBUTE_ATTENUATION,             /**< returns salFloat64; value is the current attenuation */
    salIQ_ATTRIBUTE_PREAMP,                  /**< returns salInt32; value is 1 if the preamp is on and 0 if it is off  */  
    salIQ_ATTRIBUTE_ANTENNA,                 /**< returns salInt32; value is the current antenna channel (antenna numbers start at 0.) */  
    salIQ_ATTRIBUTE_IQ_MODE,                 /**< returns salInt32; value is of type ::salIqMode indicating if the mode is block or streaming  */  
    salIQ_ATTRIBUTE_DATA_TYPE,               /**< returns salInt32;  value is of type ::salDataType indicating current data type  */  
    salIQ_ATTRIBUTE_NUM                       /**< Number of enums in this type */
} salIqAttribute;

/** Events received from the sensor
  * \enum salEventType
  * \ingroup MeasurementControl
  */
typedef enum _salEventType {
    salEVENT_SHUTDOWN,      /**< The sensor powered off */
    salEVENT_DISCONNECTED,       /**< The connection to the sensor was terminated by another application */
    salEVENT_COMM_ERROR,    /**< The sensor failed to send or read a message */
    salEVENT_UNKNOWN,       /**< An unknown event occurred */
} salEventType;

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

/** IQ Measurement States
  * \enum salIqState
  * \ingroup MeasurementControl
  */
typedef enum _salIqState {
    salIQ_STATE_NONE,
    salIQ_STATE_INIT,                    /**< initial state (idle)      */
    salIQ_STATE_STOPPED,                /**< stopped (idle)            */
    salIQ_STATE_STREAMING,                /**< (Streaming mode only) streaming, real time      */
    salIQ_STATE_STREAMING_TRANSFER,     /**< (Streaming mode only) acquisition stopped, but there is still data in sensor memory */
    salIQ_STATE_WAITING_FOR_TRIGGER,    /**< waiting for trigger   */
    salIQ_STATE_BLOCK_ACQUISITION,      /**< (Block mode only) acquiring a block of data */
    salIQ_STATE_BLOCK_TRANSFER,         /**< (Block mode only) transferring a block       */
  
    salIQ_STATE_NUM                    /**< Number of enums in this type */
} salIqState;


/** Specifies which action to take if maxBufferSeconds is exceeded in the streaming mode.
 * \enum salMaxBufferAction
 * \ingroup MeasurementControl
 */
typedef enum _salMaxBufferAction {
    salMaxBufferAction_flush,                /**< Discard data in sensor FIFO and continue acquiring data */
    salMaxBufferAction_stopAcquistion        /**< Stop acquiring data, but keep sending data until FIFO is empty. 
                                             * The measurement state will be salIQ_STATE_STREAMING_TRANSFER while there is data in the FIFO. 
                                             * The measurement state will change to salIQ_STATE_STOPPED when the FIFO is empty */
} salMaxBufferAction;

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

/** For receiving a sensor event 
 * \ingroup MeasurementControl
 */
typedef struct _salEvent 
{
    salEventType type;                   /**< Indicates the type of event */
    salUInt32 time;                      /**< Time that the event occurred in seconds UTC */
    char msg[SAL_MAX_EVENT_MSG_LEN];     /**< Additional details about the event */
    char name[SAL_MAX_EVENT_MSG_LEN];    /**< Sensor name */
} salEvent;

/** Request block for IQ streaming.
 * \ingroup MeasurementControl
 **/
typedef struct _salIqParameters {
    salUInt32  numSamples;             /**<       Number of samples */
    salFloat64 sampleRate;             /**<       Sample rate in Hertz */
    salFloat64 centerFrequency;        /**<       Center frequency in Hertz */
    salFloat64 attenuation;            /**<       IF attenuation in dB */
    salUInt32  preamp;                 /**<    pre-amp on/off  */
    salAntennaType  antenna;           /**<    which antenna input */
    salIqMode  iqMode;                 /**<    IQ Streaming or IQ Block Mode */
    salDataType dataType;              /**<    16 bit or 32 bit resolution */
    salFloat64 maxBufferSeconds;       /**<    For real-time streaming, the maximum sensor FIFO memory in seconds */
    salMaxBufferAction maxBufferAction;  /**<  For real-time streaming, what to do if maxBufferSeconds is exceeded */
} salIqParameters;



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

/** Information pertaining to a particular sensor 
 * \ingroup SystemManagement */
typedef struct _salSensorStatus {
    
    char name[SAL_MAX_SENSOR_NAME];           /**< Sensor name of the sensor (i.e. the SMS "alias"). */
    char hostName[SAL_MAX_SENSOR_HOSTNAME];   /**< Hostname of the sensor.*/

    char userHostName[SAL_MAX_SENSOR_HOSTNAME];        /**< Hostname of the host using the sensor.*/
    char userApplicationName[SAL_MAX_APPLICATION_NAME]; /**< Name of application running on the sensor.*/ 

    salUInt32 lastHeardFrom;   /**< Time (in seconds since January 1, 1970) that the sensor last reported measurement or status information */
    salLocation location;      /**< Location of the sensor when the SensorStatus was generated */

    salInt16 currentMode;     /**< Last mode as reported by the sensor; values are defined by ::salSensorMode enum */

    salInt16 timeSyncAlarms;/**< Last time synch alarm as reported by the sensor (bit map of ::salTimeAlarm values) */

    salInt16 systemAlarms; /**< Last status system alarm as reported by the sensor

     - Bit 0 : Operating          (0 = Operating, 1 = Operation Suspended)
     - Bit 1 : Learn Environment  (0 = Learn Env Not In-progress, 1 = Learn Env In-progress)
     - Bit 2 : Last Learn Env     (0 = Succeeded, 1 = Failed)
     - Bit 3 : SMS Communications (0 = Ok, 1 = Questionable)
     - Bit 4 : FPGA Image         (0 = FPGA Using Primary Image, 1 =  FPGA Using Backup Image)

     */

    salInt16 integrityAlarms; /**< Last integrity alarm as reported by the sensor

      - Bit 0 : Frequency Condition    (0 = Freq Ok, 1 = Freq Questionable)
      - Bit 1 : Temperature Condition  (0 = Temp Ok, 1 = Temperature Questionable)
      - Bit 2 : Temperature Shutdown   (0 = Temp Ok, 1 = Temperature Shutdown Pending)
      - Bit 3 : RF Power               (0 = Powered Up, 1 = Powered Down)
      - Bit 4 : Calibration Condition  (0 = Cal Ok, 1 = Cal Questionable)
      - Bit 5 : Tamper Switch          (0 = Case Closed, 1 = Case Open)
      - Bit 6 : Watchdog Switch        (0 = Watchdog Enabled, 1 =Watchdog Disabled)
      - Bit 7 : GPS TX Switch          (0 = GPS TX Enabled, 1 = GPS TX Disabled) */
    
} salSensorStatus;

/** Information pertaining to a particular sensor 
 * \ingroup SystemManagement */
typedef struct _salSensorStatus2 {
    
    char name[SAL_MAX_SENSOR_NAME];           /**< Sensor name of the sensor (i.e. the SMS "alias"). */
    char hostName[SAL_MAX_SENSOR_HOSTNAME];   /**< Hostname of the sensor.*/
    char ipAddress[SAL_MAX_SENSOR_HOSTNAME];   /**< IP address of the sensor.*/

    char userHostName[SAL_MAX_SENSOR_HOSTNAME];        /**< Hostname of the host using the sensor.*/
    char userApplicationName[SAL_MAX_APPLICATION_NAME]; /**< Name of application running on the sensor.*/ 

    salUInt32 lastHeardFrom;   /**< Time (in seconds since January 1, 1970) that the sensor last reported measurement or status information */
    salLocation location;      /**< Location of the sensor when the SensorStatus was generated */

    salInt16 currentMode;     /**< Last mode as reported by the sensor; values are defined by ::salSensorMode enum */

    salInt16 timeSyncAlarms;/**< Last time synch alarm as reported by the sensor (bit map of ::salTimeAlarm values) */

    salInt16 systemAlarms; /**< Last status system alarm as reported by the sensor

     - Bit 0 : Operating          (0 = Operating, 1 = Operation Suspended)
     - Bit 1 : Learn Environment  (0 = Learn Env Not In-progress, 1 = Learn Env In-progress)
     - Bit 2 : Last Learn Env     (0 = Succeeded, 1 = Failed)
     - Bit 3 : SMS Communications (0 = Ok, 1 = Questionable)
     - Bit 4 : FPGA Image         (0 = FPGA Using Primary Image, 1 =  FPGA Using Backup Image)

     */

    salInt16 integrityAlarms; /**< Last integrity alarm as reported by the sensor

      - Bit 0 : Frequency Condition    (0 = Freq Ok, 1 = Freq Questionable)
      - Bit 1 : Temperature Condition  (0 = Temp Ok, 1 = Temperature Questionable)
      - Bit 2 : Temperature Shutdown   (0 = Temp Ok, 1 = Temperature Shutdown Pending)
      - Bit 3 : RF Power               (0 = Powered Up, 1 = Powered Down)
      - Bit 4 : Calibration Condition  (0 = Cal Ok, 1 = Cal Questionable)
      - Bit 5 : Tamper Switch          (0 = Case Closed, 1 = Case Open)
      - Bit 6 : Watchdog Switch        (0 = Watchdog Enabled, 1 =Watchdog Disabled)
      - Bit 7 : GPS TX Switch          (0 = GPS TX Enabled, 1 = GPS TX Disabled) */
    
} salSensorStatus2;

/** GPS measured location information 
 * \ingroup MeasurementData
 * \remarks The latitude, longitude, etc. fields are only valid when the corresponding bit of the valid field is 1.
 *          For the sensor, only the latitude, longitude, and elevation fields are ever valid.
 *          The changeIndicator is used to indicate that a value has changed from its previous value. The changeIndicator
 *          for all valid fields will be set true on the first block of all measurements.
 **/
typedef struct _salGPS{
    salUInt32     version;                    /**< GPS descriptor version */
    salUInt32     reserved1;                  /**< Reserved for future use */
    salUInt32     reserved2;                  /**< Reserved for future use */

    salValidGpsMask valid;                    /**< bitmap indicates which GPS values are valid (see ::salGPS_INDICATOR for bit values) */
    salChangeGpsMask changeIndicator;         /**< bitmap indicates which GPS values have changed (see ::salGPS_INDICATOR for bit values) */

    salFloat64    latitude;                   /**< Sensor latitude in degrees; -90 (South) to +90 (North)   */
    salFloat64    longitude;                  /**< Sensor longitude in degrees; -180 (West) to +180 (East)  */
    salFloat64    altitude;                   /**< Sensor altitude in meters   */
    salFloat64    speed;                      /**< Sensor speed in meters/second over ground  */
    salFloat64    heading;                    /**< Sensor orientation with respect to true North in decimal degrees; 0 (North) to ~359.999999 degrees  */
    salFloat64    trackAngle;                 /**< Sensor direction of travel with respect to true North in decimal degrees; 0 (North) to ~359.999999 degrees  */
    salFloat64    magneticVariation;          /**< Magnetic North variation from true North in decimal degrees (-180 (West) to +180 (East))  */
    } salGPS;

/** IQ Data description header
 * \ingroup MeasurementData
 * \remarks When one of the measurement setup values (antenna, bandwidth, etc.) changes, the corresponding bit in the
 *          changeIndicator is set to 1. All bits in the changeIndicator are set to 1 for the first block of every measurement.
 **/
typedef struct _salIqData {
    salUInt32      version;                     /**< salIqData version. */
    salUInt32      sequenceNumber;              /**< Starts at 0; incremented by 1 for each data block.  */
    salUInt32      numSamples;                  /**< Number of IQ data pairs in this data block.  */
    salDataType    dataType;                    /**< Complex 16 bit OR Complex 32 bit. */
    salHandleType  streamIdentifier;            /**< Handle of the data stream that is returning this data. */
	salUInt32         userWorkspace;               /**< Value set by the workspace parameter in the call to salIqOpenDataStream().  */
    salUInt32      userStreamId;                /**< Value set by salIqArg.id in the call to salIqStart(). */
    salUInt32      timestampSeconds;            /**< Integer part of the timestamp (in UTC seconds since January 1, 1970). */
    salUInt32      timestampNSeconds;           /**< Fractional part of the timestamp (in Nanoseconds). */
    salStateEventMask stateEventIndicator;      /**< Mask of indicators for various conditions (see ::salSTATE_EVENT). */
    salRFStatusMask rfStatus;                   /**< Status of the RF Sensor RF hardware (bitmap); see the ::salRfStatusBits.  */
    salChangeMask  changeIndicator;             /**< Bitmap indicating data description values that have changed during this data block
                                                     (see ::salCHANGE for bit values).*/
    
    salAntennaType antenna;                     /**< Antenna input active for this data block. */
    salFloat64     bandwidth;                   /**< Useable RF bandwidth in Hertz. */
    salFloat64     centerFrequency;             /**< RF center frequency in Hertz for this data block. */
    salFloat64     scaleToVolts;                /**< Multiply data samples by this value to convert to Volts.   */
    salFloat64     dataFullScale;               /**< Max possible data value (in Volts). */
    salFloat64     attenuation;                 /**< Attenuation in dB; negative values indicate gain.  */
    salFloat64     sampleRate;                  /**< Sample rate in Hertz.  */
    salFloat64     temperature;                 /**< Degrees C measured on RF sensor analog hardware (temperature that may affect the signal). */
    
    salGPS         gpsGeolocation;              /**< Position description at time meaurement was made. */
    void *data;
} salIqData;

/** IQ Data collection parameter
 * \ingroup MeasurementControl
**/
typedef struct _salIqArg {
    salUInt32 reserved1;          /**< reserved for future use */
    salUInt32 reserved2;          /**< reserved for future use */
    salUInt32 reserved3;          /**< reserved for future use */
    salUInt32 id;              /**< A user-defined id that will be returned in the salIqData.userStreamId field with each IQ data block. */
} salIqArg;


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

/** IQ data callback function prototype.
 * \param iqData [out] IQ Header plus data.
 * \remarks The user callback function should return a value of 0. If the callback function returns a non-zero value
 *          the callback function will be called again with the same data. Calling
 *          SAL functions (other than salGetErrorString()) from the callback function can result in unpredictable behavior.
 * \ingroup MeasurementControl
 **/
#ifdef MATLAB_LOADLIBRARY_COMPILE
// The Matlab loadlibrary.m mechanism does not support functions with callbacks
typedef void *SAL_IQ_DATA_CALLBACK;
#else
typedef int(*SAL_IQ_DATA_CALLBACK)(salIqData *iqData);
#endif


/** Sensor event callback function prototype.
 * \param sensorEvent Pointer to a structure describing the event that occurred.
 * \param userWorkspace value that was set when the callback was registered.
 * \ingroup Session
 **/
#ifdef MATLAB_LOADLIBRARY_COMPILE
// The Matlab loadlibrary.m mechanism does not support functions with callbacks
typedef void *SAL_EVENT_CALLBACK;
#else
typedef void(*SAL_EVENT_CALLBACK)(salEvent *sensorEvent, salUInt32 userWorkspace);
#endif
  
/** Flow Control
  * \ingroup Session
  * Parameters that control measurement flow control from the Rf Sensor
  */
typedef struct _salFlowControl {
	salInt32 pacingPolicy;        /**< Pacing policy, 0 == disabled (no pacing), 1 == wait when full policy, 2 == flush when full policy */
	salFloat32 maxBacklogSeconds; /**< Max backlogSeconds, 0 == disabled */
	salFloat32 maxBytesPerSec;    /**< TX data rate threshold, 0 == disabled */
	salInt32 maxBacklogBytes;     /**< Max bytes threshold, 0 == disabled */
	salInt32 maxBacklogMessages;  /**< Max messages threshold, 0 == disabled */
} salFlowControl;

/***************************** ^^^^^^^^^^^^^^^^^^^^^^^^^^ ******************************/
/*********************************************************************************
 System functions
 *********************************************************************************/
SAL_API salGetVersion( salUInt32 *version);
SAL_API salGetVersionString(char *version, salUInt32 versionLength);
SAL_API salSetSMSAddress(char *hostname, salUInt16 port, char *directory);
SAL_API salGetSMSAddress(char *hostname, salUInt16 *port, char *directory);
SAL_API salGetSMSAddressSafe(char *hostname, salUInt32 hostnameSize, salUInt16 *port, char *directory, salUInt32 directorySize);
SAL_API salOpenSms(salHandle *smsHandle, char *hostname, salUInt16 port, char *directory);
SAL_API salQuerySmsExceptionString( char *buffer, salUInt32 bufSize);
SAL_API salOpenSensorList(salHandleType *sensorList, salUInt32 *numSensors);
SAL_API salOpenSensorList2(salHandle *sensorList, salHandle smsHandle, salUInt32 *numSensors);
SAL_API salGetNextSensor(salHandle sensorList, salSensorStatus *sensorStatus);
SAL_API salGetNextSensor2(salHandle sensorList, salSensorStatus2 *sensorStatus);
SAL_API salCloseSensorList(salHandle sensorList);
SAL_API salAddSensorToSMS(char *hostname, char *sensorName);
SAL_API salRemoveSensorFromSMS(char *sensorName);
SAL_API salGetAbsoluteLocation(salLocation *relative, salLocation *absolute);
SAL_API salComputeLocationOffset(salLocation *startLocation, salLocation *endLocation, double *x_offset, double *y_offset);
SAL_API salSetSensorGroupMode(salHandle sensorGroupHandle, salSensorMode mode);
SAL_API salRebootSensor(salHandle smsHandle, char *sensorName);

/***************************** ^^^^^^^^^^^^^^^^^^^^^^^^^^ ******************************/
/*********************************************************************************
 Session functions
 *********************************************************************************/
SAL_API salConnectSensor(salSensorHandle *sensorHandle, char *sensorName, char *applicationName, salInt32 reserved);
SAL_API salConnectSensor2(salSensorHandle *sensorHandle, salHandle smsHandle, char *sensorName, char *applicationName, salInt32 options);
SAL_API salValidSensorHandle(salSensorHandle sensorHandle);
SAL_API salDisconnectSensor(salSensorHandle sensorHandle);
SAL_API salGetSensorLocation(salSensorHandle sensorHandle, salLocation *location);
SAL_API salSetSensorLocation(salSensorHandle sensorHandle, salLocation *location);
SAL_API salGetSensorAutoAntenna(salSensorHandle sensorHandle, salUInt32 *numConfig, salAntennaAuto *config, salUInt32 configSize);
SAL_API salSetSensorAutoAntenna(salSensorHandle sensorHandle, salUInt32 numConfig, salAntennaAuto *config);
SAL_API salGetServerVersion(salSensorHandle sensorHandle, salUInt32 *version);
SAL_API salSetService(salSensorHandle sensorHandle, salService service);
SAL_API salSetSensorMode(char* sensorName, salSensorMode mode);
SAL_API salSetSensorMode2(salSensorHandle sensorHandle, salSensorMode mode);
SAL_API salGetSensorCapabilities(salSensorHandle sensorHandle, salSensorCapabilities *capabilities);                   
SAL_API salGetSensorAttribute(salSensorHandle sensorHandle,
                      salSensorAttribute sensorAttribute, 
                      void *attributeValue, salUInt32 bufferSize);
SAL_API salGetSensorAttribute2(salSensorHandle sensorHandle,
                      salSensorAttribute sensorAttribute, 
                      void *attributeValue, salUInt32 bufferSize, salUInt8 skipRefresh);
SAL_API salSetSensorAttribute(salSensorHandle sensorHandle, salSensorAttribute attribute, void *val);
SAL_API salGetErrorString(salErrorType salError, 
                               salLocalization language,
                               char *errorStringArray,
                               salInt16 arrayLength); 
SAL_API salTimePlusDuration( salUInt32 inSec, salUInt32 inNSec, salInt32 durationSign, salUInt32 durationSec, salUInt32 durationNSec, salUInt32 *outSec, salUInt32 *outNSec);
SAL_API salTimePlusDurationDouble( salUInt32 inSec, salUInt32 inNSec, salFloat64 duration, salUInt32 *outSec, salUInt32 *outNSec);
SAL_API salTimeMinusTime( salUInt32 inSecA, salUInt32 inNSecA, salUInt32 inSecB, salUInt32 inNSecB, 
	salInt32 *durationSign, salUInt32 *durationSec, salUInt32 *durationNSec);
SAL_API salTimeMinusTimeDouble( salUInt32 inSecA, salUInt32 inNSecA, salUInt32 inSecB, salUInt32 inNSecB, 
	salFloat64 *duration);
SAL_API salRegisterEventHandler(salSensorHandle sensorHandle, 
                                SAL_EVENT_CALLBACK eventCallback,
                                salUInt32 userWorkspace);
SAL_API salSensorTest(salSensorHandle sensorHandle, int reserved, char *testResults, int resultsSize);
SAL_API salSensorBeep(salSensorHandle sensorHandle);


/** Close a SAL handle
* \ingroup SystemManagement
* \param handle [in] A SAL handle
* \return salErrorType error value
* \remarks
* This function will close a handle that was opened by one of the following SAL functions:
* \code
*     salOpenSms()
*     salDiscoverSensors()
*     salConnectSensor()
*     salConnectSensor2()
*     salOpenSensorList()
*     salOpenSensorList2()
*     salIqOpenDataStream()
*     salMeasureLocation()
*     salMeasureLocation2()
*     salRecalculateLocation()
*     salRecalculateLocation2()
*     salOpenSensorGroup()
*     salRequestTimeData()
*     salStartSweep()
* \endcode
* Closing a handle allows SAL to free resources such as memory and socket connections.
*/
SAL_API salClose(salHandle handle);


/** Information pertaining to a particular sensor discovered on the network.
 * \ingroup SystemManagement */
typedef struct _salSensorInfo {
    char macAddress[SAL_MAX_SENSOR_HOSTNAME];          /**< Media access control address as a string (for example "123456789abc"). */
    char modelNumber[SAL_MAX_SENSOR_HOSTNAME];         /**< Model number of sensor (for example "3900A").*/
    char serialNumber[SAL_MAX_SENSOR_HOSTNAME];        /**< Serial number of sensor (for example "A-3900A-50001").*/
    char hostName[SAL_MAX_SENSOR_HOSTNAME];            /**< Hostname of the  sensor.*/
    char ipAddress[SAL_MAX_SENSOR_HOSTNAME];           /**< Internet protocol address of the sensor (for example "192.168.1.101").*/ 
    char smsAddress[SAL_MAX_SENSOR_HOSTNAME];          /**< Host name or IP address of last SMS that this sensor was assigned to.*/ 
    char revision[SAL_MAX_SENSOR_HOSTNAME];            /**< Firmware and FPGA revision information.*/ 
} salSensorInfo;

SAL_API salDiscoverSensors(salHandle *discoveryHandle, salHandle smsHandle, salUInt32 *numSensors);
SAL_API salGetNextDiscoveredSensor(salHandle discoveryHandle, salSensorInfo *sensorInfo);
SAL_API salAddSensor(salHandle smsHandle, char *hostname, char *sensorName);
SAL_API salRemoveSensor(salHandle smsHandle, char *sensorName);
SAL_API salForceSmsGarbageCollection( salHandle smsHandle);

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

SAL_API salLockResource(salHandle sensorHandle, salResource resource);
SAL_API salUnlockResource(salHandle sensorHandle, salResource resource);
SAL_API salAbortAll(salHandle sensorHandle);
SAL_API salBreakResourceLock(salHandle sensorHandle, salResource resource);
SAL_API salQueryResource(salHandle sensorHandle, salResource resource, salLockInfo *lockInfo);

 /** Time Synchronization Modes
  * \enum salTimeSync
  * \ingroup Session
  */
typedef enum _salTimeSync {
    salTimeSync_unknown = -1,
    salTimeSync_none,  
    salTimeSync_gps,          /**< GPS */
    salTimeSync_ieee1588,     /**< IEEE 1588 */
    salTimeSync_internal,     /**<  internal clock */
	salTimeSync_gps_1588gm    /**< GPS / 1588 Grand Master */
} salTimeSync;

typedef struct _salTimeInfo {
   salUInt32     timestampSeconds;            /**< Integer part of the timestamp (in UTC seconds since January 1, 1970). */
   salUInt32     timestampNSeconds;           /**< Fractional part of the timestamp (in Nanoseconds). */
   salUInt32     isNotSynced;                 /**< If nonzero, the clock is not synced. */
} salTimeInfo;

SAL_API salGetSensorTime(salHandle sensorHandle, salTimeInfo *timeInfo);
SAL_API salSetSensorTime(salHandle sensorHandle, salUInt32 timestampSeconds, salUInt32 timestampNSeconds);
typedef struct _salBacklogStatus {
	salFlowControl flowControlStatus;
	salUInt64 backlogBytes;      /**< Number of bytes waiting to be transferred */
	salUInt64 discardBytes;      /**< Number of bytes discarded because of backlog condition */
	salUInt32 backlogMessages;   /**< Number of messages waiting to be transferred */
	salUInt64 discardMessages;   /**< Number of messages discarded because of backlog condition */
	salFloat32 rxBytesPerSec;    /**< incoming data rate from the measurement HW */
	salFloat32 txBytesPerSec;    /**< TX data rate leaving the sensor */
	salFloat32 backlogSeconds;	 /**< Backlog in seconds */
} salBacklogStatus;

SAL_API salReleaseAllResource();

/** Location measurement status
 * \ingroup Geolocation */
typedef enum salLocateStatus {
    salLOCATE_STATUS_NONE      = 0,      /**< Initial state */
    salLOCATE_STATUS_QUEUED    = 1,      /**< Measurement request is waiting to start */
    salLOCATE_STATUS_MEASURING = 2,      /**< Measurement has started but is not finished */
    salLOCATE_STATUS_DONE      = 3,      /**< Measurement has completed, timed out, or failed */
} salLocateStatus;

/** Measurement request priority
 * \ingroup Geolocation */
typedef enum salPriority {
    salPRIORITY_LOW = 0,                /**< Lowest priority */
    salPRIORITY_MEDIUM = 1,             /**< Medium priority */
    salPRIORITY_HIGH = 2,               /**< High priority */
    salPRIORITY_CRITICAL = 3            /**< Highest priority */
} salPriority;

/** As an input value, indicates which results to return. As an output value, indicates which
 *  results are available. 
 * \ingroup Geolocation
 * */
typedef enum salLocateOutput {
    salLOCATE_OUTPUT_NONE           = 0,    /**< [out]    No results are available */
    salLOCATE_OUTPUT_ALL            = 0,    /**< [in]     Request all outputs */
    salLOCATE_OUTPUT_CORRELATION    = 1,    /**< [in|out] Request correlations / correlations results available */
    salLOCATE_OUTPUT_SPECTRUM       = 2,    /**< [in|out] Request spectra / Spectra available */
    salLOCATE_OUTPUT_IMAGE          = 4,    /**< [in|out] Request location image / location image available */
    salLOCATE_OUTPUT_LOCATION       = 8,    /**< [in|out] Request location calculation / location result available */
    salLOCATE_OUTPUT_TIMESERIES     = 16,   /**< [out]    Timeseries info available */
    salLOCATE_OUTPUT_TIME_DATA      = 32,   /**< [in|out] Request timeseries data / timeseries data available */
} salLocateOutput;

/** Doppler compensation
 * \ingroup Geolocation */
typedef enum salDopplerCompensation {
    salDOPPLER_OFF   = 0,   /**< Disable Doppler compensation  */
    salDOPPLER_ON    = 1,   /**< Force Doppler compensation independent of other measurement parms */
    salDOPPLER_AUTO  = 2    /**< Check for Doppler shifting and apply corrections if necessary */
} salDopplerCompensation;

/** Specify a geographic boundary.
 * \ingroup Geolocation */
typedef struct salRegion {
    salFloat64 north;   /**< Latitude of top boundary */
    salFloat64 south;   /**< Latitude of bottom boundary */
    salFloat64 east;    /**< Longitude of right boundary */
    salFloat64 west;    /**< Longitude of left boundary */
} salRegion;

/** Parameters for location image request.
 * \ingroup Geolocation */
typedef struct salLocateImageParms {
    salUInt32    width;                 /**< Width in pixels of the location image. The maximum is ::SAL_MAX_LOCATION_IMAGE_PIXELS */
    salUInt32    height;                /**< Height in pixels of the location image. The maximum is ::SAL_MAX_LOCATION_IMAGE_PIXELS */
    salInt32     reserved;              /**< Reserved for future use */           
} salLocateImageParms;

/** Description of the location image.
 * \ingroup Geolocation */
typedef struct salLocateImageHeader {
    salRegion    region;                /**< Geographic boundary of the location image */
    salUInt32    width;                 /**< Width in pixels of the location image. */
    salUInt32    height;                /**< Height in pixels of the location image.  */
    salUInt32    numBytes;              /**< Size of the image in bytes.  */
    salInt32     reserved;              /**< Reserved for future use */   
} salLocateImageHeader;

/** Control the results returned by location measurements.
 * \ingroup Geolocation 
 *  
*/
typedef struct salLocateResultParms {
    salRegion              region;          /**< Geographic region over which to compute measurement */
    salLocateImageParms    imageParms;      /**< Requested image details.*/
    salLocateOutput        outputTypes;     /**< Bitmap to indicate which output types (correlation, image, etc.) to include with results. */
    salDopplerCompensation dopplerComp;     /**< Doppler compensation OFF/ON/AUTO */
    salInt32               userWorkspace;   /**< User-supplied value that will be returned in the ::SAL_LOCATE_CALLBACK and in ::salLocateResult*/
    salUInt32              numSensorsMax;   /**< Hint on how many sensors may be used for this measurement.  
                                              *  If salMeasureLocation() is called with salLocateMeasParms.sensorGroupHandle set to zero, the SAL API
                                              *  does not know how many sensors will be used. The SAL API allocates space for the results for 5 sensors
                                              *  as a minimum. If numSensorsMax is greater than 5, space will be allocated for numSensorsMax. */
} salLocateResultParms;

/** Location measurement callback function prototype.
 * \param locateHandle [out] Unique location measurement handle returned by salMeasureLocation() or salRecalculateLocation().
 * \param error           [out] If this is not equal to SAL_ERR_NONE, the measurement did not complete successfully.
 * \param userWorkspace   [out] User-defined value that was set in the ::salLocateResultParms structure.
 * \remarks 
 *  The callback is called from a separate thread than the user thread that called salMeasureLocation() or salRecalculateLocation().
 * \ingroup Geolocation
 **/

typedef void(*SAL_LOCATE_CALLBACK)(salHandle locateHandle, salErrorType error, salInt32 userWorkspace);

/** Location measurement callback function prototype.
 * \param locateHandle [out] Unique location measurement handle returned by salMeasureLocation() or salRecalculateLocation().
 * \param error           [out] If this is not equal to SAL_ERR_NONE, the measurement did not complete successfully.
 * \param userWorkspace   [out] User-defined value that was set in the ::salLocateResultParms structure.
 * \remarks 
 *  The callback is called from a separate thread than the user thread that called salMeasureLocation() or salRecalculateLocation().
 * \ingroup Geolocation
 **/

typedef void(*SAL_LOCATE_CALLBACK)(salHandle locateHandle, salErrorType error, salInt32 userWorkspace);

/** Information about a location measurement.
 * \ingroup Geolocation */
typedef struct salLocateResult {
    salErrorType  errorCode;        /**< If an error occurred during the measurement, it is reported here */
    salInt32      measurementId;    /**< Measurement identifier. Use this number to recall measurements with salRecalculateLocation(). */
    salInt32      userWorkspace;    /**< User-defined value passed in with salLocateResultParms.userWorkspace */
    salLocation   location;         /**< Computed signal location */
    salFloat64    resultQuality;    /**< A quality indicator for the result (0-1.0) */
    salInt32      numSensors;       /**< how many sensors were used to make the measurement  */
    salInt32      numImageBytes;     /**< Size in bytes of location measurement image */
    salLocateOutput validData;      /**< Bitmask of available data types for this measurement */
    salFloat64    reserved;
} salLocateResult;

/** Input parameters for a location measurement.
 * \ingroup Geolocation
 **/
typedef struct salLocateMeasParms {
    salHandle  sensorGroupHandle; /**< Handle to the group of sensors to use for the measurement. 0 means use all sensors configured for geolocation. */
    salFloat64     frequency;         /**< The center frequency of the signal to be located in Hertz. */
    salFloat64     bandwidth;         /**< The 3dB-bandwidth of the measurement in Hertz. Must be less than or equal to 10 MHz. */
    salAntennaType antenna;           /**< Which antenna input to use */
    salFloat64     attenuation;       /**< Attenuation in dB relative to measured optimum attenuation */
    salUInt32      numSamples;        /**< Number of samples to use for the measurement */
    salTriggerType triggerType;       /**< The type of triggering used for this measurement  */
    salFloat64     triggerLevel;      /**< Units are db or dBm depending on the triggerType */
    salInt32       triggerTimeSecs;   /**< Trigger whole seconds; used only when using time trigger */
    salInt32       triggerTimeNSecs;   /**< Trigger fractional seconds; used only when using time trigger */
    salFloat64     timeout;           /**< A timeout in seconds, after which the location measurement will be aborted */
    salPriority    priority;          /**< The priority of this measurement. */
} salLocateMeasParms;

/** Information about a timeseries from a TDOA location measurement.
 * \ingroup Geolocation
 **/
typedef struct salTimeseriesInfo {
    char        sensorName[SAL_MAX_SENSOR_NAME];  /**< Name of sensor that measured the timeseries */
    salLocation location;                  /**< Location of sensor when measurement was made */
    salFloat64  centerFrequency;           /**< Center frequency in Hertz.*/
    salFloat64  sampleRate;                /**< Sample rate used for the time series. */
    salFloat64  bandwidth;                /**<  3 dB bandwidth of the time series. */
    salFloat64  recordLength;              /**< Duration in seconds of the timeseries */
    salUInt32   numSamples;                /**< Number of samples in the timeseries */
	salFloat64  triggerLevel;              /**< Trigger level of the sensor */
	salFloat64  attenuation;               /**< The amount of attenuation the sensor used in dB */
	salUInt32   overload;                  /**< 1 if the sensor overloaded during the timeseries, 0 otherwise */
	salUInt32   timestampSeconds;          /**< Whole seconds part of the time timeseries start time */
	salUInt32   timestampNSeconds;         /**< Fractional seconds part of the time timeseries start time, in nano-seconds */
	char        triggerSource[SAL_MAX_SENSOR_NAME]; /**< Name of sensor that caused this sensor to trigger */
	salFloat64  triggerLatency;            /**< Time difference in seconds between when the triggerSource initiated the trigger and when this sensor triggered  */
	salFloat64  variance1588;              /**< Variance of IEEE-1588 time */

} salTimeseriesInfo;

/** Description of correlation data returned by a location measurement.
 * \ingroup Geolocation */
typedef struct salCorrelationHeader {
    char sensorName1[SAL_MAX_SENSOR_NAME];    /**< Name of the first sensor involved in this correlation */
    char sensorName2[SAL_MAX_SENSOR_NAME] ;   /**< Name of the second sensor involved in this correlation */
    salFloat64 firstX;                        /**< X value in seconds of first point */
    salFloat64 deltaX;                        /**< Step in seconds between X values */
	salInt32    numPoints;                    /**< Number of points */
} salCorrelationHeader;

/** Description of spectrum data returned by a location measurement.
 * \ingroup Geolocation */
typedef struct salSpectrumHeader {
    char sensorName[SAL_MAX_SENSOR_NAME];     /**< Name of the sensor that captured the time series with this spectrum */
    salFloat64 centerFrequency;               /**< Center frequency in Hertz*/
    salFloat64 span;                          /**< Frequency span between first point and last point in Hertz */
    salUInt32 numPoints;                      /**< Number of points */
} salSpectrumHeader;


/** Create a new sensor group.
 * \deprecated use salOpenSensorGroup2() instead
 * \param  sensorGroupHandle [out] Pointer to the memory location that will hold the handle for the new sensor group.
 * \return salErrorType error value
 * \ingroup Geolocation
 * \remarks  Sensor groups are used to specify which sensors to use for geolocation measurements.
 *           
 * \par
 *           Call salClose to close the handle and free resources when you are finished with the sensor
 *           group.
 * \see salSensorGroupAddSensor() \n
 *      salSensorGroupGetNumber() \n
 *      salSensorGroupGetName()   \n
 *      salClose()   \n
 *           
 */
SAL_API salOpenSensorGroup(salHandle *sensorGroupHandle);



/** Create a new sensor group.
 * \param  sensorGroupHandle [out] Pointer to the memory location that will hold the handle for the new sensor group.
 * \param  smsHandle [in]  Handle returned by salOpenSms().
 * \return salErrorType error value
 * \ingroup Geolocation
 * \remarks  Sensor groups are used to specify which sensors to use for geolocation measurements.
 *           
 * \par
 *           Call salClose to close the handle and free resources when you are finished with the sensor
 *           group.
 *
 * \see salSensorGroupAddSensor() \n
 *      salSensorGroupGetNumber() \n
 *      salSensorGroupGetName()   \n
 *      salClose()   \n
 */
SAL_API salOpenSensorGroup2(salHandle *sensorGroupHandle, salHandle smsHandle);


/** Add a sensor to a sensor group.
 * \param sensorGroupHandle [in] Handle returned by salOpenSensorGroup().
 * \param sensorName        [in] Name of the sensor to add.
 * \return salErrorType error value
 * \ingroup Geolocation
 * \remarks The maximum number of sensors is one group is specified by ::SAL_MAX_SENSORS_PER_GROUP.
 * \see salOpenSensorGroup2() \n
 *      salSensorGroupGetNumber() \n
 *      salSensorGroupGetName()   \n
 *
 */
SAL_API salSensorGroupAddSensor(salHandle sensorGroupHandle, char *sensorName);

/** Get the number of sensors in a sensor group.
 * \param sensorGroupHandle [in] Handle returned by salOpenSensorGroup().
 * \param numSensors        [out] Number of sensors in a group.
 * \return salErrorType error value
 * \ingroup Geolocation
 * \see salOpenSensorGroup2() \n
 *      salSensorGroupAddSensor() \n
 *      salSensorGroupGetName()   \n
  * \remarks 
 *
 */
SAL_API salSensorGroupGetNumber(salHandle sensorGroupHandle, salUInt32 *numSensors);

/** Get the name of a sensor in a sensor group.
 * \param sensorGroupHandle [in] Handle returned by salOpenSensorGroup().
 * \param sensorIndex       [in] Index (0 to numSensors-1) of sensor for which to get the name.
 * \param sensorName        [out] Pointer to ::SAL_MAX_SENSOR_NAME bytes of memory to hold sensor name.
 * \return salErrorType error value
 * \ingroup Geolocation
 * \remarks 
 * \see salOpenSensorGroup2() \n
 *      salSensorGroupGetNumber() \n
 *      salSensorGroupGetName()   \n
 *
 */
SAL_API salSensorGroupGetName(salHandle sensorGroupHandle, salUInt32 sensorIndex, char *sensorName);

SAL_API salInit();

#ifdef __cplusplus
}
#endif

#endif /*__AGSAL_H */
