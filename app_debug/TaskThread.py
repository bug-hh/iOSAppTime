#!/usr/bin/env python
# coding: utf-8

import threading
from PyQt5.QtCore import pyqtSignal

class TaskThread(threading.Thread):

    signal_dt = {}
    for i in range(10):
        signal_dt[i] = pyqtSignal(int)

    def __init__(self, thread_id, target_func, args):
        threading.Thread.__init__(self, target=target_func, args=args)
        self.thread_id = thread_id

def task(n, m):
    print(m)
    for i in range(n):
        print(i)

def main():
    t = TaskThread(thread_id=0, target_func=task, args=(11, 12))
    t.start()
    t.join()

if __name__ == '__main__':
    main()