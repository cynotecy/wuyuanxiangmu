'''
程序说明：
(1)该程序是将.mat文件转换成.txt文件，然后将pico数据中>20V值剔除
(2)conversion()函数用于转换文件
(3)value_decetion()函数用于检测>20V的值并剔除
'''

from scipy.io import loadmat
import os
import numpy as np
# class_name = 'test_device'
# mat_path = r'C:\Users\ywang\Desktop\source'           # .mat文件路径
# txt_path = r'C:\Users\ywang\Desktop\out'       # .txt文件路径

# 数据格式转换 mat to txt
def conversion(class_name, mat_path, txt_path):
    cun = 1

    files = os.listdir(mat_path)
    for i in range(len(files)):
        data_path = mat_path + '\\' + files[i]
        try:
            # print(data_path)
            data = loadmat(data_path)
            new_txt_path = txt_path + '\\' + class_name + '_' + str(cun) + '.txt'
            data_new = data['A']
            file = open(new_txt_path, 'w')
            for j in range(len(data_new)):
                file.write(str(data_new[j][0]) + '\n')
            file.close()
            # print(cun)
            cun += 1
        except Exception as ex:
            continue

# 大于20V的值检测，检测到后去除
def value_decetion(txt_path):
    cun = 1
    file_list = os.listdir(txt_path)
    path_list = [os.path.join(txt_path, s) for s in file_list]
    # print(path_list)

    for root, dirs, files in os.walk(txt_path):
        for i in files:
            data_path = os.path.join(root,i)
            data = np.loadtxt(data_path).astype(np.float32)
            for j in range(len(data)):
                if np.fabs(data[j]) > 20:
                    os.remove(data_path)
                    break
            # print(data_path)
            # print(cun)
            cun += 1

if __name__ == "__main__":
    conversion(class_name,mat_path,txt_path)
    value_decetion(txt_path)