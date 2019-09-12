#!/usr/bin/env python
# coding: utf-8


import os
import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from google_algorithm.label_image import identify_pic
from app_config.config import ZHIHU_STAGE, SORTED_STAGE, ZHIHU_PERCENT

import time
import queue


class Foo(QObject):
    dt_signal = {}

    signal_0 = pyqtSignal(int)
    signal_1 = pyqtSignal(int)
    signal_2 = pyqtSignal(int)
    signal_3 = pyqtSignal(int)
    signal_4 = pyqtSignal(int)
    signal_5 = pyqtSignal(int)
    signal_6 = pyqtSignal(int)
    signal_7 = pyqtSignal(int)
    signal_8 = pyqtSignal(int)
    signal_9 = pyqtSignal(int)

    def __init__(self):
        super(Foo, self).__init__()
        for k in Foo.__dict__:
            if str(k).startswith("signal"):
                # print(k)
                # print(Foo.__dict__[k])
                cmd = "self.%s.connect(self.trigger_slot)" % k
                exec(cmd)
        self.cache = {}
        # QueueManager.register('get_queue_1')
        # QueueManager.register('get_queue_2')
        # self.manager = QueueManager(address=('localhost', 55677), authkey=b'1234')
        # self.manager.connect()
        # self.shared_queue_1 = self.manager.get_queue_1()
        # self.shared_queue_2 = self.manager.get_queue_2()

    def test_queue(self):
        str1 = "from test1.shared_queue_1"
        self.shared_queue_1.put(str1)

        str2 = "from test1.shared_queue_2"
        self.shared_queue_2.put(str2)

        while True:
            try:
                recv = self.shared_queue_1.get_nowait()
                print(recv)
                break
            except queue.Empty:
                pass

    def trigger_slot(self):
        print(1)

    def slot2(self):
        print(2)


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
        print("upper_bound: z = %d" % z)
        index, id_ret = self._check_precise(first, pic_list, pic_dir, True, target_stage)
        return index, id_ret

    def lower_bound(self, pic_dir, pic_list, first, last, value, target_stage):
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
        print("lower_bound: z = %d" % z)
        index, id_ret = self._check_precise(first, pic_list, pic_dir, False, target_stage)
        # todo check_precise 中传入目标阶段，当通过递增得到的阶段不等于目标阶段时，跳出循环，函数返回上一个 index 和 对应的 概率，出 check_precise 后，针对 words 阶段，检查概率如果低于0.85，则认为这个阶段不存在，设置 flag，首页加载时间用 end - loading 计算
        # todo 修改模型，添加推荐已更新图片，将 end 的概率改成0.8
        return index, id_ret

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
        target_precise = int(ZHIHU_PERCENT[target_stage] * 1000)
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        id_ret = identify_pic(pic_path)
        # prob = round(id_ret[1], 3)
        # prob *= 1000
        # prob = int(prob)
        direction = -1 if is_upper_bound else 1
        length = len(pic_list)

        while id_ret[0] != target_stage and pic_index < length:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = identify_pic(pic_path)

        # prob = round(id_ret[1], 3)
        # prob *= 1000
        # prob = int(prob)
        # last = None
        # while prob < target_precise and pic_index < length:
        #     y += 1
        #     pic_index += direction
        #     pic_path = os.path.join(pic_dir, pic_list[pic_index])
        #     last = id_ret
        #     id_ret = identify_pic(pic_path)
        #     prob = round(id_ret[1], 3)
        #     prob *= 1000
        #     prob = int(prob)

        print("check_precise: y = %d" % y)

        # if id_ret[0] != target_stage:
        #     return pic_index - direction, last
        # else:
        return pic_index, id_ret

    def cal_time(self, pic_dir, exclude_list):
        cur = time.time()
        ret = {}
        counter = 0
        for st in ZHIHU_STAGE:
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
            search_result = search_method(pic_dir, pic_list, 0, length, SORTED_STAGE[stage], stage)
            if not self._check_result(is_upper_bound, search_result, length):
                print("%s 阶段不存在，线程退出" % stage)
                return
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                pic_path = os.path.join(pic_dir, pic_list[index])
                ret[stage] = (self.get_create_time(pic_list[index]), pic_path, search_result[1])

        print(ret)
        # 计算启动平均时长 和 Task 平均时长
        launch_time = 0
        home_page_loading_time = 0
        home_page_loading_time_2 = 0
        if ret['loading'] != -1:
            launch_time = round((ret['loading'][0] - ret['start'][0]), 4)

        if ret['words'] != -1:
            home_page_loading_time = round((ret['words'][0] - ret['loading'][0]), 4)

        if ret['end'] != -1:
            home_page_loading_time_2 = round((ret['end'][0] - ret['loading'][0]), 4)

        # self.result_queue.put((launch_time, home_page_loading_time))
        str2 = "App 启动时长：%.3fs   App 首页加载时长：%.3fs     %.3f" % (launch_time, home_page_loading_time, home_page_loading_time_2)

        for k in ret:
            print(k, ret[k])

        print(str2)
        now = time.time()
        interval = now - cur
        print("总共计算耗时: %ds" % interval)

    def get_create_time(self, filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts



if __name__ == '__main__':
    # f = Foo()
    # ios_dir = os.path.join(TMP_IMG_DIR, "iOS")
    # pic_dir_list = os.listdir(ios_dir)
    # pic_dir_list.sort()
    # for pic_dir in pic_dir_list:
    #     if pic_dir.startswith("."):
    #         continue
    #     print(pic_dir)
    #     pic_dir_path = os.path.join(ios_dir, pic_dir)
    #     f.cal_time(pic_dir_path, config.EXCLUDED_LIST)
    #     print("################")
    #     print()
    # start = f.get_create_time("2019-08-16_18-05-03-145833")
    # loading = f.get_create_time("2019-08-16_18-05-05-522599")
    # words = f.get_create_time("2019-08-16_18-05-06-805342")
    # end = f.get_create_time("2019-08-16_18-05-07-147079")
    #
    # print("start -> loading: ", loading - start)
    # print("loading -> words", words - loading)
    # print("loading -> end: ", end - loading)
    # print("words -> end", end - words)
    pic_dir = "/Users/bughh/PycharmProjects/iOSAppTime/capture/tmp_pic/iOS"
    id_dir = "5"
    pic_name = "2019-08-16_17-49-34-890767.jpg"
    pic_path = os.path.join(pic_dir, id_dir, pic_name)
    print(identify_pic(pic_path))

# todo 1、先用带有 check_precise 跑一次所有的文件夹，其中 check_precise 只包含 「while id_ret[0] != target_stage and pic_index < length」 的情况
# todo 2、再用带有 check_precise 跑一次所有的文件夹，其中 check_precise 包含 「while id_ret[0] != target_stage and pic_index < length」和 「while prob < target_precise and pic_index < length」的情况
# todo 3、再用不带 check_precise 跑一次所有的文件夹