"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
"""
使用pico绘制瀑布图，暂未启用
"""
import time
import math
import sys, os, random
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
import pandas as pd

import matplotlib
import logging
import pymysql
from scipy.io import loadmat

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection

from monitor.waterfall.annotation.dbOperation import *
from function.dbInfo import dbInfo
from function.filesOrDirsOperate import *
logging.getLogger('matplotlib.font_manager').disabled = True

class ApplicationWindow(QWidget):
    def __init__(self, path, fatherPath):
        super().__init__()
        self.setWindowTitle("[现场电磁干扰检测特征库系统]0~30MHz频谱监测")
        self.n = 1
        self.id = 1
        self.bar = 0
        self.fileNum = 0
        self.path = path# 传入pico保存的文件夹地址
        self.fatherPath = fatherPath
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.logger = logging.getLogger("picoWaterfall")
        self.logger.addHandler(console)
        # #####################
        # self.lists = os.listdir(self.path)
        # self.txt_list = []
        # for path in self.lists:
        #     if '.csv' in path:
        #         self.txt_list.append(path)
        # if self.txt_list and len(self.txt_list) > 3:
        #     self.txt_list.sort(key=lambda fn: os.path.getmtime(self.path + "\\" + fn))
        #     print(len(self.txt_list))
        # #####################
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-140, -50)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-100, 0)

        self.nowTime = str(int(time.time()))
        norm = matplotlib.colors.Normalize(-120, -60)
        # self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
        self.freqCanvas.figure.canvas.mpl_connect('button_press_event', self.drawFreq)
        self.start = QtWidgets.QPushButton(u'开始监测')
        self.stop = QtWidgets.QPushButton(u'停止检测')

        layout.addWidget(self.start)
        layout.addWidget(self.stop)

        self.start.clicked.connect(self._start)
        self.stop.clicked.connect(self._stop)


        databaseInfo=dbInfo
        self.conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                               port=databaseInfo[1],  # 端口号
                               user=databaseInfo[2],  # 用户名
                               passwd=databaseInfo[3],  # 密码
                               db=databaseInfo[4],  # 库名
                               charset=databaseInfo[5])  # 链接字符集
        self.cur = self.conn.cursor()  # 创建游标
        self.dbCheck()
        self.filePrefix=""
        # self.getFilePrefix()

        # 定时任务
        self._timer = self.freqCanvas.new_timer(500, [(self._update_canvas, (), {})])

    def _start(self):
        if self.filePrefix != "":
            self._timer.start()
        else:
            self.getFilePrefix()
            if self.filePrefix != "":
                self._start()

    def _stop(self):
        self._timer.stop()

    def _update_canvas(self):
        self.draw()

    def drawFreq(self, event):  # 点击热力图重绘拼频谱图
        po = event.ydata
        # self.axs[1].set_ylim(-500, 0)
        if po == None:
            self.logger.info(u"提示:点击位置不对")
        elif -po > self.n or po > 0:
            self.logger.info(u"提示:该位置没有数据")
        else:
            self.logger.info(u"选中位置："+str(int(-po)))
            x, y = self.getOldData(int(-po))
            if x != "noFile":
                self.axs[0].cla()
                self.axs[0].plot(x, y)
                self.axs[0].set_ylim(-140, -50)
                self.axs[0].figure.canvas.draw()

                self.axs[0].set_title('频谱图',fontsize=16)
                self.axs[0].set_xlabel('频率/MHz',fontsize=14)
                self.axs[0].set_ylabel('功率/dBm',fontsize=14)

    def getOldData(self, n):
        if n == 1:
            path = self.fileSavingPath + '\\' + self.filePrefix.strip(" ") + '.csv'
        else:
            path = self.fileSavingPath + '\\' + self.filePrefix+'(' + str(n) +').csv'
        if not path == "noFile":
            if os.path.exists(path):
                data = pd.read_csv(path, skiprows=5)
                x = data.values[15:-3, 0]
                y = data.values[15:-3, 1]
                return x, y
        else:
            x = "noFile"
            y = "noFile"
            return x, y

    def getFilePrefix(self):
        # walk self.path to get file prefix
        fileList = os.listdir(self.path)
        if fileList:
            self.filePrefix = ''
            for file in fileList:
                if os.path.splitext(file)[1] == ".csv":
                    fullFileName = os.path.splitext(file)[0]
                    if "(" in fullFileName:
                        self.filePrefix = fullFileName.split("(")[0]
                    else:
                        self.filePrefix = fullFileName + " "
                    break
                else:
                    pass
            if self.filePrefix == '':
                QMessageBox.warning(self, "错误", "文件夹"+self.path+"中无csv型数据文件")
                # self.close()
        else:
            QMessageBox.warning(self, "错误", "文件夹" + self.path + "中无csv型数据文件")
            # self.close()

    def initialDB(self):
        # 新建表格和本地文件夹
        dirName = self.nowTime
        self.relativeDirPath = os.path.join('waterfall', 'pico', dirName)  # 数据文件相对地址（数据表中存的地址）
        self.fileSavingPath = os.path.join(self.fatherPath, 'waterfall', 'pico', dirName)  # 数据文件绝对地址（存储动作的地址）
        tableName = 'waterfall_data_pico_{}'.format(dirName)  # 数据表名
        try:
            # build the dir
            makesureDirExist(self.fileSavingPath)
            # build the table
            create = (
                "CREATE TABLE `{}`(`id` varchar(40) primary key, `create_time` bigint, `data_path` varchar(225))".format(
                    tableName))
            # print(create)
            self.cur.execute(create)
            self.conn.commit()
        except:
            QMessageBox.warning(self, '错误：', '初始化失败！')

    def dbCheck(self):
        """
        查询输入的usrp号名下的瀑布图数据库表，将数据库表按时间戳排序，
        保留时间最近的四张表，删除其余的表格和对应的文件夹,
        新建带有当前时间戳的表格
        Returns:
            tableName:新的表名
            dirPath:存储文件夹
            relativeDirPath:存储文件夹地址的数据库格式

        """
        dirsPath = os.path.join(self.fatherPath, 'waterfall', 'pico')
        makesureDirExist(dirsPath)
        try:
            dirList = list(os.walk(dirsPath))[0][1]
            # print(dirList)
        except Exception as e:
            self.logger.error(e)
        else:
            # 删除超出存储限度的表格和本地文件夹
            if len(dirList) > 4:
                for dir in dirList[0:-3]:
                    try:
                        dirPathToDrop = os.path.join(self.fatherPath, 'waterfall', 'pico', dir)
                        if os.path.exists(dirPathToDrop):
                            shutil.rmtree(dirPathToDrop)
                        # drop db record
                        drop = ("DROP TABLE `waterfall_data_pico_{}`".format(dir))
                        self.cur.execute(drop)
                        self.conn.commit()
                    except Exception as e:
                        self.conn.rollback()
                        self.logger.error(e)
        self.initialDB()

    def getData(self):
        try:
            if self.n == 1:
                path = self.path + '\\' + self.filePrefix.strip(" ") + '.csv'
            else:
                path = self.path + '\\'+ self.filePrefix+'(' + str(self.n) + ').csv'
            # print(path)
            if not path == "noFile":
                if os.path.exists(path):
                    self.logger.debug("get data from path: " + path)
                    data = pd.read_csv(path, skiprows=5, engine="python")
                    x = data.values[15:-3, 0]
                    y = data.values[15:-3, 1]
                    self.logger.debug("get data: " + str(self.n))
                    return x, y
                else:
                    x = "noFile"
                    y = "noFile"
                    return x, y
        except IOError as e:
            self.logger.error(e)
            return 0

    @dbUpload()
    def draw(self):
        self.logger.debug("draw num: " + str(self.n))
        if self.n >= -self.axs[1].get_ylim()[0]:
            self.axs[1].set_ylim(int(self.axs[1].get_ylim()[0] - 100), int(self.axs[1].get_ylim()[0]))
        try:
            # 重绘频谱图
            # print(self.path)
            self.fileNum = sum([len(x) for _, _, x in os.walk(os.path.dirname(self.path))])
            # if self.fileNum > 3 and self.fileNum > self.n+1:
            if self.fileNum > 1:
                # print('start draw')
                x, y = self.getData()
                if x == "noFile":
                    return 0
                if self.bar:
                    self.bar.remove()
                self.bar = 0
                self.logger.info('successfully getdata')
                self.axs[0].cla()
                self.axs[0].plot(x, y)
                self.axs[0].set_ylim(-140, -50)
                self.axs[0].set_title('频谱图', fontsize=16)
                self.axs[0].set_xlabel('频率/MHz', fontsize=14)
                self.axs[0].set_ylabel('功率/dBM', fontsize=14)


                heat = np.array([-self.n for x in x])
                # self.n += 1
                # self.id += 1
                points = np.array([x, heat]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                # 设置一条线并添加至瀑布图的最下方
                norm = matplotlib.colors.Normalize((y.min()+200)**2, (y.max()+200)**2)
                lc = LineCollection(segments, cmap='jet', norm=norm)
                lc.set_array((y+200)**2)
                # print(type(math.log(y)))
                # print(math.log(y))

                # 设置线宽，若瀑布图放的太大线与线之间会出现空缺，若设置太大瀑布图所得比较小时会叠加宽度，可适当调节
                lc.set_linewidth(2)
                line = self.axs[1].add_collection(lc)
                self.bar = self.freqCanvas.figure.colorbar(line, ax=self.axs[1], norm=norm, orientation='horizontal')
                self.axs[1].figure.canvas.draw()
                self.axs[1].figure.canvas.flush_events()
                # print('successful draw')
                return line
        except Exception as e:
            self.logger.error(e)
            return 0


if __name__ == "__main__":
    makesureDirExist("./logs")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m/%d %H:%M:%S %p', filename='./logs/picoWaterfallDebugLog.log', filemode='w')
    logging.info(u"日志记录开始")

    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(r'F:\CASTProgram\postgraduate_program\data\pico-waterfall-data\\',
                            "F:\CASTProgram\postgraduate_program\data\EMCfile")
    app.show()
    qapp.exec_()
