import zmq

class localZMQ():
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:6667")######根据实际情况更改ip

        self.poll = zmq.Poller()# 超时判断
        self.poll.register(self.socket, zmq.POLLIN)


    def sendMessege(self, messege):
        self.socket.send(str.encode(messege))
        socks = dict(self.poll.poll(7000))
        if socks.get(self.socket) == zmq.POLLIN:
            result = bytes.decode(self.socket.recv())
            print(result)
        else:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)

            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect("tcp://192.168.0.5:6667")  ######根据实际情况更改ip

            self.poll = zmq.Poller()  # 超时判断
            self.poll.register(self.socket, zmq.POLLIN)
            result = "超时"
        return result