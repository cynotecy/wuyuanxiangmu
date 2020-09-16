"""
@File:antennaProxy.py
@Author:lcx
@Date:2020/9/1520:02
@Desc:
"""
def antennaCommandParseProxy(command, subSock, pubSock):
    if (len(command) == 1):
        if command[0] == "antenna1":
            # 发送天线切换指令后发送采集指令后发送天线切换指令
            pass
        elif command[0] == "antenna2":
            # 发送采集指令
            pass
    elif (len(command) == 2):
        # 天线切换、采集、天线切换、采集
        pass