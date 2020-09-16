from enum import IntEnum

from _eisal_cffi import ffi, lib

class AntennaType(IntEnum):
    Antenna_TestSignal  = -4
    Antenna_Auto        = -3
    Antenna_Unknown     = -2
    Antenna_Terminated  = -1
    Antenna_1           =  0
    Antenna_2           =  1
    Antenna_TestSignal2 =  2
    Antenna_Terminated2 =  3
    Antenna_Auto2       =  4

class DataType(IntEnum):
    DATA_TYPE_NONE = -1  # Indicates no data / unknown type */
    COMPLEX_32 = 0       # 32 bit integer complex pairs (real and imaginary parts are interleaved)*/
    COMPLEX_16 = 1       # 16 bit integer complex pairs (real and imaginary parts are interleaved)*/

class Location:
    def __init__(self, latitude=0.0, longitude=0.0, elevation=0.0):
        self.latitude  = latitude     #/**< In fractional degrees, southern latitudes are negative numbers */
        self.longitude = longitude    #/**< In fractional degrees, western longitudes are negative numbers */
        self.elevation = elevation    #/**< In meters  */
    @classmethod
    def from_c_location(cls, c_location):
        return cls(c_location.latitude, c_location.longitude, c_location.elevation)



class LevelTriggerType(IntEnum):
    NONE           = 0
    ABSOLUTE_LEVEL = 0x1 << 3
    RISING         = 0x2 << 3
    FALLING        = 0x3 << 3



class LevelTrigger:
    def __init__(self, type = LevelTriggerType.NONE, level = 0.0):
        self.type  = type
        self.level = level

    def level_trigger_control(self):
        trigger_type  = ffi.new("int*", int(self.type))
        trigger_level = ffi.new("float*", float(self.level))
        control = ffi.new("salUInt64*")
        ffi.memmove(control, trigger_level, ffi.sizeof("float"))
        ffi.memmove(ffi.cast("char*", control) + ffi.sizeof("float"), trigger_type, ffi.sizeof("int"))
        return control[0]
        
    @classmethod
    def from_trigger_control(cls, control):
        trigger_type  = ffi.new("int*")
        trigger_level = ffi.new("float*")
        c_control = ffi.new("salUInt64*", control)
        ffi.memmove(trigger_level, c_control, ffi.sizeof("float"))
        ffi.memmove(trigger_type, ffi.cast("char*", c_control) + ffi.sizeof("float"), ffi.sizeof("int"))
        return cls(LevelTriggerType(trigger_type[0]), trigger_level[0])



__all__ = ["AntennaType", "DataType", "Location", "LevelTriggerType", "LevelTrigger"]