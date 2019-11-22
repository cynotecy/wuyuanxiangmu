# -*- coding: utf-8 -*-
from Ui.UitoPy.Ui_wireless_data import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QIcon
import pymysql
import time
from datetime import datetime
import sys
import shutil
import uuid
import ziyuan_rc

class MainWindow(QDialog, Ui_Dialog):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon(':/图标/ooopic_1521110980.ico'))
        self.setupUi(self)
        self.pushButton_1.clicked.connect(self.on_pushButton_clicked_1)
        self.pushButton_2.clicked.connect(self.on_pushButton_clicked_2)
        self.pushButton_3.clicked.connect(self.on_pushButton_clicked_3)
        local_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
        local_time1 = datetime.strptime(local_time,"%Y/%m/%d %H:%M:%S")
        print(type(local_time1), local_time1)
        self.dateTimeEdit.setDateTime(local_time1)
    def on_pushButton_clicked_1(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", r"..\usrp_recvfiles", )
        print(filename)
        self.lineEdit.setText(filename)

    def on_pushButton_clicked_2(self):
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                  r"..\IqOutput", )
        print(filename)
        self.lineEdit_7.setText(filename)
    def on_pushButton_clicked_3(self):
        print('upload pushed')
        if (
                self.lineEdit.text() or self.lineEdit_3.text() or self.lineEdit_9.text() or self.lineEdit_10.text()
                or self.lineEdit_4.text()):
            conn = pymysql.connect(host='localhost',  # ID地址
                                   port=3306,  # 端口号
                                   user='root',  # 用户名
                                   passwd='root',  # 密码
                                   db='cast',  # 库名
                                   charset='utf8')  # 链接字符集
            cur = conn.cursor()  # 创建游标
            device = self.comboBox.currentText()
            print(type(device))
            #
            createTime_ = self.dateTimeEdit.text()
            # 转换成时间数组
            timeArray = time.strptime(createTime_, "%Y/%m/%d %H:%M:%S")
            # 转换成时间戳
            createTime = time.mktime(timeArray)*1000
            print(type(createTime))
            #
            place = self.lineEdit_6.text()
            print(type(place))
            readfile = self.lineEdit.text()
            source = readfile
            source_arry = source.split(".")
            print(source_arry)
            id = uuid.uuid1()
            target = r'..\EMCfile\data\%s.%s' % (id, source_arry[-1])
            try:
                shutil.copy(source, target)
            except IOError as e:
                print("Unable to copy file. %s" % e)
            except:
                print("Unexpected error:", )
            datafile = '/file/%s.%s' % (id, source_arry[-1])
            print(type(datafile))
            items = self.lineEdit_2.text()
            print(type(items))
            name = self.lineEdit_3.text()
            print(type(name))
            try:
                bdwth = float(self.lineEdit_9.text())
            except:
                QMessageBox.information(self, "提示", "带宽必须为数字")
            # print(type(bdwth))
            else:
                try:
                    ctrfrq = float(self.lineEdit_10.text())
                except:
                    QMessageBox.information(self, "提示", "中心频率必须为数字")
                else:
                    # print(type(ctrfrq))
                    modulation = self.lineEdit_4.text()
                    print(type(modulation))
                    snr = self.lineEdit_5.text()
                    print(type(snr))
                    remarks = self.lineEdit_8.text()
                    print(type(remarks))

                    ################################
                    readReport = self.lineEdit_7.text()
                    reportSource = readReport
                    reportSource_arry = reportSource.split(".")
                    reportId = uuid.uuid1()
                    reportTarget = r'..\EMCfile\data\%s.%s' % (reportId, reportSource_arry[-1])
                    try:
                        shutil.copy(reportSource, reportTarget)
                    except IOError as e:
                        print("Unable to copy file. %s" % e)
                    except:
                        print("Unexpected error:", )
                    dataReport = '/file/%s.%s' % (reportId, reportSource_arry[-1])
                    ################################
                    print(name, items, createTime, device, modulation, snr, place, ctrfrq, bdwth, datafile, remarks)
                    insert = 'INSERT INTO `emc_data`(`name`, `item`, `create_time`, `device`, `modulation`' \
                             ', `snr`, `place`, `center_freq`, `band_width`, `data`, `remarks`, `report`' \
                             ') VALUES ("%s", "%s", %s, "%s", "%s", "%s", "%s",' \
                             ' "%s", "%s", "%s", "%s", "%s")'%(name, items, createTime, device, modulation, snr, place, ctrfrq, bdwth,
                                                                 datafile, remarks, dataReport) # 新增SQL语句
                    print(insert)
                    # try:
                    cur.execute(insert)  # 执行新增SQL语句
                    print('新增语句')
                    # cur.execute(sql_update)  # 执行修改SQL语句
                    # cur.execute(sql_delete)  # 执行删除SQL语句
                    conn.commit()  # 提交事务
                    # except Exception as e:
                    #     conn.rollback()  # 如果发生错误，则回滚事务
                    #     print('上传失败')
                    # finally:
                    cur.close()  # 关闭游标
                    conn.close()  # 关闭数据库
                    # self.lineEdit_6.clear()
                    # self.lineEdit.clear()
                    # self.lineEdit_2.clear()
                    # self.lineEdit_3.clear()
                    # self.lineEdit_9.clear()
                    # self.lineEdit_10.clear()
                    # self.lineEdit_4.clear()
                    # self.lineEdit_5.clear()
                    # self.lineEdit_8.clear()
                    # self.lineEdit_7.clear()
                    QMessageBox.information(self, "提示", "上传成功")
                    self.lineEdit_6.clear()
                    self.lineEdit.clear()
                    self.lineEdit_2.clear()
                    self.lineEdit_3.clear()
                    self.lineEdit_9.clear()
                    self.lineEdit_10.clear()
                    self.lineEdit_4.clear()
                    self.lineEdit_5.clear()
                    self.lineEdit_8.clear()
                    self.lineEdit_7.clear()
                    # self.close

        else:
            print('failed')
            QMessageBox.information(self, "提示", "请输入必填数据")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
