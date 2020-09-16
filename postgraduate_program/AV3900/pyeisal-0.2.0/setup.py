from setuptools import setup, find_packages

import os
import sys
import platform

req_version = (3, 6)
req_architecture = ('64bit', 'WindowsPE')

def check_python_version(req_version):
    # sys.hexversion
    # platform.python_version()
    cur_version = (sys.version_info.major, sys.version_info.minor)
    print("current python is", cur_version)
    if req_version > cur_version:
        raise SystemError("old python version detected")
    else:
        return True


check_python_version(req_version)


cur_architecture = platform.architecture()

if(cur_architecture[1] is not 'WindowsPE'):
    raise SystemError("pyeisal can only run under Windows")


sensor_model = "3900A"
bin_path = 'bin/%s/'%sensor_model
lib_path = 'lib/%s/'%sensor_model

print(cur_architecture[0])

if(cur_architecture[0] == '64bit'):
    folder_name = 'x64/'
else:
    folder_name = 'x86/'
bin_path += folder_name
lib_path += folder_name

bin_list = ['EISAL.dll', 'TCPComm.dll']
lib_list = ['eisal.lib']


bin_list[:] = [bin_path + bin_file for bin_file in bin_list]

print(bin_list)

lib_list[:] = [lib_path + lib_file for lib_file in lib_list]

print(lib_list)
    
example_path = 'example/'
example_list = ['IQ_snapshot.py', 'spectrum_snapshot.py', 'spectrum_sweep.py', 'radio_demo.py', 'matplotlibrc']
example_list[:] = [example_path + exp_file for exp_file in example_list]
print(example_list)
include_path = 'include/'
include_list = ['EISAL.h', 'SalFrequency.h', 'SalTimeData.h']
include_list[:] = [include_path + inc_file for inc_file in include_list]

setup(
        name = 'pyeisal',
        version = '0.2.0',
        author = 'yangqing',
        author_email = '15275228230@163.com',
        url = 'www.ceyear.com',
        description = 'Python bindings for eisal',
        packages=find_packages(),
        data_files=[('',        bin_list),
                    ('include', include_list),
                    ('lib',     lib_list),
                    ('example', example_list),
                    ('doc',     ['doc/README.pdf', 'doc/UserGuide.pdf']),
                    ('eisal',   ['eisal/_cdefs.h']),],
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["eisal/build_eisal.py:ffibuilder"],
        install_requires = ["cffi>=1.11.0", "matplotlib>=3.0.0", "pyqt5>=5.12.0"]
)