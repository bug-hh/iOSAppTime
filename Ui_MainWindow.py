# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iOSAppTime.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QFileDialog

from multiprocessing import Process
from threading import Thread

from queue import Queue

from ios_minicap.minicap import MinicapStream
from queue_manager import QueueManager

from config import TMP_IMG_DIR
from config import STAGE
from config import IOS_PERCENT
from config import ABOUT_TRAINING
from config import IOS_MODEL_NAME
from config import IOS_LABEL_NAME
from config import TEST_APP
from config import RETRAIN_PATH
from config import SORTED_STAGE
from config import EXCLUDED_LIST

from CalProgressDialog import CalProgressDialog
from google_algorithm.label_image import identify_pic
from QTSignal import QTSignal
from cal_time import CalTime

import os
import time
import queue
import subprocess
import threading
import math

class Ui_MainWindow(QtCore.QObject):
    def setupUi(self, MainWindow):
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
        self.actionSet_ipa_file_path = QtWidgets.QAction(MainWindow)
        self.actionSet_ipa_file_path.setObjectName("actionSet_ipa_file_path")
        self.actionAdd_model_file = QtWidgets.QAction(MainWindow)
        self.actionAdd_model_file.setObjectName("actionAdd_model_file")
        self.actionSet_training_pictures = QtWidgets.QAction(MainWindow)
        self.actionSet_training_pictures.setObjectName("actionSet_training_pictures")
        self.menu.addAction(self.actionSet_ipa_file_path)
        self.menu.addSeparator()
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

        self.CLOCK = QTimer()
        self.CLOCK.setInterval(1000)
        self.CLOCK.timeout.connect(self._count_down)

        self.i = 0
        self.percent = 20

        self.queue = Queue()
        QueueManager.register('get_queue', callable=lambda : self.queue)

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.start()
        self.shared_queue = self.manager.get_queue()

        self.start_screenshot_button.setEnabled(True)
        self.stop_screenshot_button.setEnabled(False)

        self.times = 1

        self.result_queue = Queue()

        self.fileDialog = None

    def _setup_qt_signal(self):
        screenshots_dir = os.path.join(TMP_IMG_DIR, "iOS")
        times_list = os.listdir(screenshots_dir)
        # counter 表示有多少个计算阶段
        counter = len(SORTED_STAGE) - len(EXCLUDED_LIST)
        dt = {}
        for t in times_list:
            if t.startswith("."):
                continue
            else:
                # dt 中的 value 中用于设定 progress bar 中的 maximum 值
                pic_dir = os.path.join(screenshots_dir, t)
                pic_amount = int(os.popen("ls -l %s | wc -l " % pic_dir).read())
                search_price = int(math.log(pic_amount, 2)) + 1
                search_price *= counter
                adjustment_price = 100 * counter
                search_price += adjustment_price
                dt[int(t)] = search_price

        self.cal_progress_dialog = CalProgressDialog(dt)
        self.qt_signal = QTSignal()
        for k in self.cal_progress_dialog.ui.progress_bar_dt:
            self.qt_signal.dt_signal[k].connect(self.update_progress_bar)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.start_minicap_button.setText(_translate("MainWindow", "启动 iOS-minicap"))
        self.start_screenshot_button.setText(_translate("MainWindow", "开始截图"))
        self.stop_screenshot_button.setText(_translate("MainWindow", "结束截图"))
        self.cal_button.setText(_translate("MainWindow", "计算时间"))
        self.training_button.setText(_translate("MainWindow", "一键训练"))
        self.platform_label_text.setText(_translate("MainWindow", "系统版本："))
        self.app_name_label_text.setText(_translate("MainWindow", "被测 APP 版本:"))
        self.menu.setTitle(_translate("MainWindow", "File"))
        self.actionSet_ipa_file_path.setText(_translate("MainWindow", "Set ipa file path"))
        self.actionAdd_model_file.setText(_translate("MainWindow", "Add model file"))
        self.actionSet_training_pictures.setText(_translate("MainWindow", "Set training pictures"))


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

        self.times += 1

    def _stop_screenshot_process(self):
        '''
        停止截图，只是不从连接的套接字上接受数据
        :return:
        '''
        self.shared_queue.put(-1)
        self.textBrowser.append("截图停止")

    @staticmethod
    def _get_time_stamp(pic):
        time_stamp = os.path.getctime(pic)
        return time_stamp

    def _dispatch_cal_task(self):
        screenshots_dir = os.path.join(TMP_IMG_DIR, "iOS")
        times_list = os.listdir(screenshots_dir)
        thread_list = []
        for t in times_list:
            if t.startswith("."):
                continue
            pictures_dir = os.path.join(screenshots_dir, t)
            task_thread = Thread(target=self._cal_time, args=(pictures_dir, int(t)))
            task_thread.start()
            thread_list.append(task_thread)

        for task in thread_list:
            task.join()

        aver_launch_time = 0
        aver_home_page_loading_time = 0
        count = 0
        try:
            while True:
                launch_time, loading_time = self.result_queue.get()
                aver_launch_time += launch_time
                aver_home_page_loading_time += loading_time
                count += 1
        except queue.Empty:
            pass

        aver_launch_time = aver_launch_time / count if count > 0 else 0
        aver_home_page_loading_time = aver_home_page_loading_time / count if count > 0 else 0
        str_aver = "平均启动时长：%.3f  平均加载时长: %.3f" %(aver_launch_time, aver_home_page_loading_time)
        self.textBrowser.append(str_aver)
        print(str_aver)

    def _update_cal_status(self, content):
        self.textBrowser.append(content)

    def _cal_time(self, pic_dir, times_counter):
        pic_list = os.listdir(pic_dir)
        thread_signal = self.qt_signal.dt_signal[times_counter]
        length = len(pic_list)
        ct = CalTime(main_window=self, thread_signal=thread_signal, times_counter=times_counter)
        ct.cal_time(pic_dir, EXCLUDED_LIST)


    def update_progress_bar(self, progress_bar_id, value):
        self.cal_progress_dialog.ui.progress_bar_dt[progress_bar_id].setValue(value)

    def _get_training_status(self):
        while True:
            try:
                outs, errs = self.proc_training.communicate(timeout=6)
                self.textBrowser.append(outs)
                self.textBrowser.append(errs)
                if self.proc_training.poll is not None:
                    return
            except subprocess.TimeoutExpired:
                pass


    def _start_training(self, image_path):
        output_graph = os.path.join(ABOUT_TRAINING, TEST_APP, "model", IOS_MODEL_NAME)
        output_labels = os.path.join(ABOUT_TRAINING, TEST_APP, "labels", IOS_LABEL_NAME)

        cmd = '''python3 --image_dir %s --output_graph %s --output_labels %s %s''' % (image_path, output_graph, output_labels, RETRAIN_PATH)
        self.proc_training = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc_training_status = Process(target=self._get_training_status)
        proc_training_status.start()

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
        # 添加一个 dialog，倒数 5s,倒数 5s 后，显示启动成功
        self._startup_progress_dialog()
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
        self._startup_progress_dialog()
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
        cal_process = Thread(target=self._dispatch_cal_task)
        cal_process.start()

    def on_click_training_button(self):
        # todo 弹出一个对话框，让用户选择训练图片文件夹，pb 和 label 文件不用指定路径，存放在默认路径
        # 选择完 image 文件夹后，调用 _start_training
        if not self.fileDialog:
            self._setup_file_dialog()

        if self.fileDialog.exec():
            image_path = self.fileDialog.selectedFiles()[0]
            self.fileDialog.setDirectory(image_path)
            self._start_training(image_path)

    def _setup_file_dialog(self):
        self.fileDialog = QFileDialog(parent=None, caption="Open image dir")
        self.fileDialog.setModal(True)
        self.fileDialog.setFileMode(QFileDialog.DirectoryOnly)
        self.fileDialog.setViewMode(QFileDialog.List)
        default_image_dir = os.path.join(ABOUT_TRAINING, TEST_APP, "iOS_1-50")
        self.fileDialog.setDirectory(default_image_dir)

    def _startup_progress_dialog(self):
        self.progressDialog = QProgressDialog("Waiting for ios-minicap", "cancel", 0, 5)
        self.progressDialog.setFixedWidth(500)
        self.progressDialog.setAutoClose(True)
        self.progressDialog.setModal(True)
        self.CLOCK.start(5000)

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
