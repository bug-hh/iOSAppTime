# -*- coding: utf-8 -*-

import datetime
import os
import socket
import threading
import shutil
import time
import queue

from config import TMP_IMG_DIR
from ios_minicap.banner import Banner
from datetime import datetime

from multiprocessing import Process

from queue_manager import QueueManager

from config import JSON_MINICAP_KEY
from config import JSON_PROGRESS_BAR_KEY
from config import JSON_TEXT_BROWSER_KEY

class MinicapStream(object):
    __instance = None
    __mutex = threading.Lock()

    def __init__(self, port):
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
        self.platform = "iOS"
        self.index = 0
        self.frame_size = 0
        self.connectInfo = False
        QueueManager.register('get_queue')
        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.connect()
        self.shared_queue = self.manager.get_queue()
        self.running = False
        self.times = 0
        self.image_path = ""


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

            return self.shared_queue.get_nowait()
        except queue.Empty:
            return 0

    def _create_picture_dir(self):
        self.image_path = os.path.join(TMP_IMG_DIR, self.platform, str(self.times))

        if not os.path.exists(self.image_path):
            print('创建文件夹 %s ' % self.image_path)
            os.makedirs(self.image_path)
        else:
            shutil.rmtree(self.image_path)
            print('删除已存在文件夹 %s ' % self.image_path)
            os.makedirs(self.image_path)
            print('创建文件夹 %s' % self.image_path)
            
    def read_image_stream(self):
        # 开始执行
        # 启动socket连接
        self._connect_to_minicap()
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
        
        self._create_picture_dir()
        
        while True:
            # signal == -1 响应停止截图
            signal = self._get_signal()
            while signal == -1:
                temp = self._get_signal()
                if temp > 0:
                    self.times = temp
                    self._create_picture_dir()
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
                        image_file_path = os.path.join(self.image_path, MinicapStream.get_file_name())
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
        self.minicap_socket.connect((self.ip, self.port))

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



if __name__ == '__main__':
    mini = MinicapStream(TMP_IMG_DIR, 33333, None)
    mini.run(15)
    # mini.parse()