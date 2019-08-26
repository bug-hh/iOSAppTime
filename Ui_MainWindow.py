# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iOSAppTime.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


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

from app_config.config import TMP_IMG_DIR
from app_config.config import ABOUT_TRAINING
from app_config.config import IOS_MODEL_NAME
from app_config.config import IOS_LABEL_NAME
from app_config.config import TEST_APP
from app_config.config import SORTED_STAGE
from app_config.config import EXCLUDED_LIST
from app_config.config import JSON_PROGRESS_BAR_KEY
from app_config.config import JSON_TEXT_BROWSER_KEY
from app_config.config import JSON_PID_KEY
from app_config.config import RETRAIN_PATH

from CalProgressDialog import CalProgressDialog
from QTSignal import QTSignal
from cal_time import CalTime
from google_algorithm import training


import os
import time
import queue
import subprocess
import math
import json


class Ui_MainWindow(QtCore.QObject):

    signal_training_progress = pyqtSignal(str)

    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.signal_training_progress.connect(self.update_text_browser)

    def setupUi(self, MainWindow):
        self.DEBUG = True

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
        self.start_minicap_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.start_minicap_button.setObjectName("start_minicap_button")
        self.verticalLayout.addWidget(self.start_minicap_button)
        self.start_screenshot_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.start_screenshot_button.setObjectName("start_screenshot_button")
        self.verticalLayout.addWidget(self.start_screenshot_button)
        self.stop_screenshot_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.stop_screenshot_button.setObjectName("stop_screenshot_button")
        self.verticalLayout.addWidget(self.stop_screenshot_button)
        self.cal_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cal_button.setObjectName("cal_button")
        self.verticalLayout.addWidget(self.cal_button)
        self.training_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.training_button.setObjectName("training_button")
        self.verticalLayout.addWidget(self.training_button)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 601, 471))
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 479, 601, 71))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.platform_label_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.platform_label_text.setObjectName("platform_label_text")
        self.horizontalLayout.addWidget(self.platform_label_text)
        self.platform_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.platform_label.setText("")
        self.platform_label.setObjectName("platform_label")
        self.horizontalLayout.addWidget(self.platform_label)
        self.app_name_label_text = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.app_name_label_text.setObjectName("app_name_label_text")
        self.horizontalLayout.addWidget(self.app_name_label_text)
        self.app_name_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.app_name_label.setText("")
        self.app_name_label.setObjectName("app_name_label")
        self.horizontalLayout.addWidget(self.app_name_label)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAdd_model_file = QtWidgets.QAction(MainWindow)
        self.actionAdd_model_file.setObjectName("actionAdd_model_file")
        self.actionSet_training_pictures = QtWidgets.QAction(MainWindow)
        self.actionSet_training_pictures.setObjectName("actionSet_training_pictures")
        self.menu.addAction(self.actionAdd_model_file)
        self.menu.addSeparator()
        self.menu.addAction(self.actionSet_training_pictures)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.start_minicap_button.clicked.connect(self.on_click_minicap_button)
        self.start_screenshot_button.clicked.connect(self.on_click_start_screenshot_button)
        self.stop_screenshot_button.clicked.connect(self.on_click_stop_screenshot_button)
        self.training_button.clicked.connect(self.on_click_training_button)
        self.cal_button.clicked.connect(self.on_click_cal_button)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.actionAdd_model_file.triggered.connect(self.on_click_set_model_action)
        self.actionSet_training_pictures.triggered.connect(self.on_click_set_pic_action)

        self.CLOCK = QTimer()
        self.CLOCK.setInterval(500)
        self.CLOCK.timeout.connect(self._count_down)

        self.TRAINING_CLOCK = QTimer()
        self.TRAINING_CLOCK.setInterval(1000)
        self.TRAINING_CLOCK.timeout.connect(self._training_count_down)

        self.i = 0
        self.percent = 20

        self.queue = Queue()
        self.ui_msg_queue = Queue()
        self.answer_queue = Queue()

        self.task_pid_status = {}

        QueueManager.register('get_queue', callable=lambda : self.queue)
        QueueManager.register('get_ui_msg_queue', callable=lambda : self.ui_msg_queue)
        QueueManager.register('get_answer_queue', callable=lambda : self.answer_queue)
        QueueManager.register('get_task_status', callable=lambda : self.task_pid_status)

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.start()

        self.shared_queue = self.manager.get_queue()
        self.shared_ui_msg_queue = self.manager.get_ui_msg_queue()
        self.shared_answer_queue = self.manager.get_answer_queue()
        self.shared_task_status_dt = self.manager.get_task_status()

        if self.DEBUG:
            self.start_screenshot_button.setEnabled(False)
            self.stop_screenshot_button.setEnabled(False)
            self.cal_button.setEnabled(True)
            self.training_button.setEnabled(False)

        self.times = 1

        self.fileDialog = None

        # key 代表 capture/tmp_pic/iOS 下的某个文件夹名，value 表示这个计算这个文件夹下图片序列的启动时长的时间复杂度
        self.search_price_dt = {}

        self._setup_msg_box()
        # self._setup_file_dialog("")
        self.fileDialog = None

        self.remind_user = True
        self.training_pic_dir = os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50")
        self.model_path = os.path.join(ABOUT_TRAINING, TEST_APP, "model", IOS_MODEL_NAME)

    def start_update_ui_thread(self):
        self.ui_update_thread = Thread(target=self._update_ui)
        self.ui_update_thread.setDaemon(True)
        self.ui_update_thread.start()

    def _update_ui(self):
        data_browser = ""
        data_progress = ""
        data_pid = ""
        while True:
            try:
                ui_data = self.shared_ui_msg_queue.get_nowait()
                msg = json.loads(ui_data)
                for key in msg:
                    if key == JSON_TEXT_BROWSER_KEY:
                        data_browser = msg[key]
                    elif key == JSON_PROGRESS_BAR_KEY:
                        data_progress = msg[key]
                    elif key == JSON_PID_KEY:
                        data_pid = msg[key]
                if data_browser:
                    self._update_info(data_browser, data_pid)
                if data_progress:
                    self._update_progress(data_progress)
            except queue.Empty:
                data_browser = None
                pass
            except ConnectionResetError:
                print("connection has been reset")
                return

    def _update_info(self, data_browser, pid):
        self.signal_training_progress.emit("pid %d - %s" % (pid, ''.join(data_browser)))

    def _update_progress(self, data_progress):
        pb_index, value = data_progress
        self.qt_signal.dt_signal[pb_index].emit(pb_index, value)

    def _setup_qt_signal(self):
        screenshots_dir = os.path.join(TMP_IMG_DIR, "iOS")
        times_list = os.listdir(screenshots_dir)

        # counter 表示有多少个计算阶段
        counter = len(SORTED_STAGE) - len(EXCLUDED_LIST)
        num = 0
        for t in times_list:
            if t.startswith("."):
                continue
            else:
                # dt 中的 value 中用于设定 progress bar 中的 maximum 值
                pic_dir = os.path.join(screenshots_dir, t)
                pic_amount = int(os.popen("ls -l %s | wc -l " % pic_dir).read())
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
        MainWindow.setWindowTitle(_translate("MainWindow", "App 启动时长测量工具"))
        self.start_minicap_button.setText(_translate("MainWindow", "启动 iOS-minicap"))
        self.start_screenshot_button.setText(_translate("MainWindow", "开始截图"))
        self.stop_screenshot_button.setText(_translate("MainWindow", "结束截图"))
        self.cal_button.setText(_translate("MainWindow", "计算时间"))
        self.training_button.setText(_translate("MainWindow", "一键训练"))
        self.platform_label_text.setText(_translate("MainWindow", "系统版本："))
        self.app_name_label_text.setText(_translate("MainWindow", "被测 APP 版本:"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.actionAdd_model_file.setText(_translate("MainWindow", "添加模型文件"))
        self.actionSet_training_pictures.setText(_translate("MainWindow", "设置训练图片"))

    def _start_minicap(self):
        cwd = os.getcwd()
        os.chdir("ios-minicap")
        os.system("./run.sh &")
        os.chdir(cwd)
        time.sleep(5)

    def _start_screenshot_process(self):
        # todo 点完开始截图要等待一会，再让用户点 APP，加一个 progress bar，倒数 5s 达到等待的效果
        self.minicap = MinicapStream(port=QueueManager.MINICAP_PORT)
        self.minicap.run()
        self.shared_queue.put(self.times)
        self.textBrowser.append("第 %d 次截图开始" % self.times)
        self.textBrowser.append("请等待 5 s，再点击 app 截图")

        self.times += 1

    def _stop_screenshot_process(self):
        '''
        停止截图，只是不从连接的套接字上接受数据
        :return:
        '''
        self.shared_queue.put(-1)
        self.textBrowser.append("截图停止")

    # @staticmethod
    # def _get_time_stamp(pic):
    #     time_stamp = os.path.getctime(pic)
    #     return time_stamp

    def _dispatch_cal_task(self):
        screenshots_dir = os.path.join(TMP_IMG_DIR, "iOS")
        ls = os.listdir(screenshots_dir)
        times_list = [ name for name in ls if not name.startswith(".") ]
        times_list.sort()
        i = 0
        flag_1 = False
        flag_2 = False
        length = len(self.search_price_dt)
        progress_bar_index_ls = list(self.search_price_dt.keys())
        aver_launch_time = 0
        aver_home_page_loading_time = 0
        count = 0

        while i < length:
            if not flag_1:
                pictures_dir_1 = os.path.join(screenshots_dir, times_list[i])
                task_process_1 = Process(target=self._cal_time, args=(pictures_dir_1, progress_bar_index_ls[i]))
                task_process_1.start()
                self.shared_task_status_dt.setdefault(task_process_1.pid, False)
                flag_1 = True
                i += 1

            if not flag_2 and i < length:
                pictures_dir_2 = os.path.join(screenshots_dir, times_list[i])
                task_process_2 = Process(target=self._cal_time, args=(pictures_dir_2, progress_bar_index_ls[i]))
                task_process_2.start()
                self.shared_task_status_dt.setdefault(task_process_2.pid, False)
                flag_2 = True
                i += 1

            if not task_process_1.is_alive():
                flag_1 = False

            if not task_process_2.is_alive():
                flag_2 = False

        while True:
            is_all_finished = True
            for status in self.shared_task_status_dt.values():
                is_all_finished = is_all_finished and status
            if is_all_finished:
                break

        while True:
            try:
                launch_time, loading_time = self.shared_answer_queue.get_nowait()
                aver_launch_time += launch_time
                aver_home_page_loading_time += loading_time
                count += 1
            except queue.Empty:
                break

        if self.cal_progress_dialog:
            self.cal_progress_dialog.close()

        msg = {}
        str_aver = "平均启动时长：%.3f  平均加载时长: %.3f" %(aver_launch_time / count if count != 0 else 0, aver_home_page_loading_time / count if count != 0 else 0)
        msg[JSON_TEXT_BROWSER_KEY] = str_aver
        msg[JSON_PID_KEY] = os.getpid()
        self.shared_ui_msg_queue.put(json.dumps(msg))
        print(str_aver)

    def _update_cal_status(self, content):
        self.textBrowser.append(content)

    def _cal_time(self, pic_dir, times_counter):
        pic_list = os.listdir(pic_dir)
        # thread_signal = self.qt_signal.dt_signal[times_counter]
        # length = len(pic_list)
        ct = CalTime(main_window=self, times_counter=times_counter)
        return ct.cal_time(pic_dir, EXCLUDED_LIST)

    def update_progress_bar(self, progress_bar_id, value):
        self.cal_progress_dialog.ui.progress_bar_dt[progress_bar_id].setValue(value)

    def update_text_browser(self, text):
        self.textBrowser.append(text)

    def _start_training(self, image_path):
        if self.DEBUG:
            output_graph = os.path.join(ABOUT_TRAINING, TEST_APP, "debug", "model", IOS_MODEL_NAME)
            output_labels = os.path.join(ABOUT_TRAINING, TEST_APP, "debug", "labels", IOS_LABEL_NAME)

            if not os.path.exists(output_graph):
                os.makedirs(os.path.dirname(output_graph))

            if not os.path.exists(output_labels):
                os.makedirs(os.path.dirname(output_labels))
        else:
            output_graph = os.path.join(ABOUT_TRAINING, TEST_APP, "model", IOS_MODEL_NAME)
            output_labels = os.path.join(ABOUT_TRAINING, TEST_APP, "labels", IOS_LABEL_NAME)

            if not os.path.exists(output_graph):
                os.makedirs(os.path.dirname(output_graph))

            if not os.path.exists(output_labels):
                os.makedirs(os.path.dirname(output_labels))

        process_training = Process(target=training.start_training, args=(image_path, output_graph, output_labels))
        process_training.start()
        # self._startup_progress_dialog("训练模型中", 420, False, self.TRAINING_CLOCK)


    def _checkout_ios_minicap(self):
        status, pid = Ui_MainWindow.query_service(QueueManager.MINICAP_PORT)
        if not status:
            if pid != -1:
                os.system("kill %s" % pid)
            proc_start_minicap = Process(target=self._start_minicap)
            proc_start_minicap.daemon = True
            proc_start_minicap.start()

    def on_click_minicap_button(self):
        # 首先查询 ios-minicap 的状态，如果状态不是 listen，则重新启动
        self._checkout_ios_minicap()
        self.textBrowser.append("正在启动 ios-minicap，请等待 5 s，再开始操作")
        # 添加一个 dialog，倒数 5s,倒数 5s 后，显示启动成功
        self._startup_progress_dialog("Waiting for ios-minicap", 5, True, self.CLOCK)
        self.start_screenshot_button.setEnabled(True)
        self.stop_screenshot_button.setEnabled(True)

    def on_click_start_screenshot_button(self):
        '''
        启动截图进程
        :return:
        '''
        # 每点击一次启动截图，就代表新的一轮截图，即：在capture/tmp_pic/iOS/ 下，再次新建一个文件夹，点击开始计算，就开始将所有截图进行计算，根据新建的文件夹个数反馈进度，显示在进度条上，最后给出一个总体结果到 text browser 上
        # 当点击一次启动截图后，就将启动截图按钮禁用，直到停止截图按钮被按下
        # 首先查询 ios-minicap 的状态，如果状态不是 listen，则重新启动
        self._checkout_ios_minicap()
        self._start_screenshot_process()
        self._startup_progress_dialog("Waiting for ios-minicap", 5, True, self.CLOCK)
        self.start_screenshot_button.setEnabled(False)

    def on_click_stop_screenshot_button(self):
        '''
        停止截图
        :return:
        '''
        self._stop_screenshot_process()
        self.start_screenshot_button.setEnabled(True)

    def on_click_cal_button(self):
        self._setup_qt_signal()
        self.cal_progress_dialog.show()
        cal_process = Process(target=self._dispatch_cal_task)
        cal_process.start()

    def on_click_training_button(self):
        # todo 弹出一个对话框，让用户选择训练图片文件夹，pb 和 label 文件不用指定路径，存放在默认路径
        # 选择完 image 文件夹后，调用 _start_training, self.training_pic_dir 初始化为默认路径
        if self.remind_user:
            self.message_box.exec()
            self.remind_user = False if self.check_box.isChecked() else True
            self._setup_file_dialog("Open image dir", True, os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50"))
            if self.fileDialog.exec():
                self.training_pic_dir = self.fileDialog.selectedFiles()[0]
                print(self.training_pic_dir)
                self.fileDialog.setDirectory(self.training_pic_dir)
        self._start_training(self.training_pic_dir)

    def on_click_set_pic_action(self):
        self._setup_file_dialog("打开一组训练图片文件夹的父文件夹", True, os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50"))
        self.fileDialog.exec()
        self.training_pic_dir = self.fileDialog.selectedFiles()[0]
        self.fileDialog.setDirectory(self.training_pic_dir)

    def on_click_set_model_action(self):
        self._setup_file_dialog("选择一个 模型(.pb)文件", True, os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50"))
        self.fileDialog.exec()
        self.model_path = self.fileDialog.selectedFiles()[0]
        self.fileDialog.setDirectory(self.training_pic_dir)

    def _setup_msg_box(self):
        self.message_box = QtWidgets.QMessageBox()
        self.message_box.setText("在训练之前，请先选择带有标签的图片文件夹的父文件夹")
        self.message_box.setInformativeText("不再提醒我")
        self.check_box = QtWidgets.QCheckBox()
        self.message_box.setCheckBox(self.check_box)

    def _setup_file_dialog(self, title, is_modal, default_dir):
        # self.fileDialog = QFileDialog(parent=None, caption="Open image dir")
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
        para_clock.start(max_num * 1000)

    def _training_count_down(self):
        self.progressDialog.setValue(self.i + 1)
        self.progressDialog.setLabelText("训练进度： %d/420" % self.i)
        self.i += 1
        if self.i >= 420:
            self.TRAINING_CLOCK.stop()
            self.i = 0

    def _count_down(self):
        self.progressDialog.setValue(self.i + 1)
        self.progressDialog.setLabelText("Waiting for ios-minicap: %d%%" % (self.percent))
        self.percent += 20
        self.i += 1
        if self.i == 5:
            self.CLOCK.stop()
            self.i = 0
            self.percent = 20

    @staticmethod
    def query_service(port):
        fobj = os.popen("lsof -i tcp:%d" % port)
        state = fobj.read().strip()
        if len(state) == 0:
            return False, -1
        ls = state.split("\n")

        status_list = ls[-1].split()
        status = status_list[-1]
        pid = status_list[1]
        return status == "(LISTEN)", pid
