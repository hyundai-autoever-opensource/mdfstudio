# -*- coding: utf-8 -*-
# Copyright 2020.Hyundai Autoever.All rights reserved. License under the GNU LESSER GENERAL PUBLIC LICENSE Version 3
""" Create history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Dialog for defining alternative channel names
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NameEditorDialog(object):
    def setupUi(self, NameEditorDialog):
        NameEditorDialog.setObjectName("NameEditorDialog")
        NameEditorDialog.resize(727, 379)
        NameEditorDialog.setSizeGripEnabled(True)
        NameEditorDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(NameEditorDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(NameEditorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.title_box = QtWidgets.QLineEdit(NameEditorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title_box.sizePolicy().hasHeightForWidth())
        self.title_box.setSizePolicy(sizePolicy)
        self.title_box.setText("")
        self.title_box.setObjectName("title_box")
        self.gridLayout.addWidget(self.title_box, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(373, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 2)
        self.table = QtWidgets.QTableWidget(NameEditorDialog)
        self.table.setRowCount(100)
        self.table.setColumnCount(3)
        self.table.setObjectName("table")
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.horizontalHeader().setMinimumSectionSize(50)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.table, 1, 0, 4, 3)
        self.reset_btn = QtWidgets.QPushButton(NameEditorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset_btn.sizePolicy().hasHeightForWidth())
        self.reset_btn.setSizePolicy(sizePolicy)
        self.reset_btn.setObjectName("reset_btn")
        self.gridLayout.addWidget(self.reset_btn, 1, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 271, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        self.save_btn = QtWidgets.QPushButton(NameEditorDialog)
        self.save_btn.setObjectName("save_btn")
        self.gridLayout.addWidget(self.save_btn, 3, 3, 1, 1)
        self.cancel_btn = QtWidgets.QPushButton(NameEditorDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.gridLayout.addWidget(self.cancel_btn, 4, 3, 1, 1)

        self.retranslateUi(NameEditorDialog)
        QtCore.QMetaObject.connectSlotsByName(NameEditorDialog)
        NameEditorDialog.setTabOrder(self.table, self.save_btn)
        NameEditorDialog.setTabOrder(self.save_btn, self.reset_btn)
        NameEditorDialog.setTabOrder(self.reset_btn, self.cancel_btn)

    def retranslateUi(self, NameEditorDialog):
        _translate = QtCore.QCoreApplication.translate
        NameEditorDialog.setWindowTitle(_translate("NameEditorDialog", "Define alternative channel names"))
        self.label.setText(_translate("NameEditorDialog", "Title of User-defined name list"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("NameEditorDialog", "Channel Name"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("NameEditorDialog", "User Defined Name"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("NameEditorDialog", "Remarks"))
        self.reset_btn.setText(_translate("NameEditorDialog", "Reset"))
        self.save_btn.setText(_translate("NameEditorDialog", "Save"))
        self.cancel_btn.setText(_translate("NameEditorDialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    NameEditorDialog = QtWidgets.QDialog()
    ui = Ui_NameEditorDialog()
    ui.setupUi(NameEditorDialog)
    NameEditorDialog.show()
    sys.exit(app.exec_())
