#!/usr/bin/env python
# coding: utf-8
from queue_manager import QueueManager
from multiprocessing import Process
import os

import time
import queue
import multiprocessing

class Hoo(object):
    def __init__(self, eoo):
        self.eoo = eoo
        self.shared_queue_1 = self.eoo.queue_1
        self.shared_queue_2 = self.eoo.queue_2

    def test_queue(self):
        while True:
            try:
                recv = self.shared_queue_1.get_nowait()
                print("test3.py", recv)
                break
            except queue.Empty:
                pass



def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f():
    for i in range(6):
        print("pid: %d %d" % (os.getpid(), i))
        time.sleep(2)
    return "f"

def g():
    for i in range(6, 0, -1):
        print("pid: %d %d" % (os.getpid(), i))
        time.sleep(2)
    return "g"

if __name__ == '__main__':
    dt = {'a': 1, 'b': 2}
    for i in dt.values():
        print(i)