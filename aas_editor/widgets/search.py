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

from PyQt6.QtCore import QModelIndex, QPersistentModelIndex, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QTreeView

from aas_editor.models.search_proxy_model import SearchProxyModel, treePath
from aas_editor.settings.icons import NEXT_ICON, PREV_ICON, FILTER_ICON, REGEX_ICON, CASE_ICON, CLOSE_ICON
from aas_editor.widgets.toolbar import ToolBar
from aas_editor.widgets.editWidgets import LineEdit


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
                                   statusTip="Navigate to the previous occurrence")
        self.prevBtn.setAutoRaise(True)
        self.closeBtn = QToolButton(self, icon=CLOSE_ICON, toolTip="Close",
                                    statusTip="Close search bar")
        if not closable:
            self.closeBtn.hide()
        self.closeBtn.setAutoRaise(True)

        self.foundItems: List[QPersistentModelIndex] = []
        # Typing restarts the timer: one search after a pause, not one per key
        self.searchTimer = QTimer(self, singleShot=True, interval=200, timeout=self.search)

        self.buildHandlers()
        self.initLayout()

    def buildHandlers(self):
        self.view.modelChanged.connect(self.setModel)
        self.closeBtn.clicked.connect(lambda: self.toggleView(False))
        self.nextBtn.clicked.connect(self.next)
        self.prevBtn.clicked.connect(self.previous)

        self.caseBtn.toggled.connect(self.search)
        self.filterBtn.toggled.connect(self.search)
        self.regexBtn.toggled.connect(self.search)
        self.searchLine.textChanged.connect(self.searchTimer.start)

    def closeBar(self):
        self.searchLine.setText("")
        self.hide()

    def setModel(self, model):
        if isinstance(model, SearchProxyModel):
            self.model = model
        else:
            self.model = SearchProxyModel()

    def search(self):
        self.searchTimer.stop()
        # Drop old hits first: Qt updates every live persistent index on refilter
        self.foundItems = []
        self.foundItems = self.model.search(self.searchLine.text(),
                                            filterColumns=self.filterColumns,
                                            regExp=self.regexBtn.isChecked(),
                                            filter=self.filterBtn.isChecked(),
                                            matchCase=self.caseBtn.isChecked())
        if self.foundItems:
            self.view.setCurrentIndex(QModelIndex(self.foundItems[0]))
        self.view.viewport().update()

    def next(self):
        current = treePath(self.view.currentIndex())
        # min/max, not list order: the user may re-sort the view after a search
        after = [QModelIndex(i) for i in self.foundItems if treePath(QModelIndex(i)) > current]
        if after:
            self.view.setCurrentIndex(min(after, key=treePath))

    def previous(self):
        current = treePath(self.view.currentIndex())
        before = [QModelIndex(i) for i in self.foundItems if treePath(QModelIndex(i)) < current]
        if before:
            self.view.setCurrentIndex(max(before, key=treePath))

    def toggleViewAction(self):
        return QAction("SearchBar", self,
                       statusTip="Show/hide search bar",
                       toggled=self.toggleView,
                       checkable=True,
                       # isHidden: isVisible is False until the window is shown
                       checked=not self.isHidden())

    def toggleView(self, toggled: bool):
        if toggled:
            self.show()
        else:
            self.hide()

    def showFocused(self):
        self.show()
        self.searchLine.setFocus()

    def initLayout(self):
        pathLayout = QHBoxLayout()
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
