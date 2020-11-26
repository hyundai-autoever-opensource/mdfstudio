# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
    *   init        -   Change UI (new button image, new palette, hide match_kind)
                        Filter channels started with "$"
                        Remove port information in channel name
    *   _add_window -   Remove
    *   _add_basket -   Return result to custom basket list (Modify _add_window)
    *   search_text_changed -   Match text by comparision not using regx pattern

"""
import re

from natsort import natsorted
from PyQt5 import QtWidgets, QtGui, QtCore

from ..ui.search_dialog import Ui_SearchDialog


class AdvancedSearch(Ui_SearchDialog, QtWidgets.QDialog):
    def __init__(
        self, channels_db, return_names=False, show_add_window=False, *args, **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/search3.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.setWindowIcon(icon)

        palette = QtGui.QPalette()
        br_light_sand = QtGui.QBrush(QtGui.QColor(246, 243, 242))
        br_blue = QtGui.QBrush(QtGui.QColor(0, 44, 95))
        br_sky_blue = QtGui.QBrush(QtGui.QColor(225, 239, 255))
        br_sand = QtGui.QBrush(QtGui.QColor(228, 220, 211))
        br_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        br_black = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        br_gray = QtGui.QBrush(QtGui.QColor(221, 221, 221))
        br_light_sand.setStyle(QtCore.Qt.SolidPattern)
        br_blue.setStyle(QtCore.Qt.SolidPattern)
        br_sand.setStyle(QtCore.Qt.SolidPattern)

        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, br_gray)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, br_gray)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_white)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_white)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, br_blue)

        self.setPalette(palette)

        self.result = set()
        self.to_basket = False
        self.add_window_request = False
        self.channels_db = {}

        port = False
        for channel in channels_db:
            if '\\' in channel:
                port = True
                break

        if port:
            for channel in channels_db:
                if '\\' in channel and channel[0] != "$":
                    self.channels_db[channel]=(tuple(channels_db[channel]))
        else:
            for channel in channels_db:
                if channel[0] != "$":
                    self.channels_db[channel]=(tuple(channels_db[channel]))

        self.apply_btn.clicked.connect(self._apply)
        self.add_btn.clicked.connect(self._add)
        #yda *UDC*
        # self.add_basket_btn.clicked.connect(self._add_basket)
        self.add_basket_btn.hide()
        self.cancel_btn.clicked.connect(self._cancel)

        self.search_box.editingFinished.connect(self.search_text_changed)
        self.match_kind.currentTextChanged.connect(self.search_box.textChanged.emit)

        self.search_text_changed()
        self.match_kind.hide()

        self._return_names = return_names

        # if not show_add_window:
        #     self.add_window_btn.hide()

        self.setWindowTitle("Search & select channels")

    def search_text_changed(self):
        text = self.search_box.text().strip()
        if len(text) >= 0:
            if self.match_kind.currentText() == "Wildcard":
                pattern = text.lower()

            try:
                matches = [name for name in self.channels_db if pattern in name.lower()]
                self.matches.clear()
                self.matches.addItems(matches)
                if matches:
                    self.status.setText("")
                else:
                    self.status.setText("No match found")
            except Exception as err:
                self.status.setText(str(err))
                self.matches.clear()

    def _add(self, event):
        count = self.selection.count()
        names = set(self.selection.item(i).text() for i in range(count))

        to_add = set(item.text() for item in self.matches.selectedItems())

        names = natsorted(names | to_add)

        self.selection.clear()
        self.selection.addItems(names)

    def _apply(self, event):
        count = self.selection.count()

        if self._return_names:
            self.result = set(self.selection.item(i).text() for i in range(count))
        else:
            self.result = set()
            for i in range(count):
                for entry in self.channels_db[self.selection.item(i).text()]:
                    self.result.add(entry)
        self.to_basket = False
        self.close()

    def _add_basket(self, event):
        count = self.selection.count()

        if self._return_names:
            self.result = set(self.selection.item(i).text() for i in range(count))
        else:
            self.result = set()
            for i in range(count):
                for entry in self.channels_db[self.selection.item(i).text()]:
                    self.result.add(entry)
        self.to_basket = True
        self.close()

    def _cancel(self, event):
        self.result = set()
        self.close()
