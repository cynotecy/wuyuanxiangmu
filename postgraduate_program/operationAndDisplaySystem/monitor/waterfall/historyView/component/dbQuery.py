"""
@File:tableNameCheck.py
@Author:lcx
@Date:2020/10/269:18
@Desc:表名查询
"""
import pymysql
import re
import numpy as np
def tableNameCheck(databaseInfo, tableNamePrefix):
    # tableNameReg = r'used_freq_point_list*'
    conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                           port=databaseInfo[1],  # 端口号
                           user=databaseInfo[2],  # 用户名
                           passwd=databaseInfo[3],  # 密码
                           db=databaseInfo[4],  # 库名
                           charset=databaseInfo[5])  # 链接字符集
    cur = conn.cursor()  # 创建游标
    select = 'show tables'
    cur.execute(select)
    entity = cur.fetchall()
    tableList = []
    for line in entity:
        if re.match(tableNamePrefix, line[0]):
            tableList.append(line[0])
    cur.close()
    conn.close()
    return tableList
def maxMinQuery(databaseInfo, tableName, fieldName, maxMin):
    conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                           port=databaseInfo[1],  # 端口号
                           user=databaseInfo[2],  # 用户名
                           passwd=databaseInfo[3],  # 密码
                           db=databaseInfo[4],  # 库名
                           charset=databaseInfo[5])  # 链接字符集
    cur = conn.cursor()  # 创建游标
    selectQuery = "SELECT `{}` FROM {} WHERE `{}` = (SELECT {}(`{}`) FROM {})".format(
        fieldName, tableName, fieldName, maxMin, fieldName, tableName
    )
    cur.execute(selectQuery)
    result = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return result

def intervalQuery(databaseInfo, tableName, fieldName, max, min):
    conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                           port=databaseInfo[1],  # 端口号
                           user=databaseInfo[2],  # 用户名
                           passwd=databaseInfo[3],  # 密码
                           db=databaseInfo[4],  # 库名
                           charset=databaseInfo[5])  # 链接字符集
    cur = conn.cursor()  # 创建游标
    # selectQuery = "SELECT `{}` FROM {} WHERE `{}` between {} and {}".format(
    #     fieldName, tableName, fieldName, max, min
    # )
    selectQuery = "SELECT `*` FROM {} WHERE `{}` between {} and {}".format(
        tableName, fieldName, max, min
    )
    cur.execute(selectQuery)
    result = cur.fetchall()
    cur.close()
    conn.close()
    resultArray = np.asarray(result)
    pkList = tuple(resultArray[:, 0])
    return pkList

def fieldQuery(databaseInfo, tableName, fieldName, keyFieldName, key):
    conn = pymysql.connect(host=databaseInfo[0],  # ID地址
                           port=databaseInfo[1],  # 端口号
                           user=databaseInfo[2],  # 用户名
                           passwd=databaseInfo[3],  # 密码
                           db=databaseInfo[4],  # 库名
                           charset=databaseInfo[5])  # 链接字符集
    cur = conn.cursor()  # 创建游标
    selectQuery = "SELECT `{}` FROM {} WHERE `{}` = '{}'".format(
        fieldName, tableName, keyFieldName, key
    )
    cur.execute(selectQuery)
    result = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return result

if __name__ == '__main__':
    intervalQuery(1603734401277,1603734420643)