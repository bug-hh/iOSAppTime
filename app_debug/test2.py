#!/usr/bin/env python
# coding: utf-8
from msg_queue.queue_manager import QueueManager

from multiprocessing import Process
from threading import Thread

from queue import Queue
import os
import queue


class Eoo(object):
    def __init__(self):
        self.queue_1 = Queue()
        self.queue_2 = Queue()
        QueueManager.register('get_queue_1', callable=lambda: self.queue_1)
        QueueManager.register('get_queue_2', callable=lambda: self.queue_2)
        self.manager = QueueManager(address=('localhost', 44444), authkey=b'1234')
        self.manager.start()
        self.shared_queue_1 = self.manager.get_queue_1()
        self.shared_queue_2 = self.manager.get_queue_2()

    def update_task(self):
        t = Thread(target=self.read)
        t.start()
        t.join()

    def read(self):
        try:
            while True:
                recv = self.shared_queue_1.get_nowait()
                print(recv)
        except queue.Empty:
            pass

    def task(self):
        for i in range(6):
            self.shared_queue_1.put(i)

    def test_queue(self):
        str1 = "received from test1.py shared_queue_1"
        while True:
            try:
                self.queue_1.put(str1)
                break
            except queue.Empty:
                pass

    @staticmethod
    def close_shared_server():
        state, pid = Eoo.query_service(55677)
        if pid != -1:
            os.system("kill %s" % pid)

    @staticmethod
    def query_service(port):
        fobj = os.popen("lsof -i tcp:%d" % port)
        state = fobj.read().strip()
        if len(state) == 0:
            return False, -1
        ls = state.split("\n")

        status_list = ls[-1].split()
        status = status_list[-1]
        pid = status_list[1]
        return status == "(LISTEN)", pid

if __name__ == '__main__':
    e = Eoo()
    p = Process(target=e.task)
    p.start()
    p.join()
    e.update_task()
