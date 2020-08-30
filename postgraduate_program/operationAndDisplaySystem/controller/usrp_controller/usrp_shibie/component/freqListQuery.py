"""
@File:FreqListSelect.py
@Author:lcx
@Date:2020/8/2816:38
@Desc:频点列表的数据库查询工具，输入表名，输出DTO
"""
import pymysql
from controller.usrp_controller.usrp_shibie.component.freqPointList import FreqPointList
def freqListQuery(databaseInfo, tableName):
    conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                                port=databaseInfo[1],  # 端口号
                                user=databaseInfo[2],  # 用户名
                                passwd=databaseInfo[3],  # 密码
                                db=databaseInfo[4],  # 库名
                                charset=databaseInfo[5])  # 链接字符集
    cur = conn.cursor()  # 创建游标
    select = 'select `biz_name`,`freql`,`freqr` from `%s`' %tableName
    cur.execute(select)
    entity = cur.fetchall()
    # print(entity)
    resultList = FreqPointList()
    for line in entity:
        resultList.setPointLine(line[0], [float(line[1]), float(line[2])])
        # resultList[line[0]] = [int(line[1]), int(line[2])]
    cur.close()
    conn.close()
    return resultList


if __name__ == '__main__':
    dbInfo = ['localhost',  # ID地址
                3306,  # 端口号
                'root',  # 用户名
                'root',  # 密码
                'cast',  # 库名
                'utf8']  # 链接字符集
    table = 'used_freq_point'
    rslt = freqListQuery(dbInfo, table)
    print(rslt.getPointList())
