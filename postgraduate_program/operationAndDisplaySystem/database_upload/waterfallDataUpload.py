import shutil
import uuid

import pymysql

"""
48h频域采集文件入库，每次运行时自动清空数据库表，但不会清空文件存储。
自动扫描'D:\\postgraduate_program\\48recv\\%s\\' % usrp_name下的全部文件
并将它们存储到'D:\\postgraduate_program\\EMCfile\\waterfall\\%s\\' % usrp_name中，
然后将它们在'D:\\postgraduate_program\\EMCfile\\waterfall\\%s\\' % usrp_name中的地址存储到
cast库'waterfall_data_%s' % usrp_name表中
"""

class Upload():

    def __init__(self, usrp_name):
        super(Upload, self).__init__()
        self.usrp_name = usrp_name
        self.conn = pymysql.connect(host='localhost',  # ID地址
                               port=3306,  # 端口号
                               user='root',  # 用户名
                               passwd='root',  # 密码
                               db='cast',  # 库名
                               charset='utf8')  # 链接字符集
        cur = self.conn.cursor()  # 创建游标
        delete = 'truncate table `waterfall_data_%s`' % (self.usrp_name)
        cur.execute(delete)
        cur.close()
        # local_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
        # local_time1 = datetime.strptime(local_time,"%Y/%m/%d %H:%M:%S")
        # print(type(local_time1), local_time1)

    def get_latest_file(self, data_path):
        import os
        lists = os.listdir(data_path)
        dat_list = []
        file_list = []
        for path in lists:
            if '.dat' in path:
                dat_list.append(path)
        if dat_list:
            dat_list.sort(key=lambda fn: os.path.getmtime(data_path + "\\" + fn))
        for i in range(len(dat_list)):
            file_list.append(os.path.join(data_path, dat_list[i]))
            # file_latest = os.path.join(data_path, dat_list[-1])
        return file_list
        # else:
        #     return "noFile"

    def upload(self):

        # alter = 'ALTER TABLE `waterfall_data_%s` auto_increment=1' % (self.usrp_name)
        # cur.execute(alter)  # 执行新增SQL语句
        # print('新增语句')
        self.conn.commit()  # 提交事务
        filename= r"..\48recv\%s" % self.usrp_name
        print(filename)
        readfile = self.get_latest_file(filename)
        # 上传文件
        for file in readfile:
            source = file
            source_arry = source.split(".")
            print(source_arry)
            uid = uuid.uuid1()
            target = r'..\EMCfile\waterfall\%s\%s.%s' % (self.usrp_name, uid, source_arry[-1])
            try:
                shutil.copy(source, target)
            except IOError as e:
                print("Unable to copy file. %s" % e)
            except:
                print("Unexpected error:", )
            datafile = '/file/%s.%s' % (uid, source_arry[-1])
            print(type(datafile))
            print(datafile)


            # 文件地址入库
            cur = self.conn.cursor()  # 创建游标

            insert = 'INSERT INTO `waterfall_data_%s`(`data_path`) VALUES ("%s")'%(self.usrp_name, datafile)
            # 新增SQL语句
            print(insert)
            # try:
            cur.execute(insert)  # 执行新增SQL语句
            print('新增语句')
            self.conn.commit()  # 提交事务
            cur.close()  # 关闭游标

        self.conn.close()  # 关闭数据库
        print("uploading finished")

if __name__ == '__main__':
    a = Upload('usrp1')
    file_list = a.upload()

