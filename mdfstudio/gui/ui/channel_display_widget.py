# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Remove tab_2
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChannelDiplay(object):
    def setupUi(self, ChannelDiplay):
        ChannelDiplay.setObjectName("ChannelDiplay")
        ChannelDiplay.resize(393, 38)
        ChannelDiplay.setMinimumSize(QtCore.QSize(40, 30))
        self.horizontalLayout = QtWidgets.QHBoxLayout(ChannelDiplay)
        self.horizontalLayout.setContentsMargins(2, 0, 2, 0)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.display = QtWidgets.QCheckBox(ChannelDiplay)
        self.display.setMinimumSize(QtCore.QSize(13, 13))
        self.display.setText("")
        self.display.setChecked(True)
        self.display.setObjectName("display")
        self.horizontalLayout.addWidget(self.display)
        self.color_btn = QtWidgets.QPushButton(ChannelDiplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.color_btn.sizePolicy().hasHeightForWidth())
        self.color_btn.setSizePolicy(sizePolicy)
        self.color_btn.setMinimumSize(QtCore.QSize(13, 13))
        self.color_btn.setMaximumSize(QtCore.QSize(13, 13))
        self.color_btn.setAutoFillBackground(False)
        self.color_btn.setText("")
        self.color_btn.setFlat(False)
        self.color_btn.setObjectName("color_btn")
        self.horizontalLayout.addWidget(self.color_btn)
        self.name = QtWidgets.QLabel(ChannelDiplay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy)
        self.name.setMinimumSize(QtCore.QSize(0, 26))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setKerning(True)
        self.name.setFont(font)
        self.name.setMouseTracking(False)
        self.name.setTextFormat(QtCore.Qt.PlainText)
        self.name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.name.setObjectName("name")
        self.horizontalLayout.addWidget(self.name)
        self.value = QtWidgets.QLabel(ChannelDiplay)
        self.value.setMinimumSize(QtCore.QSize(75, 0))
        self.value.setText("")
        self.value.setTextFormat(QtCore.Qt.PlainText)
        self.value.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.value.setObjectName("value")
        self.horizontalLayout.addWidget(self.value)
        self.ylink = QtWidgets.QCheckBox(ChannelDiplay)
        self.ylink.setText("")
        self.ylink.setObjectName("ylink")
        self.horizontalLayout.addWidget(self.ylink)
        self.individual_axis = QtWidgets.QCheckBox(ChannelDiplay)
        self.individual_axis.setText("")
        self.individual_axis.setObjectName("individual_axis")
        self.horizontalLayout.addWidget(self.individual_axis)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(ChannelDiplay)
        QtCore.QMetaObject.connectSlotsByName(ChannelDiplay)

    def retranslateUi(self, ChannelDiplay):
        _translate = QtCore.QCoreApplication.translate
        ChannelDiplay.setWindowTitle(_translate("ChannelDiplay", "Form"))
        self.name.setText(_translate("ChannelDiplay", "MAIN CLOCK"))
        self.ylink.setToolTip(_translate("ChannelDiplay", "enable common Y axis"))
