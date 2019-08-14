# -*- coding: utf-8 -*-
import os

PACKAGE_NAME = 'com.zhihu.ios-dev'
ACTIVITY_PATH = '.app.ui.activity.LauncherActivity'

ROOT_PATH = os.path.dirname(__file__)
RETRAIN_PATH = os.path.join(ROOT_PATH, "google_algorithm", "retrain.py")
APK_PATH = os.path.join(os.path.dirname(__file__), 'app', 'zhihu_v6_4_0.apk')
TMP_IMG_DIR = os.path.join(os.path.dirname(__file__), 'capture', 'tmp_pic')
IOS_MINICAP_PATH = os.path.join(os.path.dirname(__file__), 'minicap', 'ios_run.sh')
IOS_MODEL_NAME = "ios_zhihu_output_graph.pb"
IOS_LABEL_NAME = "ios_zhihu_output_labels.txt"

ABOUT_TRAINING = os.path.join(os.path.dirname(__file__), 'training')
TEST_APP = "zhihu"

if not os.path.exists(ABOUT_TRAINING):
    os.makedirs(ABOUT_TRAINING)

STAGE = ['start', 'newlogo', 'ad', 'loading', 'words', 'end', 'home']
ANDROID_PERCENT = {'start': 0.90, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.55, 'loading': 0.60, 'words': 0.90, 'end': 0.9}
IOS_PERCENT = {'start': 0.80, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.90, 'loading': 0.50, 'words': 0.90, 'end': 0.85, 'home': 0.90}
SORTED_STAGE = {'start':1, 'newlogo':2, 'ad':3, 'loading':4, 'words':5, 'end':6}
EXCLUDED_LIST = ['ad']
WEICHAT_SEND_MESSAGE_URL = 'http://smsc.in.zhihu.com/message/send?userid=taffy'
WEICHAT_GET_TOKEN_URL = 'http://smsc.in.zhihu.com/token'
