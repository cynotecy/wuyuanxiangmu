"""
@File:waterfallHistoryView.py
@Author:lcx
@Date:2020/10/2523:29
@Desc:瀑布图历史回看界面。
"""
import sys
import os
import time

import matplotlib
import numpy as np
from datetime import datetime
from interval import Interval

from PyQt5.QtWidgets import QApplication, QWidget
from Ui.UitoPy.Ui_waterfallHistoryView import Ui_Dialog
from monitor.waterfall.historyView.component import dbQuery
from function.dbInfo import dbInfo
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from monitor.waterfall.compresse.dbOperation import decompress
import logging
logging.getLogger('matplotlib.font_manager').disabled = True
class WaterfallHistoryView(QWidget, Ui_Dialog):
    def __init__(self, dataFatherPath, pageLimit, parent=None):
        super(WaterfallHistoryView, self).__init__(parent)
        self.setupUi(self)
        self.dataFatherPath = dataFatherPath
        self.tableListGet()
        self.pushButton.clicked.connect(self.tableListGet)
        self.pushButton_2.clicked.connect(self.timeListGet)
        self.pushButton_3.clicked.connect(self.watchBack)
        self.n = 0

        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))
        self.limit = pageLimit  # 每页条数

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        self.bar = 0
        self.verticalLayout_2.addWidget(self.toolbar)
        self.verticalLayout_2.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-100, -70)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-self.limit, 0)

    def tableListGet(self):
        tableNameReg = r'waterfall_data_usrp*'
        freqList = dbQuery.tableNameCheck(dbInfo, tableNameReg)
        for index in range(len(freqList)):
            self.comboBox.addItem("")
            self.comboBox.setItemText(index, freqList[index])

    def timeListGet(self):
        # 查询time表起止时间
        tableName = self.comboBox.currentText()
        fieldName = 'time_stamp'
        maxTimeStamp = int(dbQuery.maxMinQuery(dbInfo, tableName.replace('data', 'time'), fieldName, "max"))
        minTimeStamp = int(dbQuery.maxMinQuery(dbInfo, tableName.replace('data', 'time'), fieldName, "min"))
        self.lineEdit.setText("{}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',
                                                            time.localtime(minTimeStamp/1000)))))
        self.lineEdit_2.setText("{}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',
                                                            time.localtime(maxTimeStamp/1000)))))
        self.dateTimeEdit.setDateTime(datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(minTimeStamp/1000)),
                                      '%Y-%m-%d %H:%M:%S'))

    def getViewTime(self):
        #查询dateTimeEdit中的时间是否在表内（后舍5min），如果在，返回回溯起点和终点，如果后续不足五分钟，返回最后五分钟，否则返回错误提示
        selectedTime = self.dateTimeEdit.dateTime().toMSecsSinceEpoch()
        # 查询time表起止时间
        tableName = self.comboBox.currentText()
        fieldName = 'time_stamp'
        maxTimeStamp = int(dbQuery.maxMinQuery(dbInfo, tableName.replace('data', 'time'), fieldName, "max"))
        minTimeStamp = int(dbQuery.maxMinQuery(dbInfo, tableName.replace('data', 'time'), fieldName, "min"))
        if selectedTime in Interval(minTimeStamp, maxTimeStamp):
            startTime = selectedTime
        else:
            startTime = minTimeStamp
        endTime = startTime + 5*60*1000
        if endTime > maxTimeStamp:
            endTime = maxTimeStamp
        self.lineEdit_3.setText("{}".format(str(time.strftime('%Y-%m-%d %H:%M:%S',
                                                            time.localtime(endTime/1000)))))
        return startTime, endTime

    def getRecordList(self):
        startTime, endTime = self.getViewTime()
        tableName = self.comboBox.currentText()
        fieldName = 'time_stamp'
        pkList = dbQuery.intervalQuery(dbInfo, tableName.replace('data', 'time'), fieldName, startTime, endTime)
        return pkList

    def getdataPath(self, pk):
        tableName = self.comboBox.currentText()
        fieldName = 'data_path'
        keyFieldName = 'id'
        dataRelativePath = dbQuery.fieldQuery(dbInfo, tableName, fieldName, keyFieldName, pk)
        dataPath = os.path.join(self.dataFatherPath, dataRelativePath.replace("/file/",""))
        return dataPath

    def getData(self, dataPath):
        x, y = None, None
        try:
            if os.path.exists(dataPath):
                x, y = decompress(dataPath)  # decompress为引用的解压函数
                x, y = np.array(x), np.array(y)
        except Exception as e:
            print(repr(e))
        return x, y

        # 输入x和y，刷新频谱图区和瀑布图区

    def draw(self, x, y, basePosition):
        if self.bar:
            self.bar.remove()
        self.bar = 0
        try:
            self.axs[0].cla()
            self.axs[0].plot(x, y)
            self.axs[0].set_title('频谱图', fontsize=16)
            self.axs[0].set_xlabel('频率/MHz', fontsize=14)
            self.axs[0].set_ylabel('功率/dBm', fontsize=14)

            heat = np.array([-basePosition for x in x])
            points = np.array([x, heat]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # 设置一条线并添加至瀑布图的最下方
            norm = matplotlib.colors.Normalize(y.min(), y.max())
            lc = LineCollection(segments, cmap='jet', norm=norm)
            lc.set_array(y)

            # 设置线宽，若瀑布图放的太大线与线之间会出现空缺，若设置太大瀑布图所得比较小时会叠加宽度，可适当调节
            lc.set_linewidth(2)
            line = self.axs[1].add_collection(lc)

            self.bar = self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
            self.axs[1].figure.canvas.draw()
            self.axs[1].figure.canvas.flush_events()
            print('successful draw')
            return line
        except Exception as e:
            print('draw')
            print(repr(e))

    def watchBack(self):
        self.n = 0
        self.axs[0].cla()
        self.axs[1].cla()
        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-100, -70)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-self.limit, 0)
        if not self.lineEdit.text() or not self.lineEdit_2.text():
            raise Exception
        pkList = self.getRecordList()
        for i in range(0, len(pkList)):
            dataPath = self.getdataPath(pkList[i])
            x, y = self.getData(dataPath)
            self.draw(x, y, self.n)
            self.n += 1




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = WaterfallHistoryView("D:\myPrograms\CASTProgram\postgraduate_program\data\EMCfile", 500)
    ui.show()
    app.exec_()
