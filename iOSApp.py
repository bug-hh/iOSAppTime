#!/usr/bin/env python
# coding: utf-8

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from Ui_MainWindow import Ui_MainWindow
from queue_manager import QueueManager

import os
import sys

class iOSAppTime(QtWidgets.QMainWindow):
    def __init__(self):
        super(iOSAppTime, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.start_update_ui_thread()

def close_shared_server():
    state, pid = Ui_MainWindow.query_service(QueueManager.SHARED_PORT)
    if pid != -1:
        os.system("kill %s" % pid)

def close_minicap():
    state, pid = Ui_MainWindow.query_service(QueueManager.MINICAP_PORT)
    if pid != -1:
        os.system("kill %s" % pid)

def release_resource():
    close_shared_server()
    close_minicap()

def main():
    try:
        app = QtWidgets.QApplication([])
        application = iOSAppTime()
        application.show()
        sys.exit(app.exec())
    finally:
        release_resource()

if __name__ == '__main__':
    main()

# todo 用 2 debug 一下搜索算法
# todo textBrowser 要改
# todo 进程已经结束了，还在打印
# todo 打印的信息是纵向的，应该是横向的
# todo 截图时，等待 minicap 的时间 5s 久了一点，导致截了很多张没用的图
