# iOS App 启动时长测量工具
## 环境配置
+ 安装 adb
+ 安装 xcode
+ 安装 python 3.7
+ pip3 install tensorflow==1.13.2
+ pip3 install PyQt5

## 公共步骤
1. 手动安装需要测试的 App（本工具暂时支持「知乎」「头条」「百度」「微博」4种 App）
2. 连接手机，一次只能连接一台手机，否则无法区分
3. 执行 python3 iOSApp.py 启动程序
4. 如下图所示，选择「待测试的 App」

<div align="center">
    <img src="pictures/p1.png" width= "600" height = "400" alt = "选择待测 App" align=center>
</div>

## 操作步骤
1. 点击最下方「平台」，选择操作系统类型
2. 按照程序提示，等待「操作系统版本」识别完毕后，点击「被测 App」，选择你想要截图的 App
3. 点击「启动 minicap」，然后等待进度条结束
4. 点击「开始截图」，再点击手机上的对应 App
5. 当 App 运行到目标界面时，点击「结束截图」

<div align="center">
    <img src="pictures/p2.png" width= "600" height = "400" alt = "开始截图" align=center>
</div>


## 注意事项 1（非常重要）
1. 一定要按照提示，等待进度条结束后，再点击手机上的 App，因为该等待过程包括 iOS minicap 连接初始化过程，如果不等待，会导致「截图不全」或者「坏图（无效图片）」，所以请耐心等待进度条执行完毕。

2. 当 「目标界面」 加载完毕后，请尽早点击「结束截图」，因为如果不点击「结束截图」，那么程序将不断截图，并发送到计算机，导致整个启动阶段包含很多冗余图片。

## 注意事项 2
如果出现「Python crash」的崩溃对话框，如果出现「崩溃对话框」（如下图 4 所示），请按下面步骤进行处理：
+ 请直接关闭该「启动时长测量工具」，并重新启动它。

<div align="center">
    <img src="pictures/p4.png" width= "600" height = "400" alt = "崩溃对话框" align=center>
</div>