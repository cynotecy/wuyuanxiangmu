# coding=utf-8
"""
@File:antennaChangeThread.py
@Author:lcx
@Date:2020/9/1520:46
@Desc:
"""
from PyQt4.QtCore import QThread
import struct
import crcmod
import logging

logger = logging.getLogger("transmitPlatformLogger")
LOG_FORMAT = "%(asctime)s - %(thread)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

class AntennaChangeSend(QThread):
    def __init__(self, starts, end, pub_socket, antennaNum):
        super(AntennaChangeSend, self).__init__()
        self.starts = starts
        self.end = end
        self.pointnum = 10000000
        self.antennaNum = antennaNum
        self.socket = pub_socket
    def run(self):
        crc16_ibm = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
        HEADER = '\xAA'
        antenna_CODE = '\x07'
        if self.antennaNum == "1":
            antenna_DATA = struct.pack('!B', 1)  # 0 -> RX2 (RF2); 1 -> TX/RX (RF1)
            antenna_CRC16 = struct.pack('!H', crc16_ibm(antenna_CODE + antenna_DATA) & 0xffff)
            antenna_LENGTH = struct.pack('!I',
                                         (len(antenna_CODE) + len(antenna_DATA) + len(antenna_CRC16)) & 0xffffffff)
            antenna_msg = HEADER + antenna_LENGTH + antenna_CODE + antenna_DATA + antenna_CRC16
            self.socket.send(antenna_msg)
            logger.info(u"天线切换至RF1")
        elif self.antennaNum == "2":
            antenna_DATA = struct.pack('!B', 0)  # 0 -> RX2 (RF2); 1 -> TX/RX (RF1)
            antenna_CRC16 = struct.pack('!H', crc16_ibm(antenna_CODE + antenna_DATA) & 0xffff)
            antenna_LENGTH = struct.pack('!I',
                                         (len(antenna_CODE) + len(antenna_DATA) + len(antenna_CRC16)) & 0xffffffff)
            antenna_msg = HEADER + antenna_LENGTH + antenna_CODE + antenna_DATA + antenna_CRC16
            self.socket.send(antenna_msg)
            logger.info(u"天线切换至RF2")
        else:
            logger.info(u"错误的天线号："+self.antennaNum)