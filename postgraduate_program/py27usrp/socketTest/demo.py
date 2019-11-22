import zmq
import thread
import time
import Queue
from socketTest import socket

def threadControl():
    localQueue = Queue.Queue()
    remoteQueue = Queue.Queue()
    pubAddress1 = 'tcp://192.168.0.100:7777'
    pubAddress2 = 'tcp://192.168.0.100:6666'
    pubAddress3 = 'tcp://127.0.0.1:6666'

    subAddress1 = 'tcp://192.168.0.5:9999'
    subAddress2 = 'tcp://192.168.0.5:5555'
    subAddress3 = 'tcp://127.0.0.1:5555'
    
    reqAddress = 'tcp://127.0.0.1:6667'
    
    pubSocket1 = socket.connect(pubAddress1, 'PUB')
    pubSocket2 = socket.connect(pubAddress2, 'PUB')
    pubSocket3 = socket.connect(pubAddress3, 'PUB')

    subSocket1 = socket.connect(subAddress1, 'SUB')
    subSocket2 = socket.connect(subAddress2, 'SUB')
    subSocket3 = socket.connect(subAddress3, 'SUB')

    socketDic = dict()
    socketDic[0] = [pubSocket1, subSocket1]
    socketDic[1] = [pubSocket2, subSocket2]
    socketDic[2] = [pubSocket3, subSocket3]

    reqSocket = socket.connect(reqAddress, 'REQ')

    while 1:
        reqSocket.send('hello client')
        localRecv = reqSocket.localRecv()
        usrpNum = int(localRecv[0])
        pubsock = socketDic[usrpNum - 1][0]
        subsock = socketDic[usrpNum - 1][1]
        mode = localRecv[1]
        action = localRecv[2]
        instructionInfo = localRecv[3]
        instructionInfoList = instructionInfo.split(';')
        if mode == 'scan':
            startFreq = instructionInfoList[0]
            endFreq = instructionInfoList[1]
            scan_recv = scan_thread.Recv(q, subSocket)
            scan_send = scan_thread.Send(freq_start, freq_end, pubSocket)
            scan_recv.start()
            scan_send.run()


        # if localRecv == 'hello server':
        #     # 同步完成
        #     localQueue.put('synchronization')
        #     reqSocket.close()
        #     break
        # else:
        #     # repSocket.send('nothing')
        #     time.sleep(1)


    
def syncThread(q):
    recv = ''
    while 1:
        repSocket.send('hello client')
        recv = repSocket.recv()
        if recv == 'hello server':
            # 同步完成
            q.put('synchronization')
            repSocket.close()
            break
        else:
            # repSocket.send('nothing')
            time.sleep(1)