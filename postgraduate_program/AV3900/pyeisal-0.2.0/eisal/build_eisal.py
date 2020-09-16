import os
import platform
from cffi import FFI

sensor_model = "3900A"

ffibuilder = FFI()

mycffi_dir = os.path.dirname(__file__)

with open(os.path.join(mycffi_dir, "_cdefs.h")) as f:
    ffibuilder.cdef(f.read())

cur_architecture = platform.architecture()

library_path = ""
if(cur_architecture[0] == '32bit'):
  library_path = "../lib/%s/x86" % sensor_model
else:
  library_path = "../lib/%s/x64" % sensor_model


# This describes the extension module "_pi_cffi" to produce.
ffibuilder.set_source("_eisal_cffi",
"""
    #include "salFrequency.h"
    #include "salTimeData.h"
""",
    include_dirs=[os.path.join(mycffi_dir, "../include")],
    library_dirs=[os.path.join(mycffi_dir, library_path)],
    libraries=['eisal'] # library name, for the linker
)   

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)