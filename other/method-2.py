#!/usr/bin/env python
# coding: utf-8


import os
import datetime

from PyQt5.QtCore import QObject, pyqtSignal

from google_algorithm.label_image import Classifier

from app_config.config import ZHIHU_STAGE
from app_config.config import WEIBO_STAGE
from app_config.config import TOP_TODAY_STAGE
from app_config.config import BAIDU_STAGE

from app_config.config import TMP_IMG_ZHIHU_DIR
from app_config.config import TMP_IMG_TOP_TODAY_DIR
from app_config.config import TMP_IMG_BAIDU_DIR
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import ZHIHU_PERCENT
from app_config.config import BAIDU_PERCENT
from app_config.config import TOP_TODAY_PERCENT
from app_config.config import WEIBO_PERCENT

from app_config.config import ZHIHU_SORTED_STAGE
from app_config.config import BAIDU_SORTED_STAGE
from app_config.config import TOP_TODAY_SORTED_STAGE
from app_config.config import WEIBO_SORTED_STAGE

import time
import queue
from app_config import config

cpu_launch_time, cpu_loading_time = 0.0, 0.0
man_launch_time, man_loading_time = 0.0, 0.0
ccount = 0

class Foo(QObject):
    dt_signal = {}

    def __init__(self, test_app_code):
        super(Foo, self).__init__()
        for k in Foo.__dict__:
            if str(k).startswith("signal"):
                # print(k)
                # print(Foo.__dict__[k])
                cmd = "self.%s.connect(self.trigger_slot)" % k
                exec(cmd)
        self.cache = {}
        self.classifier = Classifier(test_app_code)

        self.start_exist = False
        self.loading_exist = False
        self.end_exist = False
        self._test_app_adapter(test_app_code)
        # QueueManager.register('get_queue_1')
        # QueueManager.register('get_queue_2')
        # self.manager = QueueManager(address=('localhost', 55677), authkey=b'1234')
        # self.manager.connect()
        # self.shared_queue_1 = self.manager.get_queue_1()
        # self.shared_queue_2 = self.manager.get_queue_2()

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

    # todo 加入对广告的判断
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
        while first < last:
            z += 1
            mid_index = first + (last - first) // 2
            while True:
                if self.cache.get(mid_index):
                    mid = self.cache[mid_index]
                else:
                    pic_path = os.path.join(pic_dir, pic_list[mid_index])
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 如果有广告，则直接丢弃该批截图序列
            if mid[0] == 'ad':
                return -1

            if self.SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
        print("upper_bound: z = %d" % z)

        return first

    # todo 加入对广告的判断
    def lower_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        if last == 0:
            return -2
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
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 如果有广告，则直接丢弃该批截图序列
            if mid[0] == 'ad':
                return -1
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

        while id_ret[0] != target_stage and 0 <= pic_index < length:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = self.classifier.identify_pic(pic_path)

        if target_stage not in ('start', 'loading', 'end'):
            return pic_index, id_ret

        prob = round(id_ret[1], 4)
        prob *= 10000
        prob = int(prob)
        last = None

        # 先找出 prob >= target_precise
        while prob < target_precise and 0 <= pic_index < length:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = self.classifier.identify_pic(pic_path)
            prob = round(id_ret[1], 4)
            prob *= 10000
            prob = int(prob)

        print("check_precise: y = %d" % y)

        # if id_ret[0] != target_stage:
        #     return pic_index - direction, last
        # else:
        return pic_index, id_ret if last is None else pic_index - 1, last

    def cal_time(self, pic_dir, exclude_list):
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
        summary = "总共包含 %d 张图片" % (length)
        print(summary)
        self.cache.clear()
        for stage in self.SORTED_STAGE:
            if stage in exclude_list:
                continue
            search_method = self.upper_bound if stage == 'start' else self.lower_bound
            is_upper_bound = True if stage == 'start' else False
            # 通过 logo 算 start ，loading、end 阶段通过求 lower_bound 计算
            bound_index = search_method(pic_dir, pic_list, 0, length, self.SORTED_STAGE[stage], stage)
            if bound_index == -1:
                ad_str = '该文件夹的截图中含有广告，丢弃这批截图序列'
                print(ad_str)
                return
            elif bound_index == -2:
                empty_str = '该文件夹为空'
                print(empty_str)
                return
            if stage == 'logo':
                stage = 'start'
            search_result = self._check_precise(bound_index, pic_list, pic_dir, is_upper_bound, stage)
            if not self._check_result(is_upper_bound, search_result, length):
                print("%s 阶段不存在" % stage)
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                pic_path = os.path.join(pic_dir, pic_list[index])
                ret[stage] = (self.get_create_time(pic_list[index]), pic_path, search_result[1])

        global ccount
        ccount += 1
        print(ret)
        print()

        if ret['start'][0] != -1:
            self.start_exist = True

        if ret['loading'][0] != -1:
            self.loading_exist = True

        if ret['end'][0] != -1:
            self.end_exist = True

        # 计算启动时长 和 Task 平均时长
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

        # self.result_queue.put((launch_time, home_page_loading_time))
        str2 = "App 启动时长：%.3fs   App 首页加载时长：%.3fs" % (launch_time, home_page_loading_time)

        for k in ret:
            print(k, ret[k])

        print(str2)
        now = time.time()
        interval = now - cur
        print("总共计算耗时: %ds" % interval)

        for k in ret:
            if ret[k] == -1:
                continue
            # d = os.path.basename(pic_dir)
            # human_value_list = config.HUMAN[d][k]
            # ts = human_value_list[0]
            # missing = int(abs(self.get_create_time(ts)*10**6 - ret[k][0]*10**6)/1000)
            # sss = "%s: %s 误差：%d ms 概率：%.8f" % (k, human_value_list[0], missing, human_value_list[-1])
            # print(sss)
        d = os.path.basename(pic_dir)
        # human_value_list = config.HUMAN[d]['app']
        # sss = "App 启动时长：%.3fs  App 首页加载时长：%.3fs(loading -> end)" \
        #     % (human_value_list[0], human_value_list[1])
        # print(sss)

        global cpu_launch_time, cpu_loading_time, man_launch_time, man_loading_time
        cpu_launch_time += (int(launch_time * 10**3))
        cpu_loading_time += (int(home_page_loading_time * 10**3))

        # man_launch_time += (int(human_value_list[0] * 10**3))
        # man_loading_time += (int(human_value_list[1] * 10**3))

        # print("######计算时长对比#######")
        # diff_1 = abs(int(launch_time * 10**3) - int(human_value_list[0] * 10**3))
        # diff_2 = abs(int(home_page_loading_time * 10**3) - int(human_value_list[1] * 10**3))
        # print("启动时长误差：%d ms   首页加载时长误差：%d ms" % (diff_1, diff_2))

    def get_create_time(self, filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts

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
                ret = self.classifier.identify_pic(path_pic)
                print(pic, ret)
            print("------------")


if __name__ == '__main__':
    # 1 知乎 2 微博 3 头条 4 百度
    f = Foo(4)
    ios_dir = os.path.join(f.TMP_IMG_DIR, "iOS")
    print(ios_dir)
    pic_dir_list = os.listdir(ios_dir)
    pic_dir_list.sort()
    for pic_dir in pic_dir_list:
        if pic_dir.startswith("."):
            continue
        if pic_dir != "6":
            continue
        print(pic_dir)
        pic_dir_path = os.path.join(ios_dir, pic_dir)
        f.cal_time(pic_dir_path, config.EXCLUDED_LIST)
        print("################")
        print()

    # cpu_launch_time = cpu_launch_time // ccount if ccount != 0 else 0
    # cpu_loading_time = cpu_loading_time // ccount if ccount != 0 else 0
    #
    # man_launch_time = man_launch_time // ccount if ccount != 0 else 0
    # man_loading_time = man_loading_time // ccount if ccount != 0 else 0
    #
    # print("平均启动时长误差：%d ms    平均首页加载时长误差: %d ms" % (abs(cpu_launch_time - man_launch_time), abs(cpu_loading_time - man_loading_time)))
    # start = f.get_create_time("2019-08-16_17-47-15-792374")
    # loading = f.get_create_time("2019-08-16_17-47-18-528193")
    # end = f.get_create_time("2019-08-16_17-47-19-860089")

    # print("start -> loading: ", loading - start)
    # print("loading -> end: ", end - loading)

    # pic_dir = "/Users/bughh/PycharmProjects/iOSAppTime/training/weibo/test/"
    # id_dir = "ad"
    # temp = os.path.join(pic_dir, id_dir)
    # print(os.path.basename(temp))
    # pic_name = "test-ad-3.jpg"
    # pic_path = os.path.join(pic_dir, id_dir, pic_name)
    # # t1 = time.time()
    # classifier = Classifier(2)
    # ret = classifier.identify_pic(pic_path)
    # print(ret)
    # t2 = time.time()
    # print(t2 - t1)
    # f = Foo()
    # f.test2()


# todo 1、先用带有 check_precise 跑一次所有的文件夹，其中 check_precise 只包含 「while id_ret[0] != target_stage and pic_index < length」 的情况
# todo 2、再用带有 check_precise 跑一次所有的文件夹，其中 check_precise 包含 「while id_ret[0] != target_stage and pic_index < length」和 「while prob < target_precise and pic_index < length」的情况
# todo 3、再用不带 check_precise 跑一次所有的文件夹