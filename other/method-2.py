#!/usr/bin/env python
# coding: utf-8


import os
import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from google_algorithm.label_image import identify_pic
from app_config.config import STAGE, SORTED_STAGE, IOS_PERCENT, TMP_IMG_DIR

import time
import queue
from app_config import config


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

        while id_ret[0] != target_stage and pic_index < length:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = identify_pic(pic_path)

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

        # if id_ret[0] != target_stage:
        #     return pic_index - direction, last
        # else:
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
        self.cache.clear()
        for stage in SORTED_STAGE:
            if stage in exclude_list:
                continue
            search_method = self.upper_bound if stage == 'start' else self.lower_bound
            is_upper_bound = True if stage == 'start' else False
            # start 通过 newlogo 来算
            bound_index = search_method(pic_dir, pic_list, 0, length, SORTED_STAGE[stage], stage)
            if stage == 'newlogo':
                stage = 'start'
            search_result = self._check_precise(bound_index, pic_list, pic_dir, is_upper_bound, stage)
            if not self._check_result(is_upper_bound, search_result, length):
                print("%s 阶段不存在，线程退出" % stage)
                return
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                pic_path = os.path.join(pic_dir, pic_list[index])
                ret[stage] = (self.get_create_time(pic_list[index]), pic_path, search_result[1])

        print(ret)
        print()

        # 计算启动平均时长 和 Task 平均时长
        launch_time = 0
        home_page_loading_time = 0
        home_page_loading_time_2 = 0
        if ret['loading'] != -1:
            launch_time = round((ret['loading'][0] - ret['start'][0]), 4)

        if ret['end'] != -1:
            home_page_loading_time = round((ret['end'][0] - ret['loading'][0]), 4)

        # self.result_queue.put((launch_time, home_page_loading_time))
        str2 = "App 启动时长：%.3fs   App 首页加载时长：%.3fs(loading->end)" % (launch_time, home_page_loading_time)

        for k in ret:
            print(k, ret[k])


        print(str2)
        now = time.time()
        interval = now - cur
        print("总共计算耗时: %ds" % interval)

        for k in ret:
            if ret[k] == -1:
                continue
            d = os.path.basename(pic_dir)
            human_value_list = config.HUMAN[d][k]
            ts = human_value_list[0]
            missing = int(abs(self.get_create_time(ts)*10**6 - ret[k][0]*10**6)/1000)
            sss = "%s: %s 误差：%d ms 概率：%.8f" % (k, human_value_list[0], missing, human_value_list[-1])
            print(sss)
        d = os.path.basename(pic_dir)
        human_value_list = config.HUMAN[d]['app']
        sss = "App 启动时长：%.3fs  App 首页加载时长：%.3fs(loading -> end)" \
            % (human_value_list[0], human_value_list[1])
        print(sss)

    def get_create_time(self, filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts

    def linear(self):
        pass

    def test2(self):
        stage_dir = os.path.join(config.ABOUT_TRAINING, "zhihu", "test2")
        stage_list = os.listdir(stage_dir)
        stage_list.sort()
        for s in stage_list:
            if s.startswith("."):
                continue
            print(s)
            path_stage = os.path.join(stage_dir, s)
            pic_list = os.listdir(path_stage)
            pic_list.sort()
            for pic in pic_list:
                if pic.startswith("."):
                    continue
                path_pic = os.path.join(path_stage, pic)
                ret = identify_pic(path_pic)
                print(pic, ret)
            print("------------")


if __name__ == '__main__':
    f = Foo()
    ios_dir = os.path.join(TMP_IMG_DIR, "iOS")
    pic_dir_list = os.listdir(ios_dir)
    pic_dir_list.sort()
    for pic_dir in pic_dir_list:
        if pic_dir.startswith("."):
            continue
        print(pic_dir)
        pic_dir_path = os.path.join(ios_dir, pic_dir)
        f.cal_time(pic_dir_path, config.EXCLUDED_LIST)
        print("################")
        print()
    # start = f.get_create_time("2019-08-16_17-59-37-988644")
    # loading = f.get_create_time("2019-08-16_17-59-40-618910")
    # end = f.get_create_time("2019-08-16_17-59-41-518037")
    #
    # print("start -> loading: ", loading - start)
    # print("loading -> end: ", end - loading)
    # pic_dir = "/Users/bughh/PycharmProjects/iOSAppTime/capture/tmp_pic/iOS"
    # id_dir = "8"
    # temp = os.path.join(pic_dir, id_dir)
    # print(os.path.basename(temp))
    # pic_name = "2019-08-16_17-59-41-518037.jpg"
    # pic_path = os.path.join(pic_dir, id_dir, pic_name)
    # # t1 = time.time()
    # ret = identify_pic(pic_path)
    # print(ret)
    # t2 = time.time()
    # print(t2 - t1)
    # f = Foo()
    # f.test2()

# todo 1、先用带有 check_precise 跑一次所有的文件夹，其中 check_precise 只包含 「while id_ret[0] != target_stage and pic_index < length」 的情况
# todo 2、再用带有 check_precise 跑一次所有的文件夹，其中 check_precise 包含 「while id_ret[0] != target_stage and pic_index < length」和 「while prob < target_precise and pic_index < length」的情况
# todo 3、再用不带 check_precise 跑一次所有的文件夹