"""
@File:waterfallDialogEngin.py
@Author:lcx
@Date:2020/1/615:23
@Desc:瀑布图子窗口
"""
from Ui.UitoPy.SpecMonitorDialog import Ui_Dialog
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QMessageBox
from monitor.waterfall import WaterFall
import threading
import queue
import os
import pymysql
import time
import uuid
from socketDemo import zmqLocal
from function import filesOrDirsOperate
from monitor.waterfall.compresse.dbOperation import compress


class WaterfallDialog(QDialog, Ui_Dialog):
    def __init__(self, usrpNum, socket, startfreq, endfreq, fatherFilePath, pageLimit=100, parent=None):
        super(WaterfallDialog, self).__init__(parent)
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
        self.fatherFilePath = fatherFilePath
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
        self.tableName, self.outputDir = self.dbCheck(usrpNum)
        # 实例化瀑布图装置对象并将其置入布局中pageLimit, dbTable, fatherFilePath, cursor
        self.waterfallWidget = WaterFall.ApplicationWindow(
            pageLimit, self.tableName, self.fatherFilePath, self.cursor, self.conn)
        self.verticalLayout.addWidget(self.waterfallWidget)
        # 开启循环任务
        self.circulate()

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
                pass
            else:
                print(type(reslt))
                resltList = reslt.split(';')
                dataForCompress = reslt.replace(';', r'\n')
                self.scanRslt = resltList
                freqList = resltList[0].split(' ')
                binsList = resltList[1].split(" ")
                x = [float(i) for i in freqList]
                y = [float(i) for i in binsList]
                # 生成DBPK
                dbPk = uuid.uuid1()
                # 开启压缩存储线程
                compressT = threading.Thread(target=compress, args=(dataForCompress, dbPk, self.cursor,
                                                                    self.tableName, self.outputDir))
                compressT.start()
                # 调用画布刷新函数
                self.waterfallWidget._update_canvas((dbPk, [x, y]))
                # 等待存储线程结束
                compressT.join()

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
                self.waterfallWidget._update_canvas(path)

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
                self.watchbackPage = self.comboBox.currentText()
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

    def dbCheck(self, usrpNum):
        """
        查询输入的usrp号名下的瀑布图数据库表，将数据库表按时间戳排序，
        保留时间最近的四张表，删除其余的表格和对应的文件夹,
        新建带有当前时间戳的表格
        Args:
            usrpNum:

        Returns:
            tableName:新的表名
            dirPath:存储文件夹

        """
        tableName = None
        dirPath = None
        dirList = list(os.walk(os.path.join(
            self.fatherFilePath, 'waterfall', 'usrp{}'.format(usrpNum))))[0][1][0]
        # 删除超出存储限度的表格和本地文件夹
        if len(dirList) > 4:
            for dir in dirList[0:-5]:
                try:
                    # drop db record
                    drop = ("DROP TABLE `waterfall_data_usrp{}_{}`".format(usrpNum, dir))
                    self.cursor.execute(drop)
                    self.conn.commit()
                except:
                    self.conn.rollback()
                    QMessageBox.warning(self, '错误：', '旧数据表删除失败')
                    break
                else:
                    dirPathToDrop = os.path.join(self.fatherFilePath, 'waterfall', 'usrp{}'.format(usrpNum), dir)
                    if os.path.exists(dirPathToDrop):
                        os.remove(dirPathToDrop)

        # 新建表格和本地文件夹
        dirName = str(int(time.time()))
        dirPath = os.path.join(self.fatherFilePath, 'waterfall', 'usrp{}'.format(usrpNum), dirName)
        tableName = 'waterfall_data_usrp{}_{}'.format(usrpNum, dirName)
        try:
            # build the dir
            filesOrDirsOperate.makesureDirExist(dirPath)
            # build the table
            create = ("CREATE TABLE `waterfall_data_usrp{}_{}`('id', 'data_path')".format(usrpNum, dirName))
            self.cursor.execute(create)
            self.conn.commit()
        except:
            QMessageBox.warning(self, '错误：', '初始化失败！')
            self.closeEvent()
        return tableName, dirPath

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
            select = ("SELECT `{}` FROM `{}` limit {} offset {} "
                      .format(self.dbField, self.dbTable, self.limit,
                              (watchBackPage - 1) * self.limit))
            self.cursor.execute(select)
            self.conn.commit()
            # 获取地址元组
            dataPathTuple = tuple(self.cursor.fetchall())
        except:
            pass
        return dataPathTuple

    def closeEvent(self, QCloseEvent):
        self.interruptFlag = 1
        while self.state:
            pass
        else:
            self.socket.close()
            self.conn.close()
            self.close()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ui = WaterfallDialog()
    ui.show()
    sys.exit(app.exec_())