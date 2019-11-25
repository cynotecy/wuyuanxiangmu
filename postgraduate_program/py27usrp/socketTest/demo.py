# -*- coding: UTF-8 -*-
import zmq
import thread
import time
from current_controller import scan_thread
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
    
    repAddress = 'tcp://127.0.0.1:6667'
    
    pubSocket1 = socket.connect(pubAddress1, 'PUB')
    # pubSocket2 = socket.connect(pubAddress2, 'PUB')
    # pubSocket3 = socket.connect(pubAddress3, 'PUB')
    #
    subSocket1 = socket.connect(subAddress1, 'SUB')
    # subSocket2 = socket.connect(subAddress2, 'SUB')
    # subSocket3 = socket.connect(subAddress3, 'SUB')

    socketDic = dict()
    socketDic[0] = [pubSocket1, subSocket1]
    # socketDic[1] = [pubSocket2, subSocket2]
    # socketDic[2] = [pubSocket3, subSocket3]

    repSocket = socket.connect(repAddress, 'REP')

    while 1:
        localRecv = repSocket.recv()
        print localRecv
        repSocket.send('hello py3')

        msg = localRecv.split(',')
        usrpNum = int(msg[0])

        pubSock = socketDic[usrpNum - 1][0]
        subSock = socketDic[usrpNum - 1][1]
        mode = msg[1]  # scan
        action = localRecv[2]  # IQ
        instructionInfo = localRecv[3]
        instructionInfoList = instructionInfo.split(';')
        if mode == 'scan':
            startFreq = instructionInfoList[0]
            endFreq = instructionInfoList[1]
            scan_recv = scan_thread.Recv(localQueue, subSock)
            scan_send = scan_thread.Send(startFreq, endFreq, pubSock)
            scan_recv.start()
            scan_send.run()
            while localQueue.empty():
                pass
            else:
                bins = localQueue.get()
                freq_list = localQueue.get()
                bins = [c - 11 for c in bins]

                f = open(r'D:\postgraduate_program\usrp_recvfiles\threshold\%s.txt' % id, 'w+')
                for i in range(len(freq_list)):
                    f.write(str(freq_list[i]) + ' ')
                f.write('\n')
                for i in range(len(bins)):
                    f.write(str(bins[i]) + ' ')
                f.close()



        # if localRecv == 'hello server':
        #     # 同步完成
        #     localQueue.put('synchronization')
        #     reqSocket.close()
        #     break
        # else:
        #     # repSocket.send('nothing')
        #     time.sleep(1)


    
# def syncThread(q):
#     recv = ''
#     while 1:
#         repSocket.send('hello client')
#         recv = repSocket.recv()
#         if recv == 'hello server':
#             # 同步完成
#             q.put('synchronization')
#             repSocket.close()
#             break
#         else:
#             # repSocket.send('nothing')
#             time.sleep(1)

if __name__ == '__main__':
    threadControl()