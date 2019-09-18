#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import time
import json

from google_algorithm.label_image import Classifier
from msg_queue.queue_manager import QueueManager

from app_config.config import ZHIHU_STAGE
from app_config.config import WEIBO_STAGE
from app_config.config import TOP_TODAY_STAGE
from app_config.config import BAIDU_STAGE

from app_config.config import TMP_IMG_ZHIHU_DIR
from app_config.config import TMP_IMG_TOP_TODAY_DIR
from app_config.config import TMP_IMG_BAIDU_DIR
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import JSON_PROGRESS_BAR_KEY
from app_config.config import JSON_TEXT_BROWSER_KEY
from app_config.config import JSON_PID_KEY
from app_config.config import JSON_ANSWER_KEY

from app_config.config import ZHIHU_PERCENT
from app_config.config import BAIDU_PERCENT
from app_config.config import TOP_TODAY_PERCENT
from app_config.config import WEIBO_PERCENT

from app_config.config import ZHIHU_SORTED_STAGE
from app_config.config import BAIDU_SORTED_STAGE
from app_config.config import TOP_TODAY_SORTED_STAGE
from app_config.config import WEIBO_SORTED_STAGE

class CalTime(object):
    def __init__(self, main_window, times_counter, test_app_code):
        self.main_window = main_window
        self.times_counter = times_counter
        self.cache = {}
        self.progress = 0

        self.classifier = Classifier(test_app_code)

        QueueManager.register('get_ui_msg_queue')
        # QueueManager.register('get_answer_queue')
        # QueueManager.register('get_task_status')

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.connect()
        self.shared_ui_msg_queue = self.manager.get_ui_msg_queue()
        # self.shared_answer_queue = self.manager.get_answer_queue()
        # self.shared_task_status_dt = self.manager.get_task_status()

        self.PID = os.getpid()
        self.STAGE_PERCENT = ZHIHU_PERCENT
        self.SORTED_STAGE = ZHIHU_SORTED_STAGE

        self.start_exist = False
        self.loading_exist = False
        self.end_exist = False

        self.bad_times = 0

        self._test_app_adapter(test_app_code)

    def _test_app_adapter(self, test_app_code):
        # 1 知乎 2 微博 3 头条 4 百度
        if test_app_code == 1:
            self.STAGE_PERCENT = ZHIHU_PERCENT
            self.SORTED_STAGE = ZHIHU_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR
            self.APP_STAGE = ZHIHU_STAGE

        elif test_app_code == 2:
            self.STAGE_PERCENT = WEIBO_PERCENT
            self.SORTED_STAGE = WEIBO_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_WEIBO_DIR
            self.APP_STAGE = WEIBO_STAGE

        elif test_app_code == 3:
            self.STAGE_PERCENT = TOP_TODAY_PERCENT
            self.SORTED_STAGE = TOP_TODAY_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_TOP_TODAY_DIR
            self.APP_STAGE = TOP_TODAY_STAGE

        elif test_app_code == 4:
            self.STAGE_PERCENT = BAIDU_PERCENT
            self.SORTED_STAGE = BAIDU_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_BAIDU_DIR
            self.APP_STAGE = BAIDU_STAGE

    def upper_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        '''
        求 pic_list 数组中 最后一个大于 value 的值的小标，即 [1,1,2,2,10,10,10,20], value = 10, 那么函数将返回下标 7，即最右边的那个 10 的下标 [first, last), 左闭右开
        如果不存在，则返回 last
        :param pic_dir:
        :param pic_list:
        :param first:
        :param last:
        :param value:
        :return:
        '''
        if last == 0:
            return -2
        z = 0
        length = last + 1
        self.bad_times = 0
        msg = {JSON_PROGRESS_BAR_KEY: None}
        while first < last:
            z += 1
            self.progress += 1
            mid_index = first + (last - first) // 2
            while True:
                if self.cache.get(mid_index):
                    mid = self.cache[mid_index]
                else:
                    pic_path = os.path.join(pic_dir, pic_list[mid_index])
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid and mid[0] != 'bad':
                    break
                else:
                    self.bad_times += 1
                    # 当出现「坏图」的次数超过(包含) 5 次时，丢弃这批数据
                    if self.bad_times >= 5:
                        return -2
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 如果有「广告」，则直接丢弃该批截图序列
            if mid[0] == 'ad':
                print('ad', pic_path)
                return -1

            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))
            if self.SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
        print("upper_bound: z = %d" % z)

        return first

    # todo 加入进度条代码
    def lower_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        if last == 0:
            return -2
        z = 0
        length = last
        self.bad_times = 0
        msg = {JSON_PROGRESS_BAR_KEY: None}
        while first < last:
            z += 1
            self.progress += 1
            mid_index = first + (last - first) // 2
            while True:
                if self.cache.get(mid_index):
                    mid = self.cache[mid_index]
                else:
                    pic_path = os.path.join(pic_dir, pic_list[mid_index])
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid and mid[0] != 'bad':
                    break
                else:
                    self.bad_times += 1
                    # 当出现「坏图」的次数超过(包含) 5 次时，丢弃这批数据
                    if self.bad_times >= 5:
                        return -2
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 如果有「广告」或 「坏图」，则直接丢弃该批截图序列
            if mid[0] == 'ad':
                print('ad', pic_path)
                return -1

            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))
            if self.SORTED_STAGE[mid[0]] < value:
                first = mid_index + 1
            else:
                last = mid_index
        print("lower_bound: z = %d" % z)

        return first

    def _check_result(self, is_upper_bound, res, last):
        if res[0] == last or res[0] < 0:
            return False

        if is_upper_bound:
            return res[0] -1 >= 0

        return True

    def _check_precise(self, pic_index, pic_list, pic_dir, is_upper_bound, target_stage):
        '''
        检查准确度是否符合预期，如果不符合，则返回符合预期的图片的索引值
        :param pic_index:
        :param pic_list:
        :param pic_dir:
        :return:
        '''

        length = len(pic_list)
        if pic_index < 0 or pic_index >= length:
            return -1, None

        y = 0
        target_precise = int(self.STAGE_PERCENT[target_stage] * 10000)
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        id_ret = self.classifier.identify_pic(pic_path)
        direction = -1 if target_stage == 'start' else 1

        msg = {}
        while id_ret[0] != target_stage and 1 <= pic_index < length - 1:
            y += 1
            self.progress += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = self.classifier.identify_pic(pic_path)
            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))

        if target_stage not in ('start', 'loading', 'end'):
            return pic_index, id_ret

        prob = round(id_ret[1], 4)
        prob *= 10000
        prob = int(prob)
        last = None

        while prob < target_precise and 1 <= pic_index < length - 1:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            last = id_ret
            id_ret = self.classifier.identify_pic(pic_path)
            prob = round(id_ret[1], 4)
            prob *= 10000
            prob = int(prob)

        print("check_precise: y = %d" % y)

        return pic_index, id_ret

    def cal_time(self, pic_dir, exclude_list):

        self.start_exist = False
        self.loading_exist = False
        self.end_exist = False

        cur = time.time()
        ret = {}
        counter = 0

        for st in self.APP_STAGE:
            ret[st] = (-1, None, None)

        ls = os.listdir(pic_dir)
        pic_list = [pic for pic in ls if not pic.startswith(".")]
        pic_list.sort()

        i = 0
        length = len(pic_list)
        summary = "文件夹 %s 总共包含 %d 张图片" % (os.path.basename(pic_dir), length)
        print(summary)
        msg = {}
        self.cache.clear()
        for stage in self.SORTED_STAGE:
            if stage in exclude_list:
                continue
            search_method = self.upper_bound if stage == 'start' else self.lower_bound
            is_upper_bound = True if stage == 'start' else False
            bound_index = search_method(pic_dir, pic_list, 0, length, self.SORTED_STAGE[stage], stage)

            if self._handle_ad_and_bad(bound_index):
                return

            # 用 'logo' 找 'start'
            if stage == 'logo':
                stage = 'start'
            search_result = self._check_precise(bound_index, pic_list, pic_dir, is_upper_bound, stage)
            if not self._check_result(is_upper_bound, search_result, length):
                error_str = "文件夹 %d: %s 阶段不存在" % (self.times_counter, stage)
                print(error_str)
                msg[JSON_TEXT_BROWSER_KEY] = tuple(error_str)
                msg[JSON_PID_KEY] = self.PID
                self.shared_ui_msg_queue.put(json.dumps(msg))
                ret[stage] = (-1, None, None)
                # self.shared_answer_queue.put((0, 0))
                # self.shared_task_status_dt.update({self.PID: True})
                # return
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                pic_path = os.path.join(pic_dir, pic_list[index])
                ret[stage] = (self.get_create_time(pic_list[index]), pic_path, search_result[1])

        if ret['start'][0] != -1:
            self.start_exist = True

        if ret['loading'][0] != -1:
            self.loading_exist = True

        if ret['end'][0] != -1:
            self.end_exist = True

        # 计算启动时长和首页加载时长
        launch_time = 0
        home_page_loading_time = 0
        if self.start_exist:
            if self.loading_exist:
                launch_time = round((ret['loading'][0] - ret['start'][0]), 4)

            if self.end_exist:
                if not self.loading_exist:
                    launch_time = round((ret['end'][0] - ret['start'][0]), 4)
                    home_page_loading_time = 0
                else:
                    home_page_loading_time = round((ret['end'][0] - ret['loading'][0]), 4)
            else:
                home_page_loading_time = 0
        else:
            launch_time = 0
            home_page_loading_time = 0

        str2 = "文件夹 %d: App 启动时长：%.3fs   App 首页加载时长：%.3fs " % (self.times_counter, launch_time, home_page_loading_time)
        print(str2)

        now = time.time()
        interval = now - cur
        total_time = "\n文件夹 %d 总共计算耗时: %ds" % (self.times_counter, interval)
        print(total_time)

        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum()

        msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, max_value)
        msg[JSON_TEXT_BROWSER_KEY] = (str2, total_time)
        msg[JSON_PID_KEY] = self.PID
        msg[JSON_ANSWER_KEY] = (launch_time, home_page_loading_time)
        self.shared_ui_msg_queue.put(json.dumps(msg))

        # self.shared_task_status_dt.update({self.PID:True})
        # self.shared_answer_queue.put((launch_time, home_page_loading_time))

    def _handle_ad_and_bad(self, bound_index):
        if bound_index >= 0:
            return False

        ad_str, bad_str = None, None
        if bound_index == -1:
            ad_str = '文件夹 %d 的截图中含有广告，丢弃这批截图序列' % self.times_counter
            print(ad_str)
        elif bound_index == -2:
            bad_str = '文件夹 %d 的截图中含有大于或等于 5 张坏图，丢弃这批截图序列' % self.times_counter
            print(bad_str)

        exception_str = ad_str if ad_str else bad_str

        msg = {}
        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum()

        msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, max_value)
        msg[JSON_TEXT_BROWSER_KEY] = tuple(exception_str)
        msg[JSON_PID_KEY] = self.PID
        msg[JSON_ANSWER_KEY] = (0, 0)
        self.shared_ui_msg_queue.put(json.dumps(msg))
        # self.shared_task_status_dt.update({self.PID: True})
        return True

    @staticmethod
    def get_create_time(filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts