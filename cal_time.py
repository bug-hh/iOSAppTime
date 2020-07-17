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
    def __init__(self, main_window, times_counter, test_app_code, debug=False, allow_ad=False):
        self.debug = debug
        self.main_window = main_window
        self.times_counter = times_counter
        self.cache = {}
        self.progress = 0
        self.allow_ad = allow_ad

        self.classifier = Classifier(test_app_code)

        if not self.debug:
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

    def upper_bound(self, pic_dir, pic_list, first, last, value):
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

            # 如果不允许有「广告」，则直接丢弃该批截图序列
            if not self.allow_ad:
                if mid[0] == 'ad':
                    print('ad', pic_path)
                    return -1

            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            if not self.debug:
                self.shared_ui_msg_queue.put(json.dumps(msg))
            if self.SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
        print("upper_bound: z = %d" % z)

        return first

    # todo 加入进度条代码
    def lower_bound(self, pic_dir, pic_list, first, last, value):
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

            # 如果不允许有「广告」或 「坏图」，则直接丢弃该批截图序列
            if not self.allow_ad:
                if mid[0] == 'ad':
                    print('ad', pic_path)
                    return -1

            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            if not self.debug:
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

    def _check_logo(self, pic_index, pic_list, pic_dir):
        '''
        if not self.allow_ad:
		    「启动时长」 = 「logo 的 uppper bound 后面的 第一张不是 logo 的图」 - start
		else:
		    「启动时长」 = 「ad 的 upper bound 后面的 第一张不是 ad 的图」 - start
		:param pic_index:
		:param pic_list:
		:param pic_dir:
		:return:
		'''
        y = 0
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        id_ret = self.classifier.identify_pic(pic_path)
        direction = 1
        length = len(pic_list)
        msg = {}
        status = 'ad' if self.allow_ad else 'logo'
        while id_ret[0] == status and 1 <= pic_index < length - 1:
            if id_ret[0] == 'ad' and not self.allow_ad:
                return -2, None
            y += 1
            print("_check_%s: y = %d" % (status, y))
            self.progress += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = self.classifier.identify_pic(pic_path)

        # 先找到「logo 的 uppper bound 后面的 第一张不是 logo 的图」,然后 check_precise, 找到 loading
        if not self.allow_ad:
            pic_index, id_ret = self._check_precise(pic_index, pic_list, pic_dir, "loading")

        return pic_index, id_ret

    def _check_precise(self, pic_index, pic_list, pic_dir, target_stage):
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
            if not self.debug:
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
        # EXCLUDED_LIST = ['ad', 'logo', 'words', 'end', 'home']
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

            bound_index = -1
            # 用 logo 的 lower_bound 往回找，找出 start
            if stage == 'start':
                bound_index = self.lower_bound(pic_dir, pic_list, 0, length, self.SORTED_STAGE['logo'])
                print(bound_index)
            # 用 logo 的 upper_bound 向前找，找出第一张不是 logo 的截图，作为 loading
            # 当有 ad 的时候，用 ad 的 upper_bound 向后找，找出第一张不是 ad 的图，作为 loading
            elif stage == 'loading':
                k = 'logo' if not self.allow_ad else 'ad'
                bound_index = self.upper_bound(pic_dir, pic_list, 0, length, self.SORTED_STAGE[k])

            is_upper_bound = True if stage == 'loading' else False

            if self._handle_ad_and_bad(bound_index):
                return


            if stage == 'start':
                search_result = self._check_precise(bound_index, pic_list, pic_dir, stage)
            else:
                search_result = self._check_logo(bound_index, pic_list, pic_dir)

            if not self._check_result(is_upper_bound, search_result, length):
                error_str = "文件夹 %d: %s 阶段不存在" % (self.times_counter, stage)
                print(error_str)
                msg[JSON_TEXT_BROWSER_KEY] = tuple(error_str)
                msg[JSON_PID_KEY] = self.PID
                if not self.debug:
                    self.shared_ui_msg_queue.put(json.dumps(msg))
                ret[stage] = (-1, None, None)
                # self.shared_answer_queue.put((0, 0))
                # self.shared_task_status_dt.update({self.PID: True})
                # return
            else:
                index = search_result[0]
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

        for key in ret:
            print(ret[key])
        print()
        str2 = "文件夹 %d: App 启动时长：%.3fs" % (self.times_counter, launch_time)
        # str2 = "文件夹 %d: App 启动时长：%.3fs   App 首页加载时长：%.3fs " % (self.times_counter, launch_time, home_page_loading_time)

        print(str2)

        now = time.time()
        interval = now - cur
        total_time = "\n文件夹 %d 总共计算耗时: %ds" % (self.times_counter, interval)
        print(total_time)

        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum() if not self.debug else 1000

        msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, max_value)
        msg[JSON_TEXT_BROWSER_KEY] = (str2, total_time)
        msg[JSON_PID_KEY] = self.PID
        msg[JSON_ANSWER_KEY] = (launch_time, home_page_loading_time)
        if not self.debug:
            self.shared_ui_msg_queue.put(json.dumps(msg))

            # self.shared_task_status_dt.update({self.PID:True})
            # self.shared_answer_queue.put((launch_time, home_page_loading_time))

    def _handle_ad_and_bad(self, bound_index):
        if self.allow_ad:
            print("允许 ad, 文件夹 %d 的截图中含有广告", self.times_counter)
            return False
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
        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum() if not self.debug else 1000

        msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, max_value)
        msg[JSON_TEXT_BROWSER_KEY] = tuple(exception_str)
        msg[JSON_PID_KEY] = self.PID
        msg[JSON_ANSWER_KEY] = (0, 0)
        if not self.debug:
            self.shared_ui_msg_queue.put(json.dumps(msg))
            # self.shared_task_status_dt.update({self.PID: True})
        return True

    @staticmethod
    def get_create_time(filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts

if __name__ == '__main__':
    screenshots_dir = os.path.join(TMP_IMG_ZHIHU_DIR, "iOS")
    ls_temp = [int(n) for n in os.listdir(screenshots_dir) if not n.startswith(".")]
    ls_temp.sort()
    EXCLUDED_LIST = ['ad', 'logo', 'words', 'end', 'home']
    # pic_name = '2020-07-09_15-34-47-496953.jpg'
    # ct = CalTime(main_window="", times_counter=7, test_app_code=1, debug=True, allow_ad=True)
    # ret = ct.classifier.identify_pic(os.path.join(screenshots_dir, "7", pic_name))
    # print(ret)
    t1 = CalTime.get_create_time("2020-07-15_18-29-13-672262.jpg")
    t2 = CalTime.get_create_time("2020-07-15_18-29-17-811100.jpg")
    print(t2 - t1)
    # for num in ls_temp:
    #     # 1 知乎 2 微博 3 头条 4 百度
    #     if num != 7:
    #         continue
    #     ct = CalTime(main_window="", times_counter=num, test_app_code=1, debug=True, allow_ad=True)
    #     pictures_dir_1 = os.path.join(screenshots_dir, str(num))
    #     ct.cal_time(pictures_dir_1, EXCLUDED_LIST)

