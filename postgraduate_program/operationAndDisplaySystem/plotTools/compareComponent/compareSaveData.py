"""
@File:compareSaveData.py
@Author:lcx
@Date:2020/10/513:57
@Desc:
"""
import os
def saveCompareData(paramList, remark, dirPath):
    for param in paramList:
        name = "_".join([param.split(":")[0], remark])
        data = param.split(":")[1]
        with open(os.path.join(dirPath, name+".txt"), "w") as f:
            f.write(data)
        # xList = param.split(":")[1].split(";")[0].split(" ")
        # xLast = xList[-10:]
        # dataArrayX = np.array(param.split(":")[1].split(";")[0].split(" ")).astype("float32")
        # dataArrayY = np.array(param.split(":")[1].split(";")[1].split(" ")).astype("float32")
        # dataDic[name] = [dataArrayX, dataArrayY]
    return dirPath