import sys

from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, \
    QApplication, QHBoxLayout, QPushButton
from operator import itemgetter


class WindowClass(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.resize(400, 300)
        self.data = []
        self.signal = []
        self.tableWidget = QTableWidget()
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
        # lists = [[(94.44397, 94.55383, 94.50195, -87.99175), (95.34424, 95.45715, 95.423584, -88.83546),
        #           (107.23389, 107.36206, 107.29187, -86.43618), (399.91577, 399.94324, 399.93408, -89.57358)],
        #          [(88.68225, 88.724976, 88.70056, -96.38175), (100.52612, 100.666504, 100.578, -94.87612),
        #           (102.40906, 102.595215, 102.49756, -90.07756)]]  # 测试数据，删掉传参
        for list in lists:
            self.dataHandle(list)
        self.signalHandle(lists)
        print("push button")
        self.tableWidget.setRowCount(len(self.signal))  # 行数
        if len(self.data) == 0:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
        else:
            self.tableWidget.setColumnCount(len(self.data))  # 列数
            col = []
            for i in self.data:
                str = i[0].__str__() + "——" + i[1].__str__()
                print(str)
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
        print("stop data view")

    # 表格数据体处理方法
    def signalHandle(self, lists):
        print("数据处理开始：", lists)
        self.signal = [[[-1, -1] for x in self.data] for x in lists]  # 初始化辅助数组长度
        print(self.signal)
        # 根据已处理好的表头参数设置表格体
        for i in range(len(lists)):
            for k in range(len(lists[i])):
                for j in range(len(self.data)):
                    if lists[i][k][0] >= self.data[j][0] and lists[i][k][1] <= self.data[j][1]:
                        if self.signal[i][k][0] == -1 and self.signal[i][k][1] == -1:
                            self.signal[i][j][0] = lists[i][k][2]
                            self.signal[i][j][1] = lists[i][k][3]
                        else:
                            self.signal[i][j][0] = max(self.signal[i][k][0], lists[i][k][2])
                            self.signal[i][j][1] = max(self.signal[i][k][1], lists[i][k][3])
        print("数据处理完毕：", self.signal)

    # 表头处理方法
    def dataHandle(self, list):
        print("表头处理开始：", self.data, list)
        for i in list:
            self.data.append(i)
        print(self.data)
        self.data.sort(key=itemgetter(0, 1))
        print("排序后：", self.data)
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
        print("表头处理完毕：", data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WindowClass()
    win.show()
    sys.exit(app.exec_())
