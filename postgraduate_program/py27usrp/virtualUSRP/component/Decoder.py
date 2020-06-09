# -*- coding: UTF-8 -*-
"""
@File:Decoder.py
@Author:lcx
@Date:2020/6/923:44
@Desc:负责对虚拟usrp收到的请求进行解码
"""
import struct

import crcmod


def decodeMsg(originMsg):
    crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
    print 'recved'
    if len(originMsg) < 6:
        print 'warning: length of msg is less than 6! Ignore this msg'
        # continue
    LENGTH = struct.unpack('!I', originMsg[1:5])[0]
    if LENGTH != (len(originMsg) - 5):
        print "warning0: the length of msg is not equal to LENGTH! Ignore this msg"
        # continue
    HEADER = originMsg[0]
    CODE = originMsg[5:6]
    DATA = originMsg[6:-2]
    CRC16 = struct.unpack('!H', originMsg[-2:])[0]
    if (HEADER != '\xAA'):
        print 'Do not handle the msg begin with %s! Ignore this msg' % (HEADER,)
        # continue
    if (CODE == '\x01'):
        return "scan"
        # continue
    elif (CODE == '\x05'):
        return "collect"