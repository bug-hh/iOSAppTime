#!/usr/bin/env python
# coding: utf-8

from appium import webdriver

class iOSDriverFactory(object):
    @staticmethod
    def get_iOS_Driver():
        iPhone7 = "fca126cd09569124c86d65d3b0afa214c3033cf6"
        iPhone7_2 = "f955925d4043f9d8fbb014da293dcf6ecc58b8aa"
        iPhone6 = "ffb5abd690e3d5c1474e18f521cc72be24c62fc8"
        iPhone8 = "2a069808570260cb5ce37bd48283c6acc6ff9146"
        UDID = iPhone7_2
        DEVICE_NAME = "iPhone"
        VERSION = "11.4.1"
        BUNDLEID = "com.zhihu.ios-dev"
        desired_caps = {}
        desired_caps['udid'] = UDID
        desired_caps['appium-version'] = "1.13.0"
        desired_caps['platformName'] = 'iOS'
        desired_caps['platformVersion'] = VERSION
        desired_caps['deviceName'] = DEVICE_NAME
        desired_caps['newCommandTimeout'] = 30000
        desired_caps['bundleId'] = BUNDLEID
        desired_caps['automationName'] = 'xcuitest'
        desired_caps['locationServicesAuthorized'] = True

        return webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

if __name__ == '__main__':
    ios_driver = iOSDriverFactory.get_iOS_Driver()