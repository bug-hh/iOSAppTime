# -*- coding: utf-8 -*-
import PyQt5.QtWidgets

import sys

from PyQt5 import QtWidgets

from Ui_ProgressDialog import Ui_ProgressDialog

class CalProgressDialog(QtWidgets.QMainWindow):
    def __init__(self, task_dt):
        super(CalProgressDialog, self).__init__()
        self.ui = Ui_ProgressDialog()
        self.ui.setupUi(self, task_dt)

def main():
    app = QtWidgets.QApplication([])
    application = CalProgressDialog()
    application.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
