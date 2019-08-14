#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import time

from google_algorithm.label_image import identify_pic

from config import STAGE, SORTED_STAGE, TMP_IMG_DIR

class CalTime(object):
    def __init__(self, main_window, thread_signal, times_counter):
        self.main_window = main_window
        self.thread_signal = thread_signal
        self.times_counter = times_counter
        self.cache = {}
        self.progress = 0


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
        z = 0
        length = last + 1
        while first < last:
            z += 1
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

            if SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
            self.progress += z
            self.thread_signal.emit(self.times_counter, self.progress)
        print("upper_bound: z = %d" % z)
        index = self._check_precise(first, pic_list, pic_dir, True)
        return index

    def lower_bound(self, pic_dir, pic_list, first, last, value):
        z = 0
        length = last
        while first < last:
            z += 1
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
            if SORTED_STAGE[mid[0]] < value:
                first = mid_index + 1
            else:
                last = mid_index
            self.progress += z
            self.thread_signal.emit(self.times_counter, self.progress)
        print("lower_bound: z = %d" % z)
        index = self._check_precise(first, pic_list, pic_dir, False)
        return index

    def _check_result(self, is_upper_bound, res, last):
        if res == last or res < 0:
            return False

        if is_upper_bound:
            return res - 1 >= 0

        return True

    def _check_precise(self, pic_index, pic_list, pic_dir, is_upper_bound):
        '''
        检查准确度是否符合预期，如果不符合，则返回符合预期的图片的索引值
        :param pic_index:
        :param pic_list:
        :param pic_dir:
        :return:
        '''
        y = 0
        target_precise = 900
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        prob = round(identify_pic(pic_path)[1], 3)
        prob *= 1000
        prob = int(prob)
        direction = -1 if is_upper_bound else 1
        while prob < target_precise:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            prob = round(identify_pic(pic_path)[1], 3)
            prob *= 1000
            prob = int(prob)
            self.progress += y
            self.thread_signal.emit(self.times_counter, self.progress)
        print("check_precise: y = %d" % y)
        return pic_index

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
        for stage in SORTED_STAGE:
            if stage in exclude_list:
                continue
            search_method = self.upper_bound if stage == 'start' else self.lower_bound
            is_upper_bound = True if stage == 'start' else False
            search_result = search_method(pic_dir, pic_list, 0, length, SORTED_STAGE[stage])
            if not self._check_result(is_upper_bound, search_result, length):
                print("%s 阶段不存在，线程退出" % stage)
                return
            else:
                if is_upper_bound:
                    search_result -= 1
                pic_path = os.path.join(pic_dir, pic_list[search_result])
                ret[stage] = CalTime.get_create_time(pic_list[search_result])

        # 计算启动平均时长 和 Task 平均时长
        launch_time = 0
        home_page_loading_time = 0
        if ret['loading'] != -1:
            launch_time += round((ret['loading'] - ret['start']), 4)

        if ret['words'] != -1:
            home_page_loading_time += round((ret['words'] - ret['loading']), 4)

        max_value = self.main_window.cal_progress_dialog.ui.progress_bar_dt[self.times_counter].maximum()
        self.thread_signal.emit(self.times_counter, max_value)
        str2 = "App 启动时长：%.3fs   App 首页加载时长：%.3fs" % (launch_time, home_page_loading_time)
        # todo 将最终结果显示在 text browser 上
        print(str2)

        now = time.time()
        interval = now - cur
        print("总共计算耗时: %ds" % interval)

    @staticmethod
    def get_create_time(filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts