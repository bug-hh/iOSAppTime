#!/usr/bin/env python
# coding: utf-8

from other.ios_driver_factory import iOSDriverFactory

def handle():
    driver = iOSDriverFactory.get_iOS_Driver()

if __name__ == '__main__':
    handle()