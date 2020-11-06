"""
@File:waterfallDialogEngin.py
@Author:lcx
@Date:2020/1/615:23
@Desc:瀑布图子窗口，调用WaterFall类提供的各种方法进行相应瀑布图显示
"""
from Ui.UitoPy.SpecMonitorDialog import Ui_Dialog
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QMessageBox
from PyQt5.QtCore import pyqtSignal
from monitor.waterfall import WaterFall
import threading
import queue
import shutil
import math
import os
import pymysql
import time
import uuid
from communication import zmqLocal
from function import filesOrDirsOperate
from monitor.waterfall.compresse.dbOperation import compress
import logging

class WaterfallDialog(QDialog, Ui_Dialog):
    signal = pyqtSignal(str)
    def __init__(self, usrpNum, socket, startfreq, endfreq, fatherFilePath, pageLimit=100, dbField = 'data_path',parent=None):
        super(WaterfallDialog, self).__init__(parent)

        self.logger = logging.getLogger("Main.WaterfallDialog")
        # 子窗口初始化
        self.setupUi(self)
        self.setWindowTitle("一体化单元{}频谱监测视图".format(usrpNum))
        self.label_3.setText("监测频段{}~{}MHz".format(str(startfreq), str(endfreq)))
        # 连接按钮
        self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)  # 暂停
        self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)  # 回溯
        # 参数赋值
        self.socket = socket
        self.startfreq = startfreq
        self.endfreq = endfreq
        self.pageLimit = pageLimit
        self.dbField = dbField
        self.fatherFilePath = fatherFilePath
        self.usrpNum = str(usrpNum)
        self.zmqLocalQ = queue.Queue()
        # 初始化定时任务控制标志位置位，该标志位使用按钮信号置位
        self.state = ''
        self.interruptFlag = 0
        self.request = 'run'
        self.singleWatchbackCid = 0# 单点回溯连接ID置0
        # 建立数据库连接并初始化数据库游标
        self.conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        self.cursor = self.conn.cursor()
        # 数据表检查
        self.tableName, self.timeTableName, self.outputDir, self.relativeOutputDir = self.dbCheck()
        # 实例化瀑布图装置对象并将其置入布局中pageLimit, dbTable, fatherFilePath, cursor
        self.waterfallWidget = WaterFall.ApplicationWindow(
            pageLimit, self.tableName, self.fatherFilePath, self.cursor, self.conn)
        self.verticalLayout.addWidget(self.waterfallWidget)

    def circulate(self):
        """
        循环任务，按标志位和请求调用各功能
        Returns:

        """
        while not self.interruptFlag:
            if not self.state:
                if not self.request:
                    time.sleep(0.1)
                    continue
                elif self.request == 'run':
                    self.run()
                elif self.request == 'watchBack':
                    self.watchBack()
            else:
                time.sleep(0.1)

    def run(self):
        """
        常规绘图模式，采集，回传，绘图+压缩入库
        Returns:

        """
        self.state = 'run'
        # 消息发送
        msg = (str(self.startfreq) + ";" + str(self.endfreq))
        zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                     args=(self.socket, msg, self.zmqLocalQ))
        zmqThread.start()
        while self.zmqLocalQ.empty():
            pass
        else:
            reslt = self.zmqLocalQ.get()
            if reslt == "超时":
                print('paraZMQrep回传远端超时信息')
                pass
                # QMessageBox.warning(self, '错误：', '子窗口通信超时！')
                # self.on_pushButton_clicked_2()
            else:
                # print(type(reslt))
                resltList = reslt.split(';')
                dataForCompress = reslt.replace(';', r'\n')
                self.scanRslt = resltList
                freqList = resltList[0].split(' ')
                binsList = resltList[1].split(" ")
                x = [float(i) for i in freqList]
                y = [float(i) for i in binsList]
                # 生成DBPK
                dbPk = str(uuid.uuid1())
                # 开启压缩存储线程
                # 应在此处切入时间戳存储，表名为pk为dbPk

                pass
                compressT = threading.Thread(target=compress, args=(dataForCompress, dbPk,
                                                                    self.cursor, self.conn,
                                                                    self.tableName, self.outputDir,
                                                                    self.relativeOutputDir))
                compressT.start()
                # 调用画布刷新函数
                # print("画布刷新成功？", self.waterfallWidget._update_canvas(dbPk, [x, y]))
                self.waterfallWidget._update_canvas(dbPk, [x, y])
                # 等待存储线程结束
                compressT.join()
                timeStamp = int(round(time.time() * 1000))
                timeTableField = ["id", "time_stamp"]
                insert = "INSERT INTO `{}`(`{}`,`{}`) VALUES ('{}','{}')".format(
                    self.timeTableName, timeTableField[0], timeTableField[1], dbPk, timeStamp)
                # print('压缩', insert)
                self.cursor.execute(insert)
                self.conn.commit()

            self.state = ''

    def watchBack(self):
        """
        回溯模式
        Returns:

        """
        self.state = 'watchBack'
        # 查询选中页对应的数据记录
        pathTuple = self.batchSelect(self.watchbackPage)
        # 遍历记录调用绘图函数
        if not pathTuple:
            QMessageBox.warning(self, '提示：', '回溯失败。')
        else:
            for path in pathTuple:
                if self.request == '':
                    break
                else:
                    self.waterfallWidget._update_canvas(path)
            if self.pushButton_3.text() == '停止回溯':
                self.waterfallWidget.countLine = self.waterfallWidget.limit + 1
                # 建立单点回溯信号槽连接
                self.singleWatchbackCid = self.waterfallWidget.freqCanvas.figure.canvas.mpl_connect(
                    'button_press_event', self.waterfallWidget.refreshFreq)
                self.pushButton_3.setText('回溯')
                self.pushButton_2.setEnabled(True)

        self.request = ''
        self.state = ''

    def on_pushButton_clicked_2(self):
        if self.pushButton_2.text() == '暂停':
            self.request = ''
            while self.state:
                pass
            else:
                # 建立单点回溯信号槽连接
                self.singleWatchbackCid = self.waterfallWidget.freqCanvas.figure.canvas.mpl_connect(
                    'button_press_event', self.waterfallWidget.refreshFreq)
                # 计算DB记录条数，生成combo中的页码
                count = ("SELECT COUNT(*) FROM {}".format(self.tableName))
                self.cursor.execute(count)
                self.conn.commit()
                countResult = self.cursor.fetchall()[0][0]
                print('数据库表共有记录{}条'.format(countResult))
                pageCount = math.ceil(int(countResult) / self.pageLimit)
                print('应产生{}页码'.format(pageCount))
                for i in range(pageCount):
                    print('正在生成第{}页页码'.format(i+1))
                    self.comboBox.addItem('')
                    self.comboBox.setItemText(i+1, str(i+1))

                # 多条回溯按钮ENABLE
                self.pushButton_3.setEnabled(True)
                self.pushButton_2.setText('开始')
        elif self.pushButton_2.text() == '开始':
            # 断开单点回溯信号槽连接
            self.waterfallWidget.freqCanvas.figure.canvas.mpl_disconnect(self.singleWatchbackCid)
            self.singleWatchbackCid = 0
            # 多条回溯按钮DISABLE
            self.pushButton_3.setEnabled(False)
            self.pushButton_2.setText('暂停')
            self.request = 'run'

    def on_pushButton_clicked_3(self):
        if self.pushButton_3.text() == '回溯':
            if not self.comboBox.currentText() == '请选择':
                self.watchbackPage = int(self.comboBox.currentText())
                # self.waterfallWidget.axs[1].cla()
                # 断开单点回溯信号槽连接
                self.waterfallWidget.freqCanvas.figure.canvas.mpl_disconnect(self.singleWatchbackCid)
                self.singleWatchbackCid = 0
                # 禁用开始按键
                self.pushButton_2.setEnabled(False)
                self.pushButton_3.setText('停止回溯')
                self.request = 'watchBack'
            else:
                QMessageBox.warning(self, '提示', '请选择回溯页码。')
        elif self.pushButton_3.text() == '停止回溯':
            self.request = ''
            while self.state:
                pass
            else:
                # 建立单点回溯信号槽连接
                self.singleWatchbackCid = self.waterfallWidget.freqCanvas.figure.canvas.mpl_connect(
                    'button_press_event', self.waterfallWidget.refreshFreq)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setText('回溯')

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
        usrpPath = os.path.join(self.fatherFilePath, 'waterfall', 'usrp{}'.format(self.usrpNum))
        filesOrDirsOperate.makesureDirExist(usrpPath)
        try:
            dirList = list(os.walk(usrpPath))[0][1]
            print(dirList)
        except:
            pass
        else:
            # 删除超出存储限度的表格和本地文件夹
            if len(dirList) > 4:
                for dir in dirList[0:-3]:
                    try:
                        dirPathToDrop = os.path.join(self.fatherFilePath, 'waterfall', 'usrp{}'.format(self.usrpNum), dir)
                        if os.path.exists(dirPathToDrop):
                            shutil.rmtree(dirPathToDrop)
                        # drop db record
                        drop = ("DROP TABLE `waterfall_data_usrp{}_{}`".format(self.usrpNum, dir))
                        self.cursor.execute(drop)
                        self.conn.commit()
                    except:
                        self.conn.rollback()
                    try:
                        timeTableDrop = ("DROP TABLE `waterfall_time_usrp{}_{}`".format(self.usrpNum, dir))
                        self.cursor.execute(timeTableDrop)
                        self.conn.commit()
                    except:
                        self.conn.rollback()

        # 新建表格和本地文件夹
        dirName = str(int(time.time()))
        relativeDirPath = os.path.join('waterfall', 'usrp{}'.format(self.usrpNum), dirName)
        dirPath = os.path.join(self.fatherFilePath, 'waterfall', 'usrp{}'.format(self.usrpNum), dirName)
        tableName = 'waterfall_data_usrp{}_{}'.format(self.usrpNum, dirName)
        timeTableName = 'waterfall_time_usrp{}_{}'.format(self.usrpNum, dirName)
        try:
            # build the dir
            filesOrDirsOperate.makesureDirExist(dirPath)
            # build the table
            create = ("CREATE TABLE `waterfall_data_usrp{}_{}`(`id` varchar(40) primary key, `data_path` varchar(225))".format(self.usrpNum, dirName))
            self.cursor.execute(create)
            timeCreate = ("CREATE TABLE `waterfall_time_usrp{}_{}`(`id` varchar(40) primary key, `time_stamp` bigint)".format(self.usrpNum, dirName))
            self.cursor.execute(timeCreate)
            self.conn.commit()
        except:
            QMessageBox.warning(self, '错误：', '初始化失败！')
            self.closeEvent()
        return tableName, timeTableName, dirPath, relativeDirPath

    def batchSelect(self, watchBackPage):
        """
        输入多条回溯页码，输出文件相对地址元组
        Args:
            watchBackPage: 字符型页码

        Returns:文件相对地址元组，若查询失败则返回空元组

        """
        dataPathTuple = ()
        try:
            watchBackPage = int(watchBackPage)
            select = ("SELECT `{}` FROM `{}` limit {},{} "
                      .format(self.dbField, self.tableName,
                              (watchBackPage - 1) * self.pageLimit, self.pageLimit))
            print('select:{}'.format(select))
            self.cursor.execute(select)
            self.conn.commit()
            # 获取地址元组
            dataPathTuple = tuple(i[0] for i in self.cursor.fetchall())
        except Exception as e:
            print('exception from batchSelect:{}'.format(repr(e)))
        return dataPathTuple

    def closeEvent(self, QCloseEvent):
        """
        关闭事件，确保当前动作完成后关闭相应连接和本窗口
        Args:
            QCloseEvent:

        Returns:

        """
        self.interruptFlag = 1
        while self.state:
            pass
        else:
            msg = ('close')
            zmqThread = threading.Thread(target=zmqLocal.zmqThread,
                                         args=(self.socket, msg, self.zmqLocalQ))
            zmqThread.start()
            while self.zmqLocalQ.empty():
                pass
            else:
                reslt = self.zmqLocalQ.get()
                print(reslt)
                self.socket.close()
                self.conn.close()
                self.signal.emit(self.usrpNum)
                self.close()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ui = WaterfallDialog()
    ui.show()
    sys.exit(app.exec_())