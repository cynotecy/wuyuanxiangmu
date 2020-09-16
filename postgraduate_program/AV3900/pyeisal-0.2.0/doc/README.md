# pyeisal

**pyeisal**是**EISAL**库的python binding，实现了频谱扫描、IQ采集、AM/FM解调等主要功能。



## 运行环境

* **操作系统**

  * Windows 10  32bit and 64bit

  * Windows 7 SP1 32bit and 64bit

    

* **python运行环境**

  * Anaconda3-2018.12
  * python3.7或更高

---

* **Mircrosoft Visual C++ 2015 Redistributable(x64)**

  安装pyeisal压缩包中所提供的`vcredist_x64.exe`。如果计算机安装过Visual Studio S2015，或者在Windows的**卸载或更改程序**页面找到`Mircrosoft Visual C++ 2015 Redistributable(x64)`,可以不安装。

  

## 安装

### 创建Python开发环境

这里介绍Anaconda环境和Python虚拟环境的创建，可根据需求选择其中一种。

#### Anaconda3

1. 安装anaconda3 Windows版，下载地址：

   >  https://www.anaconda.com/distribution/

2. 从开始菜单栏找到**Anaconda Prompt**并打开

   ```powershell
   (base) C:\Users\admin>
   ```

3. 创建一个新的Anaconda环境

   ```powershell
   (base) C:\Users\admin>conda create --name eisal-env
   ```

4. 激活新的Anaconda环境

   ```powershell
   (base) C:\Users\admin>activate eisal-env
   (eisal-env) C:\Users\admin>
   ```



#### Python虚拟环境

1. 安装**python**(3.7及以上)

这里以Python3.7 64bit为例。系统可能存在多个版本的Python，这里假设安装路径为**D:\Python\Python37**，在安装过程中在并没有选择**添加到系统Path环境变量**。

| Python版本      | 安装路径           | 是否添加到系统Path环境变量 |
| --------------- | ------------------ | -------------------------- |
| Python3.7 64bit | D:\Python\Python37 | 否                         |



2. 安装**cffi virtualenv matplotlib pyqt5**库，以及自己需要的库。打开**cmd**或**powershell**：

```powershell
X:\>D:\Python\Python37\Scripts\pip install cffi virtualenv matplotlib pyqt5
```

matplotlib以及pyqt5用于pyeisal演示。

>如果`D:\Python\Python37`和`D:\Python\Python37\Scripts`被添加到Path环境变量，这里可以直接为：
>
>```powershell
>X:>pip install cffi virtualenv matplotlib pyqt5
>```
>
>下文用到的virtualenv命令也是类似。



3. **新建Python工程目录**(假设在D盘)

```powershell
D:\>md eisal_project && cd eisal_project
D:\eisal_project>
```
用于存放Python虚拟环境和自己的Python工程。像VSCode这样的工具在打开工程目录时，能够自动找到虚拟环境。



4. **创建虚拟环境**

```powershell
D:\eisal_project>D:\Python\Python36\Scripts\virtualenv --python=D:\Python\Python37\python.exe --system-site-packages eisal-env
```

   * `--python`指定虚拟环境对应的Python解释器，这里是**Python3.7 64bit**。

   * `--system-site-packages`选项让虚拟环境可以访问对应Python的site-packages，这样之前已有的库（比如cffi、matplotlib）就可以直接使用，不需要在虚拟环境重新安装。

   * `eisal-env`是虚拟环境名，在当前路径下创建eisal-env文件夹，用于python虚拟环境，名称可任意指定。

     


5. **激活虚拟环境**

   **powershell**

   ```powershell
   D:\eisal_project>.\eisal-env\Scripts\activate.ps1
   D:\eisal_project>
   ```

   **cmd**

   ```powershell
   D:\eisal_project>.\eisal-env\Scripts\activate.bat
   (eisal-env) D:\eisal_project>
   ```

   `(eisal-env)`表示已进入虚拟环境，可以在该powershell或cmd下运行Python脚本。也可以安装该虚拟环境专用的Python库：

   ```powershell
   (eisal-env) D:\eisal_project>pip install xxx
   ```

   这里的pip在`eisal-env\Scripts`中。

   

### 安装pyeisal

1. **安装pyeisal到虚拟环境**

   解压pyeisal.rar到任意路径，并在虚拟环境命令行下进入该路径。

   ```powershell
   (eisal-env) D:\>cd pyeisal
   (eisal-env) D:\pyeisal>python .\setup.py install
   ```

   安装过程未出错表明pyeisal安装完成。如果出现访问被拒绝，可以多试几次。

   

2. **测试pyeisal库**

   连接接收机，修改系统IP与接收机处于同一网段。

   * 频谱测试

   ```powershell
   (eisal-env) D:\pyeisal>python.exe .\example\spectrum_snapshot.py 192.168.1.12
   ```

   * IQ扫描测试

   ```powershell
   (eisal-env) D:\pyeisal>python.exe .\example\iq_snapshot.py 192.168.1.12
   ```

   `192.168.1.12`是接收机IP地址，出现GUI图形和数据曲线表明测试成功。


