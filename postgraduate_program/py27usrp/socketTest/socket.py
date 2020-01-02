import zmq
def connect(address, mode):
    if mode == 'PUB':
        pubAddress = address
        pubContext = zmq.Context()
        pubSocket = pubContext.socket(zmq.PUB)
        pubSocket.bind(pubAddress)
        socket = pubSocket
    elif mode == 'SUB':
        subAddress = address
        subContext = zmq.Context()
        subSocket = subContext.socket(zmq.SUB)
        subSocket.connect(subAddress)
        subSocket.setsockopt(zmq.SUBSCRIBE, '')
        socket = subSocket
    elif mode == 'REP':
        repAddress = address
        repContext = zmq.Context()
        repSocket = repContext.socket(zmq.REP)
        repSocket.bind(repAddress)
        socket = repSocket

        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
    else:
        socket = 'socket type error'
        
    return socket