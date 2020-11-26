# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Change button names : Add window -> Add basket, Apply -> Add
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SearchDialog(object):
    def setupUi(self, SearchDialog):
        SearchDialog.setObjectName("SearchDialog")
        SearchDialog.resize(861, 607)
        SearchDialog.setSizeGripEnabled(True)
        self.grid_layout = QtWidgets.QGridLayout(SearchDialog)
        self.grid_layout.setContentsMargins(9, 9, 9, 9)
        self.grid_layout.setObjectName("grid_layout")
        self.match_kind = QtWidgets.QComboBox(SearchDialog)
        self.match_kind.setObjectName("match_kind")
        self.match_kind.addItem("")
        self.match_kind.addItem("")
        self.grid_layout.addWidget(self.match_kind, 0, 0, 1, 1)
        self.add_btn = QtWidgets.QPushButton(SearchDialog)
        self.add_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/right.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_btn.setIcon(icon)
        self.add_btn.setObjectName("add_btn")
        self.grid_layout.addWidget(self.add_btn, 5, 1, 1, 1)
        self.label = QtWidgets.QLabel(SearchDialog)
        self.label.setObjectName("label")
        self.grid_layout.addWidget(self.label, 1, 2, 1, 1)
        self.selection = MinimalListWidget(SearchDialog)
        self.selection.setObjectName("selection")
        self.grid_layout.addWidget(self.selection, 5, 2, 4, 4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancel_btn = QtWidgets.QPushButton(SearchDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout.addWidget(self.cancel_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.add_basket_btn = QtWidgets.QPushButton(SearchDialog)
        self.add_basket_btn.setObjectName("add_basket_btn")
        self.horizontalLayout.addWidget(self.add_basket_btn)
        self.apply_btn = QtWidgets.QPushButton(SearchDialog)
        self.apply_btn.setObjectName("apply_btn")
        self.horizontalLayout.addWidget(self.apply_btn)
        self.horizontalLayout.setStretch(1, 1)
        self.grid_layout.addLayout(self.horizontalLayout, 9, 0, 1, 6)
        self.status = QtWidgets.QLabel(SearchDialog)
        self.status.setText("")
        self.status.setObjectName("status")
        self.grid_layout.addWidget(self.status, 10, 0, 1, 1)
        self.search_box = QtWidgets.QLineEdit(SearchDialog)
        self.search_box.setText("")
        self.search_box.setObjectName("search_box")
        self.grid_layout.addWidget(self.search_box, 1, 0, 1, 1)
        self.matches = QtWidgets.QListWidget(SearchDialog)
        self.matches.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.matches.setObjectName("matches")
        self.grid_layout.addWidget(self.matches, 5, 0, 4, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.grid_layout.addItem(spacerItem1, 6, 1, 1, 1)
        self.grid_layout.setColumnStretch(0, 1)
        self.grid_layout.setColumnStretch(2, 1)

        self.retranslateUi(SearchDialog)
        self.match_kind.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SearchDialog)
        SearchDialog.setTabOrder(self.search_box, self.matches)
        SearchDialog.setTabOrder(self.matches, self.add_btn)
        SearchDialog.setTabOrder(self.add_btn, self.selection)
        SearchDialog.setTabOrder(self.selection, self.add_basket_btn)
        SearchDialog.setTabOrder(self.add_basket_btn, self.apply_btn)
        SearchDialog.setTabOrder(self.apply_btn, self.cancel_btn)
        SearchDialog.setTabOrder(self.cancel_btn, self.match_kind)

    def retranslateUi(self, SearchDialog):
        _translate = QtCore.QCoreApplication.translate
        SearchDialog.setWindowTitle(_translate("SearchDialog", "Dialog"))
        self.match_kind.setItemText(0, _translate("SearchDialog", "Wildcard"))
        self.match_kind.setItemText(1, _translate("SearchDialog", "Regex"))
        self.label.setText(_translate("SearchDialog", "Final selection"))
        self.cancel_btn.setText(_translate("SearchDialog", "Cancel"))
        self.add_basket_btn.setText(_translate("SearchDialog", "Add basket"))
        self.apply_btn.setText(_translate("SearchDialog", "Add"))
        self.matches.setSortingEnabled(True)
from mdfstudio.gui.widgets.list import MinimalListWidget
