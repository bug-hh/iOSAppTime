# -*- coding: utf-8 -*-
import os
import shutil

from config import TMP_IMG_DIR
from ios_minicap.minicap import MinicapStream

from subprocess import Popen
from subprocess import PIPE
from subprocess import TimeoutExpired

import socket

class Record(object):
    def __init__(self, times, port, platform, timeout=10):
        self.times = times
        self.port = port
        self.platform = platform
        self.timeout = timeout
        self.minicap = None

    def record(self, lock):
        img_path = os.path.join(TMP_IMG_DIR, self.platform, str(self.times))
        if not os.path.exists(img_path):
            print('创建文件夹 %s ' % img_path)
            os.makedirs(img_path)
        else:
            shutil.rmtree(img_path)
            print('删除创建文件夹 %s ' % img_path)
            os.makedirs(img_path)

        print('开始录屏...')
        instance = MinicapStream.get_builder(img_path, self.port, lock)
        self.minicap = instance
        instance.run(self.timeout)

    def stop_read(self):
        self.minicap.stop_read()

    def get_connect_info(self):
        return self.minicap.get_connectInfo()


if __name__ == '__main__':
    # UDID_CMD = "idevice_id -l"
    # fobj = os.popen(UDID_CMD)
    # DEVICE_ID = fobj.read().strip()
    #
    # PORT = 12345
    # RESOLUTION = "375x600"
    # PLATFORM = "iOS"
    # cwd = os.getcwd()
    # ios_minicap_path = os.path.join(cwd, "ios-minicap", "build")
    # os.chdir(ios_minicap_path)
    # os.system("./ios_minicap -u %s -p %d -r %s &" % (DEVICE_ID, PORT, RESOLUTION))
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    s.connect(("127.0.0.1", 12345))


