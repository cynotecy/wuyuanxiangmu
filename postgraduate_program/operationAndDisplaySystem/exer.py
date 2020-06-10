"""
随便写写的demo类
"""
import os
from threading import Thread
class py2Thread(Thread):
    def __init__(self):
        super(py2Thread, self).__init__()
    def run(self):
        os.system('python2 ..\py27usrp\socketTest\demo.py')

# class usrpScan_steadyStateInterference(Thread):
#     def __init__(self):
#         super(usrpScan_steadyStateInterference, self).__init__()
#
#     def run(self):
#         os.system('python2 ..\py27usrp\MainWindow_steadyStateInterference.py')
if __name__ == '__main__':
    # a = usrpScan_steadyStateInterference()
    a = py2Thread()
    a.start()
