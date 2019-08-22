#!/usr/bin/env python
# coding: utf-8

import time
import queue
import subprocess
from multiprocessing import Process


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
    from app_config.config import ABOUT_TRAINING, TEST_APP, IOS_MODEL_NAME, IOS_LABEL_NAME, RETRAIN_PATH
    import os
    from google_algorithm.training import start_training
    image_path = os.path.join(ABOUT_TRAINING, "zhihu", "iOS_1-50")
    output_graph = os.path.join(ABOUT_TRAINING, TEST_APP, "debug", "model", IOS_MODEL_NAME)
    output_labels = os.path.join(ABOUT_TRAINING, TEST_APP, "debug", "labels", IOS_LABEL_NAME)

    cmd = "python3 %s --image_dir %s --output_graph %s --output_labels %s" % (
    RETRAIN_PATH, image_path, output_graph, output_labels)
    process_training = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    fobj = open("terminal_text.txt", "w")
    while True:
        try:
            out, err = process_training.communicate(1)
            fobj.write(out)
            fobj.flush()
            if process_training.poll() is not None:
                pass
        except subprocess.TimeoutExpired:
            pass

