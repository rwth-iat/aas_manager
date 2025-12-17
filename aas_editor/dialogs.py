#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
import json

from PyQt6.QtGui import QGuiApplication
from basyx.aas.adapter.json import AASFromJsonDecoder

from typing import Optional

from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, \
    QWidget, QVBoxLayout, QScrollArea, QFrame

import widgets.buttons
import widgets.editWidgets
from aas_editor.settings import ATTRIBUTE_COLUMN
from aas_editor.utils.util import actualizeAASParents
from aas_editor.utils.util_type import getTypeName, isoftype
from aas_editor.utils.util_classes import PreObject
from aas_editor import widgets
from widgets.jsonEditor import JSONEditor
from widgets.widget_util import InputWidgetUtil

def checkIfAccepted(func):
    """Decorator for checking if user clicked ok"""

    def wrap(editDialog):
        if editDialog.result() == QDialog.DialogCode.Accepted:
            return func(editDialog)
        else:
            raise ValueError("Editing/Adding was cancelled")

    return wrap

class EditDialog(QDialog):
    """Base abstract class for custom dialogs for adding or editing data"""
    REC = QGuiApplication.primaryScreen().geometry()
    MAX_HEIGHT = int(REC.height() * 0.9)
    MIN_WIDTH = 450
    SAVED_SIZE = None
    SAVED_POSITION = None

    def __init__(self, parent=None, title=""):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                          QDialogButtonBox.StandardButton.Cancel, self)
        self.buttonCancel = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        self.buttonCancel.released.connect(self.reject)
        self.buttonOk = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.buttonOk.released.connect(self.accept)
        self.buttonOk.setDisabled(True)
        self.buttonOk.setDefault(True)
        self.buttonOk.setAutoDefault(True)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumHeight(self.MAX_HEIGHT)

        self.verticalLayout = QVBoxLayout(self)
        self.buttonBox.setContentsMargins(*self.verticalLayout.getContentsMargins())
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayoutScroll = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayoutScroll.setContentsMargins(0, 0, 0, 0)

        self.restorePosition()
        self.restoreSize()

    def adjustSize(self) -> None:
        layoutSize = self.layout().sizeHint()
        buttonsSize = self.buttonBox.sizeHint()
        result = QSize(max(layoutSize.width(), buttonsSize.width(), self.width()),
                       max(layoutSize.height(), self.height()))
        self.resize(result)

    def layout(self) -> 'QLayout':
        return self.verticalLayoutScroll

    def getObj2add(self):
        pass

    def closeEvent(self, event):
        self.savePositionAndSize(self)
        super().closeEvent(event)

    def reject(self):
        self.savePositionAndSize(self)
        super().reject()
        
    def accept(self):
        self.savePositionAndSize(self)
        super().accept()

    @classmethod
    def savePositionAndSize(cls, dialog: 'EditDialog' = None):
        cls.SAVED_POSITION = dialog.pos()
        cls.SAVED_SIZE = dialog.size()

    def restorePosition(self):
        if self.SAVED_POSITION:
            self.move(self.SAVED_POSITION)

    def restoreSize(self):
        if self.SAVED_SIZE:
            self.resize(self.SAVED_SIZE)


class EditObjDialog(EditDialog):
    SAVED_SIZE = None
    SAVED_POSITION = None

    def __init__(self, objTypeHint, parent: 'TreeView', title="", rmDefParams=True, objVal=None, **kwargs):
        title = title if title else f"Add {getTypeName(objTypeHint)}"
        EditDialog.__init__(self, parent, title=title)
        self.buttonOk.setEnabled(True)

        if not isoftype(objVal, PreObject):
            objVal = copy.deepcopy(objVal)
        actualizeAASParents(objVal)

        kwargs = {
            **kwargs,
            "rmDefParams": rmDefParams,
            "objVal": objVal,
            "parent": self,
        }

        self.inputWidget = InputWidgetUtil.getInputWidget(objTypeHint, **kwargs)
        self.inputWidget.setObjectName("mainBox")
        self.inputWidget.setStyleSheet("#mainBox{border:0;}")  # FIXME
        self.layout().addWidget(self.inputWidget)
        QTimer.singleShot(0, self.adjustSize)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.inputWidget.getObj2add()

    @checkIfAccepted
    def getPreObj(self):
        return self.inputWidget.getPreObj()


class EditObjJsonDialog(EditDialog):
    SAVED_SIZE = None
    SAVED_POSITION = None

    def __init__(self, parent: 'TreeView', title="", objVal=None, **kwargs):
        title = title if title else f"Add object from JSON"
        EditDialog.__init__(self, parent, title=title)
        self.buttonOk.setEnabled(True)

        self.inputWidget = JSONEditor(self)
        self.inputWidget.setText(objVal)
        self.layout().addWidget(self.inputWidget)
        QTimer.singleShot(0, self.adjustSize)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        obj = json.loads(self.inputWidget.text(), cls=AASFromJsonDecoder)
        return obj


class ChooseItemDialog(EditDialog):
    def __init__(self, view: 'TreeView', columnsToShow=(ATTRIBUTE_COLUMN,),
                 validator=lambda chosenIndex: chosenIndex.isValid(),
                 parent: Optional[QWidget] = None, title: str = ""):
        super(ChooseItemDialog, self).__init__(parent, title)
        self.setFixedHeight(500)
        self.validator = validator
        self.view = view
        self.view.setParent(self)
        self.view.setModelWithProxy(self.view.sourceModel())
        self.view.expandAll()
        self.view.setHeaderHidden(True)

        for column in range(self.view.model().columnCount()):
            if column not in columnsToShow:
                self.view.hideColumn(column)

        self.searchBar = widgets.SearchBar(self.view, parent=self, filterColumns=columnsToShow)
        self.toolBar = widgets.ToolBar(self)
        self.toolBar.addAction(self.view.collapseAllAct)
        self.toolBar.addAction(self.view.expandAllAct)
        self.toolBar.addWidget(self.searchBar)

        self.layout().insertWidget(0, self.toolBar)
        self.layout().insertWidget(1, self.view)
        self.buildHandlers()

    def buildHandlers(self):
        self.view.selectionModel().currentChanged.connect(self.validate)

    def validate(self):
        chosenIndex = self.view.currentIndex()
        if chosenIndex.isValid() and self.validator(chosenIndex):
            self.buttonOk.setEnabled(True)
        else:
            self.buttonOk.setDisabled(True)

    def getObj2add(self):
        return self.view.currentIndex()

    def getChosenItem(self):
        return self.getObj2add()
