# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progressdialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog, task_dt):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(383, 377)
        self.verticalLayoutWidget = QtWidgets.QWidget(ProgressDialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 371, 361))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.progress_bar_dt = {}

        for k in task_dt:
            progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
            progressBar.setProperty("value", 0)
            progressBar.setObjectName("progressBar")
            self.progress_bar_dt[k] = progressBar   # 每个 capture/tmp_pic/iOS 文件夹对应一个进度条
            self.progress_bar_dt[k].setMaximum(task_dt[k])
            self.verticalLayout.addWidget(progressBar)

        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "计算进度"))
