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
    elif mode == 'REQ':
        reqAddress = address
        reqContext = zmq.Context()
        reqSocket = reqContext.socket(zmq.REQ)
        reqSocket.bind(reqAddress)
        socket = reqSocket
    else:
        socket = 'socket type error'
        
    return socket