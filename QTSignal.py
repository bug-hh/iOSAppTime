#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtCore import pyqtSignal, QObject

class QTSignal(QObject):

    signal_0 = pyqtSignal(int, int)
    signal_1 = pyqtSignal(int, int)
    signal_2 = pyqtSignal(int, int)
    signal_3 = pyqtSignal(int, int)
    signal_4 = pyqtSignal(int, int)
    signal_5 = pyqtSignal(int, int)
    signal_6 = pyqtSignal(int, int)
    signal_7 = pyqtSignal(int, int)
    signal_8 = pyqtSignal(int, int)
    signal_9 = pyqtSignal(int, int)

    def __init__(self):
        super(QTSignal, self).__init__()
        self.dt_signal = {}
        i = 0
        for k in QTSignal.__dict__:
            if str(k).startswith("signal"):
                cmd = "self.%s.connect(self.slot_placeholder)" % k
                exec(cmd)
                cmd = "self.dt_signal[%s] = self.%s" % (i, k)
                exec(cmd)
                i += 1

        # capture/tmp_pic/iOS/ 下的文件夹名只能是数字，且范围是 1 - 10
        for key in self.dt_signal:
            self.dt_signal[key].disconnect(self.slot_placeholder)


        # for k in dialog.ui.progress_bar_dt:
        #     self.dt_signal[k].connect(main_window.update_progress_bar)

    def slot_placeholder(self):
        pass

if __name__ == '__main__':
    s = QTSignal()
    for k in s.dt_signal:
        print(k, type(k))
