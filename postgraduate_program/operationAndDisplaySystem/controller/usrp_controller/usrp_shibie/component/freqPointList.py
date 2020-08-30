"""
@File:freqPointList.py
@Author:lcx
@Date:2020/8/2816:31
@Desc:DTO,承载频点列表数据,为OrderedDict类型,k-频点名称,
v-频率区间（为1行2列list，第一个元素为起始频率,第二个元素为终止频率）
"""
import collections
class FreqPointList():
    def __init__(self):
        self.pointList = collections.OrderedDict()
    def setPointLine(self, key, value):
        self.pointList[key] = value
    def getPointList(self):
        return self.pointList