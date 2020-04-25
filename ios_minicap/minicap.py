# -*- coding: utf-8 -*-

import datetime
import os
import socket
import threading
import shutil
import queue
import time
import json

from ios_minicap.banner import Banner
from datetime import datetime

from multiprocessing import Process

from msg_queue.queue_manager import QueueManager

from app_config.config import TMP_IMG_ZHIHU_DIR
from app_config.config import TMP_IMG_TOP_TODAY_DIR
from app_config.config import TMP_IMG_BAIDU_DIR
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import JSON_SIGNAL_KEY
from app_config.config import JSON_SIGNAL_UPDATE_KEY

import app_config.config

class MinicapStream(object):
    __instance = None
    __mutex = threading.Lock()
    TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR
    image_path = TMP_IMG_DIR
    def __init__(self, port, test_app_code):
        self.ip = "127.0.0.1"  # 定义IP
        self.port = port  # 监听的端口
        self.pid = 0  # 进程ID
        self.banner = Banner()  # 用于存放banner头信息
        self.minicap_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.read_image_stream_task = None
        self.push = None
        self.GLOBAL_HEADER_LENGTH = 24
        self.FRAME_HEADER_LENGTH = 4
        self.buffer = None
        self.platform = "iOS" if port == 33333 else "Android"
        self.index = 0
        self.frame_size = 0
        self.connectInfo = False
        QueueManager.register('get_queue')
        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.connect()
        self.shared_queue = self.manager.get_queue()
        self.shared_app_info_queue = self.manager.get_app_info_update_queue()
        self.running = False
        self.times = 0
        self.test_app_code = test_app_code
        if self.test_app_code == 1:
            self.TEST_APP = "zhihu"
            MinicapStream.TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR

        elif self.test_app_code == 2:
            self.TEST_APP = "weibo"
            MinicapStream.TMP_IMG_DIR = TMP_IMG_WEIBO_DIR

        elif self.test_app_code == 3:
            self.TEST_APP = "top_today"
            MinicapStream.TMP_IMG_DIR = TMP_IMG_TOP_TODAY_DIR

        elif self.test_app_code == 4:
            self.TEST_APP = "baidu"
            MinicapStream.TMP_IMG_DIR = TMP_IMG_BAIDU_DIR

    @staticmethod
    def get_builder(img_path, port, lock):
        """Return a single instance of TestBuilder object """
        if (MinicapStream.__instance is None):
            MinicapStream.__mutex.acquire()
            if (MinicapStream.__instance is None):
                MinicapStream.__instance = MinicapStream(img_path, port)
            MinicapStream.__mutex.release()
        elif (MinicapStream.__instance.img_path != img_path):
            MinicapStream.__instance.img_path = img_path
        print('MinicapStream.__instance.img_path: %s' % img_path)
        return MinicapStream.__instance

    def run(self):
        self.read_image_stream_task = Process(target=self.read_image_stream)
        self.read_image_stream_task.daemon = True
        self.read_image_stream_task.start()

    def _get_signal(self):
        try:
            msg = self.shared_queue.get_nowait()
            return msg
        except queue.Empty:
            return 0

    def _get_queue_info(self):
        try:
            pic_dir = self.shared_app_info_queue.get_nowait()
            MinicapStream.TMP_IMG_DIR = pic_dir
            return pic_dir
        except queue.Empty:
            return MinicapStream.TMP_IMG_DIR

    def _create_picture_dir(self):
        MinicapStream.image_path = os.path.join(self._get_queue_info(), self.platform, str(self.times))

        if not os.path.exists(MinicapStream.image_path):
            print('创建文件夹 %s ' % MinicapStream.image_path)
            os.makedirs(MinicapStream.image_path)
        else:
            shutil.rmtree(MinicapStream.image_path)
            print('删除已存在文件夹 %s ' % MinicapStream.image_path)
            os.makedirs(MinicapStream.image_path)
            print('创建文件夹 %s' % MinicapStream.image_path)

            
    def read_image_stream(self):
        # 开始执行
        # 启动socket连接
        self._connect_to_minicap()
        print("连接 minicap 成功")
        read_banner_bytes = 0
        banner_length = 2
        read_frame_bytes = 0
        frame_body_length = 0
        data_body = bytearray()

        # signal > 0 表示开始截图，当 signal > 0 表示截图的次数，即：tmp_pic/ 下的文件夹名
        while True:
            self.times = self._get_signal()
            if self.times > 0:
                break

        print("开始截图")
        self._create_picture_dir()

        while True:
            # signal == -1 响应停止截图
            signal = self._get_signal()
            while signal == -1:
                temp = self._get_signal()
                if temp > 0:
                    self.times = temp
                    self._create_picture_dir()
                    status, pid = query_socket(self.port)
                    if not status:
                        self._connect_to_minicap()
                    break
                elif temp == -2:
                    self._disconnect_from_minicap()
                    return

            # signal == -2 响应终止套接字
            if self._get_signal() == -2:
                break

            reallen = self.minicap_socket.recv(self.port)
            length = len(reallen)

            if not length:
                continue
            # print(length)
            cursor = 0
            # cursor < length，存在未处理数据
            while cursor < length:
                # Banner 信息，位置 0-23
                if read_banner_bytes < banner_length:
                    if read_banner_bytes == 0:
                        self.banner.Version = reallen[cursor]
                    elif read_banner_bytes == 1:
                        banner_length = reallen[cursor]
                        self.banner.length = banner_length
                    elif read_banner_bytes in [2, 3, 4, 5]:
                        self.banner.pid += (reallen[cursor] << ((read_banner_bytes - 2) * 8)) >> 0
                    elif read_banner_bytes in [6, 7, 8, 9]:
                        self.banner.real_width += (reallen[cursor] << ((read_banner_bytes - 6) * 8)) >> 0
                    elif read_banner_bytes in [10, 11, 12, 13]:
                        self.banner.real_height += (reallen[cursor] << (
                                (read_banner_bytes - 10) * 8)) >> 0
                    elif read_banner_bytes in [14, 15, 16, 17]:
                        self.banner.virtual_width += (reallen[cursor] << (
                                (read_banner_bytes - 14) * 8)) >> 0
                    elif read_banner_bytes in [18, 19, 20, 21]:
                        self.banner.virtual_height += (reallen[cursor] << (
                                (read_banner_bytes - 18) * 8)) >> 0
                    elif read_banner_bytes == 22:
                        self.banner.Orientation = reallen[cursor] * 90
                    elif read_banner_bytes == 23:
                        self.banner.Quirks = reallen[cursor]
                    cursor += 1
                    read_banner_bytes += 1
                    if read_banner_bytes == banner_length:
                        print(self.banner.__str__())
                # 图片二进制信息，4个字符
                elif read_frame_bytes < 4:
                    frame_body_length = frame_body_length + (
                            (reallen[cursor] << (read_frame_bytes * 8)) >> 0)
                    cursor += 1
                    read_frame_bytes += 1
                else:
                    if length - cursor >= frame_body_length:
                        data_body.extend(reallen[cursor:(cursor + frame_body_length)])
                        if data_body[0] != 0xFF or data_body[1] != 0xD8:
                            return
                        # self.picture.put(dataBody)
                        # 打印 Queue 中图片数量
                        # print self.get_d()
                        # 保存图片
                        # print "pic path : " + file_path
                        image_file_path = os.path.join(MinicapStream.image_path, MinicapStream.get_file_name())
                        self.save_file(image_file_path, data_body)
                        cursor += frame_body_length
                        frame_body_length = 0
                        read_frame_bytes = 0
                        data_body = bytearray()
                    else:
                        data_body.extend(reallen[cursor:length])
                        frame_body_length -= length - cursor
                        read_frame_bytes += length - cursor
                        cursor = length

        self._disconnect_from_minicap()

    def _connect_to_minicap(self):
        status, pid = query_service(self.port)

        while not status:
            print("正在等待 minicap 初始化完成")
            status, pid = query_service(self.port)

        code = self.minicap_socket.connect_ex((self.ip, self.port))

        if code != 0:
            print(self.ip, self.port)
            print("连接 minicap 套接字失败")

    def _disconnect_from_minicap(self):
        self.minicap_socket.shutdown(2)
        self.minicap_socket.close()

    def save_file(self, file_name, data):
        file = open(file_name, "wb")
        file.write(data)
        file.flush()
        file.close()

    @staticmethod
    def get_file_name():
        now = datetime.now()
        file_name = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        return file_name + ".jpg"

def query_socket(port):
    fobj = os.popen("lsof -i tcp:%d" % port)
    state = fobj.read().strip()
    if len(state) == 0:
        return False, -1
    ls = state.split("\n")
    ls.reverse()
    for item in ls:
        status_list = item.strip().split()
        status = status_list[-1].strip()
        pid = status_list[1].strip()
        cmd_name = status_list[0].strip()
        if cmd_name == "Python":
            return status == "(ESTABLISHED)", pid
    return False, -1

def query_service(port):
    fobj = os.popen("lsof -i tcp:%d" % port)
    state = fobj.read().strip()
    if len(state) == 0:
        return False, -1
    ls = state.split("\n")
    ls.reverse()
    for item in ls:
        status_list = item.split()
        status = status_list[-1].strip()
        pid = status_list[1].strip()
        cmd_name = status_list[0].strip()
        if cmd_name in ["ios_minic", "adb"]:
            return status in ["(ESTABLISHED)", "(LISTEN)"], pid
    return False, -1

if __name__ == '__main__':
    mini = MinicapStream(TMP_IMG_ZHIHU_DIR, 33333, None)
    mini.run(15)
    # mini.parse()