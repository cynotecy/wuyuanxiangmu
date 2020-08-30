import sys

from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, \
    QApplication, QHBoxLayout, QPushButton
from operator import itemgetter


class WindowClass(QWidget):
    def __init__(self, rowNum):
        super().__init__()
        self.rowNum = rowNum
        self.layout = QHBoxLayout()
        self.resize(400, 300)
        self.data = []
        self.signal = []
        self.tableWidget = myQTableWidget(self.rowNum)
        self.tableWidget.setRowCount(1)  # 行数
        self.tableWidget.setColumnCount(1)  # 列数
        self.tableWidget.setMinimumHeight(270)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)

        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中

        self.layout.addWidget(self.tableWidget)
        # 测试按钮，点击更新table
        # self.button = QPushButton("按钮")
        # self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        # self.button.clicked.connect(self.pushButton)

    # 更新table入口，参数为[[(),()...]]
    def pushButton(self, lists):
        # lists = [[(2404.4067, 2418.5515, 2412.555, -73.214405), (2437.5, 2444.635, 2437.5122, -66.43583699999999), (2471.1792, 2471.2402, 2471.2158, -84.82172), (2471.2463, 2471.3103, 2471.2585, -84.887955)], [(2405.0508, 2405.249, 2405.1055, -84.37802), (2405.2795, 2405.2856, 2405.2795, -84.99037), (2405.3008, 2417.1082, 2411.4226, -75.14265), (2437.5732, 2437.5764, 2437.5732, -84.99987), (2437.622, 2437.6372, 2437.6282, -84.97301), (2437.8357, 2437.848, 2437.8389, -84.9613), (2437.857, 2437.8694, 2437.8633, -84.992676), (2437.8816, 2437.976, 2437.8875, -84.91774), (2438.4797, 2438.6475, 2438.562, -84.43673), (2438.6597, 2438.6658, 2438.6628, -84.98179), (2438.7878, 2438.9404, 2438.8398, -84.77556), (2439.4775, 2439.4958, 2439.4868, -84.9609)]]  # 测试数据，删掉传参
        for list in lists:
            self.dataHandle(list)
        self.signalHandle(lists)
        # print("push button")
        self.tableWidget.setRowCount(len(self.signal))  # 行数
        if len(self.data) == 0:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
        else:
            self.tableWidget.setColumnCount(len(self.data))  # 列数
            col = []
            for i in self.data:
                str = i[0].__str__() + "——" + i[1].__str__()
                # print(str)
                col.append(str)
            self.tableWidget.setHorizontalHeaderLabels(col)
            for i in range(len(self.signal)):
                item = self.signal[i]
                for j in range(len(item)):
                    if self.signal[i][j][0] == -1 and self.signal[i][j][1] == -1:
                        pass
                    else:
                        item = QTableWidgetItem("最高频率：" + self.signal[i][j][0].__str__() + ",  幅值：" + self.signal[i][j][1].__str__())
                        self.tableWidget.setItem(i, j, item)

                        self.tableWidget.setColumnWidth(j, 300)# 固定列宽
        # print("stop data view")

    # 表格数据体处理方法
    def signalHandle(self, lists):
        # print("数据处理开始：", lists)
        # print(self.data)
        self.signal = [[[-1, -1] for x in self.data] for x in lists]  # 初始化辅助数组长度
        # print(self.signal)
        # print(len(lists))
        # 根据已处理好的表头参数设置表格体
        for i in range(len(lists)):# list层数2
            for k in range(len(lists[i])):# list每层列数2\1
                for j in range(len(self.data)):#data长度
                    if lists[i][k][0] >= self.data[j][0] and lists[i][k][1] <= self.data[j][1]:

                        if self.signal[i][j][0] == -1 and self.signal[i][j][1] == -1:# 这句改了，signal不能用k寻址
                            self.signal[i][j][0] = lists[i][k][2]
                            self.signal[i][j][1] = lists[i][k][3]
                        else:
                            self.signal[i][j][1] = max(self.signal[i][j][1], lists[i][k][3])# 最大幅值
                            # 这也改了，最高频点应该以最大幅值对应的频点为准
                            if max(self.signal[i][j][1], lists[i][k][3]) == lists[i][k][3]:
                                self.signal[i][j][0] = lists[i][k][2]# 最高频点
                            else:
                                self.signal[i][j][0] = self.signal[i][j][0]
                    # if lists[i][k][0] >= self.data[j][0] and lists[i][k][1] <= self.data[j][1]:
                    #     if self.signal[i][k][0] == -1 and self.signal[i][k][1] == -1:
                    #         self.signal[i][j][0] = lists[i][k][2]
                    #         self.signal[i][j][1] = lists[i][k][3]
                    #     else:
                    #         self.signal[i][j][0] = max(self.signal[i][k][0], lists[i][k][2])
                    #         self.signal[i][j][1] = max(self.signal[i][k][1], lists[i][k][3])

        # print("数据处理完毕：", self.signal)

    # 表头处理方法
    def dataHandle(self, list):
        # print("表头处理开始：", self.data, list)
        for i in list:
            self.data.append(i)
        # print(self.data)
        self.data.sort(key=itemgetter(0, 1))
        # print("排序后：", self.data)
        data = [(self.data[0][0], self.data[0][1])]
        if len(self.data) == 1:
            pass
        else:
            i = 0
            for j in range(1, len(self.data)):
                if data[i][1] >= self.data[j][0]:
                    if data[i][1] >= self.data[j][1]:
                        pass
                    else:
                        data[i] = (data[i][0], self.data[j][1])
                else:
                    data.append((self.data[j][0], self.data[j][1]))
                    i += 1
        self.data = data
        # print("表头处理完毕：", data)

class myQTableWidget(QTableWidget):
    def __init__(self, rowNum):
        super().__init__()
        self.rowNum = rowNum
    def mouseDoubleClickEvent(self, event):
        # self.tableWidget.mouseDoubleClickEvent()
        # print("mouse double clicked")
        pos = event.pos()
        item = self.indexAt(pos)
        if item:
            self.rowNum.queue.clear()
            self.rowNum.put(item.row())
            # print("item clicked at ", item.row(), " ", item.column())

if __name__ == "__main__":
    import queue
    rN = queue.Queue()
    app = QApplication(sys.argv)
    win = WindowClass(rN)
    win.show()
    sys.exit(app.exec_())
