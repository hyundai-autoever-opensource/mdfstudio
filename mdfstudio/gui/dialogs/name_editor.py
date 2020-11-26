# -*- coding: utf-8 -*-
# Copyright 2020.Hyundai Autoever.All rights reserved. License under the GNU LESSER GENERAL PUBLIC LICENSE Version 3
from PyQt5 import QtWidgets, QtCore, QtGui
import os
import json
from pathlib import Path

from ..ui.name_editor_dialog import Ui_NameEditorDialog


class NameEditor(Ui_NameEditorDialog, QtWidgets.QDialog):
    list_changed_signal = QtCore.pyqtSignal(list)

    def __init__(self, title, udc_list, basket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.title = title
        self.udc_list = udc_list
        self.basket = basket
        self.is_edit_mode = False

        self.environ_path = os.environ['APPDATA']

        if self.title is not None:
            self.is_edit_mode = True
            self.title_box.setText(self.title)
        self.setModal(True)
        self.table.setRowCount(len(self.basket))
        for i in range(len(self.basket)):
            item = QtWidgets.QTableWidgetItem(self.basket[i])
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table.setItem(i, 0, item)

        self.save_btn.clicked.connect(self.save_name_list)
        self.reset_btn.clicked.connect(self.reset)
        self.cancel_btn.clicked.connect(self.cancel)

        if self.is_edit_mode:
            self.load_name_list()

    def load_name_list(self):
        file_name = "\\" + self.title + ".udc"
        file_name = Path(self.environ_path + file_name)

        if os.path.isfile(file_name):
            with open(file_name, "r") as infile:
                info = json.load(infile)

            items = info.get("user-defined names", [])

            for row in range(self.table.rowCount()):
                for item in items:
                    if item.split("|")[0] == self.table.item(row, 0).text():
                        user_defined_name = QtWidgets.QTableWidgetItem(item.split("|")[1])
                        remark = QtWidgets.QTableWidgetItem(item.split("|")[2])
                        self.table.setItem(row, 1, user_defined_name)
                        self.table.setItem(row, 2, remark)
                        break
        else:
            QtWidgets.QMessageBox.warning(None, "Warning",
                                          "Cannot load '" + self.title + "'. '" + self.title + "' will be deleted from the list.")
            return

    def save_name_list(self):
        new_title = self.title_box.text()
        if new_title is None:
            QtWidgets.QMessageBox.warning(None, "Warning",
                                          "Enter Title of User-defined name list")
            return
        if new_title in self.udc_list:
            reply = QtWidgets.QMessageBox.question(None, "Warning",
                                          "The title '"+ new_title +"' already exists. Do you want to replace it?")
            if reply == QtWidgets.QMessageBox.No:
                return
        else:
            self.udc_list.append(new_title)

        name_list = []
        for row in range(self.table.rowCount()):
            channel_name = self.table.item(row, 0).text()
            if self.table.item(row, 1) is None:
                user_defined_name = ""
            else:
                user_defined_name = self.table.item(row, 1).text()
            if self.table.item(row, 2) is None:
                remark = ""
            else:
                remark = self.table.item(row, 2).text()
            name_list.append(channel_name + "|" + user_defined_name + "|" + remark)

        config = {}
        config["user-defined names"] = name_list

        file_name = "\\"+ new_title +".udc"
        file_name = Path(self.environ_path + file_name)

        if file_name:
            Path(file_name).write_text(
                json.dumps(config, indent=4, sort_keys=True)
            )

        file_name = "\\UserDefinedChannel.List"
        file_name = Path(self.environ_path + file_name)

        config = {}
        config["user-defined name list"] = self.udc_list
        if file_name:
            Path(file_name).write_text(
                json.dumps(config, indent=4, sort_keys=True)
            )
        self.list_changed_signal.emit(self.udc_list)
        self.close()

    def reset(self):
        reply = QtWidgets.QMessageBox.question(None, "Warning",
                                               "Do you want to reset all?")
        if reply == QtWidgets.QMessageBox.Yes:
            self.title_box.clear()
            for row in range(self.table.rowCount()):
                item = QtWidgets.QTableWidgetItem()
                self.table.setItem(row, 1, item)
                self.table.setItem(row, 2, item)

    def cancel(self):
        self.close()