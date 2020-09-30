import eisal


def Sample_Rate(samplerate_insert=28e6):
    if samplerate_insert > 14e6:
        sample_rate = 28e6
        numblock = 100
    elif 7e6 < samplerate_insert <= 14e6:
        sample_rate = 14e6
        numblock = 6
    elif 3.5e6 < samplerate_insert <= 7e6:
        sample_rate = 7e6
        numblock = 6
    elif 1.75e6 < samplerate_insert <= 3.5e6:
        sample_rate = 3.5e6
        numblock = 6
    else:
        sample_rate = 1.75e6
        numblock = 6
    return sample_rate, numblock


def getIQData(IP, centreFreq, bdWidth, SampleRate, appName="IQDemo"):
    # return一个data字符串，格式为"中心频点 带宽 采样率; realPart（空格分隔）; imagPart（空格分隔）"
    with eisal.Connection(IP, appName) as connection:
        eisal.AbortAll(connection)
        scaner = eisal.IQScaner(connection.native_handle())
        scaner.config([centreFreq], [Sample_Rate(SampleRate)[0]])  # 设置中心频率和采样率，参数都是list类型
        transferPoint = 2048  # 一次传2048点
        nblk = Sample_Rate(SampleRate)[1]
        scaner.start(numSweep=1, numBlock=nblk, numTrasnfer=transferPoint)
        samplerate = Sample_Rate(SampleRate)[0]
        collectIformation = " ".join([str(centreFreq), str(bdWidth), str(samplerate)])
        realPart = ''
        imagPart = ''
        for header, iq in scaner:
            realPartList = [str(x) for x in iq[0:-1:2]]
            imagPartList = [str(x) for x in iq[1::2]]
            realPart_each = " ".join(realPartList)
            imagPart_each = " ".join(imagPartList)
            realPart += realPart_each + " "
            imagPart += imagPart_each + " "
        rslt = ";".join([collectIformation, realPart[:-1], imagPart[:-1]])
        # rslt = rslt[:-1]
        return rslt

if __name__ == '__main__':
    result = getIQData("172.141.11.202", 92.6e6, 8e6, 12e6, "IQDemo")
