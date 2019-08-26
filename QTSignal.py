#!/usr/bin/env python
# coding: utf-8

from PyQt5.QtCore import pyqtSignal, QObject

class QTSignal(QObject):

    for i in range(21):
        cmd = "signal_%d = pyqtSignal(int, int)" % i
        exec(cmd)

    def __init__(self):
        super(QTSignal, self).__init__()
        self.dt_signal = {}
        i = 0
        for k in QTSignal.__dict__:
            if str(k).startswith("signal"):
                cmd = "self.%s.connect(self.slot_placeholder)" % k
                exec(cmd)
                cmd = "self.dt_signal[%d] = self.%s" % (i, k)  # 用数字映射 pyqtSignal 对象
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
        print(k, s.dt_signal[k])
