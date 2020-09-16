import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset
import numpy as np
import os
import datetime
import warnings
import shutil
from scipy.io import loadmat
import logging

warnings.filterwarnings("ignore", category=DeprecationWarning)


currentPath = os.path.dirname(__file__)

logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                    format=
                    '%(asctime)s - %(levelname)s: %(message)s'  # 日志格式
                    )

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
use_cuda = False
if torch.cuda.is_available():
    use_cuda = True


# 数据格式转换 mat to txt
def conversion(class_name, mat_path, txt_path):
    cun = 1

    files = os.listdir(mat_path)
    for i in range(len(files)):
        data_path = mat_path + '\\' + files[i]
        try:
            data = loadmat(data_path)
            new_txt_path = txt_path + '\\' + class_name + '_' + str(cun) + '.txt'
            data_new = data['A']
            file = open(new_txt_path, 'w')
            for j in range(len(data_new)):
                file.write(str(data_new[j][0]) + '\n')
            file.close()
            cun += 1
        except Exception as ex:
            continue


# 大于20V的值检测，检测到后去除
def value_decetion(txt_path):
    cun = 1

    for root, dirs, files in os.walk(txt_path):
        for i in files:
            data_path = os.path.join(root,i)
            data = np.loadtxt(data_path).astype(np.float32)
            for j in range(len(data)):
                if np.fabs(data[j]) > 20:
                    os.remove(data_path)
                    break
            cun += 1


def normalization(data, axis=0):
    m = np.mean(data, axis=axis)
    s = np.std(data, axis=axis)
    data = (data - m) / s
    return data


def default_read_file(file_path):
    all_dat_path_label = []
    with open(file_path, 'r') as f:
        for line in f:
            data_path = line.strip('\n')
            all_dat_path_label.append(data_path)
    return all_dat_path_label


def default_loader_file(path, Train=True):
    data = np.loadtxt(path, dtype=np.float32)
    sig_data = np.expand_dims(normalization(data), axis=0)
    return torch.from_numpy(sig_data).float()


class MyDataset(Dataset):

    def __init__(self, file_path, Train=True, loader_data=default_loader_file, read_file=default_read_file):
        self.Train = Train
        self.loader_data = loader_data
        self.read_file = read_file
        self.datas = self.read_file(file_path)

    def __getitem__(self, item):
        # data_path, big_label = self.datas[item]
        # dat = self.loader_data(data_path, self.Train)
        # return dat, big_label
        data_path = self.datas[item]
        dat = self.loader_data(data_path, self.Train)
        return dat

    def __len__(self):
        return len(self.datas)

    def get_filepath(self):
        return self.datas


class learn_net(nn.Module):
    def __init__(self, num_classes=4):
        super(learn_net, self).__init__()   #在初始化函数调用前不能分配模块,父类初始化
        # self.num_feature = num_features
        self.num_classes = num_classes
        self.relu = nn.ReLU(inplace=True)
        self.bn1 = nn.BatchNorm1d(16)
        self.bn2 = nn.BatchNorm1d(32)
        self.bn3 = nn.BatchNorm1d(64)
        self.bn4 = nn.BatchNorm1d(128)
        self.bn5 = nn.BatchNorm1d(256)
        self.maxpool = torch.nn.MaxPool1d(kernel_size=8, stride=2, padding=1)
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=32, stride=4, padding=1, bias=False)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=64, stride=2, padding=1, bias=False)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=32, stride=4, padding=1, bias=False)
        self.conv4 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=32, stride=2, padding=1, bias=False)
        self.conv5 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=8, stride=1, padding=1, bias=False)
        self.fc1 = nn.Linear(512, 40)
        self.fc2 = nn.Linear(40, self.num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.maxpool(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.conv2(x)
        x = self.maxpool(x)
        x = self.bn2(x)
        x = self.relu(x)

        x = self.conv3(x)
        x = self.maxpool(x)
        x = self.bn3(x)
        x = self.relu(x)

        x = self.conv4(x)
        x = self.maxpool(x)
        x = self.bn4(x)
        x = self.relu(x)

        x = self.conv5(x)
        x = self.maxpool(x)
        x = self.bn5(x)
        x = self.relu(x)

        x = x.view(x.size(0), -1)
        logging.debug("after conv:{}".format(x.shape))
        x = self.fc1(x)
        out = self.fc2(x)
        return out


def train_model(model, inputs_data, Epochs):
    model.train()
    cirterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(learn_net.parameters(), lr=0.0001, betas=(0.9, 0.99), weight_decay=1e-8)
    for epoch in range(Epochs):
        running_loss, accuracy, total = 0.0, 0.0, 0.0
        for i, (input, label) in enumerate(inputs_data):
            if use_cuda:
                input, label = input.cuda(), label.cuda()
            optimizer.zero_grad()
            outputs = model(input)

            loss = cirterion(outputs, label)  #+ l2_regularization * 0.01

            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            pred_y = torch.max(outputs, 1)[1]
            accuracy += float((pred_y == label).sum())
            total += label.size(0)
            # logging.debug('[%d %5d] train_loss: %.3f  train_acc: %.3f' % (epoch + 1, i + 1, running_loss / 1, accuracy / total))
            running_loss, accuracy, total = 0.0, 0.0, 0.0
    logging.debug('finished training!')


def val_model(model, test_loader):
    key_value = {0: "fan", 1: "PA51", 2: "shipeiqi", 3: "WD_200"}
    model.eval()
    total, correct = 0.0, 0.0
    with torch.no_grad():
        pre_result = []
        for i, test_input in enumerate(test_loader):
            if use_cuda:
                test_input = test_input.cuda()
            out = model(test_input)
            pred = torch.max(out, 1)[1]
            total += test_input.size(0)
            total, correct = 0.0, 0.0
        for i in pred:
            result = key_value[i.item()]
            pre_result.append(result)
    return pre_result


def eval_model(model, logdir, test_loader):
    logging.debug('Evaluating model...')
    if use_cuda:
        checkpoint = torch.load(logdir)
    else:
        checkpoint = torch.load(logdir, map_location=lambda storage, loc: storage)
    model.load_state_dict(checkpoint)
    pre_result = val_model(model, test_loader)
    return pre_result


def get_testdata(root_path, test_path, length):
    test_files = []
    correct_result = []
    for root, dirs, files in os.walk(root_path):
        for i in files:
            # 数据读取路径
            data_path = os.path.join(root, i)
            test_files.append(data_path)

            sub_path = i.split('_')[0]
            if sub_path != 'WD':
                correct_result.append(sub_path)
            else:
                correct_result.append(sub_path+'_200')

        test_files = test_files[:length]
        correct_result = correct_result[:length]

    with open(test_path, 'w') as f:
        for test_file in test_files:
            f.write('{}\n'.format(test_file))
    return correct_result


def max_voter(pre_result):
    '''
    函数功能：返回数组中重复次数最多的元素
    :param : 测试数组
    :return: 重复次数最多的元素
    '''
    temp = 0
    for i in pre_result:
        if pre_result.count(i) > temp:
            max_str = i
            temp = pre_result.count(i)
    return max_str


# 检查文件夹内是否有txt
def dectect_folder(data_path):
    lists = os.listdir(data_path)
    txt_list = []
    for path in lists:
        if '.txt' in path:
            txt_list.append(path)
    if txt_list:
        return 1
    else:
        return 0


def remove_files(mat_path):
    '''
    函数功能：删除mat_path文件夹里的所有文件
    :param:
    :return:
    '''
    for root, dirs, files in os.walk(mat_path):
        for i in files:
            # 数据读取路径
            data_path = os.path.join(root, i)
            os.remove(data_path)


# 将测试数据按测试结果分类存放
def list_dictionary_codes(root_dir):
    paths_list = []
    for parent, dirNames, fileNames in os.walk(root_dir):
        for name in fileNames:
            ext = ['.txt']   # 需要移动文件的后缀名
            if name.endswith(tuple(ext)):
                paths_list.append(os.path.join(parent, name))
    return paths_list


def copy_move_file(root_dir, class_name, target_dir):
    paths_list = list_dictionary_codes(root_dir)
    now_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    target_path = target_dir + '\\' + "".join(class_name) + '\\' + now_time
    isExists = os.path.exists(target_path)
    if not isExists:
        os.makedirs(target_path)
    else:
        pass
    for file_path in paths_list:
        shutil.move(file_path, target_path)
        logging.debug("正在移动文件：" + file_path)
    logging.debug("done!")


def recongnize(val_data_path, logdir):
    BATCT_SIZE = 4000
    val_dataset = MyDataset(file_path=val_data_path, Train=False)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=BATCT_SIZE, shuffle=False, num_workers=0)
    net = learn_net(num_classes=4)
    if use_cuda:
        net = net.cuda()
    pre_result = eval_model(net, logdir, test_loader=val_loader)
    return pre_result


def data_read(data_path):
    read_data = []
    with open(data_path, 'r') as f:
        data = f.readlines()  # txt中所有字符串读入data
        for line in data:
            odom = line.strip('\n')  # 将单个数据分隔开存好
            odom = float(odom)
            read_data.append(odom)
    return read_data


def data_cut_v1(root_path):
    '''
    :param rootpath: #原始数据根文件夹
    :param save_root: #保存数据的根文件夹
    :return:
    '''
    cut = 0
    for root, dirs, files in os.walk(root_path):
        for i in files:
            #数据读取路径
            data_path = os.path.join(root, i)
            #数据保存路径
            sub_path = i.split('_')[0]
            if sub_path == 'WD':
                sub_path = 'WD_200'

            #数据处理
            data = data_read(data_path)
            for i in range(len(data)):
                if data[i] >= 0.150:
                    break
            data_deal = data[i: i + 24999]
            with open(data_path, 'w') as f:
                for data_row in data_deal:
                    f.write('{}\n'.format(data_row))


def delete_end_none(dir):
    paths_list = os.listdir(dir)
    ext = ['.txt']  # 需要移动文件的后缀名
    for name in paths_list:
        if name.endswith(tuple(ext)):
            data_path = os.path.join(dir, name)
            f = open(data_path, "rb+")
            f.seek(-1, os.SEEK_END)
            if f.__next__() == bytes('\n', encoding="utf8"):
                f.seek(-1, os.SEEK_END)
                f.truncate()
                f.close()
        else:
            data_dir = os.path.join(dir, name)
            data_files = os.listdir(data_dir)
            data_path = [os.path.join(data_dir, file) for file in data_files]
            for file_path in data_path:
                f = open(file_path, "rb+")
                f.seek(-1, os.SEEK_END)
                if f.__next__() == bytes('\n', encoding="utf8"):
                    f.seek(-1, os.SEEK_END)
                    f.truncate()
                    f.close()
    logging.debug('数据处理完毕！')


def detect_file(dir):
    path_list = os.listdir(dir)
    data_path = [os.path.join(dir, file) for file in path_list]
    for path in data_path:
        f = open(path, "rb+")
        lines = len(f.readlines())
        if lines != 24999:
            os.remove(path)


def configuration(txt_path, length, dataRootPath):

    test_path = os.path.join(dataRootPath, r'interference_files\allpath.txt')
    logdir = os.path.join(currentPath, 'model_saved\model_v17.pkl')
    warnings.filterwarnings("ignore")
    flag = dectect_folder(txt_path)
    if flag == 1:
        get_testdata(txt_path, test_path, length)
        pre_result = recongnize(test_path, logdir)
        pre_result = max_voter(pre_result)
        os.remove(test_path)
        return pre_result
    else:
        logging.debug("测试文件夹为空")
        return '0'


if __name__ == '__main__':
    txt_path = r'D:\myPrograms\CASTProgram\postgraduate_program\data\interference_files\txt\WD_200'   # pico存mat文件路径
    pre_result = configuration(txt_path, 10, "D:\myPrograms\CASTProgram\postgraduate_program\data")
    logging.info(pre_result)