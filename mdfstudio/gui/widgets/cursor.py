# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
    *   Cursor.__init__ -   Change cursor label color based on plot background color

"""

import pyqtgraph as pg
from PyQt5 import QtGui, QtCore


class Cursor(pg.InfiniteLine):
    def __init__(self, *args, **kwargs):

        super().__init__(
            *args, label="{value:.6f}s", labelOpts={"position": 0.04}, **kwargs
        )

        self.addMarker("^", 0)
        self.addMarker("v", 1)

        self._settings = QtCore.QSettings()
        if self._settings.value("plot_background") == "White":
            self.label.setColor(QtGui.QColor(0, 59, 126))
        else:
            self.label.setColor(QtGui.QColor("#ffffff"))

        self.label.show()

    def set_value(self, value):
        self.setPos(value)
