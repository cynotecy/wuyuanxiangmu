"""
@File:dataGet.py
@Author:lcx
@Date:2020/8/2914:48
@Desc:为SNR分析算法提供数据，判断输入的参数是文件路径还是数据，
如果是文件路径就读取成为算法所需数据格式，若是数据则调整为算法所需数据格式
"""
import numpy as np
def dataGet(arg):
    if ".txt" in arg:
        # 读取数据，格式化数据
        file = open(arg)
        lines = file.readlines()
        # realPart = lines[0].split(";")[1]
        # imagPart = lines[0].split(";")[2]

        realPart = lines[1]
        imagPart = lines[2]
        realPartList = np.array(realPart.split(" ")).astype(np.float32)
        imagPartList = np.array(imagPart.split(" ")).astype(np.float32)
        dataArray = np.transpose(np.vstack((realPartList, imagPartList)))
        file.close()
        return dataArray

    else:
        # 格式化数据
        realPart = arg.split(";")[1]
        imagPart = arg.split(";")[2]
        realPartList = np.array(realPart.split(" ")).astype(np.float32)
        imagPartList = np.array(imagPart.split(" ")).astype(np.float32)
        dataArray = np.transpose(np.vstack((realPartList, imagPartList)))
        return dataArray
if __name__ == '__main__':
    dataGet(r"D:\myPrograms\CASTProgram\postgraduate_program\data\SNR_data\SNR_data_20200830150104.txt")