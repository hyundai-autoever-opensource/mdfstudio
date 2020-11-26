# -*- coding: utf-8 -*-
# Copyright 2020.Hyundai Autoever.All rights reserved. License under the GNU LESSER GENERAL PUBLIC LICENSE Version 3


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_About(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(728, 575)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 691, 201))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit.setGeometry(QtCore.QRect(20, 30, 121, 91))
        self.textEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_2.setGeometry(QtCore.QRect(160, 30, 151, 91))
        font = QtGui.QFont()
        font.setFamily("Bodoni MT Poster Compressed")
        self.textEdit_2.setFont(font)
        self.textEdit_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setObjectName("textEdit_2")
        self.textEdit_3 = QtWidgets.QTextEdit(self.groupBox)
        self.textEdit_3.setGeometry(QtCore.QRect(20, 130, 641, 51))
        self.textEdit_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textEdit_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_3.setReadOnly(True)
        self.textEdit_3.setObjectName("textEdit_3")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(20, 220, 691, 321))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.copyright_tab = QtWidgets.QWidget()
        self.copyright_tab.setObjectName("copyright_tab")
        self.coptyright_text = QtWidgets.QTextEdit(self.copyright_tab)
        self.coptyright_text.setGeometry(QtCore.QRect(20, 20, 641, 251))
        self.coptyright_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.coptyright_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.coptyright_text.setReadOnly(True)
        self.coptyright_text.setObjectName("coptyright_text")
        self.coptyright_text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tabWidget.addTab(self.copyright_tab, "")
        self.license_tab = QtWidgets.QWidget()
        self.license_tab.setObjectName("license_tab")
        self.license_text = QtWidgets.QTextEdit(self.license_tab)
        self.license_text.setGeometry(QtCore.QRect(20, 20, 641, 251))
        self.license_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.license_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.license_text.setReadOnly(True)
        self.license_text.setObjectName("license_text")
        self.tabWidget.addTab(self.license_tab, "")
        self.package_tab = QtWidgets.QWidget()
        self.package_tab.setObjectName("package_tab")
        self.package_text = QtWidgets.QTextEdit(self.package_tab)
        self.package_text.setGeometry(QtCore.QRect(20, 20, 641, 251))
        self.package_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.package_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.package_text.setReadOnly(True)
        self.package_text.setObjectName("package_text")
        self.package_text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tabWidget.addTab(self.package_tab, "")
        self.upcoming_tab = QtWidgets.QWidget()
        self.upcoming_tab.setObjectName("upcoming_tab")
        self.upcoming_text = QtWidgets.QTextEdit(self.upcoming_tab)
        self.upcoming_text.setGeometry(QtCore.QRect(20, 20, 641, 251))
        self.upcoming_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.upcoming_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.upcoming_text.setReadOnly(True)
        self.upcoming_text.setObjectName("upcoming_text")
        self.upcoming_text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tabWidget.addTab(self.upcoming_tab, "")
        self.close_btn = QtWidgets.QPushButton(Form)
        self.close_btn.setGeometry(QtCore.QRect(588, 545, 121, 24))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        self.close_btn.setFont(font)
        self.close_btn.setObjectName("close_btn")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("Form", "Version Information for MDF Studio"))
        self.textEdit.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">MDF Studio :</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">Expired date :</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">Authorized users :</span></p></body></html>"))
        self.coptyright_text.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">This software was created by HAE.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"

"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">Used Python Open Source Library List</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">- asammdf-5.21.0 (https://github.com/danielhrisca/asammdf) : LGPL 3.0</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">Open Source Library loaded in this program can be obtained free of charge from https://github.com/hyundai-autoever-opensource/mdfstudio</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:9pt; font-weight:400;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'맑은 고딕\';font-size:8pt; font-weight:400;\">개발 : 현대오토에버 - 영업총괄사업부 - ICT수행실 - 연구개발수행팀</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.copyright_tab), _translate("Form", "Software"))
        self.license_text.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:60px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'JetBrains Mono\'; font-size:9.8pt; font-weight:400; color:#080808;\">                   GNU LESSER GENERAL PUBLIC LICENSE<br />                       Version 3, 29 June 2007<br /><br /> Copyright (C) 2007 Free Software Foundation, Inc. &lt;https://fsf.org/&gt;<br /> Everyone is permitted to copy and distribute verbatim copies<br /> of this license document, but changing it is not allowed.<br /><br /><br />  This version of the GNU Lesser General Public License incorporates<br />the terms and conditions of version 3 of the GNU General Public<br />License, supplemented by the additional permissions listed below.<br /><br />  0. Additional Definitions.<br /><br />  As used herein, &quot;this License&quot; refers to version 3 of the GNU Lesser<br />General Public License, and the &quot;GNU GPL&quot; refers to version 3 of the GNU<br />General Public License.<br /><br />  &quot;The Library&quot; refers to a covered work governed by this License,<br />other than an Application or a Combined Work as defined below.<br /><br />  An &quot;Application&quot; is any work that makes use of an interface provided<br />by the Library, but which is not otherwise based on the Library.<br />Defining a subclass of a class defined by the Library is deemed a mode<br />of using an interface provided by the Library.<br /><br />  A &quot;Combined Work&quot; is a work produced by combining or linking an<br />Application with the Library.  The particular version of the Library<br />with which the Combined Work was made is also called the &quot;Linked<br />Version&quot;.<br /><br />  The &quot;Minimal Corresponding Source&quot; for a Combined Work means the<br />Corresponding Source for the Combined Work, excluding any source code<br />for portions of the Combined Work that, considered in isolation, are<br />based on the Application, and not on the Linked Version.<br /><br />  The &quot;Corresponding Application Code&quot; for a Combined Work means the<br />object code and/or source code for the Application, including any data<br />and utility programs needed for reproducing the Combined Work from the<br />Application, but excluding the System Libraries of the Combined Work.<br /><br />  1. Exception to Section 3 of the GNU GPL.<br /><br />  You may convey a covered work under sections 3 and 4 of this License<br />without being bound by section 3 of the GNU GPL.<br /><br />  2. Conveying Modified Versions.<br /><br />  If you modify a copy of the Library, and, in your modifications, a<br />facility refers to a function or data to be supplied by an Application<br />that uses the facility (other than as an argument passed when the<br />facility is invoked), then you may convey a copy of the modified<br />version:<br /><br />   a) under this License, provided that you make a good faith effort to<br />   ensure that, in the event an Application does not supply the<br />   function or data, the facility still operates, and performs<br />   whatever part of its purpose remains meaningful, or<br /><br />   b) under the GNU GPL, with none of the additional permissions of<br />   this License applicable to that copy.<br /><br />  3. Object Code Incorporating Material from Library Header Files.<br /><br />  The object code form of an Application may incorporate material from<br />a header file that is part of the Library.  You may convey such object<br />code under terms of your choice, provided that, if the incorporated<br />material is not limited to numerical parameters, data structure<br />layouts and accessors, or small macros, inline functions and templates<br />(ten or fewer lines in length), you do both of the following:<br /><br />   a) Give prominent notice with each copy of the object code that the<br />   Library is used in it and that the Library and its use are<br />   covered by this License.<br /><br />   b) Accompany the object code with a copy of the GNU GPL and this license<br />   document.<br /><br />  4. Combined Works.<br /><br />  You may convey a Combined Work under terms of your choice that,<br />taken together, effectively do not restrict modification of the<br />portions of the Library contained in the Combined Work and reverse<br />engineering for debugging such modifications, if you also do each of<br />the following:<br /><br />   a) Give prominent notice with each copy of the Combined Work that<br />   the Library is used in it and that the Library and its use are<br />   covered by this License.<br /><br />   b) Accompany the Combined Work with a copy of the GNU GPL and this license<br />   document.<br /><br />   c) For a Combined Work that displays copyright notices during<br />   execution, include the copyright notice for the Library among<br />   these notices, as well as a reference directing the user to the<br />   copies of the GNU GPL and this license document.<br /><br />   d) Do one of the following:<br /><br />       0) Convey the Minimal Corresponding Source under the terms of this<br />       License, and the Corresponding Application Code in a form<br />       suitable for, and under terms that permit, the user to<br />       recombine or relink the Application with a modified version of<br />       the Linked Version to produce a modified Combined Work, in the<br />       manner specified by section 6 of the GNU GPL for conveying<br />       Corresponding Source.<br /><br />       1) Use a suitable shared library mechanism for linking with the<br />       Library.  A suitable mechanism is one that (a) uses at run time<br />       a copy of the Library already present on the user\'s computer<br />       system, and (b) will operate properly with a modified version<br />       of the Library that is interface-compatible with the Linked<br />       Version.<br /><br />   e) Provide Installation Information, but only if you would otherwise<br />   be required to provide such information under section 6 of the<br />   GNU GPL, and only to the extent that such information is<br />   necessary to install and execute a modified version of the<br />   Combined Work produced by recombining or relinking the<br />   Application with a modified version of the Linked Version. (If<br />   you use option 4d0, the Installation Information must accompany<br />   the Minimal Corresponding Source and Corresponding Application<br />   Code. If you use option 4d1, you must provide the Installation<br />   Information in the manner specified by section 6 of the GNU GPL<br />   for conveying Corresponding Source.)<br /><br />  5. Combined Libraries.<br /><br />  You may place library facilities that are a work based on the<br />Library side by side in a single library together with other library<br />facilities that are not Applications and are not covered by this<br />License, and convey such a combined library under terms of your<br />choice, if you do both of the following:<br /><br />   a) Accompany the combined library with a copy of the same work based<br />   on the Library, uncombined with any other library facilities,<br />   conveyed under the terms of this License.<br /><br />   b) Give prominent notice with the combined library that part of it<br />   is a work based on the Library, and explaining where to find the<br />   accompanying uncombined form of the same work.<br /><br />  6. Revised Versions of the GNU Lesser General Public License.<br /><br />  The Free Software Foundation may publish revised and/or new versions<br />of the GNU Lesser General Public License from time to time. Such new<br />versions will be similar in spirit to the present version, but may<br />differ in detail to address new problems or concerns.<br /><br />  Each version is given a distinguishing version number. If the<br />Library as you received it specifies that a certain numbered version<br />of the GNU Lesser General Public License &quot;or any later version&quot;<br />applies to it, you have the option of following the terms and<br />conditions either of that published version or of any later version<br />published by the Free Software Foundation. If the Library as you<br />received it does not specify a version number of the GNU Lesser<br />General Public License, you may choose any version of the GNU Lesser<br />General Public License ever published by the Free Software Foundation.<br /><br />  If the Library as you received it specifies that a proxy can decide<br />whether future versions of the GNU Lesser General Public License shall<br />apply, that proxy\'s public statement of acceptance of any version is<br />permanent authorization for you to choose that version for the<br />Library.<br /></span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.license_tab), _translate("Form", "License"))
        self.package_text.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">This software was developed by Python 3.7</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">MDF studio uses the following libraries:</span><span style=\" font-size:9pt; font-weight:400;\"><br />  - cChardet : to detect non-standard unicode encodings</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - hdf5storage : for Matlab v7.3 .mat export</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - lxml : for canmatrix arxml support</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - lz4 : to speed up the disk IO peformance</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - matplotlib : as fallback for Signal plotting</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - natsort : for fast channel sorting</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - numexpr : for algebraic and rational channel conversions</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - numpy : the heart that makes all tick</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - pandas : for DataFrame export</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - PyQt5 : for GUI tool</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - pyqtgraph : for GUI tool and Signal plotting (preferably the latest develop branch code)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - scipy : for Matlab v4 and v5 .mat export</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">  - wheel : for installation in virtual environments</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.package_tab), _translate("Form", "Package Information"))
        self.upcoming_text.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:600; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">This software will be updated regularly.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">---------------------------------------------------------------------------------------------------------------------</span></p>"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">Next version contains below :</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">1) Compare MDF files </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">2) Merge MDF files</span></p>\n"                                                    
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">3) ROM Editor : more convenient than INCA CDM with variable functions.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">4) INCA Control Automation</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\">5) CANDB Editor : for creating and editing CAN DBC files with NIDS template.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt; font-weight:400;\"><br /></span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.upcoming_tab), _translate("Form", "Upcoming updates"))
        self.close_btn.setText(_translate("Form", "Close"))

