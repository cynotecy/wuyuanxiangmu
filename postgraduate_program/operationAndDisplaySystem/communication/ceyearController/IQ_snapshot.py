import eisal

def getIQData(IP, centreFreq, bdWidth, appName="IQDemo"):
    # return一个data字符串，格式为"中心频点 带宽 采样率; realPart（空格分隔）; imagPart（空格分隔）"
    with eisal.Connection(IP, appName) as connection:
        snapshot = eisal.IQSnapshot(connection.native_handle())
        (header, iq) = snapshot.gene(centreFreq, bdWidth, numSweeps = 420)
        samplerate = header.sampleRate
        collectIformation = " ".join([str(centreFreq), str(bdWidth), str(samplerate)])
        realPartList = [str(x) for x in iq[1::2]]
        imagPartList = [str(x) for x in iq[::2]]
        realPart = " ".join(realPartList)
        imagPart = " ".join(imagPartList)
        rslt = ";".join([collectIformation, realPart, imagPart])
        return rslt

if __name__ == '__main__':
    # run()
    # snapshot = getSnapShotInstance("172.141.11.202", "IQDemo")
    # (header, iq) = snapshot.gene(92.6e6, 1e6)
    # writer = IQWriter()  # 写入文件
    # writer.writeToFile(r'IQ.txt', 10e3, header, iq)
    getSnapShotInstance("172.141.11.202", "IQDemo")


