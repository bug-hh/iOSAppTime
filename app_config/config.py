# -*- coding: utf-8 -*-
import os

PACKAGE_NAME = 'com.zhihu.ios-dev'

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
RETRAIN_PATH = os.path.join(ROOT_PATH, "google_algorithm", "retrain.py")

# 实时截图文件夹
TMP_IMG_ZHIHU_DIR = os.path.join(ROOT_PATH, 'capture_zhihu')
TMP_IMG_WEIBO_DIR = os.path.join(ROOT_PATH, 'capture_weibo')
TMP_IMG_TOP_TODAY_DIR = os.path.join(ROOT_PATH, 'capture_top_today')
TMP_IMG_BAIDU_DIR = os.path.join(ROOT_PATH, 'capture_baidu')

# model
iOS_ZHIHU_MODEL_NAME = "ios_zhihu_output_graph.pb"
iOS_WEIBO_MODEL_NAME = "ios_weibo_output_graph.pb"
iOS_TOP_TODAY_MODEL_NAME = "ios_top_today_output_graph.pb"
iOS_BAIDU_MODEL_NAME = "ios_baidu_output_graph.pb"

# label
iOS_ZHIHU_LABEL_NAME = "ios_zhihu_output_labels.txt"
iOS_WEIBO_LABEL_NAME = "ios_weibo_output_labels.txt"
iOS_TOP_TODAY_LABEL_NAME = "ios_top_today_output_labels.txt"
iOS_BAIDU_LABEL_NAME = "ios_baidu_output_labels.txt"

# training 文件，存「机器学习模型」和「机器学习标签」
ABOUT_TRAINING = os.path.join(ROOT_PATH, 'training')

if not os.path.exists(ABOUT_TRAINING):
    os.makedirs(ABOUT_TRAINING)

# 每个 app 启动存在的几个阶段
BAIDU_STAGE = ['start', 'logo', 'loading', 'end']
TOP_TODAY_STAGE = ['start', 'logo', 'ad', 'loading', 'end']
WEIBO_STAGE = ['start', 'logo', 'ad', 'loading', 'end']
ZHIHU_STAGE = ['start', 'logo', 'ad', 'loading', 'words', 'end']

# 每个阶段的阈值
ZHIHU_PERCENT = {'start': 0.96, 'logo': 0.90, 'ad': 0.90, 'loading': 0.96, 'words': 0.85, 'end': 0.85, 'home': 0.90}
BAIDU_PERCENT = {'start': 0.96, 'logo': 0.95, 'loading': 0.80, 'end': 0.70}
TOP_TODAY_PERCENT = {'start': 0.96, 'logo': 0.95, 'ad': 0.95, 'loading': 0.90, 'end': 0.9}
WEIBO_PERCENT ={'start': 0.9, 'logo': 0.8, 'ad': 0.9, 'loading': 0.9, 'end': 0.9}

# SYL_IOS_PERCENT = {'start': 0.997632, 'loading': 0.97324440, 'end': 0.87187050}

# 将每个阶段映射成一个数字
ZHIHU_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}
BAIDU_SORTED_STAGE = {'start': 1, 'logo': 2, 'loading': 3, 'end': 4}
TOP_TODAY_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}
WEIBO_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}

# 用 'logo' 找 start
EXCLUDED_LIST = ['start', 'ad']

# GUI Message Key
JSON_MINICAP_KEY = 'MINICAP'
JSON_PROGRESS_BAR_KEY = 'PROGRESS_BAR'
JSON_TEXT_BROWSER_KEY = 'TEXT_BROWSER'
JSON_PID_KEY = 'pid'
JSON_PROGRESS_DIALOG_CLOSE = 'PROGRESS_DIALOG_CLOSE'


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