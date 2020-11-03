"""
@File:dbOperation.py
@Author:lcx
@Date:2020/10/1422:38
@Desc:pico瀑布图数据库入库注解
"""
from functools import update_wrapper
from monitor.waterfall.compresse.LZ4 import *
import shutil
import os

def dbUpload(dbField=['id','create_time', 'data_path']):
    """
    :param:无参数，直接调用类变量
    :return:
    """
    def upload(f):
        # f接函数对象
        def load(self, *args, **kwds):
            # 调用被注解函数
            f(self, *args, **kwds)

            # 数据文件存储
            if self.n == 1:
                dataPath = os.path.join(self.path, self.filePrefix.strip(" ") + ".csv")
            else:
                dataPath = os.path.join(self.path, self.filePrefix+"({}).csv".format(self.n))
            if os.path.exists(dataPath) and self.fileNum>1:
                ctime = int(os.stat(dataPath).st_ctime*1000)
                shutil.copy(dataPath, self.fileSavingPath)
                (path, filename) = os.path.split(dataPath)

                # 数据地址记录入库
                tableName = "waterfall_data_pico_{}".format(self.nowTime)
                try:
                    insert = "INSERT INTO `{}`(`{}`,`{}`,`{}`) VALUES ('{}',{},'{}')".format(
                        tableName, dbField[0], dbField[1], dbField[2], self.n,
                        ctime, ("/file/"+ self.relativeDirPath+"/"+ filename))

                    self.cur.execute(insert)
                    self.conn.commit()
                    self.n += 1
                    self.id += 1
                except:
                    self.conn.rollback()
                    if os.path.exists(os.path.join(self.fileSavingPath, filename)):
                        os.remove(os.path.join(self.fileSavingPath, filename))
        # 更新包裹函数，使其更像被包裹函数（我理解为将被包裹函数的参数传给包裹函数）
        update_wrapper(load, f)
        return load

    return upload

def dbDownload():
    """
    :param:dbConnection, tableName, createTime
    :return:
    """
    pass


if __name__ == '__main__':
    pass
