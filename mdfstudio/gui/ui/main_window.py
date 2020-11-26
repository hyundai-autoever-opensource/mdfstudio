# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12
    Created by: PyQt5 UI code generator 5.15.0

    Comments
    ---------
    Change logo image
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PyMDFMainWindow(object):
    def setupUi(self, PyMDFMainWindow):
        PyMDFMainWindow.setObjectName("PyMDFMainWindow")
        PyMDFMainWindow.resize(800, 723)
        self.centralwidget = QtWidgets.QWidget(PyMDFMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(2, 2, 2, 2)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidgetPage1 = QtWidgets.QWidget()
        self.stackedWidgetPage1.setObjectName("stackedWidgetPage1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.stackedWidgetPage1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.files = QtWidgets.QMdiArea(self.stackedWidgetPage1)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.files.setBackground(brush)
        self.files.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.files.setObjectName("files")
        self.verticalLayout_2.addWidget(self.files)
        self.stackedWidget.addWidget(self.stackedWidgetPage1)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        PyMDFMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PyMDFMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        PyMDFMainWindow.setMenuBar(self.menubar)
        self.action_memory_minimum = QtWidgets.QAction(PyMDFMainWindow)
        self.action_memory_minimum.setCheckable(True)
        self.action_memory_minimum.setObjectName("action_memory_minimum")
        self.action_memory_full = QtWidgets.QAction(PyMDFMainWindow)
        self.action_memory_full.setCheckable(True)
        self.action_memory_full.setObjectName("action_memory_full")
        self.action_memory_low = QtWidgets.QAction(PyMDFMainWindow)
        self.action_memory_low.setCheckable(True)
        self.action_memory_low.setObjectName("action_memory_low")

        self.retranslateUi(PyMDFMainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PyMDFMainWindow)

    def retranslateUi(self, PyMDFMainWindow):
        _translate = QtCore.QCoreApplication.translate
        PyMDFMainWindow.setWindowTitle(_translate("PyMDFMainWindow", "YDAMDF Analysis tool"))
        self.action_memory_minimum.setText(_translate("PyMDFMainWindow", "minimum"))
        self.action_memory_minimum.setToolTip(_translate("PyMDFMainWindow", "Minimal memory usage by loading only the nedded block addresses"))
        self.action_memory_full.setText(_translate("PyMDFMainWindow", "full"))
        self.action_memory_full.setToolTip(_translate("PyMDFMainWindow", "Load all blocks in the RAM"))
        self.action_memory_low.setText(_translate("PyMDFMainWindow", "low"))
        self.action_memory_low.setToolTip(_translate("PyMDFMainWindow", "Load metdata block in RAM but leave the samples on disk"))

