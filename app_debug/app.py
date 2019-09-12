#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from subprocess import Popen, PIPE
from app_config.config import APK_PATH

class Android(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.APK_PATH = APK_PATH
    # Adb 命令
    def adb(self, args, *popenargs, **kwargs):
        rlt = ['adb', '-s', self.device_id]
        # rlt = ['adb']
        rlt.extend(args)
        return Popen(rlt, *popenargs, **kwargs)

    def get_aapt_data(self):
        output = os.popen('aapt dump badging %s' % self.APK_PATH).read()
        return output

    # 打开锁屏
    def unlock_screen(self):
        print('打开锁屏')
        self.adb(['shell', 'input', 'keyevent', 82])

    # 卸载 Apk
    def uninstall_apk(self, package_name):
        print('正在卸载 Apk...')
        self.adb(['uninstall', package_name]).wait()

    # 安装 Apk
    def install_apk(self, apk_path):
        print('正在安装 Apk...')
        exit_code = self.adb(['install', '-r', '-d', apk_path]).wait()
        if exit_code:
            # 安装失败则退出
            print('🌧 安装 Apk 失败')
            sys.exit(exit_code)

    def start_app(self, package_name, activity_path):
        print('启动 %s...') % package_name
        self.adb([
            'shell', 'am', 'start', '-W', '-n', '%s/%s' % (package_name, activity_path)
        ], stdout=PIPE)

    def kill_app(self, package_name):
        print('杀掉 app...')
        self.adb(['shell', 'am', 'force-stop', package_name]).wait()


class IOS(object):
    def __init__(self, bundle):
        self.udid = ''
        self.bundleId = 'com.zhihu.ios-dev'
        self.bundle = bundle

    def ios_deploy(self, args, *popenargs, **kwargs):
        # rlt = ['ios-deploy', '--id', self.udid]
        rlt = ['ios-deploy']
        rlt.extend(args)
        return Popen(rlt, *popenargs, **kwargs)

    def get_udid(self):
        p_udid = Popen('idevice_id -l', shell=True, stdout=PIPE)
        time.sleep(1)
        if p_udid.poll() is not None:
            self.udid = p_udid.stdout.readlines()[0]

    def uninstall_app(self):
        print('正在卸载 App...')
        self.ios_deploy(['--uninstall_only', '--bundle_id', '%s' % self.bundleId]).wait()

    def install_and_start_app(self):
        print('正在安装并启动 App...')
        self.ios_deploy(['--justlaunch', '--debug', '--bundle', '%s' % self.bundle])

    def install_app(self):
        print('正在安装 App...')
        self.ios_deploy(['--bundle', '%s' % self.bundle])

    def start_app(self):
        print('正在启动 App...')
        Popen('idevicedebug -u f955925d4043f9d8fbb014da293dcf6ecc58b8aa run com.zhihu.ios-dev', shell=True, stdout=PIPE)
