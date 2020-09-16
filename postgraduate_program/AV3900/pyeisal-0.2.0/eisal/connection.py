from _eisal_cffi import ffi, lib

class Connection():
    def __init__(self, sensorName, applicationName):
        self.c_handle = 0
        c_ptr_handle = ffi.new("salSensorHandle*", 0)
        sensor_name = ffi.new("char[]", sensorName.encode()) #default utf-8
        app_name = ffi.new("char[]", applicationName.encode())
        err = lib.salConnectSensor2(c_ptr_handle, 0, sensor_name, app_name, 0)
        self.c_handle = c_ptr_handle[0]
        if(err != lib.SAL_ERR_NONE):
            raise ConnectionError("Connect sensor failed!", err)

    def native_handle(self):
        return self.c_handle

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        #return False
    
    def _close(self):
        if(self.c_handle):
            lib.salClose(self.c_handle)
            self.c_handle = 0
    
    def __del__(self):
        self._close()
        
        
def AbortAll(connection):
    lib.salAbortAll(connection.native_handle())
    #if(err != lib.SAL_ERR_NONE):
    #   raise ConnectionError("AbortAll failed!", err)

if __name__ == '__main__':
    with Connection("192.168.1.88", "xls") as conn:
        print("connect it")


__all__ = ["Connection", "AbortAll"]