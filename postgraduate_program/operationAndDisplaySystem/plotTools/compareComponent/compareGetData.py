"""
@File:compareGetData.py
@Author:lcx
@Date:2020/9/2113:53
@Desc:remark表征数据备注，例如设备比对数据，remark表征天线名，天线比对数据，remark表征USRP名
"""
import numpy as np
def getCompareData(paramList, remark):

    dataDic = dict()
    # 地址解析
    if ".txt" in paramList[0]:
        pass
    # 数据解析
    else:
        for param in paramList:
            name = "_".join([param.split(":")[0], remark])
            xList = param.split(":")[1].split(";")[0].split(" ")
            xLast = xList[-10:]
            dataArrayX = np.array(param.split(":")[1].split(";")[0].split(" ")).astype("float32")
            dataArrayY = np.array(param.split(":")[1].split(";")[1].split(" ")).astype("float32")
            dataDic[name] = [dataArrayX, dataArrayY]
        return dataDic