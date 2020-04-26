# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog

from multiprocessing import Process
from threading import Thread

from queue import Queue

from ios_minicap.minicap import MinicapStream
from msg_queue.queue_manager import QueueManager

from app_config.config import TMP_IMG_ZHIHU_DIR
from app_config.config import TMP_IMG_TOP_TODAY_DIR
from app_config.config import TMP_IMG_BAIDU_DIR
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import ZHIHU_SORTED_STAGE
from app_config.config import BAIDU_SORTED_STAGE
from app_config.config import TOP_TODAY_SORTED_STAGE
from app_config.config import WEIBO_SORTED_STAGE

from app_config.config import ABOUT_TRAINING

from app_config.config import EXCLUDED_LIST

from app_config.config import JSON_PROGRESS_BAR_KEY
from app_config.config import JSON_TEXT_BROWSER_KEY
from app_config.config import JSON_PID_KEY
from app_config.config import JSON_PROGRESS_DIALOG_CLOSE
from app_config.config import JSON_ANSWER_KEY

from app_config.config import JSON_SIGNAL_KEY
from app_config.config import JSON_SIGNAL_UPDATE_KEY

from app_config.config import iOS_ZHIHU_MODEL_NAME
from app_config.config import iOS_TOP_TODAY_MODEL_NAME
from app_config.config import iOS_BAIDU_MODEL_NAME
from app_config.config import iOS_WEIBO_MODEL_NAME

from app_config.config import iOS_ZHIHU_LABEL_NAME
from app_config.config import iOS_TOP_TODAY_LABEL_NAME
from app_config.config import iOS_BAIDU_LABEL_NAME
from app_config.config import iOS_WEIBO_LABEL_NAME

import app_config.config

from CalProgressDialog import CalProgressDialog
from QTSignal import QTSignal
from cal_time import CalTime
from google_algorithm import training

import os
import time
import queue
import math
import json

class Ui_MainWindow(QtCore.QObject):

    signal_training_progress = pyqtSignal(str)

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.signal_training_progress.connect(self.update_text_browser)

        # 默认为测试 APP 为「知乎」

        self.test_app_code = 1
        self.test_os_type = None
        self.test_app_name = "知乎"

        self.TEST_APP = "zhihu"
        self.LAST_APP = ""

        self.IOS_MODEL_NAME = iOS_ZHIHU_MODEL_NAME
        self.IOS_LABEL_NAME = iOS_ZHIHU_LABEL_NAME
        self.TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR

        self.minicap = None
        self.task_process_dt = {}
        self.cal_process_ls = []
        self.answer_dt = {}

    def setupUi(self, MainWindow):
        self.DEBUG = False

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(610, 10, 181, 541))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.startMinicap = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.startMinicap.setObjectName("startMinicap")
        self.verticalLayout.addWidget(self.startMinicap)

        self.start_screenshot_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.start_screenshot_button.setObjectName("start_screenshot_button")
        self.verticalLayout.addWidget(self.start_screenshot_button)
        self.stop_screenshot_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.stop_screenshot_button.setObjectName("stop_screenshot_button")
        self.verticalLayout.addWidget(self.stop_screenshot_button)

        # 计算时长
        self.cal_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cal_button.setObjectName("cal_button")
        self.verticalLayout.addWidget(self.cal_button)

        # 一键训练
        self.training_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.training_button.setObjectName("training_button")
        self.verticalLayout.addWidget(self.training_button)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 601, 471))
        self.textBrowser.setObjectName("textBrowser")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 479, 601, 74))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.platform_label_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.platform_label_text.sizePolicy().hasHeightForWidth())
        self.platform_label_text.setSizePolicy(sizePolicy)
        self.platform_label_text.setAlignment(QtCore.Qt.AlignCenter)
        self.platform_label_text.setObjectName("platform_label_text")
        self.horizontalLayout.addWidget(self.platform_label_text)
        self.platform_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.platform_label.sizePolicy().hasHeightForWidth())
        self.platform_label.setSizePolicy(sizePolicy)
        self.platform_label.setText("")
        self.platform_label.setAlignment(QtCore.Qt.AlignCenter)
        self.platform_label.setObjectName("platform_label")
        self.horizontalLayout.addWidget(self.platform_label)

        self.platform_type_label_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.platform_type_label_text.setObjectName("platform_type_label_text")
        self.horizontalLayout.addWidget(self.platform_type_label_text)
        self.platform_type_comboBox = QtWidgets.QComboBox(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.platform_type_comboBox.sizePolicy().hasHeightForWidth())
        self.platform_type_comboBox.setSizePolicy(sizePolicy)
        self.platform_type_comboBox.setObjectName("platform_type_comboBox")
        self.horizontalLayout.addWidget(self.platform_type_comboBox)

        self.app_name_label_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_name_label_text.sizePolicy().hasHeightForWidth())
        self.app_name_label_text.setSizePolicy(sizePolicy)
        self.app_name_label_text.setAlignment(QtCore.Qt.AlignCenter)
        self.app_name_label_text.setObjectName("app_name_label_text")
        self.horizontalLayout.addWidget(self.app_name_label_text)
        self.comboBox = QtWidgets.QComboBox(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)

        MainWindow.setCentralWidget(self.centralwidget)
        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        # self.menubar.setObjectName("menubar")
        # self.menu = QtWidgets.QMenu(self.menubar)
        # self.menu.setObjectName("menu")
        # MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # self.actionAdd_model_file = QtWidgets.QAction(MainWindow)
        # self.actionAdd_model_file.setObjectName("actionAdd_model_file")
        # self.actionSet_training_pictures = QtWidgets.QAction(MainWindow)
        # self.actionSet_training_pictures.setObjectName("actionSet_training_pictures")
        # self.menu.addAction(self.actionAdd_model_file)
        # self.menu.addSeparator()
        # self.menu.addAction(self.actionSet_training_pictures)
        # self.menubar.addAction(self.menu.menuAction())

        # 添加操作系统类型下拉选项
        self.set_platform_info()

        self.retranslateUi(MainWindow)

        self.startMinicap.clicked.connect(self.on_click_start_minicap_button)
        self.start_screenshot_button.clicked.connect(self.on_click_start_screenshot_button)
        self.stop_screenshot_button.clicked.connect(self.on_click_stop_screenshot_button)
        self.training_button.clicked.connect(self.on_click_training_button)
        self.cal_button.clicked.connect(self.on_click_cal_button)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.comboBox.currentTextChanged.connect(self.on_update_test_app_info)
        self.platform_type_comboBox.currentTextChanged.connect(self.on_update_platform_type_info)

        # self.actionAdd_model_file.triggered.connect(self.on_click_set_model_action)
        # self.actionSet_training_pictures.triggered.connect(self.on_click_set_pic_action)

        self.platform_type_flag = False
        self.ios_version_flag = False
        self.app_version_flag = False

        # 毫秒
        self.interval = 200
        self.CLOCK = QTimer()
        self.CLOCK.setInterval(self.interval)
        self.CLOCK.timeout.connect(self._count_down)

        self.TRAINING_CLOCK = QTimer()
        self.TRAINING_CLOCK.setInterval(1000)
        self.TRAINING_CLOCK.timeout.connect(self._training_count_down)

        self.i = 0

        self.queue = Queue()
        self.ui_msg_queue = Queue()
        self.app_info_update_queue = Queue()
        self.answer_queue = Queue()
        self.task_pid_status = {}

        QueueManager.register('get_queue', callable=lambda : self.queue)
        QueueManager.register('get_ui_msg_queue', callable=lambda : self.ui_msg_queue)
        QueueManager.register('get_app_info_update_queue', callable=lambda : self.app_info_update_queue)
        QueueManager.register('get_answer_queue', callable=lambda : self.answer_queue)
        QueueManager.register('get_task_status', callable=lambda : self.task_pid_status)

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.start()

        self.shared_queue = self.manager.get_queue()
        self.shared_ui_msg_queue = self.manager.get_ui_msg_queue()
        self.shared_app_info_queue = self.manager.get_app_info_update_queue()
        self.shared_answer_queue = self.manager.get_answer_queue()
        self.shared_task_status_dt = self.manager.get_task_status()

        if self.DEBUG:
            self.start_screenshot_button.setEnabled(False)
            self.stop_screenshot_button.setEnabled(False)
            self.cal_button.setEnabled(False)
            self.training_button.setEnabled(False)
        else:
            self.startMinicap.setEnabled(False)
            self.start_screenshot_button.setEnabled(False)
            self.stop_screenshot_button.setEnabled(False)
            self.cal_button.setEnabled(False)
            self.training_button.setEnabled(False)

        self.times = 1

        self.fileDialog = None

        # key 代表 capture/tmp_pic/iOS 下的某个文件夹名，value 表示这个计算这个文件夹下图片序列的启动时长的时间复杂度
        self.search_price_dt = {}

        self._setup_msg_box()
        # self._setup_file_dialog("")
        self.fileDialog = None

        self.remind_user = True
        self.training_pic_dir = os.path.join(ABOUT_TRAINING, self.TEST_APP, "iOS_1-50")
        self.model_path = os.path.join(ABOUT_TRAINING, self.TEST_APP, "model", self.IOS_MODEL_NAME)

        self.WAIT_TIME = 5 # TIMES 次数

        self.task_process_1 = None
        self.task_process_2 = None


    def start_update_ui_thread(self):
        self.ui_update_thread = Thread(target=self._update_ui)
        self.ui_update_thread.setDaemon(True)
        self.ui_update_thread.start()

    def _update_ui(self):
        data_browser = ""
        data_progress = ""
        data_pid = ""
        data_answer = ""
        if not self.platform_type_flag:
            msg = {JSON_PID_KEY: os.getpid(), JSON_TEXT_BROWSER_KEY: ('请先选择 OS 平台类型', )}
            self._update_info(msg[JSON_TEXT_BROWSER_KEY], os.getpid())
        while True:
            try:
                if not self.platform_type_flag:
                    continue
                if not self.ios_version_flag:
                    self.platform_label.setText(self.query_ios_version())
                    continue

                if not self.app_version_flag:
                    self.comboBox.addItems(self.query_app_info())
                ui_data = self.shared_ui_msg_queue.get_nowait()
                if not ui_data:
                    continue
                msg = json.loads(ui_data)
                for key in msg:
                    if key == JSON_TEXT_BROWSER_KEY:
                        data_browser = msg[key]
                    elif key == JSON_PROGRESS_BAR_KEY:
                        data_progress = msg[key]
                    elif key == JSON_PID_KEY:
                        data_pid = msg[key]
                    elif key == JSON_PROGRESS_DIALOG_CLOSE:
                        self.cal_progress_dialog.close()
                    elif key == JSON_ANSWER_KEY:
                        data_answer = msg[key]

                if data_browser:
                    self._update_info(data_browser, data_pid)
                    data_browser = ""
                if data_progress:
                    self._update_progress(data_progress)
                    data_progress = ""
                if data_answer:
                    self._update_answer_dt(data_pid, data_answer[0], data_answer[1])
                    data_answer = ""

            except queue.Empty:
                data_browser = None
                pass
            except ConnectionResetError:
                print("connection has been reset")
                return

    def _update_answer_dt(self, pid, launch_time, page_loading_time):
        self.answer_dt[pid] = (launch_time, page_loading_time)
        if len(self.answer_dt) == len(self.search_price_dt) and len(self.search_price_dt) > 0:
            launch_time_ls = []
            loading_time_ls = []
            for pid in self.answer_dt:
                app_launch_time, loading_time = self.answer_dt[pid]
                if app_launch_time > 0:
                    launch_time_ls.append(int(launch_time * 1000))
                if loading_time > 0:
                    loading_time_ls.append(int(loading_time * 1000))

            launch_time_ls.sort()
            loading_time_ls.sort()

            len1 = len(launch_time_ls)
            len2 = len(loading_time_ls)

            if len1 > 2:
                aver_launch_time = 1.0 * sum(launch_time_ls[1:-1]) / (len1 - 2)
            else:
                aver_launch_time = 0

            if len2 > 2:
                aver_home_page_loading_time = 1.0 * sum(loading_time_ls[1:-1]) / (len2 - 2)
            else:
                aver_home_page_loading_time = 0

            aver_launch_time /= 1000
            aver_home_page_loading_time /= 1000

            msg = {}
            # str_aver = "平均启动时长：%.3f" % (aver_launch_time)
            str_aver = "平均启动时长：%.3f  平均加载时长: %.3f" % (aver_launch_time, aver_home_page_loading_time)
            self._update_info(str_aver, os.getpid())
            print(str_aver)
            # msg[JSON_PROGRESS_DIALOG_CLOSE] = True
            # msg[JSON_TEXT_BROWSER_KEY] = str_aver
            # msg[JSON_PID_KEY] = os.getpid()

    def _update_info(self, data_browser, pid):
        self.signal_training_progress.emit("pid %d - %s" % (pid, ''.join(data_browser)))

    def _update_progress(self, data_progress):
        pb_index, value = data_progress
        self.qt_signal.dt_signal[pb_index].emit(pb_index, value)

    def _setup_qt_signal(self):
        screenshots_dir = os.path.join(self.TMP_IMG_DIR, "iOS")
        times_list = [t for t in os.listdir(screenshots_dir) if not t.startswith(".")]
        times_list.sort()
        # counter 表示有多少个计算阶段
        counter = len(self.SORTED_STAGE) - len(EXCLUDED_LIST)
        num = 0
        for t in times_list:
            if t.startswith("."):
                continue
            else:
                # dt 中的 value 中用于设定 progress bar 中的 maximum 值
                pic_dir = os.path.join(screenshots_dir, t)
                pic_amount = int(os.popen("ls -l %s | wc -l " % pic_dir).read())
                if pic_amount <= 0:
                    continue
                search_price = int(math.log(pic_amount, 2)) + 1
                search_price *= counter  # 所有阶段「全局查找中，二分查找」的搜索次数总和的最大值
                adjustment_price = 10 * counter  # 所有阶段 「局部调整中，线性查找」的搜索次数总和的最大值
                search_price += adjustment_price
                self.search_price_dt[int(t)] = search_price # todo 调整搜索算法，最后将self.fn_index_dt 改为 dt

        self.cal_progress_dialog = CalProgressDialog(self.search_price_dt)
        self.qt_signal = QTSignal()
        # k 表示 capture/tmp_pic/iOS 下的文件夹名，用 k 去找对应的 signal
        for k in self.cal_progress_dialog.ui.progress_bar_dt:
            self.qt_signal.dt_signal[k].connect(self.update_progress_bar)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "App 特定场景截图工具"))
        self.startMinicap.setText(_translate("MainWindow", "启动 mincap"))
        self.start_screenshot_button.setText(_translate("MainWindow", "开始截图"))
        self.stop_screenshot_button.setText(_translate("MainWindow", "结束截图"))
        self.cal_button.setText(_translate("MainWindow", "计算时间"))
        self.training_button.setText(_translate("MainWindow", "一键训练"))
        self.platform_label_text.setText(_translate("MainWindow", "系统版本："))
        self.platform_type_label_text.setText(_translate("MainWindow", "平台: "))
        self.app_name_label_text.setText(_translate("MainWindow", "被测 APP :"))
        # self.menu.setTitle(_translate("MainWindow", "文件"))
        # self.actionAdd_model_file.setText(_translate("MainWindow", "添加模型文件"))
        # self.actionSet_training_pictures.setText(_translate("MainWindow", "设置训练图片"))

    def _start_minicap(self):
        cwd = os.getcwd()
        minicap_dir = "ios-minicap" if self.test_os_type == "iOS" else "android-minicap"
        os.chdir(minicap_dir)
        os.system("./run.sh &")
        os.chdir(cwd)
        time.sleep(5)

    def _start_screenshot_process(self, PORT):
        if not self.minicap:
            self.minicap = MinicapStream(port=PORT, test_app_code=self.test_app_code)
            self.minicap.run()
        elif not self.minicap.read_image_stream_task.is_alive:
            self.minicap.run()

        self.shared_queue.put(self.times)
        self.textBrowser.append("第 %d 次截图开始" % self.times)
        print("read_image_stream_task YES" if self.minicap.read_image_stream_task.is_alive() else "read_image_stream_task NO")
        self.textBrowser.append("请等待 %d s，再点击 app 截图" % int(self.interval * self.WAIT_TIME / 1000))
        # self.stop_screenshot_button.setEnabled(True)
        self.times += 1

    def _stop_screenshot_process(self):
        '''
        停止截图，只是不从连接的套接字上接受数据
        :return:
        '''
        self.shared_queue.put(-1)
        msg = {JSON_PID_KEY: os.getpid(), JSON_TEXT_BROWSER_KEY: ("截图停止",)}
        self.shared_ui_msg_queue.put(json.dumps(msg))

    def _terminate_screenshot_process(self):
        '''
        断开与 minicap 连接的套接字
        :return:
        '''
        print("断开与 minicap 连接的套接字")
        self.shared_queue.put(-2)
        msg = {JSON_PID_KEY: os.getpid(), JSON_TEXT_BROWSER_KEY: ("断开与 minicap 连接的套接字",)}
        self.shared_ui_msg_queue.put(json.dumps(msg))

    def _dispatch_cal_task(self):
        screenshots_dir = os.path.join(self.TMP_IMG_DIR, "iOS")
        times_list = list(self.search_price_dt.keys())
        times_list.sort()
        i = 0
        flag_1 = False
        flag_2 = False
        # length = len(self.search_price_dt)
        # finished_list = []
        local_answer_dt = {}
        temp_times_list = times_list.copy()
        while len(temp_times_list) > 0:

            if not self.task_process_1 or not self.task_process_1.is_alive():
                if len(temp_times_list) > 0:
                    num = temp_times_list.pop(0)
                    pictures_dir_1 = os.path.join(screenshots_dir, str(num))
                    self.task_process_1 = Process(target=self._cal_time, args=(pictures_dir_1, num))
                    self.task_process_1.start()
                    local_answer_dt[self.task_process_1.pid] = None
                    self.answer_dt[self.task_process_1.pid] = None
                    flag_1 = True

            # 去掉下面注释，则同时开启两个计算进程
            if not self.task_process_2 or not self.task_process_2.is_alive():
                if len(temp_times_list) > 0:
                    num = temp_times_list.pop(0)
                    pictures_dir_2 = os.path.join(screenshots_dir, str(num))
                    self.task_process_2 = Process(target=self._cal_time, args=(pictures_dir_2, num))
                    self.task_process_2.start()
                    local_answer_dt[self.task_process_2.pid] = None
                    self.answer_dt[self.task_process_2.pid] = None
                    flag_2 = True

    def _update_cal_status(self, content):
        self.textBrowser.append(content)

    def _cal_time(self, pic_dir, times_counter):
        ct = CalTime(main_window=self, times_counter=times_counter, test_app_code=self.test_app_code)
        return ct.cal_time(pic_dir, EXCLUDED_LIST)

    def update_progress_bar(self, progress_bar_id, value):
        self.cal_progress_dialog.ui.progress_bar_dt[progress_bar_id].setValue(value)

    def update_text_browser(self, text):
        self.textBrowser.append(text)

    def _start_training(self, image_path):
        if self.DEBUG:
            output_graph = os.path.join(ABOUT_TRAINING, self.TEST_APP, "debug", "model", self.IOS_MODEL_NAME)
            output_labels = os.path.join(ABOUT_TRAINING, self.TEST_APP, "debug", "labels", self.IOS_LABEL_NAME)

            if not os.path.exists(output_graph):
                os.makedirs(os.path.dirname(output_graph))

            if not os.path.exists(output_labels):
                os.makedirs(os.path.dirname(output_labels))
        else:
            output_graph = os.path.join(ABOUT_TRAINING, self.TEST_APP, "model", self.IOS_MODEL_NAME)
            output_labels = os.path.join(ABOUT_TRAINING, self.TEST_APP, "labels", self.IOS_LABEL_NAME)

            graph_dir = os.path.dirname(output_graph)
            if not os.path.exists(graph_dir):
                os.makedirs(graph_dir)

            label_dir = os.path.dirname(output_labels)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)

        process_training = Process(target=training.start_training, args=(image_path, output_graph, output_labels, self.TEST_APP))
        process_training.start()

    def _checkout_minicap(self, PORT):
        status, pid = Ui_MainWindow.query_service(PORT)
        if not status:
            print("minicap status: %s  pid: %s" % (status, pid))
            if pid != -1:
                os.system("kill %s" % pid)
            proc_start_minicap = Process(target=self._start_minicap)
            proc_start_minicap.daemon = True
            proc_start_minicap.start()

    # def on_click_minicap_button(self):
    #     # 首先查询 ios-minicap 的状态，如果状态不是 listen，则重新启动
    #     self._checkout_ios_minicap()
    #     self.textBrowser.append("正在启动 ios-minicap，请等待 %d s，再开始操作" % int(self.interval * self.WAIT_TIME // 1000))
    #     # 添加一个 dialog，倒数 self.WAIT_TIME s,倒数 self.WAIT_TIME s 后，显示启动成功
    #     self._startup_progress_dialog("Waiting for ios-minicap", self.WAIT_TIME, True, self.CLOCK)
    #     self.start_screenshot_button.setEnabled(True)
    #     self.stop_screenshot_button.setEnabled(True)

    def on_click_start_minicap_button(self):
        PORT = QueueManager.MINICAP_PORT if self.test_os_type == "iOS" else QueueManager.ANDROID_PORT
        self._checkout_minicap(PORT)
        if self.test_os_type == 'iOS':
            self._startup_progress_dialog("Waiting for ios-minicap", self.WAIT_TIME, True, self.CLOCK)

    def on_click_start_screenshot_button(self):
        '''
        启动截图进程
        :return:
        '''
        # 每点击一次启动截图，就代表新的一轮截图，即：在capture/tmp_pic/iOS/ 下，再次新建一个文件夹，点击开始计算，就开始将所有截图进行计算，根据新建的文件夹个数反馈进度，显示在进度条上，最后给出一个总体结果到 text browser 上
        # 当点击一次启动截图后，就将启动截图按钮禁用，直到停止截图按钮被按下
        # 首先查询 ios-minicap 的状态，如果状态不是 listen，则重新启动
        PORT = QueueManager.MINICAP_PORT if self.test_os_type == "iOS" else QueueManager.ANDROID_PORT
        self._start_screenshot_process(PORT)
        # self.start_screenshot_button.setEnabled(False)

    def on_click_stop_screenshot_button(self):
        '''
        停止截图
        :return:
        '''
        # self.start_screenshot_button.setEnabled(True)
        self._stop_screenshot_process()

    def on_click_cal_button(self):
        self.textBrowser.clear()
        self.textBrowser.append("正在启动计算进程")
        self._setup_qt_signal()
        # self.cal_progress_dialog.show()
        cal_process = Process(target=self._dispatch_cal_task)
        cal_process.start()
        self.cal_process_ls.append(cal_process.pid)
        print("cal_process pid: %d" % cal_process.pid)

    def on_click_training_button(self):
        # 弹出一个对话框，让用户选择训练图片文件夹，pb 和 label 文件不用指定路径，存放在默认路径
        # 选择完 image 文件夹后，调用 _start_training, self.training_pic_dir 初始化为默认路径
        if self.remind_user:
            self.message_box.exec()
            self.remind_user = False if self.check_box.isChecked() else True
            self._setup_file_dialog("Open image dir", True, os.path.join(ABOUT_TRAINING, self.TEST_APP, "iOS_1-50"))
            if self.fileDialog.exec():
                self.training_pic_dir = self.fileDialog.selectedFiles()[0]
                self.textBrowser.append("训练图片文件夹为：%s" % self.training_pic_dir)
                print(self.training_pic_dir)
                self.fileDialog.setDirectory(self.training_pic_dir)
        self.textBrowser.append("正在启动训练进程，请稍等")
        self._start_training(self.training_pic_dir)

    def on_click_set_pic_action(self):
        self._setup_file_dialog("打开一组训练图片文件夹的父文件夹", True, os.path.join(ABOUT_TRAINING, self.TEST_APP, "iOS_1-50"))
        self.fileDialog.exec()
        self.training_pic_dir = self.fileDialog.selectedFiles()[0]
        self.fileDialog.setDirectory(self.training_pic_dir)

    def on_click_set_model_action(self):
        self._setup_file_dialog("选择一个 模型(.pb)文件", True, os.path.join(ABOUT_TRAINING, self.TEST_APP, "iOS_1-50"))
        self.fileDialog.exec()
        self.model_path = self.fileDialog.selectedFiles()[0]
        self.fileDialog.setDirectory(self.training_pic_dir)

    def on_update_test_app_info(self, current_text):
        print(current_text)
        ls = current_text.strip().split()
        self.test_app_name = ls[0].strip()
        # 1 知乎 2 微博 3 头条 4 百度
        if self.test_app_name == "知乎":
            self.TEST_APP = "zhihu"
            self.IOS_MODEL_NAME = iOS_ZHIHU_MODEL_NAME
            self.IOS_LABEL_NAME = iOS_ZHIHU_LABEL_NAME
            self.TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR
            self.SORTED_STAGE = ZHIHU_SORTED_STAGE

        elif self.test_app_name == "微博":
            self.TEST_APP = "weibo"
            self.IOS_MODEL_NAME = iOS_WEIBO_MODEL_NAME
            self.IOS_LABEL_NAME = iOS_WEIBO_LABEL_NAME
            self.TMP_IMG_DIR = TMP_IMG_WEIBO_DIR
            self.SORTED_STAGE = WEIBO_SORTED_STAGE

        elif self.test_app_name == "今日头条":
            self.test_app_code = 3
            self.TEST_APP = "top_today"
            self.IOS_MODEL_NAME = iOS_TOP_TODAY_MODEL_NAME
            self.IOS_LABEL_NAME = iOS_TOP_TODAY_LABEL_NAME
            self.TMP_IMG_DIR = TMP_IMG_TOP_TODAY_DIR
            self.SORTED_STAGE = TOP_TODAY_SORTED_STAGE

        elif self.test_app_name == "百度":
            self.test_app_code = 4
            self.TEST_APP = "baidu"
            self.IOS_MODEL_NAME = iOS_BAIDU_MODEL_NAME
            self.IOS_LABEL_NAME = iOS_BAIDU_LABEL_NAME
            self.TMP_IMG_DIR = TMP_IMG_BAIDU_DIR
            self.SORTED_STAGE = BAIDU_SORTED_STAGE

        # 当用户选好「被测 APP」后，打开「开始截图」「一键训练」按钮
        if self.test_app_name != "None":
            if self.LAST_APP == "":
                self.LAST_APP = self.TEST_APP
            else:
                if self.LAST_APP != self.TEST_APP:
                    self.times = 1
            self.startMinicap.setEnabled(True)
            self.start_screenshot_button.setEnabled(True)
            self.stop_screenshot_button.setEnabled(True)
            self.shared_app_info_queue.put(self.TMP_IMG_DIR)
            self.training_button.setEnabled(True)
            self.cal_button.setEnabled(True)
            self.textBrowser.append("被测的 APP 是：%s, %d" % (self.test_app_name, self.test_app_code))
            self.remind_user = True
            print(self.TEST_APP)

        else:
            self.start_screenshot_button.setEnabled(False)
            self.stop_screenshot_button.setEnabled(False)
            self.cal_button.setEnabled(False)
            self.training_button.setEnabled(False)
            self.textBrowser.append("请先选择被测的 APP")

    def on_update_platform_type_info(self, current_text):
        print(current_text)
        ls = current_text.strip().split()
        # 在更换操作系统的时候，且存在与 minicap 连接的套接字时, 且更换的 OS 类型与上一次的不同时，断开原来的套接字连接
        if self.minicap and ls[0].strip() != "None" and self.test_os_type != ls[0].strip():
            self._terminate_screenshot_process()
            self.minicap = None

        self.test_os_type = ls[0].strip()
        self.textBrowser.append("操作系统平台是：%s" % self.test_os_type)
        self.comboBox.setCurrentIndex(0)
        self.textBrowser.append("正在查询操作系统版本，请稍等")
        self.platform_type_flag = True

    def _setup_msg_box(self):
        self.message_box = QtWidgets.QMessageBox()
        self.message_box.setText("在训练之前，请先选择带有标签的图片文件夹的父文件夹")
        self.message_box.setInformativeText("不再提醒我")
        self.check_box = QtWidgets.QCheckBox()
        self.message_box.setCheckBox(self.check_box)

    def _setup_file_dialog(self, title, is_modal, default_dir):
        self.fileDialog = QFileDialog(parent=None, caption=title)
        self.fileDialog.setModal(is_modal)
        self.fileDialog.setViewMode(QFileDialog.List)
        # default_image_dir = os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50")
        self.fileDialog.setDirectory(default_dir)

    def _startup_progress_dialog(self, info, max_num, is_modal, para_clock):
        # self.progressDialog = QProgressDialog("Waiting for ios-minicap", "cancel", 0, 5)
        self.i = 0
        self.progressDialog = QProgressDialog(info, "cancel", 0, max_num)
        self.progressDialog.setFixedWidth(500)
        self.progressDialog.setAutoClose(True)
        self.progressDialog.setModal(is_modal)
        para_clock.start(max_num * self.interval)

    def _training_count_down(self):
        self.progressDialog.setValue(self.i + 1)
        self.progressDialog.setLabelText("训练进度： %d/420" % self.i)
        self.i += 1
        if self.i >= 420:
            self.TRAINING_CLOCK.stop()
            self.i = 0

    def _count_down(self):
        self.i += 1
        self.progressDialog.setValue(self.i)
        self.progressDialog.setLabelText("Waiting for ios-minicap: %d%%" % int(self.i / self.WAIT_TIME * 100))

        if self.i == self.WAIT_TIME:
            self.CLOCK.stop()
            self.i = 0
            msg = {JSON_TEXT_BROWSER_KEY: "可以点击 App 截图了", JSON_PID_KEY: os.getpid()}
            self.shared_ui_msg_queue.put(json.dumps(msg))

    @staticmethod
    def query_service(port):
        fobj = os.popen("lsof -i tcp:%d" % port)
        state = fobj.read().strip()
        if len(state) == 0:
            return False, -1
        ls = state.split("\n")
        ls.reverse()
        for item in ls:
            status_list = item.split()
            status = status_list[-1].strip()
            pid = status_list[1].strip()
            cmd_name = status_list[0].strip()
            if cmd_name in ["ios_minic", "adb"]:
                return status in ["(ESTABLISHED)", "(LISTEN)"], pid
        return False, -1

    def query_ios_version(self):
        android_cmd = "adb shell getprop ro.build.version.release"
        ios_cmd = "instruments -s devices | grep -v -i simulator | grep -i null"
        cmd = ios_cmd if self.test_os_type == "iOS" else android_cmd
        fobj = os.popen(cmd)
        if self.test_os_type == "iOS":
            query_result = False if len(fobj.read()) == 0 else True
            if not query_result:
                cmd = "instruments -s devices | grep -v -i simulator | grep -i iphone"
                fobj = os.popen(cmd)
                for line in fobj:
                    ls = line.strip().split()
                    self.ios_version_flag = True
                    return "%s %s" % (self.test_os_type, ls[1])
        elif self.test_os_type == "Android":
            version = fobj.read().strip()
            self.ios_version_flag = True
            return "%s %s" % (self.test_os_type, version)
        else:
            return "请连接且信任 %s 所连接的电脑" % "iPhone" if self.test_os_type == "iOS" else "Android 设备"

    def query_app_info(self):
        '''
        查询所有安装的 app （系统 app 除外），然后生成一个列表，让用户选择对应的 app
        :return:
        '''
        ios_cmd = "ideviceinstaller -l -o list_user"
        android_cmd = "adb shell pm list packages"
        cmd = ios_cmd if self.test_os_type == "iOS" else android_cmd
        fobj = os.popen(cmd)

        ls = ["None"]
        for line in fobj:
            if line.strip().find("baidu") != -1:
                ls.append("百度")
            elif line.strip().find("zhihu.ios") != -1 or line.strip() == "package:com.zhihu.android":
                ls.append("知乎")
            elif line.strip().find("weibo") != -1:
                ls.append("微博")
            elif line.strip().find("article") != -1:
                ls.append("今日头条")

        self.app_version_flag = True if len(ls) > 1 else False

        return ls

    def set_platform_info(self):
        '''
        初始化「操作系统类型选择列表」
        :return:
        '''
        os_ls = ["None", "iOS"]
        self.platform_type_comboBox.addItems(os_ls)