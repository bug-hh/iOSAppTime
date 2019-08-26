#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import time
import json

from google_algorithm.label_image import identify_pic
from msg_queue.queue_manager import QueueManager

from app_config.config import STAGE, SORTED_STAGE
from app_config.config import JSON_PROGRESS_BAR_KEY
from app_config.config import JSON_TEXT_BROWSER_KEY
from app_config.config import JSON_PID_KEY
from app_config.config import IOS_PERCENT

class CalTime(object):
    def __init__(self, main_window, times_counter):
        self.main_window = main_window
        self.times_counter = times_counter
        self.cache = {}
        self.progress = 0

        QueueManager.register('get_ui_msg_queue')
        QueueManager.register('get_answer_queue')
        QueueManager.register('get_task_status', callable=lambda: self.task_pid_status)

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.connect()
        self.shared_ui_msg_queue = self.manager.get_ui_msg_queue()
        self.shared_answer_queue = self.manager.get_answer_queue()
        self.shared_task_status_dt = self.manager.get_task_status()

        self.PID = os.getpid()


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
        z = 0
        length = last + 1
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
                    mid = identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1
            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))
            if SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
        print("upper_bound: z = %d" % z)

        return first

    # todo 加入进度条代码
    def lower_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        z = 0
        length = last
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
                    mid = identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1
            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))
            if SORTED_STAGE[mid[0]] < value:
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
        y = 0
        target_precise = int(IOS_PERCENT[target_stage] * 10000)
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        id_ret = identify_pic(pic_path)
        direction = -1 if target_stage == 'start' else 1
        length = len(pic_list)
        msg = {}
        while id_ret[0] != target_stage and pic_index < length:
            y += 1
            self.progress += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = identify_pic(pic_path)
            msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, self.progress)
            self.shared_ui_msg_queue.put(json.dumps(msg))

        if target_stage not in ('start', 'loading', 'end'):
            return pic_index, id_ret

        prob = round(id_ret[1], 4)
        prob *= 10000
        prob = int(prob)
        last = None
        while prob < target_precise and pic_index < length:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            last = id_ret
            id_ret = identify_pic(pic_path)
            prob = round(id_ret[1], 4)
            prob *= 10000
            prob = int(prob)

        print("check_precise: y = %d" % y)

        return pic_index, id_ret

    def cal_time(self, pic_dir, exclude_list):
        cur = time.time()
        ret = {}
        counter = 0
        for st in STAGE:
            ret[st] = -1

        ls = os.listdir(pic_dir)
        pic_list = [pic for pic in ls if not pic.startswith(".")]
        pic_list.sort()

        i = 0
        length = len(pic_list)
        summary = "总共包含 %d 张图片" % (length)
        print(summary)
        msg = {}
        for stage in SORTED_STAGE:
            if stage in exclude_list:
                continue
            search_method = self.upper_bound if stage == 'start' else self.lower_bound
            is_upper_bound = True if stage == 'start' else False
            self.progress = 0
            bound_index = search_method(pic_dir, pic_list, 0, length, SORTED_STAGE[stage], stage)
            if stage == 'newlogo':
                stage = 'start'
            search_result = self._check_precise(bound_index, pic_list, pic_dir, is_upper_bound, stage)
            if not self._check_result(is_upper_bound, search_result, length):
                error_str = "文件夹 %d: %s 阶段不存在，线程退出" % (self.times_counter, stage)
                print(error_str)
                msg[JSON_TEXT_BROWSER_KEY] = tuple(error_str)
                msg[JSON_PID_KEY] = self.PID
                self.shared_ui_msg_queue.put(json.dumps(msg))
                self.shared_task_status_dt.update({self.PID: True})
                return
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                ret[stage] = CalTime.get_create_time(pic_list[index])

        # 计算启动时长和首页加载时长
        launch_time = 0
        home_page_loading_time = 0
        if ret['loading'] != -1:
            launch_time += round((ret['loading'] - ret['start']), 4)

        if ret['end'] != -1:
            home_page_loading_time += round((ret['end'] - ret['loading']), 4)

        str2 = "文件夹 %d: App 启动时长：%.3fs   App 首页加载时长：%.3fs " % (self.times_counter, launch_time, home_page_loading_time)
        print(str2)

        now = time.time()
        interval = now - cur
        total_time = "文件夹 %d 总共计算耗时: %ds" % (self.times_counter, interval)
        print(total_time)

        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum()

        msg[JSON_PROGRESS_BAR_KEY] = (self.times_counter, max_value)
        msg[JSON_TEXT_BROWSER_KEY] = (str2, total_time)
        msg[JSON_PID_KEY] = self.PID
        self.shared_ui_msg_queue.put(json.dumps(msg))

        self.shared_task_status_dt.update({self.PID:True})
        self.shared_answer_queue.put((launch_time, home_page_loading_time))

    @staticmethod
    def get_create_time(filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts