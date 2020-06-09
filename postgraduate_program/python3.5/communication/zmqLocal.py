import zmq

class localZMQ():
    """
    本类用于与py2.7编写的通信中台进行本机通信。由于是本机通信，ip地址应被设置为localhost(127.0.0.1)，
    端口号与通信中台的本机通信端口相统一就可以。目前在开发环境中设置为默认监听6667端口，
    后续为用户在生产环境中的使用考虑，应提供可更改该端口号的配置文件。
    为方便开发调试，本连接的超时重连功能暂时被注释掉了，请不要删除，后续可能需要重新设计并启用。
    """
    def __init__(self, address="tcp://127.0.0.1:6667"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.address = address
        # 如果输入了地址则按地址创建，否则默认创建监听6667端口的连接
        self.socket.connect(address)######可根据实际情况更改ip

        # self.poll = zmq.Poller()# 超时判断
        # self.poll.register(self.socket, zmq.POLLIN)
    def sendMessege(self, messege):
        """
        本方法发送消息并阻塞当前线程直到收到回传的消息后返回回传消息内容。
        Args:
            messege: 待发送的消息，类型为str

        Returns:回传消息内容，类型为str

        """
        print("{} py3 to py2 msg send!".format(self.address))
        self.socket.send(str.encode(messege))
        # socks = dict(self.poll.poll(20000))
        # if socks.get(self.socket) == zmq.POLLIN:
        result = bytes.decode(self.socket.recv())
            # print(result)
        # else:
        #     self.socket.setsockopt(zmq.LINGER, 0)
        #     self.socket.close()
        #     self.poll.unregister(self.socket)
        #
        #     self.context = zmq.Context()
        #     self.socket = self.context.socket(zmq.REQ)
        #     self.socket.connect("tcp://192.168.0.5:6667")  ######根据实际情况更改ip
        #
        #     self.poll = zmq.Poller()  # 超时判断
        #     self.poll.register(self.socket, zmq.POLLIN)
        #     result = "超时"
        return result

    def close(self):
        self.socket.close()


def zmqThread(socket, msg, q):
    """
    该方法为localZMQ的调用方法，需要为通信功能单独开启线程时建议使用该方法开启一个通信线程。
    本项目中大多数通信功能的实现方式为：
    初始化时创建localZMQ实例，需要发信+收信时另起一个线程调用该方法，
    传入localZMQ实例、消息内容和队列实现一次通信，以避免通信过程中对主线程造成阻塞。
    Args:
        socket: 通信对象，类型为localZMQ
        msg: 待发送的消息，类型为str
        q: 队列，类型为Queue，用于线程间通信

    Returns:

    """
    reslt = socket.sendMessege(msg)
    q.put(reslt)