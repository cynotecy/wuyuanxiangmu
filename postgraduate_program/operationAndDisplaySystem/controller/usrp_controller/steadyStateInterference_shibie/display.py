import sys

from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, \
    QApplication, QHBoxLayout, QPushButton
from operator import itemgetter


class WindowClass(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        # self.resize(400, 300)
        self.data = []
        self.signal = []
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)  # 行数
        self.tableWidget.setColumnCount(1)  # 列数
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中

        self.layout.addWidget(self.tableWidget)

        # self.button = QPushButton("按钮")
        # self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        # self.button.clicked.connect(self.pushButton)

    def pushButton(self, list):
        # list = [(1, 2, 3, 4), (1, 3, 5, 6), (5, 7, 4, 4)]
        for i in list:
            self.dataHandle(i)
        self.signalHandle(list)
        print("push button")
        # self.tableWidget.setRowCount(len(self.signal))  # 行数
        self.tableWidget.setRowCount(1)  # 行数
        if len(self.data) == 0:
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
        else:
            self.tableWidget.setColumnCount(len(self.data))  # 列数
            col = []
            for i in self.data:
                str = i[0].__str__() + "—" + i[1].__str__()
                print(str)
                col.append(str)
                print(col)
            self.tableWidget.setHorizontalHeaderLabels(col)# 设表头
            for i in range(len(self.signal)):  # 注意上面列表中数字加单引号，否则下面不显示(或者下面str方法转化一下即可)
                item = self.signal[i]
                for j in range(len(item)):
                    item = QTableWidgetItem(" ".join(self.signal[i][j]))
                    if not " ".join(self.signal[i][j])==' ':
                        self.tableWidget.setItem(0, j, item)
                    # else:
                    #     item2 = QTableWidgetItem('item2')
                    #     self.tableWidget.setItem(i, j, item2)
        print("stop data view")

    def signalHandle(self, lists):
        print("数据处理开始：", lists)
        self.signal = [[] for x in lists]
        for i in range(len(lists)):
            for j in range(len(self.data)):
                if lists[i][0] >= self.data[j][0] and lists[i][1] <= self.data[j][1]:
                    self.signal[i].append([lists[i][2].__str__() + ":" + lists[i][3].__str__()])
                else:
                    self.signal[i].append([" "])
        print("数据处理完毕：", self.signal)

    def dataHandle(self, tuple):
        print("表头处理开始：", self.data)
        self.data.append(tuple)
        self.data.sort(key=itemgetter(0, 1))
        print("排序后：", self.data)
        data = [(self.data[0][0], self.data[0][1])]
        lastData = self.data[len(self.data) - 1]
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
