import thread
import threading
import time
lock = threading.Lock()
def print1(q):
    while True:
        print 'thread1'
        with lock:
            if not q.empty():
                # print 'q not empty'
                content = q.get()
                if content == 2:
                    print '2 in q'
                    q.put(1)
                else:
                    print '1 in q'
                    q.put(content)
            else:
                q.put(1)
        time.sleep(0.5)

def print2(q):
    while True:
        print 'thread2'
        with lock:
            if not q.empty():
                content = q.get()
                if content == 1:
                    print '1 in q'
                    q.put(2)
                else:
                    print '2 in q'
                    q.put(content)
            else:
                q.put(2)
        time.sleep(0.5)
if __name__ == '__main__':
    import Queue
    q = Queue.Queue()
    # q.put(1)
    th2 = threading.Thread(target=print2(q))
    th1 = threading.Thread(target=print1(q))
    th1.start()
    th2.start()

