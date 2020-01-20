# -*- coding: UTF-8 -*-

"""
@File:fakeTransmit2.py
@Author:lcx
@Date:2020/1/1512:08
@Desc:
"""
import zmq
import time
def recvTest():
    pubAddress = 'tcp://127.0.0.1:7777'
    pubContext = zmq.Context()
    pubSocket = pubContext.socket(zmq.PUB)
    pubSocket.bind(pubAddress)

    msgSend = '1'
    while 1:
        time.sleep(0.1)
        pubSocket.send(msgSend)
        print '接收线程已发送接受请求'

if __name__ == '__main__':
    recvTest()