import os
from threading import Thread
class py2Thread(Thread):
    def __init__(self):
        super(py2Thread, self).__init__()
    def run(self):
        os.system('python2 ..\..\py27usrp\socketTest\demo.py')
if __name__ == '__main__':
    a = py2Thread()
    a.start()
