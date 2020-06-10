import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
import math
#该函数为信噪比计算最终版本
#wideth：采集带宽，需要前端传入

class SNR_finally(Thread):
    # trigger = pyqtSignal(int)

    def __init__(self, data_path,wideth,q):
        super(SNR_finally, self).__init__()
        self.data_path = data_path
        self.wideth = wideth
        self.q = q

    def run(self):
        self.caculate()
    def read_dat(self):
        x = np.loadtxt(self.data_path, dtype=str, delimiter=' ')[0, 0:-1]
        y = np.loadtxt(self.data_path, dtype=str, delimiter=' ')[1, 0:-1]
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        x = np.asarray(x)
        y = np.asarray(y)
        return x, y

    def caculate(self):
        try:
            x, y = self.read_dat()
            # plt.figure()
            # plt.plot(x, y)
            # plt.show()
            y_power = pow(10, y / 10) / 0.001
            sum_power = np.sum(y_power)
            signal_medium=round((x[0]+x[-1])/2)
            start_point=round(signal_medium-self.wideth)
            # end_point=round(signal_medium+wideth)
            for i in range(len(x)):
                if x[i]-start_point>0.00001:
                    break
            sum_valid_power = np.sum(y_power[i:round(len(x)-i)])
            # plt.figure()
            # plt.plot(x[i:round(len(x)-i)], y[i:round(len(x)-i)])
            # plt.show()

            #noise_power = sum_power - sum_valid_power
            noise_power = ((sum_power - sum_valid_power) / (2*i)) * (len(x) - 2*i)
            db = 10 * math.log10(sum_valid_power / noise_power)
            db = round(db, 3)
            db = np.str(db) + "db"
            self.q.put(db)
            # return db
        except:
            self.q.put('判断失败')

if __name__ == '__main__':
    import queue
    import time
    q = queue.Queue()
    data_path = r"..\steadyStateInterference_recvfiles\20190814181451.txt"
    db=SNR_finally(data_path, 0.2, q)# 单位M
    db.start()
    time.sleep(3)
    print(q.get())
