"""
@File:dataGet_spectrum.py
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
        
        #fre = np.array(lines[0].strip().split(" ")).astype(np.float32)
        amp_list = np.array(lines[1].strip().split(" ")).astype(np.float32)
        return amp_list

    else:
        # 格式化数据
        #fre = arg.split(";")[0]
        amp = arg.split(";")[1]

        #fre_list = np.array(fre.split(" ")).astype(np.float32)
        amp_list = np.array(amp.split(" ")).astype(np.float32)
        return amp_list

if __name__ == '__main__':
    dataGet(r"test_800.txt")