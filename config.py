# -*- coding: utf-8 -*-
import os

PACKAGE_NAME = 'com.zhihu.ios-dev'
ACTIVITY_PATH = '.app.ui.activity.LauncherActivity'

ROOT_PATH = os.path.dirname(__file__)
RETRAIN_PATH = os.path.join(ROOT_PATH, "google_algorithm", "retrain.py")
APK_PATH = os.path.join(os.path.dirname(__file__), 'app', 'zhihu_v6_4_0.apk')

TMP_IMG_DIR = os.path.join(os.path.dirname(__file__), 'capture', 'tmp_pic')
# TMP_IMG_DIR = os.path.join(os.path.dirname(__file__), 'capture2', 'tmp_pic2')


IOS_MINICAP_PATH = os.path.join(os.path.dirname(__file__), 'minicap', 'ios_run.sh')
IOS_MODEL_NAME = "ios_zhihu_output_graph.pb"
IOS_LABEL_NAME = "ios_zhihu_output_labels.txt"

ABOUT_TRAINING = os.path.join(os.path.dirname(__file__), 'training')
ABOUT_CAPTURE = os.path.join(os.path.dirname(__file__), 'capture', 'tmp_pic', 'iOS')

TEST_APP = "zhihu"

if not os.path.exists(ABOUT_TRAINING):
    os.makedirs(ABOUT_TRAINING)

STAGE = ['start', 'newlogo', 'ad', 'loading', 'words', 'end', 'home']
ANDROID_PERCENT = {'start': 0.90, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.55, 'loading': 0.60, 'words': 0.90, 'end': 0.9}
IOS_PERCENT = {'start': 0.90, 'oldlogo': 0.90, 'newlogo': 0.90, 'ad': 0.90, 'loading': 0.90, 'words': 0.85, 'end': 0.85, 'home': 0.90}
SORTED_STAGE = {'start':1, 'newlogo':2, 'ad':3, 'loading':4, 'words':5, 'end':6}
EXCLUDED_LIST = ['start', 'ad']
JSON_MINICAP_KEY = 'MINICAP'
JSON_PROGRESS_BAR_KEY = 'PROGRESS_BAR'
JSON_TEXT_BROWSER_KEY = 'TEXT_BROWSER'
JSON_PID_KEY = 'pid'


HUMAN = {
    '2': {
        'start': ['2019-08-16_17-47-15-511255', 348, 0.9994531],
        'loading': ['2019-08-16_17-47-18-542763', 118, 0.9371213],
        'words': ['2019-08-16_17-47-19-827864', 47, 0.8076513],
        'end': ['2019-08-16_17-47-19-860089', 135, 0.9949949],
        'app': [3.03, 1.285, 1.317, 0.032]
    },

    '5': {
        'start': ['2019-08-16_17-49-30-581613', 198, 0.9994024],
        'loading': ['2019-08-16_17-49-33-897587', 143, 0.9678663],
        'words': ['2019-08-16_17-49-34-307329', 77, 0.8322137],
        'end': ['2019-08-16_17-49-34-890767', 424, 0.76388365],
        'app': [3.3, 0.409, 0.993, 0.583]
    },

    '6': {
        'start': ['2019-08-16_17-50-11-075394', 219, 0.999164],
        'loading': ['2019-08-16_17-50-13-224837', 100, 0.9066735],
        'words': ['2019-08-16_17-50-14-542264', 47, 0.9305444],
        'end': ['2019-08-16_17-50-14-643593', 0, 0.917635],
        'app': [2.14, 1.317, 1.418, 0.103]
    },

    '7': {
        'start': ['2019-08-16_17-59-02-923061', 280, 0.999280],
        'loading': ['2019-08-16_17-59-06-069106', 106, 0.9465108],
        'words': ['2019-08-16_17-59-06-840339', 67, 0.9773755],
        'end': ['2019-08-16_17-59-07-151216', 0, 0.5085088],
        'app': [3.14, 0.771, 1.082, 0.31]
    },

    '8': {
        'start': ['2019-08-16_17-59-37-755498', 338, 0.9991936],
        'loading': ['2019-08-16_17-59-40-656836', 93, 0.9778666],
        'words': ['2019-08-16_17-59-41-155057', 87,  0.66565025],
        'end': ['2019-08-16_17-59-41-650565', 452, 0.56756794],
        'app': [2.9, 0.498, 0.993, 0.495]
    },

    '9': {
        'start': ['2019-08-16_18-05-03-145833', 58, 0.99937963],
        'loading': ['2019-08-16_18-05-05-522599', 103, 0.9243997],
        'words': ['2019-08-16_18-05-06-805342', 77, 0.9471387],
        'end': ['2019-08-16_18-05-07-147079', 25, 0.9837452],
        'app': [2.376, 1.282, 1.624, 0.341]
    },

    '10': {
        'start': ['2019-08-16_18-07-06-331515', '', 0.9994531],
        'loading': ['2019-08-16_18-07-08-709858', '', 0.9827017],
        'words': ['2019-08-16_18-07-09-379070', '', 0.98374486],
        'end': ['2019-08-16_18-07-09-764880', '', 0.96275914],
        'app': [2.37, 0.669, 1.055, 0.385]
    }
}