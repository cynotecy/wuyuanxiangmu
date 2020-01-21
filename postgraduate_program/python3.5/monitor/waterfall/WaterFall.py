"""
===============
Embedding in Qt
===============

Simple Qt application embedding Matplotlib canvases.  This program will work
equally well using Qt4 and Qt5.  Either version of Qt can be selected (for
example) by setting the ``MPLBACKEND`` environment variable to "Qt4Agg" or
"Qt5Agg", or by first importing the desired version of PyQt.
"""
import time
import sys, os, random
import numpy as np
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

import matplotlib
import pymysql

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from monitor.waterfall.compresse.dbOperation import decompress


class ApplicationWindow(QWidget):
    def __init__(self, pageLimit, dbTable, fatherFilePath, cursor, connect, dbField="data_path"):
        super().__init__()
        matplotlib.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.layout = QtWidgets.QVBoxLayout(self)
        self.freqCanvas = FigureCanvas(Figure(figsize=(9, 6)))

        self.dbTable = dbTable  # 数据库表
        self.dbField = dbField  # 存地址的数据库字段
        self.fatherFilePath = fatherFilePath  # 数据文件存储父地址，即EMCfile文件夹绝对地址
        self.limit = pageLimit  # 每页条数
        self.drawingTimes = 1  # 普通模式绘图次数
        self.countLine = 1  # 当前页绘图条数
        self.y_pyDic = {}
        self.figureKind = 'normal'
        self.cursor = cursor
        self.conn = connect

        # 添加工具栏
        self.toolbar = NavigationToolbar(self.freqCanvas, self)
        self.bar = 0
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.freqCanvas)

        self.axs = self.freqCanvas.figure.subplots(2, 1, sharex=True)

        self.axs[0].set_xlim(150, 200)
        self.axs[0].set_ylim(-100, -70)
        self.axs[1].set_xlim(150, 200)
        self.axs[1].set_ylim(-self.limit, 0)

    # 图区刷新器，输入(数据库主键,[x,y])或(回看页码)，刷新两个图区
    def _update_canvas(self, *arg):
        """

        Args:
            *arg:元组，长度为1时为(watchbackPath,)，即多条回溯每条的地址；长度为2时为(DBPK, [x, y])，即普通绘图

        Returns:绘图结果，普通绘图时一般都是True，当回溯数据库查询不到数据记录时为False

        """
        reslt = True
        if len(arg) == 2:
            if not self.figureKind == 'normal':
                self.figureKind = 'normal'
                self.axs[1].cla()
                self.axs[1].set_ylim(-int(self.drawingTimes + self.limit - 1), -int(self.drawingTimes))
                self.countLine = 1
                self.y_pyDic = {}
            elif self.figureKind == 'normal' and self.countLine > self.limit:
                self.countLine = 1
                self.axs[1].cla()
                self.y_pyDic = {}
                self.axs[1].set_ylim(-int(self.drawingTimes + self.limit - 1), -int(self.drawingTimes))
            dbPk = arg[0]
            self.y_pyDic[self.drawingTimes] = dbPk
            #####
            # x = arg[1][0]
            # y = arg[1][1]
            x = np.array(arg[1][0])
            y = np.array(arg[1][1])
            try:
                self.draw(x, y, self.drawingTimes)
                self.countLine += 1
                self.drawingTimes += 1
            except Exception as e:
                print('_update_')
                print(repr(e))
                reslt = False

        elif len(arg) == 1:
            watchBackPath = arg[0]
            if not self.figureKind == 'watchback':
                self.figureKind = 'watchback'
                self.countLine = 1
                self.y_pyDic = {}
                self.axs[1].cla()
                self.axs[1].set_ylim(-int(self.limit + 1), 1)
            elif self.countLine == self.limit + 1:
                self.countLine = 1
                self.y_pyDic = {}
                self.axs[1].cla()
                self.axs[1].set_ylim(-int(self.limit + 1), 1)
            # dataPathList = [i[0] for i in self.batchSelect(watchBackPage)]
            dataPath = self.addressResolution(watchBackPath, self.fatherFilePath)
            self.y_pyDic[self.countLine] = dataPath
            x, y = self.getData(dataPath)
            try:
                self.draw(x, y, self.countLine)
                print("已画{}".format(self.countLine))
                self.countLine += 1
            except Exception as e:
                print('_update_')
                print(repr(e))
                reslt = False

        return reslt

    # 单条回溯器，输入鼠标左键点击事件，刷新频谱图区
    def refreshFreq(self, event):
        """
        点击瀑布图重绘频谱图，
        根据event产生的ydata取数据，并内部调用_update_canvas函数绘图
        Args:
            event:
        Returns:
        """
        po = event.ydata
        print(po)
        # self.axs[1].set_ylim(-100, 0)
        if po == None:
            print("提示:点击位置不对")
        elif self.figureKind == 'normal' and -po > self.drawingTimes or po > 0:
            print("提示:该位置没有数据")
        elif self.figureKind == 'watchback' and -po > self.countLine or po > 0:
            print("提示:该位置没有数据")
        else:
            try:
                if self.figureKind == 'normal':
                    print(self.y_pyDic.keys())
                    dbPk = self.y_pyDic[math.ceil(-po)]
                    dataPathRelative = self.singleSelect(dbPk)
                    dataPath = self.addressResolution(dataPathRelative, self.fatherFilePath)  # 地址解析
                else:
                    dataPath = self.y_pyDic[math.ceil(-po)]
                x, y = self.getData(dataPath)
                self.axs[0].cla()
                self.axs[0].plot(x, y)
                self.axs[0].figure.canvas.draw()

                self.axs[0].set_title('频谱图',fontsize=16)
                self.axs[0].set_xlabel('频率/MHz',fontsize=14)
                self.axs[0].set_ylabel('功率/dBm',fontsize=14)
                print(self.axs[0].figure.canvas == self.axs[1].figure.canvas)
            except Exception as e:
                print('单点回溯失败')
                print('单点回溯错误:{}'.format(repr(e)))

    # 输入单条回溯数据库主键，输出文件相对地址
    def singleSelect(self, dbPk):
        try:
            select = ("SELECT `{}` FROM `{}` WHERE `id`='{}'"
                      .format(self.dbField, self.dbTable, dbPk))
            print(select)
            self.cursor.execute(select)
            self.conn.commit()
            # 获取单条地址记录
            dataPath = tuple(i[0] for i in self.cursor.fetchall())[0]
            print(dataPath)
        except Exception as e:
            print('single select exception:{}'.format(repr(e)))
            dataPath = 0
        return dataPath

    # # 输入多条回溯页码，输出文件相对地址元组
    # def batchSelect(self, watchBackPage):
    #     dataPathTuple = ()
    #     try:
    #         watchBackPage = int(watchBackPage)
    #         select = ("SELECT `{}` FROM `{}` limit {} offset {} "
    #                   .format(self.dbField, self.dbTable, self.limit,
    #                           (watchBackPage-1)*self.limit))
    #         self.cursor.execute(select)
    #         # 获取地址元组
    #         dataPathTuple = tuple(self.cursor.fetchall())
    #     except:
    #         pass
    #     return dataPathTuple

    # 输入文件绝对地址，输出x和y
    def getData(self, dataPath):
        x, y = None, None
        try:
            if os.path.exists(dataPath):
                x, y = decompress(dataPath)  # decompress为引用的解压函数
                x, y = np.array(x), np.array(y)
        except Exception as e:
            print(repr(e))
        return x, y

    # 地址解析器，输入数据库中存的文件地址、父绝对地址，输出文件绝对地址
    def addressResolution(self, field, fatherPath):
        """

        Args:
            field: 格式为/file/waterfall/usrpN/时间戳
            fatherPath: 格式为......./EMCfile

        Returns:
            dataPath: 文件绝对地址

        """
        dataPath = ''
        try:
            dataPath = field.replace("/file", fatherPath)
        except:
            pass
        return dataPath

    # 输入x和y，刷新频谱图区和瀑布图区
    def draw(self, x, y, basePosition):
        if self.bar:
            self.bar.remove()
        self.bar = 0
        try:
            self.axs[0].cla()
            self.axs[0].plot(x, y)
            self.axs[0].set_title('频谱图',fontsize=16)
            self.axs[0].set_xlabel('频率/MHz',fontsize=14)
            self.axs[0].set_ylabel('功率/dBm',fontsize=14)

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


if __name__ == "__main__":
    watchbackPage = 1
    pageLimit = 2
    dbTable = 'waterfall_data_usrp2_1579530177'
    fatherFilePath = r'D:\myPrograms\CASTProgram\postgraduate_program\EMCfile'
    # 建立数据库连接并初始化数据库游标
    connect = pymysql.connect(host='localhost',  # ID地址
                                port=3306,  # 端口号
                                user='root',  # 用户名
                                passwd='root',  # 密码
                                db='cast',  # 库名
                                charset='utf8')  # 链接字符集
    cursor = connect.cursor()
    def batchSelect(watchBackPage):
        dataPathTuple = ()
        try:
            watchBackPage = int(watchBackPage)
            # select = ("SELECT `{}` FROM `{}` limit {} offset {} "
            #           .format('data_path', dbTable, pageLimit,
            #                   (watchBackPage - 1) * pageLimit))
            select = ("SELECT `{}` FROM `{}` limit {} offset {} "
                      .format('data_path', dbTable, 100,
                              (watchBackPage - 1) * 100))
            cursor.execute(select)
            connect.commit()
            # 获取地址元组
            dataPathTuple = tuple(i[0] for i in cursor.fetchall())
        except:
            pass
        return dataPathTuple


    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow(pageLimit, dbTable, fatherFilePath, cursor, connect)
    app.show()

    # 查询选中页对应的数据记录
    pathTuple = batchSelect(watchbackPage)
    print(pathTuple)
    import threading
    # 遍历记录调用绘图函数
    if not pathTuple:
        print('未查询到记录')
    else:
        i = 0
        for path in pathTuple:
            dataPath = app.addressResolution(path, app.fatherFilePath)
            x, y = app.getData(dataPath)
            # print(x)
            app._update_canvas(i, [x, y])
            # app.startTimer(path)
            # app._update_canvas(path)

    qapp.exec_()