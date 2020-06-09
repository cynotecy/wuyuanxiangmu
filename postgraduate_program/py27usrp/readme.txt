运行demo.py即可开启通信转发中台

如无usrp实物，可运行virtualUSRP.VirtualTransmit.py开启虚拟USRP。
该虚拟USRP的扫频和采集功能得到的数据参数将不受指令参数控制，
只要收到扫频指令，就会回传一个随机的900-950MHz频谱；
只要收到采集指令，就会回传一个中心频率940.6MHz，带宽3MHz，采样率12.5MHz的IQ数据。