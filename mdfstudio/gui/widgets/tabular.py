# -*- coding: utf-8 -*-
# -------------------
""" Edit history
    Author : yda
    Date : 2020-11-26

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
    *	Tabular.__init__ : Fix format as phys, Create context menu connected with open_menu,  allow extendedSelection, show sampling rate, calculate time scale to get proper value of dataframe length to display
	*	Tabular.clicked : Emit signal to plot widget to set cursor on clicked value
	*	Tabular.build_request : Before building tabular, check valid singals and append signals to mdf as ordered
	*	Tabular.items_deleted : If all signals are deleted, do not build tabular
	*	Tabular.items_rearranged : If signals order is changed, reindex signals as rearraged and build again.
	*	Tabular.build : Delete remove_prefix function, calculate _min, _max value, modify calculation of count to apply real sampling rate not fixed value
	*	Tabular.from_plot : Select certain row of which timestamp comes from plot widget
	*	Tabular._display : Removed
	*	Tabular.to_config : Add raster value to configuration file
	*	Tabular.dragEnterEvent : Package name changed
	*	Tabular.dropEvent : Package name changed
	*	Tabular.open_menu : Add context menu - Copy
	*	Tabular.keyPressEvent : Disable key_up and key_down on treewidget. C+Ctrl to copy value
	*	Tabular.add_new_channels : Removed
	*	Tabular.time_as_date_changed : Removed
	*	Tabular.remove_prefix_changed : Removed
	*	Tabular.prefix_changed : Removed
	*   Tabular._scroll_tree : Removed
	*   Tabular.scroll_pressed : set with_scroll flag true when slider pressed/moved/released
	*   Tabular.calculate_pos : Calculate length of dataframe on each scroll position considering treewidget's height and signals's entire size
	*   Tabular.time_to_pos : Find scroll's position which contains certain timestamp and select the right row
	*   Tabular.check_bound : Set scroll's position when scroll moved. Fix errors from original source code (_scroll_tree)
	*   Tabular.display : Display partial dataframe on treewidget by scroll's position. Fix errors from original source code (_display)
"""

import datetime
import logging
from traceback import format_exc
import gc
import math

import numpy as np
import numpy.core.defchararray as npchar
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui

from ...blocks.utils import csv_bytearray2hex, csv_int2hex, pandas_query_compatible
from ..utils import extract_mime_names
from ..ui import resource_rc as resource_rc
from ..ui.tabular import Ui_TabularDisplay
from .tabular_filter import TabularFilter
from ...mdf import MDF

logger = logging.getLogger("mdfstudio.gui")
LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo


class Tabular(Ui_TabularDisplay, QtWidgets.QWidget):
    add_channels_request = QtCore.pyqtSignal(list)
    link_plot_signal = QtCore.pyqtSignal(float)
    delete_channels_request = QtCore.pyqtSignal(list)
    delete_cursor1_request =QtCore.pyqtSignal()

    def __init__(self, mdf=None, signals=None, start=0, inverted_dict=None, sampling_rate=99999, ignore_value2text_conversions=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.mdf_ = mdf
        self.start = start
        self.inverted_dict = inverted_dict
        self.ignore_value2text_conversions = ignore_value2text_conversions

        self.format = "phys"
        self._min = 99999999
        self._max = -99999999
        self._inhibit = False
        self.timestamp_ = -1
        self.rate = 99999
        self.columns = []

        self.with_scroll = False
        self.scroll_flag = 'max'
        self.prev_first = 0
        self.prev_last = 0

        if signals is None:
            self.signals = pd.DataFrame()
        else:
            dropped = {}

            signals = signals.drop(columns=list(dropped))
            for name, s in dropped.items():
                signals[name] = s
            self.signals = signals

        self.size = len(self.signals.index)
        self.view_count = -1
        self.current_pos = -1
        self.scroll_direction = None
        self.repeat_display = False
        self.max_pos = -1
        self.pos_array = []
        self.pass_display = False
        self.with_scroll = False

        self.setAcceptDrops(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_menu)
        self.tree_scroll.sliderPressed.connect(self.scroll_pressed)
        self.tree_scroll.sliderReleased.connect(self.scroll_pressed)
        self.tree_scroll.sliderMoved.connect(self.scroll_pressed)
        # self.tree.setStyleSheet("QTreeWidget::item:focused {background : #0076c8; color: 16777215;}") # fixed color

        self.tree.keyPressEvent = self.keyPressEvent

        if sampling_rate < self.rate:
            self.rate = sampling_rate

        self.label_raster.setText(f"[Sampling Rate : {self.rate}]")

        self.as_hex = [
            name.endswith(
                (
                    "CAN_DataFrame.ID",
                    "FLX_Frame.ID",
                    "FlexRay_DataFrame.ID",
                    "LIN_Frame.ID",
                    "MOST_DataFrame.ID",
                    "ETH_Frame.ID",
                )
            )
            for name in self.signals.columns
        ]

        self._original_index = self.signals.index.values

        self.time_scale = self.rate

        self.from_plot_signal = False

        self.build(self.mdf_, self.signals, True)
        self.repeat_display = True

        self.sort.stateChanged.connect(self.sorting_changed)
        self.tree.header().sortIndicatorChanged.connect(self._sort)

        self.tree_scroll.valueChanged.connect(self.display)
        self.tree.verticalScrollBar().valueChanged.connect(self.check_bound)
        self.tree.itemClicked.connect(self.clicked)

        self.sort.hide()

    def calculate_pos(self, window_height=None):
        if window_height is not None:
            self.view_count = int(window_height)
        else:
            self.view_count = int((self.tree.height() - self.tree.header().height()) / 12.2) + 1

        self.pos_array = []

        if self.size <= self.view_count * 5:
            if math.fmod(self.size, (self.view_count)) == 0:
                self.max_pos = int(self.size / (self.view_count)) + 0
            else:
                self.max_pos = int(self.size / (self.view_count)) + 1
            pos_data = (0, self.size-1, self.signals.index[0], self.signals.index[- 1], 0, self.size-1)
            self.pos_array.append(pos_data)
        else:
            self.repeat_display = True
            if math.fmod(self.size , (self.view_count)) == 0:
                self.max_pos = int(self.size / (self.view_count)) + 0
            else:
                self.max_pos = int(self.size / (self.view_count)) + 1
            for pos in range(self.max_pos):
                if pos == 0:
                    pos_data = (0, self.view_count - 1, self.signals.index[0], self.signals.index[self.view_count-1], 0, self.view_count * 5 - 1)
                elif pos == 1:
                    pos_data = (0, self.view_count * (pos+1) - 1, self.signals.index[0], self.signals.index[self.view_count * (pos+1) - 1], 0, self.view_count * 5 - 1)
                elif pos == self.max_pos-2:
                    pos_data = (self.view_count * (pos-1), self.size-1, self.signals.index[self.view_count * (pos-1)], self.signals.index[-1], self.view_count * (pos-3), self.size-1)
                elif pos == self.max_pos-1:
                    pos_data = (self.view_count * (pos-1), self.size-1, self.signals.index[self.view_count * (pos-1)], self.signals.index[-1], self.view_count * (pos-4), self.size-1)
                else:
                    if self.view_count * (pos+2) - 1 > self.size-1:
                        last_pos1 = self.size-1
                    else:
                        last_pos1 = self.view_count * (pos+2) - 1
                    if  self.view_count * (pos+3) - 1 > self.size-1:
                        last_pos2 = self.size - 1
                    else:
                        last_pos2 = self.view_count * (pos+3) - 1
                    pos_data = (self.view_count * (pos-1), last_pos1, self.signals.index[self.view_count * (pos-1)], self.signals.index[last_pos1], self.view_count * (pos-2),last_pos2)
                self.pos_array.append(pos_data)

        self.tree_scroll.setMaximum(self.max_pos)

    def time_to_pos(self, timestamp):
        self.tree.clearSelection()
        if len(self.signals.index) ==0:
            return
        if timestamp == self.signals.index[-1]:
            self.display(self.max_pos-1)
            self.tree.scrollToBottom()
            self.tree.findItems(str(timestamp), QtCore.Qt.MatchExactly, column=0)[0].setSelected(True)
            return

        for i in range(self.max_pos):
            if timestamp <= self.pos_array[i][3]:
                self.display(i)
                self.tree.scrollToItem(self.tree.findItems(str(timestamp), QtCore.Qt.MatchExactly, column=0)[0])
                self.tree.findItems(str(timestamp), QtCore.Qt.MatchExactly, column=0)[0].setSelected(True)
                return

    def check_bound(self, value):
        if not self.repeat_display:
            self.tree_scroll.setMaximum(self.tree.verticalScrollBar().maximum())
            self.tree_scroll.setMinimum(self.tree.verticalScrollBar().minimum())
            self.tree_scroll.setValue(self.tree.verticalScrollBar().value())
            if value == self.tree.verticalScrollBar().minimum() and self.tree_scroll.value() != self.tree_scroll.minimum() :
                if self.tree_scroll.minimum() != self.tree_scroll.value() and value !=0:
                    self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().value() + self.tree.verticalScrollBar().singleStep())
            elif value == self.tree.verticalScrollBar().maximum():
                if self.tree_scroll.maximum() != self.tree_scroll.value():
                    self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().value() - self.tree.verticalScrollBar().singleStep())
            if value == 0:
                self.tree_scroll.setValue(0)
            if value == self.tree.verticalScrollBar().maximum():
                self.tree_scroll.setValue(self.tree_scroll.maximum())
        else:
            pos = self.current_pos

            if value == self.tree.verticalScrollBar().minimum() and self.tree_scroll.value() != self.tree_scroll.minimum():
                if pos < 3:
                    self.pass_display = True
                else:
                    self.pass_display = False
                self.tree_scroll.setValue(pos - self.tree_scroll.singleStep())
                self.pass_display = False
                self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().value() + self.tree.verticalScrollBar().singleStep())

                if pos == 0 or pos == 1 or pos ==2:
                    pass
                elif pos == self.max_pos - 2:
                    self.tree.scrollToItem(self.tree.topLevelItem(self.tree.verticalScrollBar().maximum() + self.view_count))
                elif pos == self.max_pos - 1:
                    pass
                else:
                    self.tree.scrollToItem(self.tree.topLevelItem(self.tree.verticalScrollBar().maximum() - self.view_count * 2))
            elif value == self.tree.verticalScrollBar().maximum() and pos!=self.max_pos:
                if pos + 3 > self.max_pos :
                    self.pass_display = True
                else:
                    self.pass_display = False
                self.tree_scroll.setValue(pos + self.tree_scroll.singleStep())
                self.pass_display = False
                if pos < self.max_pos:
                    self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().value() - self.tree.verticalScrollBar().singleStep())
                    if pos + 2 < self.max_pos:
                        if pos == 0:
                            pass
                        elif pos == 1:
                            self.tree.scrollToItem(self.tree.topLevelItem(self.tree.verticalScrollBar().maximum()))
                        else:
                            self.tree.scrollToItem(self.tree.topLevelItem(self.tree.verticalScrollBar().maximum() - self.view_count))
                else:
                    self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().maximum())

    def display(self, pos):
        if self.pass_display:
            self.current_pos = pos
            return

        if not self.repeat_display :
            self.tree_scroll.setMaximum(self.tree.verticalScrollBar().maximum())
            self.tree_scroll.setMinimum(self.tree.verticalScrollBar().minimum())
            self.tree.verticalScrollBar().setValue(self.tree_scroll.value())
            return

        if pos >= self.max_pos:
            pos = self.max_pos-1
        if pos <= 0:
            pos = 0

        self.tree.clear()
        df_first_index = self.pos_array[pos][4]
        df_last_index = self.pos_array[pos][5]
        df = self.signals.iloc[df_first_index:df_last_index+1]

        if df.index.dtype.kind == "M":
            index = df.index.tz_localize("UTC").tz_convert(LOCAL_TIMEZONE)
        else:
            index = df.index
        items = [
            index.astype(str),
        ]

        for i, name in enumerate(df.columns):
            column = df[name]
            kind = column.dtype.kind
            if self.as_hex[i - 1]:
                items.append(pd.Series(csv_int2hex(column.astype("<u4"))).values)
            else:

                if kind in "uif":
                    items.append(column.astype(str))
                elif kind == "S":
                    try:
                        items.append(npchar.decode(column, "utf-8"))
                    except:
                        items.append(npchar.decode(column, "latin-1"))
                elif kind == "O":
                    try:
                        items.append(pd.Series(csv_bytearray2hex(df[name])).values)
                    except:
                        items.append(pd.Series(df[name]).values)
                else:
                    items.append(column)

        items = [QtWidgets.QTreeWidgetItem(row) for row in zip(*items)]

        self.tree.addTopLevelItems(items)
        self.tree.setSortingEnabled(self.sort.checkState() == QtCore.Qt.Checked)

        del [[df]]
        gc.collect()

        self.current_pos = pos

        if self.tree_scroll.maximum() != self.tree_scroll.value():
            pass
        else:
            self.tree.verticalScrollBar().setValue(self.tree.verticalScrollBar().maximum())

        if self.tree_scroll.minimum() != self.tree_scroll.value():
            pass
        else:
            if self.with_scroll:
                self.tree.verticalScrollBar().setValue(1)
            else:
                self.tree.verticalScrollBar().setValue(0)
        if self.size <= self.view_count * 5:
            self.repeat_display = False

            if self.size <= self.view_count:
                self.tree_scroll.setMaximum(0)
                self.tree_scroll.setMinimum(0)

        self.with_scroll = False

    def clicked(self):
        pos = float(self.tree.currentItem().text(0))
        self.link_plot_signal.emit(pos)

    def _sort(self, index, mode):
        ascending = mode == QtCore.Qt.AscendingOrder
        names = [self.signals.index.name, *self.signals.columns]
        name = names[index]

        if index:
            try:
                self.signals.sort_values(
                    by=[name, "timestamps"], ascending=ascending, inplace=True
                )
            except:
                pass
        else:
            self.signals.sort_index(ascending=ascending, inplace=True)

        self.tree_scroll.setSliderPosition(self.tree_scroll.maximum())
        self.tree_scroll.setSliderPosition(self.tree_scroll.minimum())

    def build_request(self, signals):
        pop_index = []
        columns = []
        column_order = []
        signals = signals[0]
        for index in range(len(signals)):
            sig = signals[index]
            if not sig.enable:
                pop_index.append(index)
            else:
                columns.append(sig.name)
        for index in reversed(range(len(signals))):
            if index in pop_index:
                signals.pop(index)
        if len(signals) == 0:
            self.signals = pd.DataFrame()
            self.delete_cursor1_request.emit()
        else:
            if len(self.columns) > 0:
                for col in self.columns:
                    if col in columns:
                        column_order.append(col)
            self.mdf_ = MDF()
            self.mdf_.append(signals)
            self.signals = self.mdf_.to_dataframe(
                time_from_zero=False,
                ignore_value2text_conversions=self.ignore_value2text_conversions,
            )
            if len(column_order) > 0:
                self.signals = self.signals.reindex(columns=column_order)
        self.build(self.mdf_, self.signals)

    def items_deleted(self, names):
        for name in names:
            self.signals.pop(name)
        if len(self.signals.columns) > 0 :
            self.build(self.mdf_, self.signals)

    def items_rearranged(self, columns):
        columns = columns
        self.columns = []
        enable = []
        for col in columns:
            self.columns.append(col[0])
            if col[1]:
               enable.append(col[0])
        self.signals = self.signals.reindex(columns=enable)
        self.build(self.mdf_, self.signals)

    def build(self, mdf, df, reset_header_names=False):
        self.tree.setSortingEnabled(False)
        self.tree.clear()

        self.repeat_display = True

        self.mdf_ = mdf

        if df.empty:
            return
        self.signals = df
        names = [df.index.name, *df.columns]

        if reset_header_names:
            self.header_names = names

        self.tree.setColumnCount(len(names))
        self.tree.setHeaderLabels(names)

        self.size = len(df.index)
        self.position = 0

        self._min = min(self._min, df.index[0])
        self._max = max(self._max, df.index[-1])

        self.tree_scroll.setMaximum(self.max_pos)
        self.tree_scroll.setMinimum(0)
        self.tree_scroll.setSliderPosition(0)

        self.calculate_pos()
        self.display(0)

    def from_plot(self, timestamp):
        self.timestamp_ = timestamp
        self.from_plot_signal = True
        self.tree_scroll.setValue(timestamp-self._min)
        if timestamp == self._max:
            pass
        else:
            try:
                self.tree.clearSelection()
                self.tree.scrollToItem(self.tree.findItems(str(timestamp), QtCore.Qt.MatchExactly, column=0)[0])
                self.tree.findItems(str(timestamp), QtCore.Qt.MatchExactly, column=0)[0].setSelected(True)

            except Exception as e:
                print(e)
        self.from_plot_signal = False

    def scroll_pressed(self):
        if not self.with_scroll:
            self.with_scroll = True

    def to_config(self):
        if self.inverted_dict is not None:
            if len(self.inverted_dict) > 0:
                columns = []
                for col_name in self.signals.columns:
                    if col_name in self.inverted_dict:
                        name = self.inverted_dict[col_name]
                        if name is not None:
                            columns.append(name)
                    else:
                        columns.append(col_name)
        else:
            columns = list(self.signals.columns)

        config = {
            "sorted": self.sort.checkState() == QtCore.Qt.Checked,
            "raster": self.rate,
            "channels": columns,
        }

        return config

    def sorting_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.tree.setSortingEnabled(True)
            self.tree.header().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        else:
            self.tree.setSortingEnabled(False)

        self._display(0)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat("application/octet-stream-mdfstudio"):
            e.accept()
        super().dragEnterEvent(e)

    def dropEvent(self, e):
        data = e.mimeData()
        if data.hasFormat("application/octet-stream-mdfstudio"):
            names = extract_mime_names(data)
            self.add_channels_request.emit(names)
        else:
            super().dropEvent(e)

    def open_menu(self, position):

        selected_items = self.tree.selectedItems()
        if selected_items is None:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(self.tr("Copy (Ctrl+C)"))

        action = menu.exec_(self.tree.viewport().mapToGlobal(position))

        if action is None:
            return
        if action.text() == "Copy (Ctrl+C)":
            event = QtGui.QKeyEvent(
                QtCore.QEvent.KeyPress, QtCore.Qt.Key_C, QtCore.Qt.ControlModifier,
            )
            self.keyPressEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        modifier = event.modifiers()

        if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_Down:
            event.ignore()
            return

        if key == QtCore.Qt.Key_C and modifier == QtCore.Qt.ControlModifier:
            selected_items = self.tree.selectedItems()
            result = ""

            for name in self.header_names:
                result += name + "\t"
            result = result[:-2]
            result += "\n"

            col_count = len(self.header_names)
            for item in selected_items:
                for col in range(col_count):
                    result += item.text(col) + "\t"
                result = result[:-2]
                result += "\n"
            QtWidgets.QApplication.instance().clipboard().setText(result)
