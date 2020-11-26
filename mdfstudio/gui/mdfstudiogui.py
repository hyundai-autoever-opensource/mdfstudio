# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets

from mdfstudio.gui.utils import excepthook
from mdfstudio.gui.widgets.main import MainWindow

sys.excepthook = excepthook

def main():

    if len(sys.argv) > 1:
        args = sys.argv[1]
    else:
        args = None

    app = QtWidgets.QApplication(sys.argv)

    app.setOrganizationName("py-mdfstudio")
    app.setOrganizationDomain("py-mdfstudio")
    app.setApplicationName("py-mdfstudio")
    main = MainWindow(args)
    main.setMinimumHeight(768)
    main.setMinimumWidth(1280)

    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    app.exec_()


if __name__ == "__main__":
    main()
