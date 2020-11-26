# -*- coding: utf-8 -*-
# Copyright 2020.Hyundai Autoever.All rights reserved. License under the GNU LESSER GENERAL PUBLIC LICENSE Version 3
""" Create history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Dialog for user-defined-name information
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NameInfoDialog(object):
    def setupUi(self, NameInfoDialog):
        NameInfoDialog.setObjectName("NameInfoDialog")
        NameInfoDialog.resize(376, 291)
        NameInfoDialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(NameInfoDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(NameInfoDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.user_channel_list = QtWidgets.QListWidget(NameInfoDialog)
        self.user_channel_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.user_channel_list.setObjectName("user_channel_list")
        self.gridLayout.addWidget(self.user_channel_list, 1, 0, 7, 1)
        self.new_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.new_btn.setObjectName("new_btn")
        self.gridLayout.addWidget(self.new_btn, 1, 1, 1, 1)
        self.edit_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.edit_btn.setObjectName("edit_btn")
        self.gridLayout.addWidget(self.edit_btn, 2, 1, 1, 1)
        self.delete_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.delete_btn.setObjectName("delete_btn")
        self.gridLayout.addWidget(self.delete_btn, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 102, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.apply_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.apply_btn.setObjectName("apply_btn")
        self.gridLayout.addWidget(self.apply_btn, 5, 1, 1, 1)
        self.reset_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.reset_btn.setObjectName("reset_btn")
        self.gridLayout.addWidget(self.reset_btn, 6, 1, 1, 1)
        self.close_btn = QtWidgets.QPushButton(NameInfoDialog)
        self.close_btn.setObjectName("close_btn")
        self.gridLayout.addWidget(self.close_btn, 7, 1, 1, 1)

        self.retranslateUi(NameInfoDialog)
        QtCore.QMetaObject.connectSlotsByName(NameInfoDialog)

    def retranslateUi(self, NameInfoDialog):
        _translate = QtCore.QCoreApplication.translate
        NameInfoDialog.setWindowTitle(_translate("NameInfoDialog", "Show User-defined Channel List"))
        self.label.setText(_translate("NameInfoDialog", "User-defined (alternative) channel name list"))
        self.new_btn.setText(_translate("NameInfoDialog", "New"))
        self.edit_btn.setText(_translate("NameInfoDialog", "Edit"))
        self.delete_btn.setText(_translate("NameInfoDialog", "Delete"))
        self.apply_btn.setText(_translate("NameInfoDialog", "Apply"))
        self.reset_btn.setText(_translate("NameInfoDialog", "Reset"))
        self.close_btn.setText(_translate("NameInfoDialog", "Close"))
