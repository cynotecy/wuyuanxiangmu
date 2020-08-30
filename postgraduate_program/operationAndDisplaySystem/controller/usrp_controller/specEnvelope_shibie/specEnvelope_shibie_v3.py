import numpy as np
from controller.usrp_controller.specEnvelope_shibie.functions_v3 import*
import matplotlib.pyplot as plt
base = ['GSM900', 'WCDMA', 'WLAN(2.4G)', 'CDMA800', 'GSM1800', 'FDD_LTE', 'TD_SCDMA']
freq = [[935, 960], [2130, 2145], [2400, 2483], [870, 880], [1805, 1840], [1850, 1875], [2010, 2025]]
def baoluoshibie(file_path):
    # print("频谱包络识别算法启动......")
    if not ('\\' in file_path or '/' in file_path):
        xList = file_path[0]
        yList = file_path[1]
        x_lable = np.array(xList)
        x_lable = x_lable.astype(np.float32)
        y_lable = np.array(yList)
        y_lable = y_lable.astype(np.float32)
    else:
        x_lable = read_dat_hang(file_path, 0)
        y_lable = read_dat_hang(file_path, 1)
    L = len(x_lable)
    c = x_lable[-1] - x_lable[0]
    # print('待检测信号的频段范围：', x_lable[0],'——', x_lable[-1],'频段长度',c)
    # |((x_lable[-1] <= 2575+c) & (x_lable[-1] >= 2555)))
    if not (((x_lable[-1] <= 880+c) & (x_lable[-1] >= 870)) | ((x_lable[-1] <= 960+c) & (x_lable[-1] >= 935)) | ((x_lable[-1] <= 1840+c) & (x_lable[-1] >= 1805)) | ((x_lable[-1] <= 1875+c) & (x_lable[-1] >= 1850)) | ((x_lable[-1] <= 2025+c) & (x_lable[-1] >= 2010)) | ((x_lable[-1] <= 2145+c) & (x_lable[-1] >= 2130)) | ((x_lable[-1] <= 2483+c) & (x_lable[-1] >= 2400))):
        # print(x_lable[0], x_lable[-1])
        s = '超出样本库范围'
        return [s]

    for m in range(0,7):
        if (x_lable[-1] <= freq[m][1] + c) & (x_lable[-1] >= freq[m][0]):
            path = r'..\operationAndDisplaySystem\controller\usrp_controller\specEnvelope_shibie\Normal_data' +'\\' + base[m] + '.txt'
            normal = read_dat(path)
            xinhao_name = base[m]
            xx1 = max(x_lable[0],freq[m][0])
            xx2 = min(x_lable[-1],freq[m][1])
            x_compare_begin = np.where((x_lable <= xx1+0.01)&(x_lable >= xx1-0.01))
            d = len(x_compare_begin[0]) // 2
            beginn = x_compare_begin[0][d]
            # print('交集起始频率：', xx1,'模糊对应值：', x_lable[beginn])
            # print('起始频率的下标索引',beginn)
            x_compare_end = np.where((x_lable <= xx2 + 0.01) & (x_lable >= xx2 - 0.01))
            d = len(x_compare_end[0]) // 2
            endd = x_compare_end[0][d]
            # print(d, len(x_compare_end[0]), x_lable[endd])
            # print('交集终止频率：', xx2, '模糊对应：', x_lable[endd])
            # print('终止频率的下标索引', endd)
            xinhao_startEnd = [x_lable[beginn],x_lable[endd]]
            xinhao_range = [beginn, endd]
            if (xx2-xx1)<5:
                continue

            y_lable_compare = y_lable[beginn: endd]#截取在线信号的频段
            y_lable_compare = normalization(y_lable_compare, axis=0)
            y_list = ave_and_slope(y_lable_compare, 30, 15)

            buchang = (freq[m][1] - freq[m][0]) / len(normal[0])
            normal_xx1 =int(abs((xx1 - freq[m][0]) // buchang))
            normal_xx2 = int(abs((xx2 - freq[m][0]) // buchang))
            yangben_range = [normal_xx1, normal_xx2]
            normal_for_f = normal[:, normal_xx1:normal_xx2]  # 截取样本信号

            chang_sig = len(y_list)
            normal_data = normal_for_f
            if chang_sig > 1000:#信号太长了，做再次抽样处理
                dd = chang_sig // 1000 + 1
                s = slice(0, chang_sig, dd)  # 滑动平均完做抽样处理
                y_list = y_list[s]  # 抽样结果
                normal_data = normal_for_f[:,s]
                # print('比对样本的原始长度：', normal_xx2-normal_xx1,'比对样本抽样后长度：',len(normal_data[0]))
                # print('抽样前的信号长度：',chang_sig, '抽样后的信号长度：',len(y_list))


            result, ratee, num_for_yangben = classify(xinhao_name, y_list, normal_data, 0.4)
            if result == 1:
                s = base[m]#包络相似的信号
                return [s, ratee, xinhao_range, yangben_range, num_for_yangben, xinhao_startEnd]
                # xinhao_range是一个list里面存了x的起止坐标，yangben_range也是个list里面是样本的索引，num_for_yangben是样本编号
            elif result == 0:
                s = '相似度低,无法识别'
                return [s]

if __name__ == '__main__':

    ss = baoluoshibie(r"..\specEnvelope_recvfiles\报错信号.txt")
    # print(ss)
    # print(str(ss[5][0])+','+str(ss[5][1]))



