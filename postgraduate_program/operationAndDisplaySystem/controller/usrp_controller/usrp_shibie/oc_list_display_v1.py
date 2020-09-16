import sys

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, \
    QApplication, QHBoxLayout, QPushButton
from operator import itemgetter


class WindowClass(QWidget):
    def __init__(self):
        super().__init__()
        # self.rowNum = rowNum
        self.layout = QHBoxLayout()
        self.resize(1200, 300)
        self.data = []
        self.signal = []
        self.tableWidget = QTableWidget()
        # self.tableWidget = myQTableWidget(self.rowNum)# 使用queue参数，实例化点击响应类
        self.tableWidget.setRowCount(1)  # 行数
        self.tableWidget.setColumnCount(1)  # 列数
        self.tableWidget.setMinimumHeight(270)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)

        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        self.tableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 设置只能选中一行
        self.tableWidget.setEditTriggers(QTableView.NoEditTriggers)  # 不可编辑
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只有行选中
        self.tableWidget.setColumnCount(5)  #设置表格一共有五列

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(14)
        # self.tableWidget.setHorizontalHeaderLabels(['频段', '中心频率', '幅值', '调制方式', '频点识别'])  # 设置表头文字
        item = QtWidgets.QTableWidgetItem('频段')
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem('中心频率')
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem('幅值')
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem('调制方式')
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem('频点识别')
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.setColumnWidth(0, 280)
        self.tableWidget.setColumnWidth(2, 230)
        self.tableWidget.setColumnWidth(3, 310)
        self.tableWidget.setColumnWidth(4, 230)
        self.tableWidget.setFont(font)
        self.layout.addWidget(self.tableWidget)

        self.setLayout(self.layout)
        # 测试按钮，点击更新table
        # self.button = QPushButton("按钮")
        # self.layout.addWidget(self.button)
        # self.button2 = QPushButton("超频点选定")
        # self.layout.addWidget(self.button2)
        # self.button.clicked.connect(self.pushButton)
        # self.button2.clicked.connect(self.getRow)

    # 更新table入口，参数为[[(),()...]]
    def pushButton(self, lists):

        # print("push button")
        self.tableWidget.setRowCount(len(lists[0]))  # 行数
        # print(len(lists[0]))
        # print(range(len(lists[0])))
        for i in range(len(lists[0])):
            se = lists[0][i][0].__str__()+':'+lists[0][i][1].__str__()
            md = lists[0][i][2].__str__()
            hg = lists[0][i][3].__str__()
            # print(se)
            # print(md)
            # print(hg)
            item1 = QTableWidgetItem(se)
            item2 = QTableWidgetItem(md)
            item3 = QTableWidgetItem(hg)
            self.tableWidget.setItem(i, 0, item1)
            self.tableWidget.setItem(i, 1, item2)
            self.tableWidget.setItem(i, 2, item3)

    # 获取选中的行号
    def getRow(self):
        self.selectedRow = list()
        item = self.tableWidget.selectedItems()
        for i in item:
            if self.tableWidget.indexFromItem(i).row() not in self.selectedRow:
                self.selectedRow.append(self.tableWidget.indexFromItem(i).row())
        self.selectedRow.sort()
        # if self.rowNum.empty():
        #     self.rowNum.put(self.selectedRow)
        # else:
        #     self.rowNum.get()
        #     self.rowNum.put(self.selectedRow)
        # print("选中的行：", end='')
        # print(self.selectedRow)
        return self.selectedRow


if __name__ == "__main__":
    import queue
    rN = queue.Queue()
    app = QApplication(sys.argv)
    win = WindowClass()
    lists = [[(57.7453613283, 57.7575683595, 57.7514648439, -67.2741775513),
             (64.2456054689, 64.2578125001, 64.2486572267, -66.8712921143)]]  # 测试数据，删掉传参
    win.pushButton(lists)
    win.show()
    sys.exit(app.exec_())
