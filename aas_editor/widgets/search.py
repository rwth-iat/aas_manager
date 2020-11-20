from typing import List

from PyQt5.QtCore import QModelIndex, QPersistentModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QToolButton, QAction, QTreeView

from aas_editor.models.search_proxy_model import SearchProxyModel
from aas_editor.settings import REGEX_ICON, CASE_ICON, NEXT_ICON, PREV_ICON, FILTER_ICON, \
    NAME_ROLE, ATTRIBUTE_COLUMN, CLOSE_ICON
from aas_editor.util import absRow


class SearchBar(QWidget):
    def __init__(self, view: QTreeView, filterColumns: List[int], parent: QWidget, closable=False):
        super(SearchBar, self).__init__(parent)
        self.view = view
        self.setModel(view.model())
        self.filterColumns = filterColumns

        self.searchLine = QLineEdit(self)
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
        self.foundItems = self.model.setHighLightFilter(self.searchLine.text(),
                                                        filterColumns=self.filterColumns,
                                                        regExp=self.regexBtn.isChecked(),
                                                        filter=self.filterBtn.isChecked(),
                                                        matchCase=self.caseBtn.isChecked())
        if self.foundItems:
            self.view.setCurrentIndex(QModelIndex(self.foundItems[0]))

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
