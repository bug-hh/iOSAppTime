#!/usr/bin/env python
# coding: utf-8

from app_debug.ios_driver_factory import iOSDriverFactory

def handle():
    driver = iOSDriverFactory.get_iOS_Driver()

if __name__ == '__main__':
    handle()