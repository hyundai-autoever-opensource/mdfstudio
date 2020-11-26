# -*- coding: utf-8 -*-
# Copyright 2020.Hyundai Autoever.All rights reserved. License under the GNU LESSER GENERAL PUBLIC LICENSE Version 3
from PyQt5 import QtWidgets, QtCore, QtGui
from functools import partial
import os
import json
from pathlib import Path

from ..ui.name_info_dialog import Ui_NameInfoDialog
from ..dialogs.name_editor import NameEditor


class NameInfo(Ui_NameInfoDialog, QtWidgets.QDialog):
    apply_alternative_names_signal = QtCore.pyqtSignal(dict)

    def __init__(self, basket, udc_list, loaded_udc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.basket = basket

        self.environ_path = os.environ['APPDATA']
        self.udc_list = udc_list
        self.loaded_udc = loaded_udc

        self.setModal(True)
        self.edit_btn.setEnabled(False)

        self.new_btn.clicked.connect(partial(self.show_dialog, "new"))
        self.edit_btn.clicked.connect(partial(self.show_dialog, "edit"))
        self.delete_btn.clicked.connect(self.delete_list)
        self.close_btn.clicked.connect(self.close)
        self.apply_btn.clicked.connect(self.apply_names)
        self.reset_btn.clicked.connect(self.reset_names)

        self.update_list()

        # if self.loaded_udc is not None:
        #     self.apply_names()

    def show_dialog(self, mode):
        if len(self.basket) == 0:
            QtWidgets.QMessageBox.warning(None, "Warning", "An empty custom basket : Add channel(s) to custom basket.")
            return
        udc_title = None

        selected_item = self.user_channel_list.currentItem()

        if mode == "edit":
            if selected_item is None:
                QtWidgets.QMessageBox.warning(None, "Warning", "Select an item to edit. Nothing selected.")
                return
            udc_title = selected_item.text()

            file_name = "\\" + udc_title + ".udc"
            file_name = Path(self.environ_path + file_name)

            if not os.path.isfile(file_name):
                QtWidgets.QMessageBox.warning(None, "Warning",
                                              "Cannot load '" + udc_title + "'. '" + udc_title + "' will be deleted from the list.")
                self.delete_list(udc_title)
                return

        dialog = NameEditor(udc_title, self.udc_list, self.basket)
        dialog.list_changed_signal.connect(self.update_list)
        dialog.exec_()

    def delete_btn_clicked(self):
        selected_item = self.user_channel_list.currentItem()
        if selected_item is None:
            QtWidgets.QMessageBox.warning(None, "Warning", "Select an item to delete. Nothing selected.")
            return
        reply = QtWidgets.QMessageBox.question(None, "Warning",
                                               "'" + selected_item.text() + "' will be deleted. Continue?")
        if reply == QtWidgets.QMessageBox.No:
            return
        self.delete_list(selected_item.text())

    def delete_list(self, title):
        file_name = "\\" + title + ".udc"
        file_name = Path(self.environ_path + file_name)

        if os.path.isfile(file_name):
            os.remove(file_name)

        file_name = "\\UserDefinedChannel.List"
        file_name = Path(self.environ_path + file_name)

        self.udc_list.remove(title)

        config = {}
        config["user-defined name list"] = self.udc_list
        if file_name:
            Path(file_name).write_text(
                json.dumps(config, indent=4, sort_keys=True)
            )
        self.update_list()

    def reset_names(self):
        self.apply_alternative_names_signal.emit({})
        self.close()

    def apply_names(self):
        selected_item = self.user_channel_list.currentItem()

        if selected_item is None:
            QtWidgets.QMessageBox.warning(None, "Warning", "Select an item to edit. Nothing selected.")
            return
        udc_title = selected_item.text()

        file_name = "\\" + udc_title + ".udc"
        file_name = Path(self.environ_path + file_name)

        if not os.path.isfile(file_name):
            QtWidgets.QMessageBox.warning(None, "Warning",
                                          "Cannot load '" + udc_title + "'. '" + udc_title + "' will be deleted from the list.")
            self.delete_list(udc_title)
            return

        with open(file_name, "r") as infile:
            info = json.load(infile)
        items = info.get("user-defined names", [])

        udc_dict = {}
        udc_dict["udc_filename"] = udc_title
        for channel in self.basket:
            for item in items:
                if item.split("|")[0] == channel:
                    udc_dict[channel] = item.split("|")[1]
                    break
        self.apply_alternative_names_signal.emit(udc_dict)
        self.close()

    def save_user_channel(self):
        udc_list = []
        for row in range(self.user_channel_list.count()):
            udc_list.append(self.user_channel_list.item(row).text())

        config = {}
        config["info"] = udc_list

        file_name = "\\UserDefinedChannel.List"
        file_name = Path(self.environ_path + file_name)

        if file_name:
            Path(file_name).write_text(
                json.dumps(config, indent=4, sort_keys=True)
            )

    def update_list(self, udc_list=None):
        if udc_list:
            self.udc_list = udc_list
        view = self.user_channel_list
        view.clear()

        if len(self.udc_list) > 0:
            i = 0
            for item in self.udc_list:
                view.addItem(item)
                if item == self.loaded_udc:
                    view.item(i).setBackground(QtGui.QBrush(QtGui.QColor("#e2e2e2")))
                i += 1
            self.edit_btn.setEnabled(True)
        else:
            self.edit_btn.setEnabled(False)