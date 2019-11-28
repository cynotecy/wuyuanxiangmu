from socketDemo import zmqLocal
import os

# os.system('taskkill /f /t /im python2.exe')  # 杀掉python2任务

zmqLocal = zmqLocal.localZMQ()
startfreq = 50
endfreq = 70
startfreq = startfreq*1000000
endfreq = endfreq*1000000
reslt = zmqLocal.sendMessege('2,scan,IQ,' + str(startfreq) + ";" +str(endfreq))
print(reslt)
