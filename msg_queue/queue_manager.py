#!/usr/bin/env python
# coding: utf-8

from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    SHARED_PORT = 44455
    MINICAP_PORT = 33333
    ANDROID_PORT = 1313