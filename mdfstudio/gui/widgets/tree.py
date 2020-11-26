# -*- coding: utf-8 -*-
""" Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio

    Functions
    ---------
	*	TreeWidget.__init__ : Add setAcceptDrop(True)
	*	TreeWidget.mouseMoveEvent : Enable tree items to move up and down, not inserted into other items.
	*	TreeWidget.dragEnterEvent : dragEnterEvent is accepted only when sources from channels_view or filter_view
"""
import json
from struct import pack

from PyQt5 import QtCore, QtGui, QtWidgets

class TreeWidget(QtWidgets.QTreeWidget):
    items_rearranged = QtCore.pyqtSignal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)
        self.can_delete_items = True
        self.setAcceptDrops(True)
        self.isAccepted = False

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Space:
            selected_items = self.selectedItems()
            if not selected_items:
                return
            elif len(selected_items) == 1:
                item = selected_items[0]
                checked = item.checkState(0)
                if checked == QtCore.Qt.Checked:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(0, QtCore.Qt.Checked)
            else:
                if any(
                    item.checkState(0) == QtCore.Qt.Unchecked for item in selected_items
                ):
                    checked = QtCore.Qt.Checked
                else:
                    checked = QtCore.Qt.Unchecked
                for item in selected_items:
                    item.setCheckState(0, checked)
        else:
            super().keyPressEvent(event)

    def mouseMoveEvent(self, e):

        def get_data(item):
            data = set()
            count = item.childCount()

            if count:
                for i in range(count):
                    child = item.child(i)

                    if child.childCount():
                        data = data | get_data(child)
                    else:

                        name = child.name.encode("utf-8")
                        entry = child.entry
                        if entry[1] != 0xFFFFFFFFFFFFFFFF:
                            data.add(
                                (
                                    str(child.mdf_uuid).encode("ascii"),
                                    name,
                                    entry[0],
                                    entry[1],
                                    len(name),
                                )
                            )
            else:
                name = item.name.encode("utf-8")
                entry = item.entry
                if entry[1] != 0xFFFFFFFFFFFFFFFF:
                    data.add(
                        (
                            str(item.mdf_uuid).encode("ascii"),
                            name,
                            entry[0],
                            entry[1],
                            len(name),
                        )
                    )

            return data

        selected_items = self.selectedItems()

        mimeData = QtCore.QMimeData()

        data = set()
        for item in selected_items:
            data = data | get_data(item)

        data = [
            pack(
                f"<36s3q{name_length}s",
                uuid,
                group_index,
                channel_index,
                name_length,
                name,
            )
            for uuid, name, group_index, channel_index, name_length in sorted(data)
        ]

        mimeData.setData(
            "application/octet-stream-mdfstudio", QtCore.QByteArray(b"".join(data))
        )

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        drag.setHotSpot(e.pos() - self.rect().topLeft())

        # drag.exec_(QtCore.Qt.MoveAction)
        #drag.exec_(QtCore.Qt.TargetMoveAction)
        tNo = -1

        for i in range(self.topLevelItemCount()):
            if self.topLevelItem(i).isSelected():
                tNo = i
                break

        drag.exec(QtCore.Qt.CopyAction)
        if not self.isAccepted:
            return

        # drag.exec(QtCore.Qt.CopyAction)

        for i in reversed(range(self.topLevelItemCount())):
            if self.topLevelItem(i).childCount() > 0 :
                children = self.topLevelItem(i).takeChildren()
                if i == 0:
                    if tNo == 0:
                        self.insertTopLevelItems(1, children)
                    else:
                        self.insertTopLevelItems(0, children)
                elif i == self.topLevelItemCount() - 1:
                    if tNo == self.topLevelItemCount() - 1:
                        self.insertTopLevelItems(i+1, children)
                    else:
                        self.insertTopLevelItems(i, children)
                else:
                    self.insertTopLevelItems(i+1, children)

        self.items_rearranged.emit()


    def dragEnterEvent(self, e):
        if e.source().property("channels_view") == 3 or e.source().objectName()=="filter_tree":
            if e.mimeData().hasFormat("application/octet-stream-mdfstudio"):
                self.isAccepted = True
                e.accept()

            # super().dragEnterEvent(e)
        else:
            e.ignore()
            e.setAccepted(False)
            self.isAccepted = False

    def dropEvent(self, e):
        if e.source() is self:
            # QtGui.QAbstractItemView.dropEvent(self, e)
            super().dropEvent(e)

            # self.currentItem().setSelected(True)
            # self.setExpanded(self.currentIndex(), False)

    def getCurrentItems(self):

        """Returns Current top level item and child index.
        If no child is selected, returns -1.
        """

        # Check if top level item is selected or child selected
        if self.indexOfTopLevelItem(self.currentItem()) == -1:
            return self.currentItem().parent(), self.currentItem().parent().indexOfChild(
                self.currentItem())
        else:
            return self.currentItem(), -1

    def dropMimeData(self, parent, row, data, action):
        if action == QtCore.Qt.MoveAction:
            return self.moveSelection(parent, row)
        return False

    def moveSelection(self, parent, position):
        # save the selected items
        selection = [QtCore.QPersistentModelIndex(i)
                     for i in self.selectedIndexes()]
        parent_index = self.indexFromItem(parent)
        if parent_index in selection:
            return False
        # save the drop location in case it gets moved
        target = self.model().index(position, 0, parent_index).row()
        if target < 0:
            target = position
        # remove the selected items
        taken = []
        for index in reversed(selection):
            item = self.itemFromIndex(QtCore.QModelIndex(index))
            if item is None or item.parent() is None:
                taken.append(self.takeTopLevelItem(index.row()))
            else:
                taken.append(item.parent().takeChild(index.row()))
        # insert the selected items at their new positions
        while taken:
            if position == -1:
                # append the items if position not specified
                if parent_index.isValid():
                    parent.insertChild(
                        parent.childCount(), taken.pop(0))
                else:
                    self.insertTopLevelItem(
                        self.topLevelItemCount(), taken.pop(0))
            else:
                # insert the items at the specified position
                if parent_index.isValid():
                    parent.insertChild(min(target,
                                           parent.childCount()), taken.pop(0))
                else:
                    self.insertTopLevelItem(min(target,
                                                self.topLevelItemCount()), taken.pop(0))
