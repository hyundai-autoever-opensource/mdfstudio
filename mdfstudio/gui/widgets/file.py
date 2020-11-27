# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------

    *   FileWidget.__init__ :   Change UI (new button image, new palette, change tab structure - merge cut, resample, export tab into filter tab)
                        Add unit sort list and custom basket list to channels_tree
                        Add file's unit list in info tab
    *   FileWidget.whence_changed : whence and time_from_zero can't be checked at the same time
    *   FileWidget.time_from_zero_changed : whence and time_from_zero can't be checked at the same time
    *   FileWidget.open_menu :  Create context menu of each tree item
    *   FileWidget.item_clicked : Set check state when item is clicked
    *   FileWidget._update_channel_tree : Add unit sort and custom basket into treewidget
    *   FileWidget.export_changed : Enable checkboxes when export type is mat
    *   FileWidget.search : Add result to custom basket list
    *   FileWidget.to_config : Change configuration format
    *   FileWidget.save_channel_list : Change file format (*.cfg)
    *   FileWidget.load_channel_list : Load channel list into custom basket
    *   FileWidget.save_filter_list : Delete
    *   FileWidget.clear_channels :Add unit sort and custom basket into treewidget
    *   FileWidget.select_all_channels : Add unit sort and custom basket into treewidget
    *   FileWidget.add_basket : Add selected channel items into custom basket
    *   FileWidget.delete_basket : Remove all items in custom basket
    *   FileWidget.reorder_basket : Reorder sequence of items in custom basket
    *   FileWidget.closeEvent : Emit close signal
    *   FileWidget.save_last_work : If save configuration mode is on, save configuration file
    *   FileWidget.before_close : If save configuration mode is on, ask whether user wants to save configuration
    *   FileWidget.cut : Inform minimum / maximum timestamp values
    *   FileWidget.export : Execute filter, cut, resample and save(export) mdf file together. Separate kwargs by mdf versions.
    *   FileWidget._create_window : Change window type(Plot, Tabular, "Plot+Tabular) and add raster selection dialog box
    *   FileWidget.move_up : move custom basket item up
    *   FileWidget.move_down : move custom basket item down
    *   FileWidget.aspect_changed : Remove other tabs but export tab and channels tab

"""
from datetime import datetime
from functools import partial, reduce
import json
import os
from pathlib import Path
from tempfile import gettempdir
from time import perf_counter
from traceback import format_exc
from uuid import uuid4

from natsort import natsorted
import numpy as np
import pandas as pd
import psutil
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from ...blocks.utils import csv_bytearray2hex, extract_cncomment_xml, MdfException
from ...blocks.v4_constants import FLAG_CG_BUS_EVENT
from ...mdf import MDF, SUPPORTED_VERSIONS
from ..dialogs.advanced_search import AdvancedSearch
from ..dialogs.channel_group_info import ChannelGroupInfoDialog
from ..dialogs.channel_info import ChannelInfoDialog
from ..dialogs.name_info import NameInfo
from ..ui.file_widget import Ui_file_widget
from ..utils import (
    add_children,
    compute_signal,
    get_required_signals,
    HelperChannel,
    load_dsp,
    load_lab,
    run_thread_with_progress,
    setup_progress,
    TERMINATED,
)
from .mdi_area import MdiAreaWidget, WithMDIArea
from .numeric import Numeric
from .plot import Plot
from .tree import TreeWidget
from .tree_item import TreeItem

class FileWidget(WithMDIArea, Ui_file_widget, QtWidgets.QWidget):

    open_new_file = QtCore.pyqtSignal(str)
    close_subwindow = QtCore.pyqtSignal(object, bool)

    def __init__(
        self,
        file_name,
        with_dots,
        subplots=False,
        subplots_link=False,
        ignore_value2text_conversions=False,
        apply_alternative_names=False,
        *args,
        **kwargs,
    ):
        super(Ui_file_widget, self).__init__(*args, **kwargs)
        WithMDIArea.__init__(self,subplots, subplots_link, ignore_value2text_conversions)
        self.setupUi(self)
        self.single_time_base.setCheckState(QtCore.Qt.Checked)
        self._settings = QtCore.QSettings()
        self.uuid = uuid4()

        file_name = Path(file_name)
        self.subplots = subplots
        self.subplots_link = subplots_link
        self.ignore_value2text_conversions = ignore_value2text_conversions
        self.with_dots = with_dots

        self.file_name = file_name
        self.environ_path = os.environ['APPDATA']
        self.progress = None
        self.mdf = None
        self.info_index = None
        self._viewbox = pg.ViewBox()
        self._viewbox.setXRange(0, 10)
        self.basket = []
        self.basket_entry = set()

        palette = QtGui.QPalette()
        br_light_sand = QtGui.QBrush(QtGui.QColor(246, 243, 242))
        br_blue = QtGui.QBrush(QtGui.QColor(0, 44, 95))
        br_sky_blue = QtGui.QBrush(QtGui.QColor(170, 202, 230))
        br_sand = QtGui.QBrush(QtGui.QColor(228, 220, 211))
        br_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        br_black = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        br_gray = QtGui.QBrush(QtGui.QColor(221, 221, 221))
        br_light_sand.setStyle(QtCore.Qt.SolidPattern)
        br_blue.setStyle(QtCore.Qt.SolidPattern)
        br_sand.setStyle(QtCore.Qt.SolidPattern)

        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, br_gray)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, br_gray)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, br_gray)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, br_gray)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, br_blue)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, br_gray)
        self.setPalette(palette)


        #yda 2020-10-08 *UDC*
        # self.apply_alternative_names = apply_alternative_names
        # self.udc_dict = {}
        # self.loaded_udc = None

        progress = QtWidgets.QProgressDialog(
            f'Opening "{self.file_name}"', "", 0, 100, self.parent()
        )

        progress.setWindowModality(QtCore.Qt.ApplicationModal)
        progress.setCancelButton(None)
        progress.setAutoClose(True)
        progress.setWindowTitle("Opening measurement")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/upload2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        progress.setWindowIcon(icon)
        progress.show()

        if file_name.suffix.lower() in (".erg", ".bsig"):
            extension = file_name.suffix.lower().strip(".")
            progress.setLabelText(f"Converting from {extension} to mdf")

            from mfile import ERG, BSIG

            if file_name.suffix.lower() == ".erg":
                cls = ERG
            else:
                cls = BSIG

            out_file = Path(gettempdir()) / file_name.name

            mdf_path = (
                cls(file_name).export_mdf().save(out_file.with_suffix(".tmp.mf4"))
            )
            self.mdf = MDF(mdf_path)
        elif file_name.suffix.lower() == ".zip":
            progress.setLabelText("Opening zipped MF4 file")
            from mfile import ZIP

            self.mdf = ZIP(file_name)
        else:
            if file_name.suffix.lower() == ".dl3":
                progress.setLabelText("Converting from dl3 to mdf")
                datalyser_active = any(
                    proc.name() == "Datalyser3.exe" for proc in psutil.process_iter()
                )
                out_file = Path(gettempdir()) / file_name.name

                import win32com.client
                index = 0
                while True:
                    mdf_name = out_file.with_suffix(f".{index}.mdf")
                    if mdf_name.exists():
                        index += 1
                    else:
                        break
                datalyser = win32com.client.Dispatch("Datalyser3.Datalyser3_COM")
                if not datalyser_active:
                    try:
                        datalyser.DCOM_set_datalyser_visibility(False)
                    except:
                        pass
                datalyser.DCOM_convert_file_mdf_dl3(file_name, str(mdf_name), 0)
                if not datalyser_active:
                    datalyser.DCOM_TerminateDAS()
                file_name = mdf_name

            target = MDF
            kwargs = {"name": file_name, "callback": self.update_progress}

            self.mdf = run_thread_with_progress(
                self,
                target=target,
                kwargs=kwargs,
                factor=33,
                offset=0,
                progress=progress,
            )
            if self.mdf is TERMINATED:
                return

        channels_db_items = sorted(self.mdf.channels_db, key=lambda x: x.lower())
        self.channels_db_items = channels_db_items

        self.raster_set = set()
        for channel in self.channels_db_items:
            if channel[0] == "$" or channel == "time":
                continue

            raster = float(self.mdf.get_channel_metadata(channel, self.mdf.channels_db[channel][0][0]).sampling_rate)
            self.raster_set.add(raster)

        progress.setLabelText("Loading graphical elements")
        progress.setValue(37)

        sub_splitter = QtWidgets.QSplitter(self)
        sub_splitter.setOrientation(QtCore.Qt.Vertical)
        channel_and_search = QtWidgets.QWidget(sub_splitter)
        # self.splitter.setSizes([2,8])

        vbox = QtWidgets.QVBoxLayout(channel_and_search)
        vbox.setSpacing(2)

        self.select_all_btn = QtWidgets.QPushButton("", channel_and_search)
        self.select_all_btn.setToolTip("Select all channels")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/images/check3"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.select_all_btn.setIcon(icon1)
        self.select_all_filter_btn.setIcon(icon1)

        self.clear_channels_btn = QtWidgets.QPushButton("", channel_and_search)
        self.clear_channels_btn.setToolTip("Reset selection")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/images/reset4.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.clear_channels_btn.setIcon(icon)
        self.clear_channels_btn.setObjectName("clear_channels_btn")

        self.advanced_search_btn = QtWidgets.QPushButton("", channel_and_search)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/images/search3.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.advanced_search_btn.setIcon(icon)
        self.advanced_search_btn.setToolTip("Advanced search and select channels")
        self.advanced_search_btn.clicked.connect(self.search)

        self.add_basket_btn = QtWidgets.QPushButton("", channel_and_search)
        self.add_basket_btn.setToolTip("Insert channels to Custom Basket")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/images/basket2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.add_basket_btn.setIcon(icon1)

        self.delete_basket_btn = QtWidgets.QPushButton("", channel_and_search)
        self.delete_basket_btn.setToolTip("Delete channels from Custom Basket")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/images/delete2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.delete_basket_btn.setIcon(icon1)

        self.load_channel_list_btn = QtWidgets.QPushButton("", channel_and_search)
        self.load_channel_list_btn.setToolTip("Load saved configuration")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/images/upload2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.load_channel_list_btn.setIcon(icon1)
        self.load_channel_list_btn.setObjectName("load_channel_list_btn")

        self.save_channel_list_btn = QtWidgets.QPushButton("", channel_and_search)
        self.save_channel_list_btn.setToolTip("Save configuration")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/images/download2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.save_channel_list_btn.setIcon(icon2)
        self.save_channel_list_btn.setObjectName("save_channel_list_btn")

        self.create_window_btn = QtWidgets.QPushButton("", channel_and_search)
        self.create_window_btn.setToolTip("Create window using the checked channels")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/images/channel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.create_window_btn.setIcon(icon3)
        self.create_window_btn.setObjectName("create_window_btn")

        # self.user_channel_btn = QtWidgets.QPushButton("", channel_and_search)
        # self.user_channel_btn.setToolTip("Set User Defined Channels")
        # icon1 = QtGui.QIcon()
        # icon1.addPixmap(
        #     QtGui.QPixmap(":/images/plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
        # )
        # self.user_channel_btn.setIcon(icon1)

        hbox = QtWidgets.QHBoxLayout()

        hbox.addWidget(self.select_all_btn)
        hbox.addWidget(self.clear_channels_btn)
        hbox.addWidget(self.advanced_search_btn)
        hbox.addWidget(self.add_basket_btn)
        hbox.addWidget(self.delete_basket_btn)
        self.delete_basket_btn.setVisible(False)
        hbox.addWidget(self.load_channel_list_btn)
        hbox.addWidget(self.save_channel_list_btn)
        # hbox.addWidget(self.user_channel_btn)
        hbox.addWidget(self.create_window_btn)

        hbox.addSpacerItem(
            QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
        )
        vbox.addLayout(hbox)

        self.channel_view = QtWidgets.QComboBox()
        self.channel_view.addItems(["Natural sort", "Internal file structure", "Unit sort", "[Custom Basket]"])
        self.channel_view.currentIndexChanged.connect(self._update_channel_tree)
        self.channel_view.setCurrentIndex(0)
        vbox.addWidget(self.channel_view)

        self.channels_tree = TreeWidget(self)
        self.channels_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.channels_tree.setAcceptDrops(True)
        self.channels_tree.setHeaderLabel("Channels")
        self.channels_tree.setToolTip(
            "Right click channel to see extended information"
        )
        self.channels_tree.itemDoubleClicked.connect(self.item_clicked)
        self.channels_tree.items_rearranged.connect(self.reorder_basket)
        self.channels_tree.setCursor(QtCore.Qt.PointingHandCursor)
        # self.channels_tree.itemClicked.connect(self.item_clicked)
        self.channels_tree.itemSelectionChanged.connect(self.item_clicked)
        self.channels_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.channels_tree.customContextMenuRequested.connect(self.open_menu)

        vbox.addWidget(self.channels_tree, 1)

        self.mdi_area = MdiAreaWidget()
        self.mdi_area.add_window_request.connect(self.add_window)
        self.mdi_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.splitter.addWidget(self.mdi_area)
        self.splitter.setSizes([300, 2100])
        self.channels_layout.insertWidget(0, sub_splitter)

        self.filter_view = QtWidgets.QComboBox()
        self.filter_view.addItems(["[Custom Basket]"])
        self.filter_view.setCurrentIndex(0)
        self.filter_view.currentIndexChanged.connect(self._update_channel_tree)
        self.filter_layout.addWidget(self.filter_view, 1, 0, 1, 1)

        self.filter_tree = TreeWidget(self)
        self.filter_tree.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.filter_tree.setObjectName("filter_tree")
        self.filter_tree.setHeaderLabel("Channels")
        self.filter_tree.setToolTip("Right click channel to see extended information")
        self.filter_tree.items_rearranged.connect(self.reorder_basket)
        self.filter_tree.itemDoubleClicked.connect(self.item_clicked)
        self.filter_tree.setCursor(QtCore.Qt.PointingHandCursor)
        self.filter_tree.itemClicked.connect(self.item_clicked)
        self.filter_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.filter_tree.customContextMenuRequested.connect(self.open_menu)
        self.filter_layout.addWidget(self.filter_tree, 2, 0, 13, 1)

        progress.setValue(70)

        self.raster_type_channel.toggled.connect(self.set_raster_type)

        progress.setValue(90)

        self.resample_format.insertItems(0, SUPPORTED_VERSIONS)
        index = self.resample_format.findText(self.mdf.version)
        if index >= 0:
            self.resample_format.setCurrentIndex(index)
        self.resample_compression.insertItems(
            0, ("no compression", "deflate", "transposed deflate")
        )
        self.resample_split_size.setValue(10)
        self.resample_btn.clicked.connect(self.resample)

        self.filter_format.insertItems(0, SUPPORTED_VERSIONS)
        index = self.filter_format.findText(self.mdf.version)
        if index >= 0:
            self.filter_format.setCurrentIndex(index)
        self.filter_compression.insertItems(
            0, ("no compression", "deflate", "transposed deflate")
        )
        self.filter_split_size.setValue(10)

        self.convert_format.insertItems(0, SUPPORTED_VERSIONS)
        self.convert_compression.insertItems(
            0, ("no compression", "deflate", "transposed deflate")
        )
        self.convert_split_size.setValue(10)
        self.convert_btn.clicked.connect(self.convert)

        self.cut_format.insertItems(0, SUPPORTED_VERSIONS)
        index = self.cut_format.findText(self.mdf.version)
        if index >= 0:
            self.cut_format.setCurrentIndex(index)
        self.cut_compression.insertItems(
            0, ("no compression", "deflate", "transposed deflate")
        )
        self.cut_split_size.setValue(10)
        self.cut_btn.clicked.connect(self.cut)

        self.cut_interval.hide()

        # self.extract_can_format.insertItems(0, SUPPORTED_VERSIONS)
        # index = self.extract_can_format.findText(self.mdf.version)
        # if index >= 0:
        #     self.extract_can_format.setCurrentIndex(index)
        # self.extract_can_compression.insertItems(
        #     0, ("no compression", "deflate", "transposed deflate")
        # )
        # self.extract_can_btn.clicked.connect(self.extract_can_logging)
        # self.extract_can_csv_btn.clicked.connect(self.extract_can_csv_logging)
        # self.load_can_database_btn.clicked.connect(self.load_can_database)

        # if self.mdf.version >= "4.00":
        #     if any(
        #         group.channel_group.flags & FLAG_CG_BUS_EVENT
        #         for group in self.mdf.groups
        #     ):
        #         self.aspects.setTabEnabled(7, True)
        #     else:
        #         self.aspects.setTabEnabled(7, False)
        # else:
        #     self.aspects.setTabEnabled(7, False)

        progress.setValue(99)

        self.cut_start.setSingleStep(0.001)
        self.cut_start.setDecimals(3)
        self.cut_stop.setSingleStep(0.001)
        self.cut_stop.setDecimals(3)
        self.raster.setSingleStep(0.001)
        self.raster.setDecimals(3)

        self.empty_channels.insertItems(0, ("skip", "zeros"))
        self.empty_channels_can.insertItems(0, ("skip", "zeros"))
        self.mat_format.insertItems(0, ("4", "5", "7.3"))
        self.oned_as.insertItems(0, ("row", "column"))
        self.export_type.insertItems(0, ("csv", "mdf", "mat"))
        self.export_compression.setEnabled(False)
        self.empty_channels.setEnabled(False)
        self.mat_format.setEnabled(False)
        self.oned_as.setEnabled(False)
        self.export_btn.clicked.connect(self.export)
        self.export_type.currentTextChanged.connect(self.export_changed)
        self.export_type.setCurrentIndex(0)

        # info tab
        file_stats = os.stat(self.mdf.name)
        file_info = QtWidgets.QTreeWidgetItem()
        file_info.setText(0, "File information")

        self.info.addTopLevelItem(file_info)

        children = []

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Path")
        item.setText(1, str(self.mdf.name))
        children.append(item)

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Size")
        item.setText(1, f"{file_stats.st_size / 1024 / 1024:.1f} MB")
        children.append(item)

        date_ = datetime.fromtimestamp(file_stats.st_ctime)
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Created")
        item.setText(1, date_.strftime("%d-%b-%Y %H-%M-%S"))
        children.append(item)

        date_ = datetime.fromtimestamp(file_stats.st_mtime)
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Last modified")
        item.setText(1, date_.strftime("%d-%b-%Y %H:%M:%S"))
        children.append(item)

        file_info.addChildren(children)

        mdf_info = QtWidgets.QTreeWidgetItem()
        mdf_info.setText(0, "MDF information")

        self.info.addTopLevelItem(mdf_info)

        children = []

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Version")
        item.setText(1, self.mdf.version)
        children.append(item)

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Program identification")
        item.setText(
            1,
            self.mdf.identification.program_identification.decode("ascii").strip(
                " \r\n\t\0"
            ),
        )
        children.append(item)

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Measurement start time")
        item.setText(
            1, self.mdf.header.start_time.strftime("%d-%b-%Y %H:%M:%S + %fus UTC")
        )
        children.append(item)

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "Measurement comment")
        item.setText(1, self.mdf.header.comment)
        item.setTextAlignment(0, QtCore.Qt.AlignTop)
        children.append(item)

        # channels = QtWidgets.QTreeWidgetItem()
        # channels.setText(0, "Total channel count")
        # channels.setText(
        #     1, str(sum(len(entry) for entry in self.mdf.channels_db.values()))
        # )
        # children.append(channels)

        channel_groups = QtWidgets.QTreeWidgetItem()
        channel_groups.setText(0, "Channel groups")
        channel_groups.setText(1, str(len(self.mdf.groups)))
        children.append(channel_groups)

        channel_groups_children = []
        for i, group in enumerate(self.mdf.groups):
            channel_group = group.channel_group
            if hasattr(channel_group, "comment"):
                comment = channel_group.comment
            else:
                comment = ""
            if comment:
                name = f"Channel group {i} ({comment})"
            else:
                name = f"Channel group {i}"

            cycles = channel_group.cycles_nr
            if self.mdf.version < "4.00":
                size = channel_group.samples_byte_nr * cycles
            else:
                if channel_group.flags & 0x1:
                    size = channel_group.samples_byte_nr + (
                        channel_group.invalidation_bytes_nr << 32
                    )
                else:
                    size = (
                        channel_group.samples_byte_nr
                        + channel_group.invalidation_bytes_nr
                    ) * cycles

            channel_group = QtWidgets.QTreeWidgetItem()
            channel_group.setText(0, name)

            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, "Channels")
            item.setText(1, f"{len(group.channels)}")
            channel_group.addChild(item)

            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, "Cycles")
            item.setText(1, str(cycles))
            channel_group.addChild(item)

            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, "Raw size")
            item.setText(1, f"{size / 1024 / 1024:.1f} MB")
            channel_group.addChild(item)

            channel_groups_children.append(channel_group)

        channel_groups.addChildren(channel_groups_children)

        unit_groups = QtWidgets.QTreeWidgetItem()
        unit_groups.setText(0, "Unit info")
        children.append(unit_groups)

        unit_group = set()

        for group in self.mdf.groups:
            for ch in group.channels:
                unit_group.add(self.mdf.get_channel_unit(ch.name))

        unit_group = list(unit_group)
        unit_group.sort(key=lambda x: x.upper())

        for i, unit in enumerate(unit_group):
            if unit != "":
                unit_group = TreeItem((i, 0), mdf_uuid=self.uuid)
                unit_group.setText(0, unit)
                unit_groups.addChild(unit_group)

        mdf_info.addChildren(children)

        self.info.expandAll()

        self.info.header().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )

        self.aspects.setCurrentIndex(0)
        self.aspects.currentChanged.connect(self.aspect_changed)

        progress.setValue(100)
        progress.deleteLater()

        self.create_window_btn.clicked.connect(self._create_window)
        self.clear_channels_btn.clicked.connect(self.clear_channels)
        self.load_channel_list_btn.clicked.connect(partial(self.load_channel_list,None))
        self.save_channel_list_btn.clicked.connect(self.save_channel_list)
        self.select_all_btn.clicked.connect(self.select_all_channels)
        self.select_all_filter_btn.clicked.connect(self.select_all_channels)
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        self.add_basket_btn.clicked.connect(self.add_basket)
        self.delete_basket_btn.clicked.connect(self.delete_basket)
        self.delete_filter_btn.clicked.connect(self.delete_basket)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        self.whence.toggled.connect(self.whence_changed)
        self.time_from_zero.toggled.connect(self.time_from_zero_changed)
        #YDA 2020-10-08 *UDC*
        # self.user_channel_btn.clicked.connect(self.show_name_info_dialog)

        self.aspects.setTabVisible(1, False)
        self.aspects.setTabVisible(2, False)
        self.aspects.setTabVisible(3, False)
        self.aspects.setTabVisible(5, True)
        self.aspects.setTabVisible(6, True)
        self.aspects.setTabVisible(7,False)
        self.aspects.setTabEnabled(1, False)
        self.aspects.setTabEnabled(2, False)
        self.aspects.setTabEnabled(3, False)
        self.aspects.setTabEnabled(5, False)
        self.aspects.setTabEnabled(6, False)
        self.aspects.setTabEnabled(7, False)
        self.setAcceptDrops(True)

        self._update_channel_tree()

    def whence_changed(self):
        if self.whence.checkState() == self.time_from_zero.checkState() == QtCore.Qt.Checked:
            self.time_from_zero.setCheckState(QtCore.Qt.Unchecked)

    def time_from_zero_changed(self):
        if self.whence.checkState() == self.time_from_zero.checkState() == QtCore.Qt.Checked:
            self.whence.setCheckState(QtCore.Qt.Unchecked)


    def open_menu(self, position):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
        else:
            widget = self.channels_tree

        item = widget.itemAt(position)
        if item is None:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(self.tr("Show info"))

        action = menu.exec_(widget.viewport().mapToGlobal(position))
        if action is None:
            return
        if action.text() == "Show info":
            self.show_info(item,0)

    def item_clicked(self):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
        else:
            widget = self.channels_tree
        items = widget.selectedItems()
        for item in items:
            checked = item.checkState(0)

            if checked == QtCore.Qt.Checked:
                item.setCheckState(0, QtCore.Qt.Unchecked)
            else:
                item.setCheckState(0, QtCore.Qt.Checked)

    def set_raster_type(self, event):
        if self.raster_type_channel.isChecked():
            self.raster_channel.setEnabled(True)
            self.raster.setEnabled(False)
            self.raster.setValue(0)
        else:
            self.raster_channel.setEnabled(False)
            self.raster_channel.setCurrentIndex(0)
            self.raster.setEnabled(True)

    def _update_channel_tree(self, index=None):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
            view = self.filter_view
            self._settings.setValue("filter_view", self.filter_view.currentText())
            widget.clear()

            if len(self.basket) == 0:
                return
            items = self.basket
            for item in items:
                channel = TreeItem(item.entry, item.name, mdf_uuid=self.uuid)
                channel.setText(0, item.name)
                channel.setCheckState(0, QtCore.Qt.Unchecked)
                # channel.setForeground(0, QtGui.QBrush(QtGui.QColor("#0000ff")))
                # channel.setBackground(0, QtGui.QBrush(QtGui.QColor("#e2e2e2")))
                widget.addTopLevelItem(channel)
            return
        else:
            widget = self.channels_tree
            view = self.channel_view
            self._settings.setValue("channels_view", self.channel_view.currentText())
            widget.setProperty("channels_view",self.channel_view.currentIndex())

        if view.currentIndex() == -1:
            return

        iterator = QtWidgets.QTreeWidgetItemIterator(widget)
        signals = set()

        if view.currentText() == "[Custom Basket]":
            self.add_basket_btn.setVisible(False)
            self.delete_basket_btn.setVisible(True)
            # self.user_channel_btn.setVisible(True)
        else:
            self.add_basket_btn.setVisible(True)
            self.delete_basket_btn.setVisible(False)
            # self.user_channel_btn.setVisible(False)
            if view.currentText() == "Natural sort":
                while iterator.value():
                    item = iterator.value()

                    if item.entry[1] != 0xFFFFFFFFFFFFFFFF:
                        if item.checkState(0) == QtCore.Qt.Checked:
                            signals.add(item.entry)

                    iterator += 1
            else:
                while iterator.value():
                    item = iterator.value()

                    if item.checkState(0) == QtCore.Qt.Checked:
                        signals.add(item.entry)

                    iterator += 1

        widget.clear()

        if view.currentText() == "Natural sort":
            items = []
            for i, group in enumerate(self.mdf.groups):
                for j, ch in enumerate(group.channels):
                    entry = i, j

                    if ch.name == "time":
                        continue

                    channel = TreeItem(entry, ch.name, mdf_uuid=self.uuid)
                    channel.setText(0, ch.name)
                    if entry in signals:
                        channel.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        channel.setCheckState(0, QtCore.Qt.Unchecked)

                    if entry in self.basket_entry:
                        channel.setForeground(0,QtGui.QBrush(QtGui.QColor("#0000ff")))
                        channel.setBackground(0,QtGui.QBrush(QtGui.QColor("#e2e2e2")))
                        channel.setFont(0, QtGui.QFont("Gulim", weight=QtGui.QFont.Bold))
                    else:
                        channel.setForeground(0,QtGui.QBrush(QtGui.QColor("#000000")))

                    items.append(channel)

            if len(items) < 30000:
                items = natsorted(items, key=lambda x: x.name)
            else:
                items.sort(key=lambda x: x.name)
            widget.addTopLevelItems(items)
        elif view.currentText() == "Internal file structure":
            for i, group in enumerate(self.mdf.groups):
                entry = i, 0xFFFFFFFFFFFFFFFF
                channel_group = TreeItem(entry, mdf_uuid=self.uuid)
                comment = group.channel_group.comment
                comment = extract_cncomment_xml(comment)

                if comment:
                    channel_group.setText(0, f"Channel group {i} ({comment})")
                else:
                    channel_group.setText(0, f"Channel group {i}")

                channel_group.setFlags(
                    channel_group.flags()
                    | QtCore.Qt.ItemIsTristate
                    | QtCore.Qt.ItemIsUserCheckable
                )

                widget.addTopLevelItem(channel_group)

                channels = [
                    HelperChannel(name=ch.name, entry=(i, j))
                    for j, ch in enumerate(group.channels)
                ]

                add_children(
                    channel_group,
                    channels,
                    group.channel_dependencies,
                    signals,
                    self.basket_entry,
                    entries=None,
                    mdf_uuid=self.uuid,
                )
        elif self.channel_view.currentText() =="Unit sort":
            unit_group = set()
            items = []

            for group in self.mdf.groups:
                for ch in group.channels:
                    unit_group.add(self.mdf.get_channel_unit(ch.name))

            unit_group = list(unit_group)
            unit_group.sort(key=lambda x: x.upper())

            for i, unit in enumerate(unit_group):
                unit_group = TreeItem((i, 0), mdf_uuid=self.uuid)
                if unit == "":
                    unit_group.setText(0, f"unit  ( )")
                else:
                    unit_group.setText(0, f"unit  ({unit})")
                unit_group.setFlags(
                    unit_group.flags()
                    | QtCore.Qt.ItemIsTristate
                    | QtCore.Qt.ItemIsUserCheckable
                )

                items = []

                for i, group in enumerate(self.mdf.groups):
                    for j, ch in enumerate(group.channels):
                        entry = i, j
                        if ch.name == "time":
                            continue

                        if unit == self.mdf.get_channel_unit(ch.name):

                            channel = TreeItem(entry, ch.name, mdf_uuid=self.uuid)
                            channel.setText(0, ch.name)

                            if entry in signals:
                                channel.setCheckState(0, QtCore.Qt.Checked)
                            else:
                                channel.setCheckState(0, QtCore.Qt.Unchecked)

                            if entry in self.basket_entry:
                                channel.setForeground(0, QtGui.QBrush(QtGui.QColor("#0000ff")))
                                channel.setBackground(0, QtGui.QBrush(QtGui.QColor("#e2e2e2")))
                                channel.setFont(0, QtGui.QFont("Gulim", weight=QtGui.QFont.Bold))
                            else:
                                channel.setForeground(0, QtGui.QBrush(QtGui.QColor("#000000")))
                            items.append(channel)
                if len(items) == 0:
                    continue
                else:
                    widget.addTopLevelItem(unit_group)
                    if len(items) < 30000:
                        items = natsorted(items, key=lambda x: x.name.upper())
                    else:
                        items.sort(key=lambda x: x.name.upper())
                    unit_group.addChildren(items)

            widget.addTopLevelItems(items)
        else:
            if len(self.basket) == 0:
                return
            items = self.basket
            for item in items:
                channel = TreeItem(item.entry, item.name, mdf_uuid=self.uuid)
                channel.setText(0, item.name)
                channel.setCheckState(0, QtCore.Qt.Unchecked)
                # channel.setForeground(0, QtGui.QBrush(QtGui.QColor("#0000ff")))
                # channel.setBackground(0, QtGui.QBrush(QtGui.QColor("#e2e2e2")))
                widget.addTopLevelItem(channel)

    def export_changed(self, name):
        if name == "mat":
            self.export_compression.setEnabled(True)
            self.export_compression.clear()
            self.export_compression.addItems(["enabled", "disabled"])
            self.export_compression.setCurrentIndex(-1)
            self.empty_channels.setEnabled(True)
            self.mat_format.setEnabled(True)
            self.oned_as.setEnabled(True)
        else:
            self.export_compression.clear()
            self.export_compression.setEnabled(False)
            self.empty_channels.setEnabled(False)
            self.mat_format.setEnabled(False)
            self.oned_as.setEnabled(False)

    def search(self):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Channels":
            show_add_window = True
            widget = self.channels_tree
        else:
            show_add_window = True
            widget = self.filter_tree
        dlg = AdvancedSearch(
            self.mdf.channels_db, show_add_window=show_add_window, parent=self,
        )
        dlg.setModal(True)
        dlg.exec_()
        to_basket = dlg.to_basket
        result = dlg.result
        if result:
            self.channel_view.setCurrentIndex(0)

            names = set()

            iterator = QtWidgets.QTreeWidgetItemIterator(widget)
            while iterator.value():
                item = iterator.value()

                if item.entry in result:
                    item.setCheckState(0, QtCore.Qt.Checked)
                    names.add(item.text(0))

                    if to_basket:
                        if item.entry not in self.basket_entry:
                            self.basket_entry.add(item.entry)
                            self.basket.append(item)
                iterator += 1
            if to_basket:
                self.channel_view.setCurrentIndex(3)
            else:
                self.channel_view.setCurrentIndex(0)
            self._update_channel_tree()

    def to_config(self):
        config = {}
        basket_signals = []

        for item in self.basket:
            basket_signals.append(item.name)

        config["selected_channels"] = [basket_signals]
        config["file_path"] = [str(self.file_name)]
        #yda 2020-10-13 *UDC*
        # config["current_udc"] = [self.udc_dict["udc_filename"]]
        # config["current_udc"] = ""

        windows = []
        for window in self.mdi_area.subWindowList():
            wid = window.widget()
            window_config = {
                "title": window.windowTitle(),
                "configuration": wid.to_config(),
            }
            if isinstance(wid, Plot):
                if wid.tabular:
                    window_config["type"] = "Plot+Tabular"
                else:
                    window_config["type"] = "Plot"
            else:
                window_config["type"] = "Tabular"
            windows.append(window_config)
        config["windows"] = windows

        return config

    def save_channel_list(self, event=None, file_name=None):
        if file_name is None:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Select output channel list file", "", "CFG files (*.cfg)"
            )
        if file_name:
            Path(file_name).write_text(
                json.dumps(self.to_config(), indent=4, sort_keys=True)
            )

    def load_channel_list(self, file_name=None):
        if file_name is None:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Select channel list file",
                "",
                "Config file (*.cfg);;TXT files (*.txt);;Display files (*.dsp);;CANape Lab file (*.lab);;All file types (*.cfg *.dsp *.lab *.txt)",
                "All file types (*.cfg *.dsp *.lab *.txt)",
            )

        if file_name:
            if not isinstance(file_name, dict):
                file_name = Path(file_name)

                extension =  file_name.suffix.lower()
                if extension == ".dsp":
                    info = load_dsp(file_name)
                    channels = info.get("display", [])

                elif extension == ".lab":
                    info = load_lab(file_name)
                    if info:
                        section, ok = QtWidgets.QInputDialog.getItem(
                            None,
                            "Select section",
                            "Available sections:",
                            list(info),
                            0,
                            False,
                        )
                        if ok:
                            channels = info[section]
                        else:
                            return

                elif extension in ('.cfg', '.txt'):
                    with open(file_name, "r") as infile:
                        info = json.load(infile)
                    channels = info.get("selected_channels", [])
                    #yda 2020-10-13 *UDC*
                    # udc_file = info.get("current_udc", [])
            else:
                info = file_name
                channels = info.get("selected_channels", [])
                # yda 2020-10-13 *UDC*
                # udc_file = info.get("current_udc", [])

            #yda 2020-10-13 *UDC*
            # if udc_file:
            #     self.loaded_udc = udc_file[0]
            if channels:
                channels = channels[0]
                widget = self.channels_tree
                view = self.channel_view
                view.setCurrentIndex(0)
                self._settings.setValue("channels_view", self.channel_view.currentText())

                for channel in channels:
                    iterator = QtWidgets.QTreeWidgetItemIterator(widget)
                    while iterator.value():
                        item = iterator.value()
                        channel_name = item.text(0)

                        if channel_name == channel and item.entry not in self.basket_entry:
                            self.basket.append(item)
                            self.basket_entry.add(item.entry)
                        iterator += 1
            self._update_channel_tree()
            for window in info.get("windows", []):
                self.load_window(window)

    def compute_cut_hints(self):
        t_min = []
        t_max = []
        for i, group in enumerate(self.mdf.groups):
            cycles_nr = group.channel_group.cycles_nr
            if cycles_nr:
                master_min = self.mdf.get_master(i, record_offset=0, record_count=1,)
                if len(master_min):
                    t_min.append(master_min[0])
                self.mdf._master_channel_cache.clear()
                master_max = self.mdf.get_master(
                    i, record_offset=cycles_nr - 1, record_count=1,
                )
                if len(master_max):
                    t_max.append(master_max[0])
                self.mdf._master_channel_cache.clear()

        if t_min:
            time_range = t_min, t_max

            self.cut_start.setRange(*time_range)
            self.cut_stop.setRange(*time_range)

            self.cut_interval.setText(
                "Cut interval ({:.6f}s - {:.6f}s)".format(*time_range)
            )
        else:
            self.cut_start.setRange(0, 0)
            self.cut_stop.setRange(0, 0)

            self.cut_interval.setText("Empty measurement")

    def update_progress(self, current_index, max_index):
        self.progress = current_index, max_index

    #YDA 2020-10-08 *UDC*
    # def show_name_info_dialog(self):
    #     basket = []
    #     for item in self.basket:
    #         basket.append(item.name)
    #
    #     file_name = "\\UserDefinedChannel.List"
    #     file_name = Path(self.environ_path + file_name)
    #
    #     if os.path.isfile(file_name):
    #         with open(file_name, "r") as infile:
    #             info = json.load(infile)
    #         items = info.get("user-defined name list", [])
    #
    #     loaded_udc = self.loaded_udc
    #
    #     dialog = NameInfo(basket, items, loaded_udc)
    #     dialog.apply_alternative_names_signal.connect(self.get_udc_dict)
    #     dialog.exec_()

    #yda 2020-10-08 *UDC*
    # def get_udc_dict(self, udc_dict):
    #     self.udc_dict = udc_dict
    #     print(self.udc_dict)

    def show_info(self, item, column):
        group_index, index = item.entry
        if index == 0xFFFFFFFFFFFFFFFF:
            group = self.mdf.groups[group_index]
            msg = ChannelGroupInfoDialog(self.mdf, group, group_index, self)
            msg.show()
        else:
            channel = self.mdf.get_channel_metadata(group=group_index, index=index)
            msg = ChannelInfoDialog(channel, self)
            msg.show()

    def clear_filter(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.filter_tree)
        while iterator.value():
            item = iterator.value()
            item.setCheckState(0, QtCore.Qt.Unchecked)
            iterator += 1

    def clear_channels(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.channels_tree)

        if self.channel_view.currentIndex() == 0 or self.channel_view.currentIndex() == 3:
            while iterator.value():
                item = iterator.value()
                item.setCheckState(0, QtCore.Qt.Unchecked)
                iterator += 1
        else:
            while iterator.value():
                item = iterator.value()
                if item.parent() is None:
                    item.setExpanded(False)
                else:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                iterator += 1

    def select_all_channels(self):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
            iterator = QtWidgets.QTreeWidgetItemIterator(widget)

            while iterator.value():
                item = iterator.value()
                item.setCheckState(0, QtCore.Qt.Checked)
                iterator += 1
        else:
            widget = self.channels_tree
            view = self.channel_view
            iterator = QtWidgets.QTreeWidgetItemIterator(widget)

            if view.currentIndex() == 0 or view.currentIndex() == 3 :
                while iterator.value():
                    item = iterator.value()
                    item.setCheckState(0, QtCore.Qt.Checked)
                    iterator += 1
            else:
                while iterator.value():
                    item = iterator.value()
                    if item.parent() is None:
                        item.setExpanded(False)
                    else:
                        item.setCheckState(0, QtCore.Qt.Checked)
                    iterator += 1

    def add_basket(self):
        widget = self.channels_tree
        iterator = QtWidgets.QTreeWidgetItemIterator(widget)
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == QtCore.Qt.Checked and item.childCount()==0:
                if item.entry not in self.basket_entry:
                    self.basket_entry.add(item.entry)
                    self.basket.append(item)
            iterator +=1
        self._update_channel_tree()

    def delete_basket(self):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Channels":
            widget = self.channels_tree
        else:
            widget = self.filter_tree
        iterator = QtWidgets.QTreeWidgetItemIterator(widget)
        index = 0
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == QtCore.Qt.Checked:
                self.basket.pop(index)
                self.basket_entry.remove(item.entry)
            else:
                index +=1
            iterator +=1
        self._update_channel_tree()
        self.raster_channel.clear()

        if len(self.basket) == 0:
            return

        items = self.basket
        for item in items:
            self.raster_channel.addItem(item.name)

    def reorder_basket(self):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
        else:
            widget = self.channels_tree
        iterator = QtWidgets.QTreeWidgetItemIterator(widget)
        self.basket_entry = set()
        self.basket = []
        while iterator.value():
            item = iterator.value()
            self.basket_entry.add(item.entry)
            self.basket.append(item)
            iterator += 1

    def closeEvent(self, event):
        self.close_subwindow.emit(self, True)

    def save_last_work(self, info):
        if self._settings.value("open_option") == "Mode Off":
            return
        file_name = '\\' + str(self.mdf.name).split("\\")[-1] + ".cfg"
        file_name = Path(self.environ_path + file_name)

        if file_name:
            Path(file_name).write_text(
                json.dumps(info, indent=4, sort_keys=True)
            )
        return

    def before_close(self, msg_request):
        if self._settings.value("open_option") == "Mode Off":
            return
        config = self.to_config()
        if msg_request:
            reply = QtGui.QMessageBox.question(self, 'Message',
                                               "Do you want to save current works?", QtGui.QMessageBox.Yes |
                                               QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        else:
            reply = QtGui.QMessageBox.Yes
        if reply == QtGui.QMessageBox.Yes:
            self.save_last_work(config)

    def close(self):
        mdf_name = self.mdf.name
        self.mdf.close()
        if self.file_name.suffix.lower() in (".dl3", ".erg"):
            mdf_name.unlink()
        self.channels_tree.clear()
        self.filter_tree.clear()
        self.mdf = None

    def convert(self, event):
        version = self.convert_format.currentText()

        if version < "4.00":
            filter = "MDF version 3 files (*.dat *.mdf)"
            suffix = ".mdf"
        else:
            filter = "MDF version 4 files (*.mf4)"
            suffix = ".mf4"

        split = self.convert_split.checkState() == QtCore.Qt.Checked
        if split:
            split_size = int(self.convert_split_size.value() * 1024 * 1024)
        else:
            split_size = 0

        self.mdf.configure(write_fragment_size=split_size)

        compression = self.convert_compression.currentIndex()

        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select output measurement file",
            "",
            f"{filter};;All files (*.*)",
            filter,
        )

        if file_name:
            file_name = Path(file_name).with_suffix(suffix)

            progress = setup_progress(
                parent=self,
                title="Converting measurement",
                message=f'Converting "{self.file_name}" from {self.mdf.version} to {version}',
                icon_name="convert",
            )

            # convert self.mdf
            target = self.mdf.convert
            kwargs = {"version": version}

            mdf = run_thread_with_progress(
                self,
                target=target,
                kwargs=kwargs,
                factor=50,
                offset=0,
                progress=progress,
            )

            if mdf is TERMINATED:
                progress.cancel()
                return

            mdf.configure(write_fragment_size=split_size)

            # then save it
            progress.setLabelText(f'Saving converted file "{file_name}"')

            target = mdf.save
            kwargs = {"dst": file_name, "compression": compression, "overwrite": True}

            run_thread_with_progress(
                self,
                target=target,
                kwargs=kwargs,
                factor=50,
                offset=50,
                progress=progress,
            )

            self.progress = None
            progress.cancel()

    def resample(self, mdf):

        version = self.mdf.version
        time_from_zero = self.time_from_zero.checkState() == QtCore.Qt.Checked

        if self.raster_type_channel.isChecked():
            raster = self.raster_channel.currentText()

            if raster == "":
                QtWidgets.QMessageBox.warning(None, "Message",
                                              "Channel name is not selected")
                mdf = TERMINATED
                return mdf
            group_index = self.mdf.channels_db[raster][0][0]
            raster = self.mdf.get_channel_metadata(raster, group_index).sampling_rate

        else:
            raster = self.raster.value()
            if raster == 0:
                QtWidgets.QMessageBox.warning(None, "Message",
                                              "Raster must be greater than 0.")
                mdf = TERMINATED
                return mdf

        progress = setup_progress(
            parent=self,
            title="Resampling measurement",
            message=f'Resampling "{self.file_name}" to {raster}s raster ',
            icon_name="resample",
        )

        # resample self.mdf
        target = mdf.resample
        kwargs = {
            "raster": raster,
            "version": version,
            "time_from_zero": time_from_zero,
        }

        mdf = run_thread_with_progress(
            self,
            target=target,
            kwargs=kwargs,
            factor=66,
            offset=0,
            progress=progress,
        )

        if mdf is TERMINATED:
            progress.cancel()
            return

        self.progress = None
        progress.cancel()

        if isinstance(raster,str):
            raster = self.mdf.get_channel_metadata(raster, self.mdf.get(raster).group_index).sampling_rate

        return mdf, raster

    def cut(self, mdf, min, max):
        version = mdf.version
        start = self.cut_start.value()
        stop = self.cut_stop.value()
        time_from_zero = self.time_from_zero.checkState() == QtCore.Qt.Checked

        if start == stop == 0:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          "Start value and End value is 0.")
            return TERMINATED

        if start > stop:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          "Start value is greater than End value.")
            return TERMINATED

        if start > max:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          f'Maximum time value is {max}')
            return TERMINATED

        if stop < min:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          f'Minimum time value is {min}')
            return TERMINATED

        if self.whence.checkState() == QtCore.Qt.Checked:
            whence = 1
        else:
            whence = 0

        progress = setup_progress(
            parent=self,
            title="Cutting measurement",
            message=f'Cutting "{self.file_name}" from {start}s to {stop}s',
            icon_name="cut",
        )

        # cut self.mdf
        target = mdf.cut
        kwargs = {
            "start": start,
            "stop": stop,
            "whence": whence,
            "version": version,
            "time_from_zero": time_from_zero,
        }

        mdf = run_thread_with_progress(
            self,
            target=target,
            kwargs=kwargs,
            factor=66,
            offset=0,
            progress=progress,
        )

        if mdf is TERMINATED:
            progress.cancel()
            return

        self.progress = None
        progress.cancel()

        return mdf

    def export(self, event):
        export_type = self.export_type.currentText()

        single_time_base = self.single_time_base.checkState() == QtCore.Qt.Checked
        time_from_zero = self.time_from_zero.checkState() == QtCore.Qt.Checked
        use_display_names = self.use_display_names.checkState() == QtCore.Qt.Checked
        empty_channels = self.empty_channels.currentText()
        mat_format = self.mat_format.currentText()
        raster = self.raster.value()
        oned_as = self.oned_as.currentText()
        reduce_memory_usage = self.reduce_memory_usage.checkState() == QtCore.Qt.Checked
        time_as_date = False

        iterator = QtWidgets.QTreeWidgetItemIterator(self.filter_tree)
        channels = []
        rasters = []
        columns = []

        if iterator.value() is None:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          "No channel item in custom basket.")
            return

        while iterator.value():
            item = iterator.value()
            checked = False
            if item.checkState(0) == QtCore.Qt.Checked:
                checked = True
                group, index = item.entry
                if index != 0xFFFFFFFFFFFFFFFF:
                    channels.append((item.name, group, index))
                    rasters.append(self.mdf.get_channel_metadata(item.name, group).sampling_rate)
                    columns.append(item.name)
                    # self.scene().exportDialog.min = np.amin(self.all_timebase)
                    # self.scene().exportDialog.max = np.amax(self.all_timebase)
            iterator += 1

        if not checked:
            QtWidgets.QMessageBox.warning(None, "Message",
                                          "Nothing selected.")
            return

        selected_signals = self.mdf.select(
            channels,
            ignore_value2text_conversions=self.ignore_value2text_conversions,
            copy_master=False,
            validate=True,
            raw=True,
        )

        timebases = [
            sig.timestamps
            for sig in selected_signals
        ]
        try:
            all_timebase = np.unique(np.concatenate(timebases))
        except MemoryError:
            all_timebase = reduce(np.union1d, timebases)

        min = all_timebase[0]
        max = all_timebase[-1]

        version = self.mdf.version

        if version < "4.00":
            filter = "MDF version 3 files (*.dat *.mdf)"
            suffix = ".mdf"
        else:
            filter = "MDF version 4 files (*.mf4)"
            suffix = ".mf4"

        split = self.filter_split.checkState() == QtCore.Qt.Checked
        if split:
            split_size = int(self.filter_split_size.value() * 1024 * 1024)
        else:
            split_size = 0

        self.mdf.configure(write_fragment_size=split_size)

        compression = self.filter_compression.currentIndex()

        progress = setup_progress(
            parent=self,
            title="Filtering measurement",
            message=f'Filtering selected channels from "{self.file_name}"',
            icon_name="filter",
        )

        # filtering self.mdf
        target = self.mdf.filter
        kwargs = {"channels": channels, "version": version}

        new_mdf = run_thread_with_progress(
            self,
            target=target,
            kwargs=kwargs,
            factor=33,
            offset=0,
            progress=progress,
        )

        if new_mdf is TERMINATED:
            progress.cancel()
            return

        self.progress = None
        progress.cancel()

        if self.cut_group.isChecked():
            new_mdf = self.cut(new_mdf, min, max)

        if new_mdf is TERMINATED:
            progress.cancel()
            return

        if self.resample_group.isChecked():
            if self.resample(new_mdf) == TERMINATED:
                progress.cancel()
                return
            new_mdf = self.resample(new_mdf)[0]
            raster = self.resample(new_mdf)[1]
        else:
            raster = None

        if new_mdf is TERMINATED:
            progress.cancel()
            return

        new_mdf.configure(write_fragment_size=split_size)

        filters = {
                "mdf": "mdf files (*.mdf)",
                "mf4": "mdf files (*.mf4)",
                "xlsx": "xlsx files (*.xlsx)",
                "csv": "CSV files (*.csv)",
                "hdf5": "HDF5 files (*.hdf)",
                "mat": "Matlab MAT files (*.mat)",
                "parquet": "Apache Parquet files (*.parquet)",
            }

        if export_type == "mdf":
            if float(self.mdf.version) >= 4:
                export_type = "mf4"

        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select export file",
            "",
            f"{filters[export_type]};;All files (*.*)",
            filters[export_type],
        )

        if file_name:
            progress = setup_progress(
                parent=self,
                title="Export measurement",
                message=f'Exporting "{self.file_name}" to {export_type}',
                icon_name="export",
            )

            if export_type in ("mdf", "mf4"):
                # then save it
                progress.setLabelText(f'Saving mdf file "{file_name}"')

                target = new_mdf.save
                kwargs = {"dst": file_name, "compression": compression, "overwrite": True}

                run_thread_with_progress(
                    self,
                    target=target,
                    kwargs=kwargs,
                    factor=34,
                    offset=66,
                    progress=progress,
                )

            else:
                if export_type == "mat":
                    if compression:
                        compression = True if compression == "enabled" else False
                    else:
                        compression = False

                # cut self.mdf
                target = new_mdf.export
                kwargs = {
                    "fmt": export_type,
                    "filename": file_name,
                    "single_time_base": single_time_base,
                    "use_display_names": use_display_names,
                    "time_from_zero": time_from_zero,
                    "empty_channels": empty_channels,
                    "format": mat_format,
                    "raster": raster,
                    "oned_as": oned_as,
                    "reduce_memory_usage": reduce_memory_usage,
                    "compression": compression,
                    "time_as_date": time_as_date,
                    "ignore_value2text_conversions" : self.ignore_value2text_conversions,
                    "columns":columns
                }

                new_mdf = run_thread_with_progress(
                    self,
                    target=target,
                    kwargs=kwargs,
                    factor=100,
                    offset=0,
                    progress=progress,
                )

                if new_mdf is TERMINATED:
                    progress.cancel()
                    return

            QtWidgets.QMessageBox.information(None, "Message",
                                          "Completed.")
            self.progress = None
            progress.cancel()

    def _create_window(self, event):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.channels_tree)
        checked = False
        rasters = set()

        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == QtCore.Qt.Checked:

                if item.entry[1] == 0xFFFFFFFFFFFFFFFF:
                    iterator += 1
                    continue
                if item.name == '':
                    iterator += 1
                    continue
                if item.name[0] == "$":
                    iterator += 1
                    continue
                checked = True
                raster = float(self.mdf.get_channel_metadata(item.name, item.entry[0]).sampling_rate)
                rasters.add(raster)
            iterator += 1
        if not checked:
            return

        raster_max = max(rasters)

        for raster in self.raster_set:
            rasters.add(raster)

        rasters = sorted(rasters,reverse=True)
        index = rasters.index(raster_max)

        raster_list = []
        for raster in rasters:
            raster_list.append(str(raster))

        ret, ok = QtWidgets.QInputDialog.getItem(
            self,
            "Select window type",
            "Type:",
            ["Plot", "Tabular", "Plot+Tabular"],
            0,
            False,
        )
        if not ok:
            return

        ret1, ok1 = QtWidgets.QInputDialog.getItem(
            self,
            "Select sampling rate",
            "Raster:",
            raster_list,
            index,
            False,
        )

        if ok and ok1:
            try:
                iter(event)
                signals = event
            except:
                iterator = QtWidgets.QTreeWidgetItemIterator(self.channels_tree)

                signals = []

                if self.channel_view.currentIndex() == 0 or self.channel_view.currentIndex() == 3:
                    while iterator.value():
                        item = iterator.value()

                        if item.checkState(0) == QtCore.Qt.Checked:
                            if item.name[0] == "$":
                                item.setCheckState(0, QtCore.Qt.Unchecked)
                                continue
                            group, index = item.entry
                            ch = self.mdf.groups[group].channels[index]
                            if not ch.component_addr:
                                signals.append((None, group, index, self.uuid))

                        iterator += 1
                else:
                    while iterator.value():
                        item = iterator.value()
                        if item.parent() is None:
                            iterator += 1
                            continue
                        if item.checkState(0) == QtCore.Qt.Checked:
                            if item.name[0] == "$":
                                item.setCheckState(0, QtCore.Qt.Unchecked)
                                continue
                            group, index = item.entry
                            ch = self.mdf.groups[group].channels[index]
                            if not ch.component_addr:
                                signals.append((None, group, index, self.uuid))

                        iterator += 1
            self.add_window((ret, signals, ret1))

    def move_up(self):
        widget = self.filter_tree
        selected = []

        for i in range(widget.topLevelItemCount()):
            if widget.topLevelItem(i).isSelected():
                selected.append(i)

        for index in selected:
            if index == 0:
                return
            else:
                item = self.basket[index]
                self.basket.pop(index)
                self.basket.insert(index - 1, item)
        self._update_channel_tree()
        for index in selected:
            widget.topLevelItem(index-1).setSelected(True)

    def move_down(self):
        widget = self.filter_tree
        selected = []

        for i in range(widget.topLevelItemCount()):
            if widget.topLevelItem(i).isSelected():
                selected.append(i)

        for index in reversed(selected):
            if index == widget.topLevelItemCount()-1:
                return
            else:
                item = self.basket[index]
                self.basket.pop(index)
                self.basket.insert(index + 1, item)
        self._update_channel_tree()
        for index in selected:
            widget.topLevelItem(index+1).setSelected(True)

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()

        if key == QtCore.Qt.Key_F and modifier == QtCore.Qt.ControlModifier:
            self.search()
        else:
            super().keyPressEvent(event)

    def aspect_changed(self, index):
        if self.aspects.tabText(self.aspects.currentIndex()) == "Export":
            widget = self.filter_tree
            widget.clear()
            self.raster_channel.clear()

            if len(self.basket) == 0:
                return

            items = self.basket

            for item in items:
                channel = TreeItem(item.entry, item.name, mdf_uuid=self.uuid)
                channel.setText(0, item.name)
                channel.setCheckState(0, QtCore.Qt.Checked)
                widget.addTopLevelItem(channel)

                self.raster_channel.addItem(item.name)

        elif self.aspects.tabText(self.aspects.currentIndex()) == "Channels":
            self._update_channel_tree()
        else:
            pass
