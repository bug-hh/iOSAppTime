# -*- coding: utf-8 -*-
import os

PACKAGE_NAME = 'com.zhihu.ios-dev'
ACTIVITY_PATH = '.app.ui.activity.LauncherActivity'

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RETRAIN_PATH = os.path.join(ROOT_PATH, "google_algorithm", "retrain.py")
APK_PATH = os.path.join(ROOT_PATH, 'app', 'zhihu_v6_4_0.apk')
TMP_IMG_DIR = os.path.join(ROOT_PATH, 'capture', 'tmp_pic')
# TMP_IMG_DIR = os.path.join(os.path.dirname(__file__), 'capture2', 'tmp_pic2')

IOS_MODEL_NAME = "ios_zhihu_output_graph.pb"
IOS_LABEL_NAME = "ios_zhihu_output_labels.txt"

ABOUT_TRAINING = os.path.join(ROOT_PATH, 'training')
ABOUT_CAPTURE = os.path.join(ROOT_PATH, 'capture', 'tmp_pic', 'iOS')

TEST_APP = "zhihu"

if not os.path.exists(ABOUT_TRAINING):
    os.makedirs(ABOUT_TRAINING)

STAGE = ['start', 'newlogo', 'ad', 'loading', 'words', 'end', 'home']
ANDROID_PERCENT = {'start': 0.90, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.55, 'loading': 0.60, 'words': 0.90, 'end': 0.9}
IOS_PERCENT = {'start': 0.96, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.90, 'loading': 0.98, 'words': 0.85, 'end': 0.85, 'home': 0.90}
SORTED_STAGE = {'start':1, 'newlogo':2, 'ad':3, 'loading':4, 'end':5}
EXCLUDED_LIST = ['start', 'ad']
JSON_MINICAP_KEY = 'MINICAP'
JSON_PROGRESS_BAR_KEY = 'PROGRESS_BAR'
JSON_TEXT_BROWSER_KEY = 'TEXT_BROWSER'
JSON_PID_KEY = 'pid'


HUMAN = {
    '2': {
        'start': ['2019-08-16_17-47-15-792374', 348, 0.99791116],
        'loading': ['2019-08-16_17-47-18-528193', 118, 0.97574824],
        'end': ['2019-08-16_17-47-19-860089', 135, 0.9958556],
        'app': [2.735, 1.331]
    },

    '5': {
        'start': ['2019-08-16_17-49-30-716272', 198, 0.9982168],
        'loading': ['2019-08-16_17-49-33-859590', 143, 0.9732444],
        'end': ['2019-08-16_17-49-34-890767', 424, 0.92708856],
        'app': [3.143, 1.031]
    },

    '6': {
        'start': ['2019-08-16_17-50-11-219618', 219, 0.99856025],
        'loading': ['2019-08-16_17-50-13-224837', 100, 0.9905061],
        'end': ['2019-08-16_17-50-14-643593', 0, 0.9895837],
        'app': [2.005, 1.418]
    },

    '7': {
        'start': ['2019-08-16_17-59-03-187622', 280, 0.997632],
        'loading': ['2019-08-16_17-59-06-069106', 106, 0.981791],
        'end': ['2019-08-16_17-59-07-151216', 0, 0.8718705],
        'app': [2.881, 1.082]
    },

    '8': {
        'start': ['2019-08-16_17-59-37-988644', 338, 0.99865294],
        'loading': ['2019-08-16_17-59-40-618910', 93, 0.986413],
        'end': ['2019-08-16_17-59-41-518037', 452, 0.88572186],
        'app': [2.630, 0.899]
    },

    '9': {
        'start': ['2019-08-16_18-05-03-391840', 58, 0.99850994],
        'loading': ['2019-08-16_18-05-05-522599', 103, 0.9863165],
        'end': ['2019-08-16_18-05-07-147079', 25, 0.9948336],
        'app': [2.130, 1.624]
    },

    '10': {
        'start': ['2019-08-16_18-07-06-594719', '', 0.9992337],
        'loading': ['2019-08-16_18-07-08-686230', '', 0.97442853],
        'end': ['2019-08-16_18-07-09-764880', '', 0.9749767],
        'app': [2.091, 1.078]
    }
}