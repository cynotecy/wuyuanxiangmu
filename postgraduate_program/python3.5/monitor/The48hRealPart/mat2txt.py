'''
程序说明：
(1)该程序是将.mat文件转换成.txt文件
(2)conversion()函数用于转换文件
'''

from scipy.io import loadmat
import os
import numpy as np
import time
# mat_path = r'..\realpart_files\pico_original'           # .mat文件路径
# txt_path = r'..\realpart_files\pico'       # .txt文件路径

# 数据格式转换 mat to txt
def conversion(mat_path=r'..\realpart_files\pico_original'):
    files = os.listdir(mat_path)
    for i in range(len(files)):
        data_path = mat_path + '\\' + files[i]
        try:
            # print(data_path)
            data = loadmat(data_path)
            nowtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            new_txt_path = r'..\realpart_files\pico\%s.txt' % nowtime
            data_new = data['A']
            file = open(new_txt_path, 'a+')
            for j in range(len(data_new)):
                file.write(str(data_new[j][0]) + '\n')
            file.close()
        except Exception as ex:
            continue
    print('finished conversing')

if __name__ == "__main__":
    conversion(class_name,mat_path,txt_path)
    value_decetion(txt_path)