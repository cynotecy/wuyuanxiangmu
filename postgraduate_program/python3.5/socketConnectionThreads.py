from threading import Thread

class IQSingleProcess(Thread):
    def __init__(self, path, q):
        super(IQSingleProcess, self).__init__()
        self.path = path
        self.data = ''
        self.q = q
    def run(self):
        a = usrp_shibie_v3.play(self.path)
        self.q.put(a)