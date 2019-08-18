# -*- coding: utf-8 -*-
import os
import threading
import time
from subprocess import PIPE

from other.app import Android
from config import PACKAGE_NAME, ACTIVITY_PATH, TMP_IMG_DIR, ANDROID_PERCENT, STAGE
from google_algorithm.label_image import identify_pic
from record import Record


class AndroidTester(object):
    def __init__(self, test_count, platform, device_id):
        self.test_count = test_count
        self.total_time = {}  # 存储样式：total_time = {totaltime:tasks_times}
        self.total_time_lock = threading.Lock()
        self.platform = platform
        self.device_id = device_id
        self.android = Android(device_id)
        self.apk_info = {}
        self.result = []

    def _get_apk_info(self):
        data = self.android.get_aapt_data()
        print('data : ' + data)
        for line in data.split("\n"):
            if line.startswith("package:"):
                for word in line.split(" "):
                    if "=" in word:
                        word = word.replace("'", "")
                        self.apk_info[word.split("=")[0]] = word.split("=")[1]

    def _get_time_stamp(self, pic):
        time_stamp = os.path.getctime(pic)
        return time_stamp


    def _calculate(self, times, start_time, tasks_times, target_stage=""):
        if target_stage == "":
            return None
        print('开始识别第 %s 次启动图片' % times)
        stage_time = [{'start': start_time}]
        ret = {}
        for st in STAGE:
            ret[st] = -1
        ret['start'] = start_time
        percent = ANDROID_PERCENT

        # 遍历截图，flag 记录当前识别阶段
        dir_path = os.path.join(TMP_IMG_DIR, str(times))  # 文件夹路径
        pics = os.listdir(dir_path)
        pics.sort()
        last_result = ''
        for pic in pics:
            file_path = os.path.join(dir_path, pic)  # 图片路径

            # 拿到图片的识别结果
            current_result = identify_pic(file_path)
            if current_result[0] == 'ad':
                return
            # print('%s 识别结果为：%s' % (file_path, current_result))
            if ret[current_result[0]] == -1 and current_result[1] > percent[current_result[0]]:
                ret[current_result[0]] = self._get_time_stamp(os.path.join(dir_path, pic))
            else:
                continue

        self.result.append(ret)

    def test(self):
        # 前 10 次不计入启动，出现广告概率较高
        for times in range(5):
            self.android.start_app(PACKAGE_NAME, ACTIVITY_PATH)
            time.sleep(12)
            self.android.kill_app(PACKAGE_NAME)
            time.sleep(5)

        thread_list = []
        for times in range(self.test_count):
            rec = Record(times, 1313, 15)
            self.record = threading.Thread(target=rec.record, args=()).start()
            # 清除所有 Logcat
            self.android.adb(['logcat', '-c']).wait()
            p_logcat = self.android.adb(['logcat', 'TaskManager:D', '*:S'], stdout=PIPE)

            # 启动 LauncherActivity
            print('正在启动 MainActivity 进行测试...')
            p_am = self.android.adb([
                'shell', 'am', 'start', '-W', '-n', '%s/%s' % (PACKAGE_NAME, ACTIVITY_PATH)
            ], stdout=PIPE)
            self.start_time = time.time()

            # 等待 MainActivity 启动完毕
            while p_am.poll() is None:
                time.sleep(0.1)

            # 终止 Logcat，计算 task 启动时间。tasks_times = {task:time}
            p_logcat.terminate()
            # tasks_times = get_each_task_time(p_am, p_logcat)
            tasks_times = {}
            time.sleep(15)
            self.android.kill_app(PACKAGE_NAME)

            # 新建线程，后台识别图片，并将线程加入 thread_list
            t = threading.Thread(target=self._calculate, args=(times, self.start_time, tasks_times, "loading"))
            t.start()
            thread_list.append(t)

            time.sleep(5)

        # 等待 thread_list 中全部线程执行完毕
        for t in thread_list:
            t.join()

        # 计算启动平均时长 和 Task 平均时长
        aver_launch_time = 0
        aver_home_page_loading_time = 0
        count_launch = 0
        count_page_loading = 0
        for dt in self.result:
            if dt['loading'] != -1:
                aver_launch_time += round((dt['loading'] - dt['start']), 4)
                count_launch += 1
            if dt['words'] != -1:
                aver_home_page_loading_time += round((dt['words'] - dt['loading']), 4)
                count_page_loading += 1

        return aver_launch_time / count_launch, aver_home_page_loading_time / count_page_loading

