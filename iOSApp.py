#!/usr/bin/env python
# coding: utf-8

from PyQt5 import QtWidgets

from Ui_MainWindow import Ui_MainWindow
from msg_queue.queue_manager import QueueManager

import os
import sys
import app_config
import shutil

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
    release_resource()
    try:
        app = QtWidgets.QApplication([])
        application = iOSAppTime()
        application.show()
        sys.exit(app.exec())
    finally:
        release_resource()

if __name__ == '__main__':
    main()


# todo 被测 app 中两个「知乎」

