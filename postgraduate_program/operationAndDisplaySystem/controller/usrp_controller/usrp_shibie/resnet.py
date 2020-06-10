import torch
import torch.nn as nn


class Bottleneck(nn.Module):                                        #residual结构的构建
    def __init__(self, inplanes, planes, depth_bottleneck, stride=1):
        super(Bottleneck, self).__init__()
        self.inplanes = inplanes
        self.planes = planes
        self.depth_bottleneck = depth_bottleneck
        self.stride = stride
        self.conv1 = nn.Conv1d(inplanes, depth_bottleneck, kernel_size=17, stride=stride, padding=8, bias=False)
        self.bn1 = nn.BatchNorm1d(inplanes)
        self.conv2 = nn.Conv1d(depth_bottleneck, planes, kernel_size=17, stride=1, padding=8, bias=False)
        self.bn2 = nn.BatchNorm1d(self.planes)
        self.relu = nn.ReLU(inplace=True)
        self.Dropout = nn.Dropout(p=0.2)
        self.maxpool = nn.MaxPool1d(kernel_size=1, stride=stride)
        self.conv1d_same = nn.Conv1d(in_channels=inplanes, out_channels=self.planes, kernel_size=1, stride=self.stride)

    def forward(self, x):
        input = x
        residual = self.bn1(x)
        residual = self.relu(residual)
        residual = self.Dropout(residual)

        residual = self.conv1(residual)
        residual = self.Dropout(residual)

        residual = self.conv2(residual)

        #residual = self.bn2(residual)
        if self.planes == self.inplanes:
            if self.stride == 1:
                short_cut = input
            else:
                short_cut = self.maxpool(input)
        else:
            short_cut = self.conv1d_same(input)
        output = residual + short_cut
        output = self.relu(output)
        return output

class ResNet(nn.Module):
    def __init__(self, block, layers_arg, num_classes=25):
        super(ResNet, self).__init__()
        self.inplanes = 64
        self.num_classes = num_classes                      #17                    8
        self.conv1 = nn.Conv1d(1, self.inplanes, kernel_size=17, stride=1, padding=8, bias=False)
        self.conv2 = nn.Conv1d(self.inplanes, self.inplanes, kernel_size=17, stride=2, padding=8, bias=False)
        self.conv3 = nn.Conv1d(self.inplanes, self.inplanes, kernel_size=17, stride=1, padding=8, bias=False)
        self.bn = nn.BatchNorm1d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool1d(kernel_size=1, stride=2)
        self.layers = self._make_layer(block, layers_arg)

        self.Dropout = nn.Dropout(p=0.2)
        self.fc = nn.Linear(64 * 32, self.num_classes)

        # for m in self.modules():
        #     if isinstance(m, nn.Conv1d):
        #         nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        #     elif isinstance(m, nn.BatchNorm1d):
        #         nn.init.constant_(m.weight, 1)
        #         nn.init.constant_(m.bias, 0)

    def _make_layer(self, block, layers_arg):
        layers = []
        for unit in layers_arg:
            for unit_arg in unit:
                unit_depth, unit_depth_bottleneck, unit_stride = unit_arg
                layers.append(block(self.inplanes, unit_depth, unit_depth_bottleneck, unit_stride)) #将每个blocks的第一个residual结构保存在layers列表中
                self.inplanes = unit_depth
        return nn.Sequential(*layers)


    def forward(self, x):
        x = self.conv1(x)
        shortcut = self.maxpool(x)
        x = self.conv2(x)
        x = self.Dropout(x)
        x = self.conv3(x)
        x = x + shortcut

        x = self.layers(x)
        x = self.bn(x)
        x = self.relu(x)
        #print(x.size())
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        #print(x.data.cpu().numpy())
        return x
