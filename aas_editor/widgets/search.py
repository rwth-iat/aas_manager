#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from typing import List

from PyQt5.QtCore import QModelIndex, QPersistentModelIndex
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QAction, QTreeView

from aas_editor.models.search_proxy_model import SearchProxyModel
from aas_editor.settings.app_settings import NAME_ROLE, HIGHLIGHT_YELLOW
from aas_editor.settings.icon_settings import NEXT_ICON, PREV_ICON, FILTER_ICON, REGEX_ICON, CASE_ICON, CLOSE_ICON
from aas_editor.utils.util import absRow
from aas_editor.widgets import ToolBar
from aas_editor.widgets.lineEdit import LineEdit


class SearchBar(ToolBar):
    def __init__(self, view: QTreeView, filterColumns: List[int], parent: QWidget, closable=False):
        super(SearchBar, self).__init__(parent)
        self.view = view
        self.setModel(view.model())
        self.filterColumns = filterColumns

        self.searchLine = LineEdit(self)
        self.searchLine.setClearButtonEnabled(True)
        self.searchLine.setPlaceholderText("Search")
        self.filterBtn = QToolButton(self, icon=FILTER_ICON, toolTip="Filter",
                                    statusTip="Leave only matching items", checkable=True)
        self.filterBtn.setAutoRaise(True)
        self.regexBtn = QToolButton(self, icon=REGEX_ICON, toolTip="Regex",
                                    statusTip="Use regular expression", checkable=True)
        self.regexBtn.setAutoRaise(True)
        self.caseBtn = QToolButton(self, icon=CASE_ICON, toolTip="Match case",
                                   statusTip="Match upper/under case", checkable=True)
        self.caseBtn.setAutoRaise(True)
        self.nextBtn = QToolButton(self, icon=NEXT_ICON, toolTip="Next",
                                   statusTip="Navigate to the next occurrence")
        self.nextBtn.setAutoRaise(True)
        self.prevBtn = QToolButton(self, icon=PREV_ICON, toolTip="Previous",
                                   statusTip="Navigate to the prevous occurrence")
        self.prevBtn.setAutoRaise(True)
        self.closeBtn = QToolButton(self, icon=CLOSE_ICON, toolTip="Close",
                                    statusTip="Close search bar")
        if not closable:
            self.closeBtn.hide()
        self.closeBtn.setAutoRaise(True)

        self.foundItems: List[QPersistentModelIndex] = []

        self.buildHandlers()
        self.initLayout()

    def buildHandlers(self):
        self.view.modelChanged.connect(self.setModel)
        self.closeBtn.clicked.connect(self.closeBar)
        self.nextBtn.clicked.connect(self.next)
        self.prevBtn.clicked.connect(self.previous)

        self.caseBtn.toggled.connect(self.search)
        self.filterBtn.toggled.connect(self.search)
        self.regexBtn.toggled.connect(self.search)
        self.searchLine.textChanged.connect(self.search)

    def closeBar(self):
        self.searchLine.setText("")
        self.hide()

    def setModel(self, model):
        if isinstance(model, SearchProxyModel):
            self.model = model
        else:
            self.model = SearchProxyModel()
        self.model.setRecursiveFilteringEnabled(True)

    def search(self):
        self.view.itemDelegate().clearBgColors()
        self.foundItems = self.model.search(self.searchLine.text(),
                                            filterColumns=self.filterColumns,
                                            regExp=self.regexBtn.isChecked(),
                                            filter=self.filterBtn.isChecked(),
                                            matchCase=self.caseBtn.isChecked())
        if self.foundItems:
            self.view.setCurrentIndex(QModelIndex(self.foundItems[0]))
            for item in self.foundItems:
                self.view.itemDelegate().setBgColor(QModelIndex(item), QBrush(HIGHLIGHT_YELLOW))
        self.model.dataChanged.emit(QModelIndex(), QModelIndex())

    def next(self):
        items = [QModelIndex(i) for i in self.foundItems]
        items.sort(key=absRow)
        for item in items:
            print(item.data(NAME_ROLE))
        print(self.view.currentIndex().data(NAME_ROLE))
        for item in items:
            if absRow(item) > absRow(self.view.currentIndex()):
                self.view.setCurrentIndex(item)
                return

    def previous(self):
        items = [QModelIndex(i) for i in self.foundItems]
        items.sort(key=absRow, reverse=True)
        for item in items:
            print(item.data(NAME_ROLE))
        for item in items:
            if absRow(item) < absRow(self.view.currentIndex()):
                self.view.setCurrentIndex(item)
                return

    def toggleViewAction(self):
        return QAction("searchBar", self,
                       statusTip="Show/hide search bar",
                       toggled=self.toggleView,
                       checkable=True,
                       checked=True)

    def toggleView(self, toggled: bool):
        if toggled:
            self.show()
        else:
            self.hide()

    def initLayout(self):
        pathLayout = QHBoxLayout(self)
        pathLayout.setContentsMargins(0, 0, 0, 0)
        pathLayout.setSpacing(0)
        pathLayout.addWidget(self.searchLine)
        pathLayout.addWidget(self.prevBtn)
        pathLayout.addWidget(self.nextBtn)
        pathLayout.addWidget(self.filterBtn)
        pathLayout.addWidget(self.caseBtn)
        pathLayout.addWidget(self.regexBtn)
        pathLayout.addWidget(self.closeBtn)
        searchBtns = QWidget(self)
        searchBtns.setLayout(pathLayout)
        self.addWidget(searchBtns)
