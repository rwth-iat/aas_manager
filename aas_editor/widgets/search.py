from PyQt5.QtCore import QAbstractProxyModel, QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QToolButton, QAction

from aas_editor.settings import REGEX_ICON, CASE_ICON, NEXT_ICON, PREV_ICON


class SearchBar(QWidget):
    def __init__(self, proxymodel: QSortFilterProxyModel, parent: QWidget):
        super(SearchBar, self).__init__(parent)
        self.model = proxymodel
        self.searchLine = QLineEdit(self)
        self.searchLine.setClearButtonEnabled(True)
        self.searchLine.setPlaceholderText("Search")
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

        self.buildHandlers()
        self.initLayout()

    def buildHandlers(self):
        self.caseBtn.toggled.connect(self.setMatchCase)
        self.regexBtn.toggled.connect(self.setRegex)
        self.searchLine.textChanged.connect(self.search)

    def setMatchCase(self, checked: bool):
        if checked:
            self.model.setFilterCaseSensitivity(Qt.CaseSensitive)
        else:
            self.model.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def setRegex(self, checked: bool):
        self.search(self.searchLine.text())

    def search(self, text: str):
        if self.regexBtn.isChecked():
            self.model.setFilterRegExp(text)
        else:
            self.model.setFilterFixedString(text)

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
        pathLayout.addWidget(self.caseBtn)
        pathLayout.addWidget(self.regexBtn)
