# -*- coding: utf-8 -*-
import os
import threading
import time

from config import PACKAGE_NAME
from config import TMP_IMG_DIR
from config import IOS_PERCENT
from config import STAGE

from google_algorithm.label_image import identify_pic

from record import Record

from other.ios_driver_factory import iOSDriverFactory

class IOSTester(object):
    LOCK = threading.Lock()
    def __init__(self, test_count, platform, device_id, port, resolution):
        self.test_count = test_count
        self.total_time = {}  # 存储样式：total_time = {totaltime:tasks_times}
        self.total_time_lock = threading.Lock()
        self.platform = platform
        self.device_id = device_id
        self.apk_info = {}
        self.result = []
        self.port = port
        self.resolution = resolution
        self.ios_driver = iOSDriverFactory.get_iOS_Driver()

    def _get_time_stamp(self, pic):
        time_stamp = os.path.getctime(pic)
        return time_stamp

    def stop_app(self):
        self.ios_driver.terminate_app(PACKAGE_NAME)
        time.sleep(8)
        tap_object = {}
        tap_object['x'] = 5
        tap_object['y'] = 5
        self.ios_driver.execute_script("mobile: tap", tap_object)
        self.ios_driver.execute_script('mobile: swipe', {'direction': 'up'})
        self.ios_driver.execute_script('mobile: pressButton', {'name': 'home'})
        time.sleep(8)

    def _calculate(self, times, start_time, target_stage=""):
        if target_stage == "":
            return None
        print('开始识别第 %s 次启动图片' % times)
        stage_time = [{'start': start_time}]
        ret = {}
        for st in STAGE:
            ret[st] = -1
        ret['start'] = start_time
        percent = IOS_PERCENT

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
        # IOSTester.LOCK.acquire()
        self.result.append(ret)
        # IOSTester.LOCK.release()

    def test(self):
        time.sleep(5)
        thread_list = []
        for times in range(self.test_count):
            self.start_time = time.time()
            rec = Record(times, 12345, 15)
            self.record = threading.Thread(target=rec.record, args=()).start()

            print('启动 app..')
            self.ios_driver.launch_app()
            time.sleep(8)

            print('开启计算线程')
            t = threading.Thread(target=self._calculate, args=(times, self.start_time))
            t.start()
            thread_list.append(t)

        # 等待 thread_list 中全部线程执行完毕
        for t in thread_list:
            t.join()

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

if __name__ == '__main__':
    tester = IOSTester(1, "iOS", "ABCD", "12345", "400x600")
    tester.ios_driver.start_recording_screen()