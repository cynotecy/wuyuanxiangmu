
"""
文件、文件夹、数据库操作函数合集
"""
import os
import shutil
import time
import pymysql

#清空文件夹，本来没有就创建一个
def cleanDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        time.sleep(1)
        os.mkdir(path)

#清空数据库表
def cleanDBTable(dbInfo, tableName):
    cleanDBTableConn = pymysql.connect(dbInfo)  # 链接字符集
    cleanDBTableCur = cleanDBTableConn.cursor()  # 创建游标
    cleanDBTableCurDelete = 'truncate table `%s`' % tableName
    cleanDBTableCur.execute(cleanDBTableCurDelete)
    cleanDBTableCur.close()

#文件夹存在保证
def makesureDirExist(path):
    if not os.path.exists(path):
        os.makedirs(path)

#文件存在检测，判断文件夹中是否有fileType类型的文件
def dirNotEmpty(fileType, dirPath):
    lists = os.listdir(dirPath)
    rslt = False
    for path in lists:
        if ('.' + fileType) in path:
            rslt = True
            break
    return rslt

# 获取文件夹中最新的文件
def getLatestFile(fileType, dataPath):
    lists = os.listdir(dataPath)
    typeList = []
    for path in lists:
        if '.' + fileType in path:
            typeList.append(path)
    typeList.sort(key=lambda fn: os.path.getmtime(dataPath + "\\" + fn))
    fileLatest = os.path.join(dataPath, typeList[-1])
    return fileLatest

# 文件夹扫描线程，dir中的文件数量达到rowNum时关闭线程且将文件数量置入队列中
def floderScanThread(dirName, rowNum, q):
    while True:
        time.sleep(1)
        fileNum = sum([len(x) for _, _, x in os.walk(os.path.dirname(dirName))])
        if fileNum == rowNum and q.empty():
            q.put(fileNum)
            break
        elif fileNum == rowNum and not q.empty():
            q.get()
            q.put(fileNum)
            break
