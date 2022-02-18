# -*- coding: utf-8 -*-

#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

# Form implementation generated from reading ui file 'aas_editor/mainwindow_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout

from aas_editor.settings.app_settings import APPLICATION_NAME, TOOLBARS_HEIGHT, ATTRIBUTE_COLUMN, AppSettings
from aas_editor.widgets import ToolBar, PackTreeView, TabWidget, SearchBar


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(2, 0, 2, 0)

        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setObjectName("splitter")

        # Left part
        self.leftLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.leftLayoutWidget.setObjectName("layoutWidget")
        self.leftVerticalLayout = QtWidgets.QVBoxLayout(self.leftLayoutWidget)
        self.leftVerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.leftVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftVerticalLayout.setSpacing(5)
        self.leftVerticalLayout.setObjectName("verticalLayout")

        self.packTreeView = PackTreeView(self.leftLayoutWidget)
        self.packTreeView.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.packTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.packTreeView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.packTreeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.packTreeView.setObjectName("packTreeView")

        self.toolBar = ToolBar(self.leftLayoutWidget)
        self.toolBar.setObjectName("toolBar")
        self.leftVerticalLayout.addWidget(self.toolBar)
        self.searchBarPack = SearchBar(self.packTreeView, filterColumns=[ATTRIBUTE_COLUMN],
                                       parent=self.leftLayoutWidget, closable=True)
        self.leftVerticalLayout.addWidget(self.searchBarPack)


        self.leftVerticalLayout.addWidget(self.packTreeView)

        # Right part
        self.rightLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.rightLayoutWidget.setObjectName("rightLayoutWidget")
        self.rightVerticalLayout = QtWidgets.QVBoxLayout(self.rightLayoutWidget)
        self.rightVerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.rightVerticalLayout.setContentsMargins(0, 0, 0, 0)
        self.rightVerticalLayout.setObjectName("rightVerticalLayout")

        self.splitterTabWidgets = QtWidgets.QSplitter(self.rightLayoutWidget)
        self.splitterTabWidgets.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTabWidgets.setFrameShape(QFrame.StyledPanel)
        self.rightVerticalLayout.addWidget(self.splitterTabWidgets)

        self.mainTabWidget = TabWidget(self.splitterTabWidgets, unclosable=True)
        self.mainTabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", APPLICATION_NAME))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

    def setOrientation(self, o: QtCore.Qt.Orientation):
        if o == QtCore.Qt.Horizontal:
            self.splitter.setOrientation(QtCore.Qt.Horizontal)
            AppSettings.ORIENTATION.setValue(QtCore.Qt.Horizontal)
        elif o == QtCore.Qt.Vertical:
            self.splitter.setOrientation(QtCore.Qt.Vertical)
            AppSettings.ORIENTATION.setValue(QtCore.Qt.Vertical)

