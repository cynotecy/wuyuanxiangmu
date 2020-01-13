"""
@File:compressAndInsert.py
@Author:lcx
@Date:2020/1/1014:47
@Desc:压缩解压算法的上层封装，负责压缩入库和出库解压
"""
import os
from monitor.waterfall.compresse import LZ4

def compress(data, dbPk, dbCursor, dbTable, outputDir, dbField=['id', 'data_path']):
    outputPath = LZ4.lz4_compression(data, dbPk, outputDir)
    try:
        insert = 'INSERT INTO `{}`(`{}`,`{}`) VALUES ({},{})'.format(
            dbTable, dbField[0], dbField[1], dbPk, outputPath)
        dbCursor.excute(insert)
        dbCursor.commit()
    except:
        dbCursor.rollback()
        if os.path.exists(outputPath):
            os.remove(outputPath)

def decompress(path):
    x, y = LZ4.lz4_decompression(path)
    return x, y