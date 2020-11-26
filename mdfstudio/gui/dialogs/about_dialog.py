from PyQt5 import QtWidgets, QtGui, QtCore

from ..ui.about import Ui_About
from ...version import __target_kor__ as target_kor
from ...version import __target__ as target
from ...version import __expired__ as expired
from ...version import __version__ as version

class AboutWidget(Ui_About, QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/main_icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.setWindowIcon(icon)

        palette = QtGui.QPalette()
        br_blue = QtGui.QBrush(QtGui.QColor(0, 59, 126))
        br_white = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        br_black = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        br_light_sand = QtGui.QBrush(QtGui.QColor(246, 243, 242))
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, br_light_sand)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, br_light_sand)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, br_light_sand)
        self.setPalette(palette)

        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, br_white)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, br_white)
        self.tabWidget.setPalette(palette)

        self.setWindowTitle(f"About MDF Studio - {target}")
        _translate = QtCore.QCoreApplication.translate
        self.textEdit_2.setHtml(_translate("Form",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Bodoni MT Poster Compressed\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
                                           f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Calibri\'; font-size:9pt; font-weight:400;\">{version}</span></p>\n"
                                           "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\'; font-size:9pt; font-weight:400;\"><br /></p>\n"
                                           f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Calibri\'; font-size:9pt; font-weight:400;\">{expired}</span></p>\n"
                                           "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Calibri\'; font-size:9pt; font-weight:400;\"><br /></p>\n"
                                           f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'맑은 고딕\'; font-size:9pt; font-weight:400;\">{target_kor}</span></p></body></html>"))
        self.textEdit_3.setHtml(_translate("Form",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
                                           "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400; color:#080808;\">MDF Studio is asam mdf file viewer &amp; converter for research and analysis, including LGPL 3.0 open source license (asammdf, mdfstudio)</span></p></body></html>"))

        self.close_btn.clicked.connect(self.close)