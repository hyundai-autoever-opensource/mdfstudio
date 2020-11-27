# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
    *	MainWindow.__init__ : Change UI (Modify menubar, new button icons)
	*	MainWindow.open_about : Execute AboutWidget
	*	MainWindow.open_url : Open url by iExplore
	*	MainWindow.help : Open manual (pdf file)
	*	MainWindow.plot_action : Looking for Plot widget by focuswidget's parent
	*	MainWindow.toggle_dots : Window widget type changed
	*	MainWindow.show_sub_windows : Window widget type changed
	*	MainWindow.set_open_option : Save open_option state
	*	MainWindow.set_subplot_option : Window widget type changed
	*	MainWindow.set_theme : Change palette theme
	*	MainWindow.set_full_screen : Set active subwindow shown maximized
	*	MainWindow.set_subplot_link_option : Window widget type changed
	*	MainWindow.set_ignore_value2text_conversions_option : Window widget type changed
	*	MainWindow.open : Run open_file only when currentIndex == 0
	*	MainWindow._open_file : Save recently opened file list
	*	MainWindow.close_file : Show main page when there is no window
	*	MainWindow.closeEvent : Save configuration if mode is on
	*	MainWindow.kill_proc_tree : Kill all processes when closed
	*	MainWindow.mode_changed : package name changed
	*	MainWindow.keyPressEvent : window type changed
	*	MainWindow.comparison_info : Window widget type changed
	*	MainWindow.load_last_mdf : Show recently opened file list in menu
	*	MainWindow.save_last_mdf : Save recently opend file info in recent.cfg file
	*	MainWindow.clear_cache : Remove recently opened file list
	*	MainWindow.load_last_work : Load window configuration if exists
	*	MainWindow.save_last_work : Save window configuration

"""
from functools import partial
import gc
import json
import os
from pathlib import Path
from textwrap import wrap
import psutil
import sys
import webbrowser

from natsort import natsorted
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from ...version import __version__ as libversion
from ...version import __target__ as libtarget
from ..dialogs.multi_search import MultiSearch
from ..ui.main_window import Ui_PyMDFMainWindow

from .batch import BatchWidget
from .file import FileWidget
from .mdi_area import MdiAreaWidget, WithMDIArea
from .plot import Plot, _Plot
from .tabular import Tabular
from ..ui import qresource
from ..dialogs.about_dialog import AboutWidget


class MainWindow(WithMDIArea, Ui_PyMDFMainWindow, QtWidgets.QMainWindow):

    def __init__(self, files=None, *args, **kwargs):
        super(Ui_PyMDFMainWindow, self).__init__(*args, **kwargs)
        WithMDIArea.__init__(self)
        self.setupUi(self)
        self._settings = QtCore.QSettings()
        self._light_palette = self.palette()

        self.ignore_value2text_conversions = self._settings.value(
            "ignore_value2text_conversions", True, type=bool
        )

        #yda *UDC*
        # self.apply_alternative_names = self._settings.value(
        #     "apply_alternative_names", False, type=bool
        # )
        self.apply_alternative_names = False

        self.batch = BatchWidget(self.ignore_value2text_conversions)
        self.stackedWidget.addWidget(self.batch)

        self.environ_path = os.environ['APPDATA']
        self.recent_files = []
        self.msg_request = True

        # -------------------
        # splitter = QtWidgets.QSplitter()
        # splitter.setOrientation(QtCore.Qt.Horizontal)
        # splitter.setSizes([4, 6])
        # widget = QtWidgets.QWidget()
        # vbox = QtWidgets.QVBoxLayout()
        # vbox.setSpacing(2)
        #
        # multi_search = QtWidgets.QPushButton("Search")
        # icon = QtGui.QIcon()
        # icon.addPixmap(
        #     QtGui.QPixmap(":/images/search1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        # multi_search.setIcon(icon)
        # multi_search.clicked.connect(self.comparison_search)
        #
        # multi_open = QtWidgets.QPushButton("Open")
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/images/open1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # multi_open.setIcon(icon)
        # multi_open.clicked.connect(self.open_compare_files)
        #
        # hbox = QtWidgets.QHBoxLayout()
        # hbox.addWidget(multi_search)
        # hbox.addWidget(multi_open)
        # hbox.addStretch()
        #
        # vbox.addLayout(hbox)
        # self.compare_list = MinimalListWidget()
        # vbox.addWidget(self.compare_list)
        # widget.setLayout(vbox)
        # splitter.addWidget(widget)
        #
        # self.mdi_area = MdiAreaWidget(self)
        # self.mdi_area.add_window_request.connect(self.add_window)
        # self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        #
        # splitter.addWidget(self.mdi_area)
        #
        # self.stackedWidget.addWidget(splitter)
        #-------------------

        widget = QtWidgets.QWidget()
        widget.setObjectName("CompareFile")
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        multi_search = QtWidgets.QPushButton("Search")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/images/search1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        multi_search.setIcon(icon)
        multi_search.clicked.connect(self.comparison_search)

        multi_info = QtWidgets.QPushButton("Measurements information")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/info1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        multi_info.setIcon(icon)
        multi_info.clicked.connect(self.comparison_info)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(multi_search)
        hbox.addWidget(multi_info)
        hbox.addStretch()

        self.mdi_area = MdiAreaWidget(self)
        self.mdi_area.add_window_request.connect(self.add_window)
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        layout.addLayout(hbox)
        layout.addWidget(self.mdi_area)

        self.stackedWidget.addWidget(widget)

        self.progress = None

        self.menubar.setStyleSheet("QMenuBar { background: #002c5f; color: white}");

        self.file_menu = self.menubar.addMenu("&File")
        open_group = QtWidgets.QActionGroup(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/open2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action = QtWidgets.QAction(icon, "&Open", self.file_menu)
        action.triggered.connect(self.open)
        action.setObjectName("open_action")
        action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        open_group.addAction(action)
        open_group.setObjectName("open_group")
        self.file_menu.addActions(open_group.actions())

        # mode_actions
        menu = QtWidgets.QMenu("&Mode", self.menubar)
        mode_actions = QtWidgets.QActionGroup(self)

        for option in ("Single files", "Comparison", "Merge files"):
            action = QtWidgets.QAction("&"+option, menu)
            action.setCheckable(True)
            mode_actions.addAction(action)
            action.triggered.connect(partial(self.set_mode, option))

            # if option == self._settings.value("mode", "Single files"):
            if option == "Single files":
                action.setChecked(True)
                action.triggered.emit()
            else:
                action.setEnabled(False)    #later.. someone...

        menu.addActions(mode_actions.actions())
        self.menubar.addMenu(menu)

        menu = QtWidgets.QMenu("&Settings", self.menubar)
        self.menubar.addMenu(menu)

        open_option = QtWidgets.QActionGroup(self)

        for option in ("Mode On", "Mode Off"):

            action = QtWidgets.QAction(option, menu)
            action.setCheckable(True)
            open_option.addAction(action)
            action.triggered.connect(partial(self.set_open_option, option))

            if option == self._settings.value("open_option", "Mode On"):
                action.setChecked(True)
                action.triggered.emit()

        submenu = QtWidgets.QMenu("&Save configurations", self.menubar)
        submenu.addActions(open_option.actions())
        menu.addMenu(submenu)

        # search mode menu
        theme_option = QtWidgets.QActionGroup(self)
        theme_option.setEnabled(False)

        for option in ("Dark", "Light"):

            action = QtWidgets.QAction("&"+option, menu)
            action.setCheckable(True)
            theme_option.addAction(action)
            action.triggered.connect(partial(self.set_theme, option))

            if option == self._settings.value("theme", "Light"):
                action.setChecked(True)
                action.triggered.emit()

        submenu = QtWidgets.QMenu("&Theme", self.menubar)
        submenu.addActions(theme_option.actions())
        menu.addMenu(submenu)

        menu = QtWidgets.QMenu("&View", self.menubar)
        self.menubar.addMenu(menu)

        # sub plots
        subplot_action = QtWidgets.QAction("&Sub-plots", menu)
        subplot_action.setCheckable(True)

        state = self._settings.value("subplots", True, type=bool)
        subplot_action.toggled.connect(self.set_subplot_option)
        subplot_action.triggered.connect(self.set_subplot_option)
        subplot_action.setChecked(state)
        menu.addAction(subplot_action)

        subplot_action = QtWidgets.QAction("&Link sub-plots X-axis", menu)
        subplot_action.setCheckable(True)
        state = self._settings.value("subplots_link", False, type=bool)
        subplot_action.toggled.connect(self.set_subplot_link_option)
        subplot_action.setChecked(state)
        menu.addAction(subplot_action)

        subplot_action = QtWidgets.QAction("&Ignore value2text conversions", menu)
        subplot_action.setCheckable(True)
        subplot_action.toggled.connect(self.set_ignore_value2text_conversions_option)
        subplot_action.setChecked(self.ignore_value2text_conversions)
        menu.addAction(subplot_action)

        # yda 2020-10-08 *UDC*
        # subplot_action = QtWidgets.QAction("Apply user-defined channel names", menu)
        # subplot_action.triggered.connect(self.show_name_info_dialog)
        # menu.addAction(subplot_action)
        # menu.addSeparator()

        # plot background
        plot_background_option = QtWidgets.QActionGroup(self)

        for option in ("Black", "White"):
            action = QtWidgets.QAction("&"+option, menu)
            action.setCheckable(True)
            plot_background_option.addAction(action)
            action.triggered.connect(partial(self.set_plot_background, option))

            if option == self._settings.value("plot_background", "White"):
                action.setChecked(True)
                action.triggered.emit()

        submenu = QtWidgets.QMenu("&Plot background", self.menubar)
        submenu.addActions(plot_background_option.actions())
        menu.addMenu(submenu)
        menu.addSeparator()

        # sub_plots
        subs = QtWidgets.QActionGroup(self)

        action = QtWidgets.QAction("{: <20}\tShift+F".format("&Full screen mode"), menu)
        action.triggered.connect(self.set_full_screen)
        action.setShortcut(QtGui.QKeySequence("Shift+F"))
        subs.addAction(action)

        action = QtWidgets.QAction("{: <20}\tShift+C".format("&Cascade sub-plots"), menu)
        action.triggered.connect(partial(self.show_sub_windows, mode="cascade"))
        action.setShortcut(QtGui.QKeySequence("Shift+C"))
        subs.addAction(action)

        action = QtWidgets.QAction(
            "{: <20}\tShift+T".format("&Tile sub-plots in a grid"), menu
        )
        action.triggered.connect(partial(self.show_sub_windows, mode="tile"))
        action.setShortcut(QtGui.QKeySequence("Shift+T"))
        subs.addAction(action)

        action = QtWidgets.QAction(
            "{: <20}\tShift+V".format("&Tile sub-plots vertically"), menu
        )
        action.triggered.connect(partial(self.show_sub_windows, mode="tile vertically"))
        action.setShortcut(QtGui.QKeySequence("Shift+V"))
        subs.addAction(action)

        action = QtWidgets.QAction(
            "{: <20}\tShift+H".format("&Tile sub-plots horizontally"), menu
        )
        action.triggered.connect(
            partial(self.show_sub_windows, mode="tile horizontally")
        )
        action.setShortcut(QtGui.QKeySequence("Shift+H"))
        subs.addAction(action)
        menu.addActions(subs.actions())

        self.plot_menu = QtWidgets.QMenu("&Plot", self.menubar)

        # plot option menu
        plot_actions = QtWidgets.QActionGroup(self)

        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/fit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action = QtWidgets.QAction(f"{'&Fit Y-axis on the screen': <20}\tF", menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_F))
        action.setShortcut(QtCore.Qt.Key_F)
        plot_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/images/grid1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action = QtWidgets.QAction("{: <20}\tG".format("&Grid"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_G))
        action.setShortcut(QtCore.Qt.Key_G)
        plot_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/images/home1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action = QtWidgets.QAction("{: <20}\tH".format("&Home"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_H))
        action.setShortcut(QtCore.Qt.Key_H)
        plot_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(
        #     QtGui.QPixmap(":/list2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        action = QtWidgets.QAction("{: <20}\tS".format("&Stack"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_S))
        action.setShortcut(QtCore.Qt.Key_S)
        plot_actions.addAction(action)

        action = QtWidgets.QAction("{: <20}\t.".format("&Toggle dots"), menu)
        action.triggered.connect(self.toggle_dots)
        action.setShortcut(QtCore.Qt.Key_Period)
        plot_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action = QtWidgets.QAction("{: <20}\tIns".format("&Insert computation"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_Insert))
        action.setShortcut(QtCore.Qt.Key_Insert)
        plot_actions.addAction(action)

        action = QtWidgets.QAction("{: <20}\tAlt+W".format("&Window Screenshot (Plot)"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_W, modifier=QtCore.Qt.AltModifier))
        action.setShortcut(QtGui.QKeySequence("Alt+W"))
        plot_actions.addAction(action)

        # cursors
        cursors_actions = QtWidgets.QActionGroup(self)

        # icon = QtGui.QIcon()
        # icon.addPixmap(
        #     QtGui.QPixmap(":/cursor.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        action = QtWidgets.QAction("{: <20}\tC".format("&Cursor"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_C))
        action.setShortcut(QtCore.Qt.Key_C)
        cursors_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(
        #     QtGui.QPixmap(":/range.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        action = QtWidgets.QAction("{: <20}\tR".format("&Range"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_R))
        action.setShortcut(QtCore.Qt.Key_R)
        cursors_actions.addAction(action)

        # icon = QtGui.QIcon()
        # icon.addPixmap(
        #     QtGui.QPixmap(":/lock_range.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        action = QtWidgets.QAction("{: <20}\tY".format("&Lock/unlock range"), menu)
        action.triggered.connect(partial(self.plot_action, key=QtCore.Qt.Key_Y))
        action.setShortcut(QtCore.Qt.Key_Y)
        cursors_actions.addAction(action)

        self.plot_menu.addActions(plot_actions.actions())
        self.plot_menu.addSeparator()
        self.plot_menu.addActions(cursors_actions.actions())
        self.plot_menu.addSeparator()
        self.menubar.addMenu(self.plot_menu)

        menu = self.menubar.addMenu("&Help")
        open_group = QtWidgets.QActionGroup(self)
        action = QtWidgets.QAction("&About", menu)
        action.triggered.connect(self.open_about)
        open_group.addAction(action)
        action = QtWidgets.QAction("&Visit github page", menu)
        action.triggered.connect(self.github)
        open_group.addAction(action)
        menu.addActions(open_group.actions())

        self.load_last_mdf()

        self.with_dots = self._settings.value("dots", False, type=bool)
        self.setWindowTitle(f"MDF Studio for {libtarget} {libversion}")

        self.set_subplot_option(self._settings.value("subplots", "Disabled"))
        self.set_subplot_link_option(self._settings.value("subplots_link", "Disabled"))

        self.files.setTabsClosable(True)

        self.setAcceptDrops(True)
        self.stackedWidget.currentChanged.connect(self.mode_changed)

        label = QtWidgets.QLabel(self)
        label.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        label.setScaledContents(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.stackedWidget.addWidget(label)

        if files:
            self.stackedWidget.setCurrentIndex(0)
            self._open_file(files)
        else:
            self.stackedWidget.setCurrentIndex(3)

        self.show()

    def github(self):
        webbrowser.open_new(r"https://github.com/hyundai-autoever-opensource/mdfstudio/")

    def plot_action(self, key, modifier=QtCore.Qt.NoModifier):
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, modifier)
        if self.stackedWidget.currentIndex() == 0:
            widget = None
            if isinstance(self.files.focusWidget().parent().parent().parent(), Plot):
                widget = self.files.focusWidget().parent().parent().parent()
            elif isinstance(self.files.focusWidget().parent().parent(), Plot):
                widget = self.files.focusWidget().parent().parent()
            elif isinstance(self.files.focusWidget(), _Plot):
                widget = self.files.focusWidget()
            elif isinstance(self.files.focusWidget().parent(), Tabular):
                widget = self.files.focusWidget().parent().parent().parent().parent().parent()
            else:
                event.ignore()
                return

            # widget = None
            # for index in range(len(self.files.subWindowList())):
            #     if self.files.subWindowList()[index].isActiveWindow():
            #         widget = self.files.subWindowList()[index].widget()
            if widget:
                widget.keyPressEvent(event)
            # if widget and widget.get_current_plot():
            #     widget.get_current_plot().keyPressEvent(event)
        elif self.stackedWidget.currentIndex() == 2:
            widget = self
            if widget and widget.get_current_plot():
                widget.get_current_plot().keyPressEvent(event)

    def toggle_dots(self):
        self.with_dots = not self.with_dots
        self._settings.setValue("dots", self.with_dots)

        count = len(self.files.subWindowList())

        for window in self.files.subWindowList():
            widget = window.widget()
            widget.set_line_style(with_dots=self.with_dots)

        self.set_line_style(with_dots=self.with_dots)

    def show_sub_windows(self, mode):
        if self.stackedWidget.currentIndex() == 0:
            for window in self.files.subWindowList():
                widget = window.widget()
                if widget:
                    if mode == "tile":
                        widget.mdi_area.tileSubWindows()
                    elif mode == "cascade":
                        widget.mdi_area.cascadeSubWindows()
                    elif mode == "tile vertically":
                        widget.mdi_area.tile_vertically()
                    elif mode == "tile horizontally":
                        widget.mdi_area.tile_horizontally()
        else:
            widget = self
            if widget:
                if mode == "tile":
                    widget.mdi_area.tileSubWindows()
                elif mode == "cascade":
                    widget.mdi_area.cascadeSubWindows()
                elif mode == "tile vertically":
                    widget.mdi_area.tile_vertically()
                elif mode == "tile horizontally":
                    widget.mdi_area.tile_horizontally()

    def set_open_option(self, state):
        self._settings.setValue("open_option", state)

    def set_subplot_option(self, state):
        if isinstance(state, str):
            state = True if state == "true" else False
        self.set_subplots(state)
        self._settings.setValue("subplots", state)

        for window in self.files.subWindowList():
            window.widget().set_subplots(state)

    def set_plot_background(self, option):
        self._settings.setValue("plot_background", option)
        if option == "Black":
            pg.setConfigOption("background", "k")
            pg.setConfigOption("foreground", "w")
        else:
            pg.setConfigOption("background", "w")
            pg.setConfigOption("foreground", "k")

    def set_mode(self, option):
        # self._settings.setValue("mode", option)
        if option == "Single files":
            # self._settings.setValue("mode","Single files")
            self.stackedWidget.setCurrentIndex(0)
        elif option == "Comparison":
            # self._settings.setValue("mode", "Comparison")
            self.stackedWidget.setCurrentIndex(2)
        else:
            # self._settings.setValue("mode","Merge files")
            self.stackedWidget.setCurrentIndex(1)

    def set_theme(self, option):
        self._settings.setValue("theme", option)
        app = QtWidgets.QApplication.instance()
        if option == "Light":
            br_light_sand = QtGui.QBrush(QtGui.QColor(246, 243, 242))
            br_blue = QtGui.QBrush(QtGui.QColor(0, 44, 95))
            br_sand = QtGui.QBrush(QtGui.QColor(228, 220, 211))
            br_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            br_gray = QtGui.QBrush(QtGui.QColor(221, 221, 221))
            br_light_sand.setStyle(QtCore.Qt.SolidPattern)
            br_blue.setStyle(QtCore.Qt.SolidPattern)
            br_sand.setStyle(QtCore.Qt.SolidPattern)

            self._light_palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_light_sand)
            self._light_palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_light_sand)
            self._light_palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, br_blue)
            self._light_palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, br_white)

            app.setPalette(self._light_palette)
        else:

            palette = QtGui.QPalette()
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(82, 82, 82))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
            brush = QtGui.QBrush(QtGui.QColor(68, 68, 68))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
            brush = QtGui.QBrush(QtGui.QColor(36, 36, 36))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(82, 82, 82))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
            brush = QtGui.QBrush(QtGui.QColor(68, 68, 68))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
            brush = QtGui.QBrush(QtGui.QColor(36, 36, 36))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(
                QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush
            )
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(82, 82, 82))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
            brush = QtGui.QBrush(QtGui.QColor(68, 68, 68))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
            brush = QtGui.QBrush(QtGui.QColor(36, 36, 36))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
            brush = QtGui.QBrush(QtGui.QColor(27, 27, 27))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
            brush = QtGui.QBrush(QtGui.QColor(55, 55, 55))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(
                QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush
            )
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
            brush = QtGui.QBrush(QtGui.QColor(100, 100, 100))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
            app.setPalette(palette)

    def set_full_screen(self):
        if len(self.files.subWindowList()) > 0:
            for window in self.files.subWindowList():
                if window.focusWidget():
                    if len(window.widget().mdi_area.subWindowList()) >0:
                        widget = window.widget().mdi_area.activeSubWindow()
                        if widget is None:
                            return

                        widget.showMaximized()

                        main_splitter = window.widget().splitter
                        main_size = main_splitter.sizes()

                        if str(widget.objectName())[0] == "P":
                            # widget.widget().splitter._previous_state = widget.widget().splitter.sizes()
                            sub_splitter = widget.widget().splitter
                            sub_size = sub_splitter.sizes()

                            if main_size[0] == sub_size[0] == sub_size[4] == 0:
                                window.widget().mdi_area.tileSubWindows()
                                main_splitter.setSizes([300, 2100])
                                widget.widget().splitter.btn_full_clicked(True)

                            else:
                                widget.widget().splitter.btn_full_clicked(False)
                                main_splitter.setSizes([0,10])
                        else:
                            if main_size[0] == 0:
                                window.widget().mdi_area.tileSubWindows()
                                main_splitter.setSizes([300, 2100])
                            else:
                                main_splitter.setSizes([0,10])



    def set_subplot_link_option(self, state):
        if isinstance(state, str):
            state = True if state == "true" else False
        self.set_subplots_link(state)
        self._settings.setValue("subplots_link", state)
        for window in self.files.subWindowList():
            window.widget().set_subplots_link(self.subplots_link)

    # yda 2020-10-13 *UDC*
    # def show_name_info_dialog(self):
    #     if self.files.subWindowList():
    #         widget = self.files.activeSubWindow().widget()
    #         if widget:
    #             basket = []
    #             for item in widget.basket:
    #                 basket.append(item.name)
    #
    #             file_name = "\\UserDefinedChannel.List"
    #             file_name = Path(self.environ_path + file_name)
    #
    #             if os.path.isfile(file_name):
    #                 with open(file_name, "r") as infile:
    #                     info = json.load(infile)
    #                 items = info.get("user-defined name list", [])
    #
    #             dialog = NameInfo(basket, items, widget.loaded_udc)
    #             dialog.apply_alternative_names_signal.connect(widget.get_udc_dict)
    #             dialog.exec_()
    #     else:
    #         return

    # yda 2020-10-08 *UDC*
    # def set_apply_alternatvie_names_option(self, state):
    #     if isinstance(state, str):
    #         state = True if state == "true" else False
    #     self.apply_alternative_names = state
    #     self._settings.setValue("apply_alternative_names", state)
    #
    #     for window in self.files.subWindowList():
    #         window.widget().apply_alternative_names = state

    def set_ignore_value2text_conversions_option(self, state):
        if isinstance(state, str):
            state = True if state == "true" else False
        self.ignore_value2text_conversions = state
        self._settings.setValue("ignore_value2text_conversions", state)

        for window in self.files.subWindowList():
            window.widget().ignore_value2text_conversions = state

        self.batch.ignore_value2text_conversions = state

    def update_progress(self, current_index, max_index):
        self.progress = current_index, max_index

    def open_compare_files(self, event):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select measurement file",
            "",
            "MDF v3 (*.dat *.mdf);;MDF v4(*.mf4);;DL3/ERG files (*.dl3 *.erg);;All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
            "All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
        )

        if file_names:
            self.compare_list.addItems(natsorted(file_names))
            count = self.compare_list.count()

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(":/images/open1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

            for row in range(count):
                self.compare_list.item(row).setIcon(icon)

    def open_batch_files(self, event):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select measurement file",
            "",
            "MDF v3 (*.dat *.mdf);;MDF v4(*.mf4);;DL3/ERG files (*.dl3 *.erg);;All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
            "All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
        )

        if file_names:
            self.batch.files_list.addItems(natsorted(file_names))
            count = self.batch.files_list.count()

            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(":/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )

            for row in range(count):
                self.batch.files_list.item(row).setIcon(icon)

    def open(self, event):
        if self.stackedWidget.currentIndex() == 2:
            self.open_batch_files(event)
        else:
            self.open_file(event)
            self.stackedWidget.setCurrentIndex(0)

    def _open_file(self, file_name):
        for window in self.files.subWindowList():
            if "\\" in file_name:
                f_name = file_name.split("\\")[-1]
            else:
                f_name = file_name.split("/")[-1]
            if f_name == window.windowTitle():
                QtWidgets.QMessageBox.warning(None, "Message", f"{f_name} is already opened.")
                return

        file_name = Path(file_name)
        try:
            widget = FileWidget(
                file_name,
                self.with_dots,
                self.subplots,
                self.subplots_link,
                self.ignore_value2text_conversions,
                self.apply_alternative_names,
                self,
            )
        except:
            raise
        else:
            widget.close_subwindow.connect(self.close_file)
            w = self.files.addSubWindow(widget)
            w.setWindowTitle(file_name.name)

            icon = QtGui.QIcon()
            pixmap = QtGui.QPixmap(1,1)
            pixmap.fill(QtCore.Qt.transparent)
            icon.addPixmap(pixmap)
            w.setWindowIcon(icon)
            w.showMaximized()

            widget.open_new_file.connect(self._open_file)

        self.save_last_mdf(str(file_name))
        self.load_last_mdf()
        saved_config = self.load_last_work(file_name.name)
        if saved_config:
            widget.load_channel_list(saved_config)
        self.stackedWidget.setCurrentIndex(0)

    def open_file(self, event):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select measurement file",
            self._settings.value("last_opened_path", "", str),
            "MDF v3 (*.dat *.mdf);;MDF v4 (*.mf4);;DL3/ERG files (*.dl3 *.erg);;All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
            "All files (*.dat *.mdf *.mf4 *.dl3 *.erg)",
        )
        if file_names:
            self._settings.setValue("last_opened_path", file_names[0])
            gc.collect()

        for file_name in natsorted(file_names):
            self._open_file(file_name)

    def close_file(self, widget):
        if isinstance(widget, FileWidget):
            widget.before_close(self.msg_request)
        else:
            widget.widget().before_close(self.msg_request)
        widget.close()
        # self.files.removeSubWindow(widget[0])
        # if self.files.subWindowList() is None:
        #     self.stackedWidget.setCurrentIndex(3)
        #     return
        # for window in self.files.subWindowList():
        #     widget = window.widget()
        #     if widget.isActiveWindow():
        #         print("active")
        #         config = widget.to_config()
        #         reply = QtGui.QMessageBox.question(self, 'Message',
        #                                            "현재 작업 중인 내용을 저장하시겠습니까?", QtGui.QMessageBox.Yes |
        #                                            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        #
        #         if reply == QtGui.QMessageBox.Yes:
        #             self.save_last_work(config)
        #
        #         # widget.setParent(None)
        #         widget.close()
        #         # # self.files.removeSubWindow(widget)
        #         # window.close()
        #         widget.parentWidget().close()
        #         return
        if len(self.files.subWindowList()) == 1:
            self.stackedWidget.setCurrentIndex(3)

    def closeEvent(self, event):
        if len(self.files.subWindowList()) == 0:
            pass
        else:
            if self._settings.value("open_option") == "Mode Off":
                return
            reply = QtGui.QMessageBox.question(self, 'Message', "Do you want to save current works?",
                                               QtGui.QMessageBox.SaveAll | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel,
                                               QtGui.QMessageBox.SaveAll)
            if reply == QtGui.QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QtGui.QMessageBox.Discard:
                self.close()
            elif reply == QtGui.QMessageBox.SaveAll:
                self.msg_request = False
                for i in range(len(self.files.subWindowList(0))):
                    self.close_file(self.files.subWindowList(0)[0])
        self.close_export_dialog()
        # self.stackedWidget.setCurrentIndex(3)

    def close_export_dialog(self):
        self.kill_proc_tree()

    def kill_proc_tree(including_parent=True):
        parent = psutil.Process()
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        gone, still_alive = psutil.wait_procs(children, timeout=5)
        if including_parent:
            parent.kill()
            parent.wait(5)

    def dragEnterEvent(self, e):
        e.accept()


    def dropEvent(self, e):
        try:
            if self.stackedWidget.currentIndex() == 0:
                for path in e.mimeData().text().splitlines():
                    path = Path(path.replace(r"file:///", ""))
                    if path.suffix.lower() in (".dat", ".mdf", ".mf4"):
                        self._open_file(path)
            else:
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(":/file.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
                )

                for path in e.mimeData().text().splitlines():
                    path = Path(path.replace(r"file:///", ""))
                    if path.suffix.lower() in (".dat", ".mdf", ".mf4"):
                        row = self.batch.files_list.count()
                        self.batch.files_list.addItem(str(path))
                        self.batch.files_list.item(row).setIcon(icon)
        except:
            pass

    def mode_changed(self, index):
        if index == 0:
            self.plot_menu.setEnabled(True)
            self.setWindowTitle(
                f"MDF Studio for {libtarget} {libversion}"
            )
            if not self.files.subWindowList():
                self.stackedWidget.setCurrentIndex(3)
        elif index == 1:
            self.plot_menu.setEnabled(False)
            self.setWindowTitle(
                f"MDF Studio for {libtarget} {libversion}"
            )
        elif index == 2:
            self.plot_menu.setEnabled(True)
            self.setWindowTitle(
                f"MDF Studio for {libtarget} {libversion}"
            )

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()

        if len(self.files.subWindowList()) == 0:
            event.ignore()
            return

        if key == QtCore.Qt.Key_F and modifier == QtCore.Qt.ControlModifier:
            if self.files.subWindowList() and self.stackedWidget.currentIndex() == 0:
                self.focusWidget().widget().keyPressEvent(event)
            elif self.files.subWindowList() and self.stackedWidget.currentIndex() == 2:
                count = len(self.files.subWindowList())
                channels_dbs = [
                    self.files.subWindowList(i)[0].widget().mdf.channels_db for i in range(count)
                    # self.files.widget(i).mdf.channels_db for i in range(count)
                ]
                measurements = [
                    str(self.files.subWindowList(i)[0].widget().mdf.name) for i in range(count)
                    # str(self.files.widget(i).mdf.name) for i in range(count)
                ]

                dlg = MultiSearch(channels_dbs, measurements, parent=self, )
                dlg.setModal(True)
                dlg.exec_()
                result = dlg.result
                if result:

                    ret, ok = QtWidgets.QInputDialog.getItem(
                        None,
                        "Select window type",
                        "Type:",
                        ["Plot", "Tabular", "Plot+Tabular"],
                        0,
                        False,
                    )
                    if ok:
                        names = [
                            (None, *entry, self.files.subWindowList(file_index)[0].widget().uuid)
                            for file_index, entry in result
                        ]
                        self.add_window((ret, names))

        else:
            super().keyPressEvent(event)

    def comparison_search(self, event):
        event = QtGui.QKeyEvent(
            QtCore.QEvent.KeyPress, QtCore.Qt.Key_F, QtCore.Qt.ControlModifier
        )
        self.keyPressEvent(event)

    def comparison_info(self, event):
        measurements = []
        for window in self.files.subWindowList():
            widget = window.widget()
            measurements.append(str(widget.mdf.name))

        info = []
        for i, name in enumerate(measurements, 1):
            info.extend(wrap(f"{i:> 2}: {name}", 120))

        QtWidgets.QMessageBox.information(
            self, "Measurement files used for comparison", "\n".join(info),
        )

    def load_last_mdf(self):
        file_name = "\\recent.cfg"
        file_name = Path(self.environ_path + file_name)

        if os.path.isfile(file_name):
            with open(file_name, "r") as infile:
                info = json.load(infile)
            file_list = info.get("file_path", [])

            if file_list:
                file_menu = self.file_menu
                for action in file_menu.actions():
                    if action.objectName() == "open_action":
                        pass
                    else:
                        file_menu.removeAction(action)
                self.recent_files = []

                file_menu.addSeparator()
                file_group = QtWidgets.QActionGroup(self)

                index = 0
                for file in file_list:
                    if os.path.isfile(file):
                        self.recent_files.append(file)
                        title = str(file).split("\\")
                        title = title[-1]
                        action = QtWidgets.QAction(f"&{index}. {title}", file_group)
                        action.triggered.connect(partial(self._open_file, file))
                        file_group.addAction(action)
                        index += 1

                file_menu.addActions(file_group.actions())

                file_menu.addSeparator()
                cache_group = QtWidgets.QActionGroup(self)
                action = QtWidgets.QAction("Clear Cache", cache_group)
                action.triggered.connect(self.clear_cache)
                cache_group.addAction(action)
                file_menu.addActions(cache_group.actions())

            else:
                self.recent_files = []
                self.file_menu.clear()

    def save_last_mdf(self, last_file):
        current_file = last_file
        recent_files = self.recent_files

        if current_file in recent_files:
            recent_files.remove(current_file)
        else:
            if len(recent_files) > 9:
                recent_files.pop(9)

        recent_files.insert(0,current_file)
        self.recent_files = recent_files

        config = {}
        config["file_path"] = self.recent_files

        file_name = "\\recent.cfg"
        file_name = Path(self.environ_path + file_name)

        if file_name:
            Path(file_name).write_text(
                json.dumps(config, indent=4, sort_keys=True)
            )

    def clear_cache(self):
        file_name = "\\recent.cfg"
        file_name = Path(self.environ_path + file_name)

        if os.path.isfile(file_name):
            os.remove(file_name)
            file_menu = self.file_menu
            for action in file_menu.actions():
                if action.objectName() == "open_action":
                    pass
                else:
                    file_menu.removeAction(action)
            for cfg in self.recent_files:
                cfg = Path(self.environ_path + "\\"+ cfg.split("\\")[-1] + ".cfg")
                if os.path.isfile(cfg):
                    os.remove(cfg)
            self.recent_files = []

    def load_last_work(self, file_name):
        if self._settings.value("open_option") == "Mode Off":
            return

        file_name = '\\' + file_name + ".cfg"
        file_name = Path(self.environ_path + file_name)
        if os.path.isfile(file_name):
            reply = QtGui.QMessageBox.question(self, 'Message',
                                               "Do you want to open this file from the last save point?", QtGui.QMessageBox.Yes |
                                               QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

            if reply == QtGui.QMessageBox.Yes:
                return file_name

    def save_last_work(self, info):
        if self._settings.value("open_option") == "Mode Off":
            return
        file_name = '\\'+ Path(info["file_path"][0]).name + ".cfg"
        file_name = Path(self.environ_path + file_name)

        if file_name:
            Path(file_name).write_text(
                json.dumps(info, indent=4, sort_keys=True)
            )
        return

    def help(self, event):
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")

            return os.path.join(base_path, relative_path)

        file_path_chm = "C:\Program Files (x86)\mdfstudio\manual.chm"
        file_path_pdf = "C:\Program Files (x86)\mdfstudio\manual.pdf"
        if os.path.isfile(file_path_chm):
            os.startfile(file_path_chm)
        elif os.path.isfile(file_path_pdf):
            os.startfile(file_path_pdf)

    def open_about(self):
        widget = AboutWidget()
        widget.exec_()

    def open_url(self, event):
        webbrowser.open_new(r"https://moaform.com/q/mdBiwO")
