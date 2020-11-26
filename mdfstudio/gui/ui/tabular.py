# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Remove filter and query ui and all the related controls
    Move Enable colum sorting checkbox to top-right side
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TabularDisplay(object):
    def setupUi(self, TabularDisplay):
        TabularDisplay.setObjectName("TabularDisplay")
        TabularDisplay.resize(821, 618)
        self.gridLayout = QtWidgets.QGridLayout(TabularDisplay)
        self.gridLayout.setObjectName("gridLayout")
        self.label_raster = QtWidgets.QLabel(TabularDisplay)
        self.label_raster.setObjectName("label_raster")
        self.gridLayout.addWidget(self.label_raster, 0, 0, 1, 1)
        self.sort = QtWidgets.QCheckBox(TabularDisplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sort.sizePolicy().hasHeightForWidth())
        self.sort.setSizePolicy(sizePolicy)
        self.sort.setObjectName("sort")
        self.gridLayout.addWidget(self.sort, 0, 1, 1, 1)
        self.tree = QtWidgets.QTreeWidget(TabularDisplay)
        font = QtGui.QFont()
        font.setFamily("Lucida Console")
        self.tree.setFont(font)
        self.tree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tree.setUniformRowHeights(True)
        self.tree.setObjectName("tree")
        self.tree.headerItem().setText(0, "1")
        self.gridLayout.addWidget(self.tree, 1, 0, 1, 2)
        self.tree_scroll = QtWidgets.QScrollBar(TabularDisplay)
        self.tree_scroll.setMaximum(9999)
        self.tree_scroll.setSingleStep(1)
        self.tree_scroll.setPageStep(10)
        self.tree_scroll.setOrientation(QtCore.Qt.Vertical)
        self.tree_scroll.setInvertedAppearance(False)
        self.tree_scroll.setObjectName("tree_scroll")
        self.gridLayout.addWidget(self.tree_scroll, 1, 2, 1, 1)

        self.retranslateUi(TabularDisplay)
        QtCore.QMetaObject.connectSlotsByName(TabularDisplay)

    def retranslateUi(self, TabularDisplay):
        _translate = QtCore.QCoreApplication.translate
        TabularDisplay.setWindowTitle(_translate("TabularDisplay", "Form"))
        self.label_raster.setText(_translate("TabularDisplay", "TextLabel"))
        self.sort.setText(_translate("TabularDisplay", "Enable column sorting"))
