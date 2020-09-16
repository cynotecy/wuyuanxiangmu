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
        paras = np.array(lines[0].split(" ")).astype(np.float32)
        Fs = paras[2]
        realPartList = np.array(realPart.split(" ")).astype(np.float32)
        imagPartList = np.array(imagPart.split(" ")).astype(np.float32)
        dataArray = np.transpose(np.vstack((realPartList, imagPartList)))
        m = int(12500000/Fs)
        x = np.linspace(0, dataArray.shape[0], dataArray.shape[0]*m)
        dataArray_interp = np.zeros((dataArray.shape[0]*m, 2))
        dataArray_interp[:,0] = np.interp(x, range(dataArray.shape[0]), dataArray[:,0])
        dataArray_interp[:,1] = np.interp(x, range(dataArray.shape[0]), dataArray[:,1])
        file.close()
        return dataArray_interp[500:500+10000,:]

    else:
        # 格式化数据
        realPart = arg.split(";")[1]
        imagPart = arg.split(";")[2]
        paras = np.array((arg.split(";")[0]).split(" ")).astype(np.float32)
        Fs = paras[2]
        realPartList = np.array(realPart.split(" ")).astype(np.float32)
        imagPartList = np.array(imagPart.split(" ")).astype(np.float32)
        dataArray = np.transpose(np.vstack((realPartList, imagPartList)))
        m = int(12500000/Fs)
        x = np.linspace(0, dataArray.shape[0], dataArray.shape[0]*m)
        dataArray_interp = np.zeros((dataArray.shape[0]*m, 2))
        dataArray_interp[:,0] = np.interp(x, range(dataArray.shape[0]), dataArray[:,0])
        dataArray_interp[:,1] = np.interp(x, range(dataArray.shape[0]), dataArray[:,1])
        return dataArray_interp[500:500+10000,:]

if __name__ == '__main__':
    dataGet(r"D:\myPrograms\CASTProgram\postgraduate_program\data\usrp_recvfiles\auto_recognize\oc_collect_20200908143134.txt")