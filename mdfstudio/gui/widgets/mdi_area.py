# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
    *	MdiAreaWidget.__init__ : Change UI (new palette)
	*	MdiAreaWidget.dropEvent : Window type changed, Check channels' raster and convert raster if raster < 0.001
	*	MdiAreaWidget.tile_vertically : Return if there is no subwindow
	*	MdiAreaWidget.tile_horizontally : Return if there is no subwindow
	*	WithMDIArea.__init__ : Add attributes
	*	WithMDIArea.add_new_channels : Window type changed (Remove Numeric, Add Plot+Tabular).
	                            Exclude channels if name started with "$".
	                            Resample channels by selected raster
	*	WithMDIArea.add_window : Window type changed (Remove Numeric, Add Plot+Tabular).
	                            Exclude channels if name started with "$".
	                            Resample channels by selected raster.
	                            Set object name of each window.
	*	WithMDIArea.load_window : Get raster from configuration file.
	                            Window type changed (Remove Numeric, Add Plot+Tabular).
	                            Exclude channels if name started with "$".
	                            Resample channels by selected raster.
	                            Set object name of each window.
	*	WithMDIArea.file_by_uuid : Window widget type changed

"""
from datetime import datetime
from functools import partial
import json
from traceback import format_exc
import gc

from natsort import natsorted
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

from ...mdf import MDF
from ...blocks import v4_constants as v4c
from ...blocks.utils import csv_bytearray2hex, extract_cncomment_xml, MdfException
from ..dialogs.channel_info import ChannelInfoDialog
from ..utils import (
    add_children,
    compute_signal,
    COLORS,
    extract_mime_names,
    get_required_signals,
    HelperChannel,
    load_dsp,
    run_thread_with_progress,
    setup_progress,
    TERMINATED,
)
from .numeric import Numeric
from .plot import Plot
from .tabular import Tabular
from .tree import TreeWidget

class MdiAreaWidget(QtWidgets.QMdiArea):
    add_window_request = QtCore.pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.show()

        palette = QtGui.QPalette()
        br_light_sand = QtGui.QBrush(QtGui.QColor(246, 243, 242))
        br_blue = QtGui.QBrush(QtGui.QColor(0, 59, 126))
        br_sand = QtGui.QBrush(QtGui.QColor(228, 220, 211))
        br_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        br_black = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        br_light_sand.setStyle(QtCore.Qt.SolidPattern)
        br_blue.setStyle(QtCore.Qt.SolidPattern)
        br_sand.setStyle(QtCore.Qt.SolidPattern)

        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, br_black)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_white)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_white)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, br_blue)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, br_white)
        self.setPalette(palette)

    def dragEnterEvent(self, e):
        e.accept()
        super().dragEnterEvent(e)

    def dropEvent(self, e):
        if e.source() is self:
            super().dropEvent(e)
        else:
            data = e.mimeData()
            if data.hasFormat("application/octet-stream-mdfstudio"):
                rasters = set()
                checked = False

                names = extract_mime_names(data)
                file = self.parent().parent().parent().parent().parent()

                for signal in names:
                    if signal[0][0] == "$":
                        names.remove(signal)
                        continue
                    else:
                        checked = True
                        raster = float(file.mdf.get_channel_metadata(signal[0], signal[1]).sampling_rate)
                        rasters.add(raster)
                if not checked:
                    return

                raster_max = max(rasters)

                for raster in file.raster_set:
                    rasters.add(raster)

                rasters = sorted(rasters, reverse=True)
                index = rasters.index(raster_max)

                raster_list = []
                for raster in rasters:
                    raster_list.append(str(raster))

                ret, ok = QtWidgets.QInputDialog.getItem(
                    None,
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
                    self.add_window_request.emit([ret, names, ret1])

    def tile_vertically(self):
        sub_windows = self.subWindowList()
        if len(sub_windows) == 0:
            return

        position = QtCore.QPoint(0, 0)
        width = self.width()
        height = self.height()
        ratio = height // len(sub_windows)

        for window in sub_windows:
            rect = QtCore.QRect(0, 0, width, ratio)

            window.setGeometry(rect)
            window.move(position)
            position.setY(position.y() + ratio)

    def tile_horizontally(self):
        sub_windows = self.subWindowList()
        if len(sub_windows) == 0:
            return

        position = QtCore.QPoint(0, 0)
        width = self.width()
        height = self.height()
        ratio = width // len(sub_windows)

        for window in sub_windows:
            rect = QtCore.QRect(0, 0, ratio, height)

            window.setGeometry(rect)
            window.move(position)
            position.setX(position.x() + ratio)

class WithMDIArea:
    def __init__(self, subplots=False, subplots_link=False, ignore_value2text_conversions=False,*args, **kwargs):
        self._cursor_source = None
        self._region_source = None
        self._window_counter = 0

        self._settings = QtCore.QSettings()
        #yda 2020-10-08 *UDC*
        # if self._settings.value("apply_alternative_names") == "true":
        #     self.apply_alternative_names = True
        # else:
        #     self.apply_alternative_names = False
        self.subplots = subplots
        self.subplots_link = subplots_link
        self.ignore_value2text_conversions = ignore_value2text_conversions

    def add_new_channels(self, names, widget):
        with_tabular = True
        if isinstance(widget, Plot):
            if widget.tabular is None:
                with_tabular = False
        try:
            signals_ = [name for name in names if name[1:] != (-1, -1)]
            computed = [json.loads(name[0]) for name in names if name[1:] == (-1, -1)]
            uuids = set(entry[3] for entry in signals_)
            signals = []
            raster = widget.rate
            min_sampling_rate = []

            for uuid in uuids:
                uuids_signals = [entry[:3] for entry in signals_ if entry[3] == uuid]

                file_info = self.file_by_uuid(uuid)
                if not file_info:
                    continue

                file_index, file = file_info

                selected_signals = file.mdf.select(
                    uuids_signals,
                    ignore_value2text_conversions=self.ignore_value2text_conversions,
                    copy_master=False,
                    validate=True,
                    raw=True,
                )
                delete_sig = []
                for sig, sig_ in zip(selected_signals, uuids_signals):
                    sig.group_index = sig_[1]
                    sig.channel_index = sig_[2]
                    sig.computed = False
                    sig.computation = {}
                    sig.mdf_uuid = uuid

                    if not hasattr(self, "mdf"):
                        # MainWindow => comparison plots
                        sig.tooltip = f"{sig.name}\n@ {file.file_name}"
                        sig.name = f"{file_index + 1}: {sig.name}"
                    # min_sampling_rate.append(file.mdf.get_channel_metadata(sig_[0], sig_[1]).sampling_rate)
                    if sig.name[0] == "$":
                        delete_sig.append(sig)
                if len(delete_sig) >0:
                    for sig in delete_sig:
                        selected_signals.remove(sig)
                signals.extend(selected_signals)

                signals = [
                    sig
                    for sig in signals
                    if sig.samples.dtype.kind not in "SU"
                       and not sig.samples.dtype.names
                       and not len(sig.samples.shape) > 1
                ]

            for signal in signals:
                if len(signal.samples.shape) > 1:
                    signal.samples = csv_bytearray2hex(pd.Series(list(signal.samples)))

                if signal.name.endswith("CAN_DataFrame.ID"):
                    signal.samples = signal.samples.astype("<u4") & 0x1FFFFFFF

            signals = sigs = natsorted(signals, key=lambda x: x.name)

            new_mdf = MDF()
            new_mdf.append(signals)
            new_mdf = new_mdf.resample(raster)
            channels = new_mdf.iter_channels(copy_master=True)
            resampled_signals = []
            for ch in channels:
                for sig in signals:
                    if sig.name == ch.name:
                        ch.group_index = sig.group_index
                        ch.channel_index = sig.channel_index
                        break
                resampled_signals.append(ch)
            signals = resampled_signals

            if isinstance(widget, Plot):
                add_request = widget.add_new_channels(signals)
                if not add_request:
                    return

                if computed:
                    measured_signals = {sig.name: sig for sig in sigs}
                    if measured_signals:
                        all_timebase = np.unique(
                            np.concatenate(
                                [sig.timestamps for sig in measured_signals.values()]
                            )
                        )
                    else:
                        all_timebase = []

                    required_channels = []
                    for ch in computed:
                        required_channels.extend(get_required_signals(ch))

                    required_channels = set(required_channels)
                    required_channels = [
                        (None, *self.mdf.whereis(channel)[0])
                        for channel in required_channels
                        if channel not in list(measured_signals) and channel in self.mdf
                    ]
                    required_channels = {
                        sig.name: sig
                        for sig in self.mdf.select(
                            required_channels,
                            ignore_value2text_conversions=self.ignore_value2text_conversions,
                            copy_master=False,
                        )
                    }

                    required_channels.update(measured_signals)

                    computed_signals = {}

                    for channel in computed:
                        computation = channel["computation"]

                        try:
                            signal = compute_signal(
                                computation, required_channels, all_timebase
                            )
                            signal.color = channel["color"]
                            signal.computed = True
                            signal.computation = channel["computation"]
                            signal.name = channel["name"]
                            signal.unit = channel["unit"]
                            signal.group_index = -1
                            signal.channel_index = -1

                            computed_signals[signal.name] = signal
                        except:
                            pass
                    computed_signals = list(computed_signals.values())
                    signals += computed_signals
                    widget.add_new_channels(computed_signals)

            if with_tabular:
                if isinstance(widget.parent().parent().parent().parent(), Plot):
                    widget.parent().parent().parent().parent().add_new_channels(signals)
                if isinstance(widget, Plot):
                    widget = widget.tabular

                mdf_ = widget.mdf_
                new = []
                for sig in signals:
                    if sig.name not in mdf_.channels_db:
                        new.append(sig)
                if len(new) == 0:
                    return
                mdf_.append(new)
                mdf_= mdf_.resample(raster=raster)

                df = mdf_.to_dataframe(
                    time_from_zero=False,
                    ignore_value2text_conversions=self.ignore_value2text_conversions,
                )

                widget.as_hex = []
                for name in df.columns:
                    if name.endswith(
                            (
                                    "CAN_DataFrame.ID",
                                    "FLX_Frame.ID",
                                    "FlexRay_DataFrame.ID",
                                    "LIN_Frame.ID",
                                    "MOST_DataFrame.ID",
                                    "ETH_Frame.ID",
                            )
                    ):
                        df[name] = df[name].astype("<u4") & 0x1FFFFFFF
                        widget.as_hex.append(True)
                    else:
                        widget.as_hex.append(False)
                widget.build(mdf_, df, True)

        except MdfException:
            print(format_exc())

    def add_window(self, args):
        window_type, names, raster = args
        raster = float(raster)
        #yda 2020-10-08 *UDC*
        # udc_dict_ = self.udc_dict
        min_sampling_rate = []

        if names and isinstance(names[0], str):
            signals_ = [
                (None, *self.mdf.whereis(name)[0]) for name in names if name in self.mdf
            ]
            computed = []
        else:
            signals_ = [name for name in names if name[1:] != (-1, -1)]

            computed = [json.loads(name[0]) for name in names if name[1:] == (-1, -1)]

        if not signals_:
            return

        uuids = set(entry[3] for entry in signals_)

        signals = []

        for uuid in uuids:
            uuids_signals = [entry[:3] for entry in signals_ if entry[3] == uuid]
            file_info = self.file_by_uuid(uuid)
            if not file_info:
                continue

            file_index, file = file_info

            selected_signals = file.mdf.select(
                uuids_signals,
                ignore_value2text_conversions=self.ignore_value2text_conversions,
                copy_master=False,
                validate=True,
                raw=True,
            )

            for sig, sig_ in zip(selected_signals, uuids_signals):
                if sig.name[0] == "$":
                    continue

                sig.group_index = sig_[1]
                sig.channel_index = sig_[2]
                sig.computed = False
                sig.computation = {}
                sig.mdf_uuid = uuid

                if not hasattr(self, "mdf"):
                    # MainWindow => comparison plots\
                    # min_sampling_rate.append(file.mdf.get_channel_metadata(sig.name, sig_[1]).sampling_rate)
                    sig.tooltip = f"{sig.name}\n@ {file.file_name}"
                    sig.name = f"{file_index + 1}: {sig.name}"
                # else:
                    # min_sampling_rate.append(file.mdf.get_channel_metadata(sig.name, sig_[1]).sampling_rate)

            signals.extend(selected_signals)

        signals = [
            sig
            for sig in signals
            if sig.samples.dtype.kind not in "SU"
               and not sig.samples.dtype.names
               and not len(sig.samples.shape) > 1
               and not len(sig.samples) == 0
        ]

        for signal in signals:
            if len(signal.samples.shape) > 1:
                signal.samples = csv_bytearray2hex(pd.Series(list(signal.samples)))

            if signal.name.endswith("CAN_DataFrame.ID"):
                signal.samples = signal.samples.astype("<u4") & 0x1FFFFFFF

            #yda 2020-10-08 *UDC*
            # if self.apply_alternative_names:
            #     name = udc_dict_.get(signal.name)
            #     if name is not None:
            #         signal.name = udc_dict_.get(signal.name)

        signals = natsorted(signals, key=lambda x: x.name)

        if hasattr(self, "mdf"):
            events = []
            origin = self.mdf.start_time

            if self.mdf.version >= "4.00":
                mdf_events = list(self.mdf.events)

                for pos, event in enumerate(mdf_events):
                    event_info = {}
                    event_info["value"] = event.value
                    event_info["type"] = v4c.EVENT_TYPE_TO_STRING[event.event_type]
                    description = event.name
                    if event.comment:
                        description += f" ({event.comment})"
                    event_info["description"] = description
                    event_info["index"] = pos

                    if event.range_type == v4c.EVENT_RANGE_TYPE_POINT:
                        events.append(event_info)
                    elif event.range_type == v4c.EVENT_RANGE_TYPE_BEGINNING:
                        events.append([event_info])
                    else:
                        parent = events[event.parent]
                        parent.append(event_info)
                        events.append(None)
                events = [ev for ev in events if ev is not None]
            else:
                for gp in self.mdf.groups:
                    if not gp.trigger:
                        continue

                    for i in range(gp.trigger.trigger_events_nr):
                        event = {
                            "value": gp.trigger[f"trigger_{i}_time"],
                            "index": i,
                            "description": gp.trigger.comment,
                            "type": v4c.EVENT_TYPE_TO_STRING[
                                v4c.EVENT_TYPE_TRIGGER
                            ],
                        }
                        events.append(event)
        else:
            events = []
            origin = self.files.subWindowList(0)[0].widget().mdf.start_time

        new_mdf = MDF()
        new_mdf.append(signals)
        new_mdf = new_mdf.resample(raster)
        channels = new_mdf.iter_channels(copy_master=True)
        resampled_signals = []
        for ch in channels:
            for sig in signals:
                if sig.name == ch.name:
                    ch.group_index = sig.group_index
                    ch.channel_index = sig.channel_index
                    break
            resampled_signals.append(ch)
        signals = resampled_signals

        if window_type == "Plot":
            tabular = None
        else:
            # new_mdf = MDF()
            # new_mdf.append(signals)
            df = new_mdf.to_dataframe(
                time_from_zero=False,
                ignore_value2text_conversions=self.ignore_value2text_conversions,
            )
            if hasattr(self, "mdf"):
                tabular = Tabular(new_mdf, df, start=self.mdf.header.start_time.timestamp(), sampling_rate=raster, ignore_value2text_conversions=self.ignore_value2text_conversions)
            else:
                tabular = Tabular(new_mdf, df, start=self.files.subWindowList(0)[0].widget().mdf.header.start_time.timestamp(), sampling_rate=raster, ignore_value2text_conversions=self.ignore_value2text_conversions)
            tabular.add_channels_request.connect(partial(self.add_new_channels, widget=tabular))


        if window_type == "Plot" or window_type == "Plot+Tabular":
            #yda 2020-10-08 *UDC*
            # if self.apply_alternative_names:
            #     inverted_dict = {value : key for (key, value) in udc_dict_.items()}
            #     plot = Plot([], events=events, with_dots=self.with_dots, origin=origin, tabular=tabular, file_info=file_info, inverted_dict=inverted_dict, sampling_rate=min(min_sampling_rate))
            # else:
            plot = Plot([], events=events, with_dots=self.with_dots, ignore_value2text_conversions=self.ignore_value2text_conversions, origin=origin, tabular=tabular, file_info=file_info, sampling_rate=raster)

            if not self.subplots:
                for mdi in self.mdi_area.subWindowList():
                    mdi.close()
                w = self.mdi_area.addSubWindow(plot)
                w.showMaximized()
            else:
                w = self.mdi_area.addSubWindow(plot)
                if len(self.mdi_area.subWindowList()) == 1:
                    w.showMaximized()
                else:
                    w.show()
                    self.mdi_area.tileSubWindows()

            plot.hide()
            plot.add_new_channels(signals)
            plot.show()
            menu = w.systemMenu()

            def set_title(mdi):
                name, ok = QtWidgets.QInputDialog.getText(
                    None, "Set sub-plot title", "Title:",
                )
                if ok and name:
                    mdi.setWindowTitle(name)

            action = QtWidgets.QAction("Set title", menu)
            action.triggered.connect(partial(set_title, w))
            before = menu.actions()[0]
            menu.insertAction(before, action)
            # w.setSystemMenu(menu)
            w.setObjectName("P" + datetime.now().strftime("%Y%m%d_%H:%M:%S"))

            w.setWindowTitle(f"{window_type} {self._window_counter}")
            self._window_counter += 1

            if self.subplots_link:

                for i, mdi in enumerate(self.mdi_area.subWindowList()):
                    try:
                        viewbox = mdi.widget().plot.viewbox
                        if plot.plot.viewbox is not viewbox:
                            plot.plot.viewbox.setXLink(viewbox)
                        break
                    except:
                        continue

            plot.add_channels_request.connect(
                partial(self.add_new_channels, widget=plot)
            )
            plot.show_properties.connect(self._show_info)
            self.set_subplots_link(self.subplots_link)

            plot.close_request.connect(self.mdi_area.activeSubWindow().close)
            if tabular is not None:
                tabular.tree.header().setSectionsMovable(False)
        else:
            #yda 2020-10-08 *UDC*
            # if self.apply_alternative_names:
            #     inverted_dict = {value: key for (key, value) in udc_dict_.items()}
            #     tabular = Tabular(new_mdf, df, start=self.mdf.header.start_time.timestamp(),inverted_dict=inverted_dict, sampling_rate=min(min_sampling_rate))
            # else:
            if hasattr(self, "mdf"):
                tabular = Tabular(new_mdf, df, start=self.mdf.header.start_time.timestamp(), sampling_rate=raster)
            else:
                tabular = Tabular(new_mdf, df,
                                  start=self.files.subWindowList(0)[0].widget().mdf.header.start_time.timestamp(),
                                  sampling_rate=raster,
                                  ignore_value2text_conversions=self.ignore_value2text_conversions)

            if not self.subplots:
                for mdi in self.mdi_area.subWindowList():
                    mdi.close()
                w = self.mdi_area.addSubWindow(tabular)
                w.showMaximized()
            else:
                w = self.mdi_area.addSubWindow(tabular)
                if len(self.mdi_area.subWindowList()) == 1:
                    w.showMaximized()
                else:
                    w.show()
                    self.mdi_area.tileSubWindows()
            menu = w.systemMenu()
            w.setObjectName("T" + datetime.now().strftime("%Y%m%d_%H:%M:%S"))

            def set_title(mdi):
                name, ok = QtWidgets.QInputDialog.getText(
                    None, "Set sub-plot title", "Title:",
                )
                if ok and name:
                    mdi.setWindowTitle(name)

            action = QtWidgets.QAction("Set title", menu)
            action.triggered.connect(partial(set_title, w))
            before = menu.actions()[0]
            menu.insertAction(before, action)
            # w.setSystemMenu(menu)

            w.setWindowTitle(f"Tabular {self._window_counter}")
            self._window_counter += 1

            tabular.add_channels_request.connect(
                partial(self.add_new_channels, widget=tabular)
            )
        if "Tabular" in window_type:
            tabular.calculate_pos()
            tabular.display(0)


    def get_current_plot(self):
        mdi = self.mdi_area.activeSubWindow()
        if mdi is not None:
            widget = mdi.widget()
            if isinstance(widget, Plot):
                return widget
            else:
                return None
        else:
            return None

    def load_window(self, window_info):
        uuid = self.uuid
        raster = window_info["configuration"]["raster"]
        min_sampling_rate = []

        file_info = self.file_by_uuid(uuid)
        file_index, file = file_info

        if window_info["type"] == "Plot" or window_info["type"] == "Plot+Tabular":
            found_signals = [
                channel
                for channel in window_info["configuration"]["channels"]
                if not channel["computed"] and channel["name"] in self.mdf
            ]

            measured_signals_ = [
                (None, *self.mdf.whereis(channel["name"])[0])
                for channel in found_signals
            ]

            measured_signals = {
                sig.name: sig
                for sig in self.mdf.select(
                    measured_signals_,
                    ignore_value2text_conversions=self.ignore_value2text_conversions,
                    copy_master=False,
                    validate=True,
                    raw=True,
                )
            }

            for signal, entry_info, channel in zip(measured_signals.values(), measured_signals_, found_signals):
                if signal.name[0] == "$":
                    continue
                signal.computed = False
                signal.computation = {}
                signal.color = channel["color"]
                signal.group_index = entry_info[1]
                signal.channel_index = entry_info[2]
                signal.mdf_uuid = uuid

                # min_sampling_rate.append(self.mdf.get_channel_metadata(signal.name, signal.group_index).sampling_rate)

            if measured_signals:
                all_timebase = np.unique(
                    np.concatenate(
                        [sig.timestamps for sig in measured_signals.values()]
                    )
                )
            else:
                all_timebase = []

            computed_signals_descriptions = [
                channel
                for channel in window_info["configuration"]["channels"]
                if channel["computed"]
            ]

            required_channels = []
            for ch in computed_signals_descriptions:
                required_channels.extend(get_required_signals(ch))

            required_channels = set(required_channels)
            required_channels = [
                (None, *self.mdf.whereis(channel)[0])
                for channel in required_channels
                if channel not in list(measured_signals) and channel in self.mdf
            ]
            required_channels = {
                sig.name: sig
                for sig in self.mdf.select(
                    required_channels,
                    ignore_value2text_conversions=self.ignore_value2text_conversions,
                    copy_master=False,
                )
            }
            required_channels.update(measured_signals)

            computed_signals = {}

            for channel in computed_signals_descriptions:
                computation = channel["computation"]

                try:
                    signal = compute_signal(
                        computation, required_channels, all_timebase
                    )
                    signal.color = channel["color"]
                    signal.computed = True
                    signal.computation = channel["computation"]
                    signal.name = channel["name"]
                    signal.unit = channel["unit"]
                    signal.group_index = -1
                    signal.channel_index = -1
                    signal.mdf_uuid = uuid

                    computed_signals[signal.name] = signal
                except:
                    pass

            signals = list(measured_signals.values()) + list(computed_signals.values())

            signals = [
                sig
                for sig in signals
                if sig.samples.dtype.kind not in "SU"
                   and not sig.samples.dtype.names
                   and not len(sig.samples.shape) > 1
            ]

            if not signals:
                return

            if hasattr(self, "mdf"):
                events = []
                origin = self.mdf.start_time

                if self.mdf.version >= "4.00":
                    mdf_events = list(self.mdf.events)

                    for pos, event in enumerate(mdf_events):
                        event_info = {}
                        event_info["value"] = event.value
                        event_info["type"] = v4c.EVENT_TYPE_TO_STRING[event.event_type]
                        description = event.name
                        if event.comment:
                            description += f" ({event.comment})"
                        event_info["description"] = description
                        event_info["index"] = pos

                        if event.range_type == v4c.EVENT_RANGE_TYPE_POINT:
                            events.append(event_info)
                        elif event.range_type == v4c.EVENT_RANGE_TYPE_BEGINNING:
                            events.append([event_info])
                        else:
                            parent = events[event.parent]
                            parent.append(event_info)
                            events.append(None)
                    events = [ev for ev in events if ev is not None]
                else:
                    for gp in self.mdf.groups:
                        if not gp.trigger:
                            continue

                        for i in range(gp.trigger.trigger_events_nr):
                            event = {
                                "value": gp.trigger[f"trigger_{i}_time"],
                                "index": i,
                                "description": gp.trigger.comment,
                                "type": v4c.EVENT_TYPE_TO_STRING[
                                    v4c.EVENT_TYPE_TRIGGER
                                ],
                            }
                            events.append(event)
            else:
                events = []
                origin = self.files.widget(0).mdf.start_time

            new_mdf = MDF()
            new_mdf.append(signals)
            new_mdf = new_mdf.resample(raster)
            channels = new_mdf.iter_channels(copy_master=True)
            resampled_signals = []
            for ch in channels:
                for sig in signals:
                    if sig.name == ch.name:
                        ch.group_index = sig.group_index
                        ch.channel_index = sig.channel_index
                        ch.color = sig.color
                        if sig.group_index == -1 and sig.channel_index == -1:
                            ch.computation = sig.computation
                            ch.computed = True
                        break
                resampled_signals.append(ch)
            signals = resampled_signals

            if window_info["type"] == "Plot":
                tabular = None
            else:
                # new_mdf = MDF()
                # new_mdf.append(signals)

                df = new_mdf.to_dataframe(
                    time_from_zero=False,
                    ignore_value2text_conversions=self.ignore_value2text_conversions,
                )
                tabular = Tabular(new_mdf, df, start=self.mdf.header.start_time.timestamp(), sampling_rate=raster, ignore_value2text_conversions=self.ignore_value2text_conversions)

            plot = Plot([], self.with_dots, ignore_value2text_conversions=self.ignore_value2text_conversions, events=events, origin=origin, tabular=tabular, file_info=file_info, sampling_rate=raster)

            if not self.subplots:
                for mdi in self.mdi_area.subWindowList():
                    mdi.close()
                w = self.mdi_area.addSubWindow(plot)
                w.showMaximized()

            else:
                w = self.mdi_area.addSubWindow(plot)

                if len(self.mdi_area.subWindowList()) == 1:
                    w.showMaximized()
                else:
                    w.show()
                    self.mdi_area.tileSubWindows()
            self.mdi_area.setFocus()
            plot.hide()

            plot.add_new_channels(signals)
            needs_update = False
            for channel, sig in zip(found_signals, plot.plot.signals):
                if "mode" in channel:
                    sig.mode = channel["mode"]
                    needs_update = True
            if needs_update:
                plot.plot.update_lines(force=True)

            plot.show()

            menu = w.systemMenu()

            def set_title(mdi):
                name, ok = QtWidgets.QInputDialog.getText(
                    None, "Set sub-plot title", "Title:",
                )
                if ok and name:
                    mdi.setWindowTitle(name)

            action = QtWidgets.QAction("Set title", menu)
            action.triggered.connect(partial(set_title, w))
            before = menu.actions()[0]
            menu.insertAction(before, action)
            # w.setSystemMenu(menu)

            w.setObjectName("P"+datetime.now().strftime("%Y%m%d_%H:%M:%S"))

            if window_info["title"]:
                w.setWindowTitle(window_info["title"])
            else:
                w.setWindowTitle(f"Plot {self._window_counter}")
                self._window_counter += 1

            plot.add_channels_request.connect(
                partial(self.add_new_channels, widget=plot)
            )

            descriptions = {
                channel["name"]: channel
                for channel in window_info["configuration"]["channels"]
            }

            count = plot.channel_selection.count()

            for i in range(count):
                wid = plot.channel_selection.itemWidget(plot.channel_selection.item(i))
                name = wid._name

                description = descriptions[name]

                wid.set_fmt(description["fmt"])
                wid.set_precision(description["precision"])
                wid.ranges = {
                    (range["start"], range["stop"]): range["color"]
                    for range in description["ranges"]
                }
                wid.ylink.setCheckState(
                    QtCore.Qt.Checked
                    if description["common_axis"]
                    else QtCore.Qt.Unchecked
                )
                wid.display.setCheckState(
                    QtCore.Qt.Checked if description["enabled"] else QtCore.Qt.Unchecked
                )

            self.set_subplots_link(self.subplots_link)
            plot.close_request.connect(w.close)

            if tabular is not None:
                tabular.calculate_pos(w.height()/2)
                tabular.display(0)
                tabular.tree.header().setSectionsMovable(False)

        if window_info["type"] == "Tabular":
            signals_ = [
                (name, *self.mdf.whereis(name)[0])
                for name in window_info["configuration"]["channels"]
                if name in self.mdf
            ]
            for signal in signals_:
                if signal[0] == "$":
                    continue
                # min_sampling_rate.append(self.mdf.get_channel_metadata(signal[0], signal[1]).sampling_rate)
            if not signals_:
                return

            new_mdf = self.mdf.filter(signals_)
            new_mdf = new_mdf.resample(raster=raster)

            signals = new_mdf.to_dataframe(
                ignore_value2text_conversions=self.ignore_value2text_conversions,
            )

            tabular = Tabular(new_mdf, signals, start=new_mdf.header.start_time.timestamp(), sampling_rate=raster)
            tabular.info_channels = signals_

            if not self.subplots:
                for mdi in self.mdi_area.subWindowList():
                    mdi.close()
                w = self.mdi_area.addSubWindow(tabular)

                w.showMaximized()
            else:
                w = self.mdi_area.addSubWindow(tabular)

                if len(self.mdi_area.subWindowList()) == 1:
                    w.showMaximized()
                else:
                    w.show()
                    self.mdi_area.tileSubWindows()

            if window_info["title"]:
                w.setWindowTitle(window_info["title"])
            else:
                w.setWindowTitle(f"Tabular {self._window_counter}")
                self._window_counter += 1
            self.mdi_area.setFocus()

            tabular.sort.setCheckState(
                QtCore.Qt.Checked
                if window_info["configuration"]["sorted"]
                else QtCore.Qt.Unchecked
            )

            menu = w.systemMenu()
            w.setObjectName("T" + datetime.now().strftime("%Y%m%d_%H:%M:%S"))

            def set_title(mdi):
                name, ok = QtWidgets.QInputDialog.getText(
                    None, "Set sub-plot title", "Title:",
                )
                if ok and name:
                    mdi.setWindowTitle(name)

            action = QtWidgets.QAction("Set title", menu)
            action.triggered.connect(partial(set_title, w))
            before = menu.actions()[0]
            menu.insertAction(before, action)

            tabular.add_channels_request.connect(partial(self.add_new_channels, widget=tabular))
            tabular.calculate_pos(w.height())
            tabular.display(0)
            # w.setSystemMenu(menu)

    def set_line_style(self, with_dots=None):
        if with_dots is not None:

            self.with_dots = with_dots

            current_plot = self.get_current_plot()
            if current_plot:
                current_plot.plot.update_lines(with_dots=with_dots)

    def set_subplots(self, option):
        self.subplots = option

    def set_subplots_link(self, subplots_link):
        self.subplots_link = subplots_link
        viewbox = None
        if subplots_link:
            for i, mdi in enumerate(self.mdi_area.subWindowList()):
                widget = mdi.widget()
                if isinstance(widget, Plot):
                    if viewbox is None:
                        viewbox = widget.plot.viewbox
                    else:
                        widget.plot.viewbox.setXLink(viewbox)
                    widget.cursor_moved_signal.connect(self.set_cursor)
                    widget.cursor_removed_signal.connect(self.remove_cursor)
                    widget.region_removed_signal.connect(self.remove_region)
                    widget.region_moved_signal.connect(self.set_region)
                elif isinstance(widget, Numeric):
                    widget.timestamp_changed_signal.connect(self.set_cursor)
        else:
            for mdi in self.mdi_area.subWindowList():
                widget = mdi.widget()
                if isinstance(widget, Plot):
                    widget.plot.viewbox.setXLink(None)
                    try:
                        widget.cursor_moved_signal.disconnect(self.set_cursor)
                    except:
                        pass
                    try:
                        widget.cursor_removed_signal.disconnect(self.remove_cursor)
                    except:
                        pass
                    try:
                        widget.region_removed_signal.disconnect(self.remove_region)
                    except:
                        pass
                    try:
                        widget.region_modified_signal.disconnect(self.set_region)
                    except:
                        pass
                elif isinstance(widget, Numeric):
                    try:
                        widget.timestamp_changed_signal.disconnect(self.set_cursor)
                    except:
                        pass

    def set_cursor(self, widget, pos):
        if self._cursor_source is None:
            self._cursor_source = widget
            for mdi in self.mdi_area.subWindowList():
                wid = mdi.widget()
                if isinstance(wid, Plot) and wid is not widget:
                    if wid.plot.cursor1 is None:
                        event = QtGui.QKeyEvent(
                            QtCore.QEvent.KeyPress,
                            QtCore.Qt.Key_C,
                            QtCore.Qt.NoModifier,
                        )
                        wid.plot.keyPressEvent(event)
                    wid.plot.cursor1.setPos(pos)
                elif isinstance(wid, Numeric) and wid is not widget:
                    wid.timestamp.setValue(pos)
            self._cursor_source = None

    def set_region(self, widget, region):
        if self._region_source is None:
            self._region_source = widget
            for mdi in self.mdi_area.subWindowList():
                wid = mdi.widget()
                if isinstance(wid, Plot) and wid is not widget:
                    if wid.plot.region is None:
                        event = QtGui.QKeyEvent(
                            QtCore.QEvent.KeyPress,
                            QtCore.Qt.Key_R,
                            QtCore.Qt.NoModifier,
                        )
                        wid.plot.keyPressEvent(event)
                    wid.plot.region.setRegion(region)
            self._region_source = None

    def remove_cursor(self, widget):
        if self._cursor_source is None:
            self._cursor_source = widget
            for mdi in self.mdi_area.subWindowList():
                plt = mdi.widget()
                if isinstance(plt, Plot) and plt is not widget:
                    plt.cursor_removed()
            self._cursor_source = None

    def remove_region(self, widget):
        if self._region_source is None:
            self._region_source = widget
            for mdi in self.mdi_area.subWindowList():
                plt = mdi.widget()
                if isinstance(plt, Plot) and plt is not widget:
                    if plt.plot.region is not None:
                        event = QtGui.QKeyEvent(
                            QtCore.QEvent.KeyPress,
                            QtCore.Qt.Key_R,
                            QtCore.Qt.NoModifier,
                        )
                        plt.plot.keyPressEvent(event)
            self._region_source = None

    def save_all_subplots(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select output measurement file", "", "MDF version 4 files (*.mf4)",
        )

        if file_name:
            with MDF() as mdf:
                for mdi in self.mdi_area.subWindowList():
                    plt = mdi.widget()

                    mdf.append(plt.plot.signals)
                mdf.save(file_name, overwrite=True)

    def file_by_uuid(self, uuid):
        try:
            for file_index in range(len(self.files.subWindowList())):
                if self.files.subWindowList(file_index)[0].widget().uuid == uuid:
                    return file_index, self.files.subWindowList(file_index)[0].widget()
            return None
        except:
            if self.uuid == uuid:
                return 0, self
            else:
                return None

    def _show_info(self, lst):
        group_index, index, uuid = lst
        file_info = self.file_by_uuid(uuid)
        if file_info:
            _, file = file_info
            channel = file.mdf.get_channel_metadata(group=group_index, index=index)

            msg = ChannelInfoDialog(channel, self)
            msg.show()
