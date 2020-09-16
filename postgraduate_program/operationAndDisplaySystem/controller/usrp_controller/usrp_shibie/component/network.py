import torch
import torch.nn as nn
import torch.utils.data
import torch.nn.functional as F 


# 用于ResNet18和34的残差块，用的是2个3x3的卷积
class BasicBlock(nn.Module):
    expansion = 1
    def __init__(self, in_channels, out_channels, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3,
                               stride=stride, padding=1, bias=False)#如果stride=1，不改变长宽；如果stride！=1，下面要经过处理
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3,
                               stride=1, padding=1, bias=False) #这个卷积层不改变输入的长宽
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.shortcut = nn.Sequential()
        # 经过处理后的x要与x的维度相同(尺寸和深度)
        # 如果不相同，需要添加卷积把输入x变换为同一维度
        if stride != 1 or in_channels != self.expansion*out_channels: #第一层卷积层stride！=1或者输入与输出通道数不相同
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_channels, self.expansion * out_channels,
                          kernel_size=1, stride=stride, bias=False), #padding=0，kener_size和第一层卷积层相同，输出长宽与第一层卷积层相同
                nn.BatchNorm1d(self.expansion * out_channels)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x))) #经过第一层卷积层+BatchNorm+ReLU
        out = self.bn2(self.conv2(out)) #经过第二层卷积层+BatchNorm
        out += self.shortcut(x) #输出和shortcut相加
        out = F.relu(out)
        return out

#################################################################################

# 用于ResNet50,101和152的残差块，用的是1x1+3x3+1x1的卷积
class Bottleneck(nn.Module):
    # 前面1x1和3x3卷积的filter个数相等，最后1x1卷积是其expansion倍
    expansion = 4

    def __init__(self, in_planes, planes, stride=1):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv1d(in_planes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm1d(planes)
        self.conv2 = nn.Conv1d(planes, planes, kernel_size=3,
                               stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm1d(planes)
        self.conv3 = nn.Conv1d(planes, self.expansion*planes,
                               kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm1d(self.expansion*planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion*planes:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_planes, self.expansion*planes,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(self.expansion*planes)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

###########################################################

class ResNet(nn.Module):
    def __init__(self, block, num_blocks, num_classes=25):
        super(ResNet, self).__init__()
        self.in_channels = 64

        self.conv1 = nn.Conv1d(1, 64, kernel_size=3,
                               stride=1, padding=1, bias=False) #这个卷积层不改变输入的长宽
        self.bn1 = nn.BatchNorm1d(64)
        
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)

        self.linear = nn.Linear(128*128*block.expansion, num_classes)
        #这里需要修改大小，和最后一个block输出匹配

    def _make_layer(self, block, out_channels, num_blocks, stride):
        strides = [stride] + [1]*(num_blocks-1) #strides = [stride,1,1,1...](num_blocks-1)个1，存储每个残差块里每一个卷积层的stride
        layers = []
        for stride in strides:
            layers.append(block(self.in_channels, out_channels, stride))
            self.in_channels = out_channels * block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 4)
        #print("after avg_pool: {}".format(out.size()))
        # 打印最后一个block输出的长宽和维度，方便计算全连接层的输入维度,don't have to calculate batch size
        out = out.view(out.size(0), -1) #进入全连接层前，压缩成一维张量
        out = self.linear(out)
        #out = F.softmax(out,dim=1) #使用softmax
        return out


def ResNet18():
    return ResNet(BasicBlock, [2,2,2,2])

#########################################


def ResNet34():
    return ResNet(BasicBlock, [3,4,6,3])


def ResNet50():
    return ResNet(Bottleneck, [3,4,6,3])

def ResNet101():
    return ResNet(Bottleneck, [3,4,23,3])

def ResNet152():
    return ResNet(Bottleneck, [3,8,36,3])

################################################################
'''
class Net(nn.Module):   #新建网络,继承nn.Module类

	def __init__(self, num_classes=2):
		super(Net, self).__init__()
		self.features = torch.nn.Sequential(
			torch.nn.Conv2d(in_channels=3, out_channels=64, kernel_size=11, stride=4, padding=2),
			torch.nn.ReLU(),
			torch.nn.MaxPool2d(kernel_size=3, stride=2),
			torch.nn.Conv2d(64, 192, kernel_size=5, padding=2),
			torch.nn.ReLU(),
			torch.nn.MaxPool2d(kernel_size=3, stride=2),
			torch.nn.Conv2d(192, 384, kernel_size=3, padding=1),
			torch.nn.ReLU(),
			torch.nn.Conv2d(384, 256, kernel_size=3, padding=1),
			torch.nn.ReLU(),
			torch.nn.Conv2d(256, 256, kernel_size=3, padding=1),
			torch.nn.ReLU(),
			torch.nn.MaxPool2d(kernel_size=3, stride=2)
		)
		self.classifier = torch.nn.Sequential(
			torch.nn.Dropout(0.5),
			torch.nn.Linear(256 * 5 * 5, 1024),
			torch.nn.ReLU(),
			torch.nn.Dropout(0.5),
			torch.nn.Linear(1024, 128),
			torch.nn.ReLU(),
			torch.nn.Linear(128, num_classes)
		)
	def forward(self, x):
		x = self.features(x)
		x = x.view(x.size(0), 256 * 5 * 5)
		print()
		out = self.classifier(x)
		return out
'''
###############################################################
'''
	def __init__(self):
		super(Net,self).__init__() #初始化父类构造函数
		self.conv1 = torch.nn.Conv2d(3,16,3,padding=1) #第一个卷积层，输入3通道,输入图片是3通道的，输出16通道，卷积核3*3，padding=1
											           #输入数据大小200*200，输出16，200*200
											           #第一层池化层输出16，100*100
		self.conv2 = torch.nn.Conv2d(16,16,3,padding=1) #第二个卷积层，输入16通道，卷积核3*3，padding=1
                                                        #输出16，100*100
                                                        #第二层池化层输出16，50*50
		self.fc1 = nn.Linear(50*50*16,128) #第一个全连接层,输入是第二个池化层的输出
		self.fc2 = nn.Linear(128,64)        #第二个全连接层
		self.fc3 = nn.Linear(64,2)          #第三个全连接层，输出维数2，两种分类

	def forward(self,x): #重写父类forward方法，前向传播
		x = self.conv1(x) #经过第一个卷积层
		x = F.relu(x)     #经过relu激活
		x = F.max_pool2d(x,2) #经过第一个池化层，卷积核2*2
		                      #16,100*100
		x = self.conv2(x) #经过第二个卷积层
		x = F.relu(x)     #经过relu激活
		x = F.max_pool2d(x,2) #经过第二个池化层，卷积核2*2
		                      #16，50*50
		x = x.view(x.size(0),-1) #全连接层输入要求是一维张量，把池化层的输出压扁成一维
		x = F.relu(self.fc1(x))  #经过第一个全连接层并激活
		x = F.relu(self.fc2(x))  #经过第二个全连接层并激活
		x = self.fc3(x)          #经过第三个全连接层
        
		return F.softmax(x,dim=1)#做softmax分类，归一化并使所有输出相加为1，输出的是每种可能的概率
'''