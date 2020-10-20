from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from aas.model import Submodel, AssetAdministrationShell, Asset, SubmodelElement

from aas_editor.models import Package
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE
from aas_editor.views.treeview import TreeView


class PackTreeView(TreeView):
    """Singleton class"""
    __instance = None

    @staticmethod
    def instance() -> 'PackTreeView':
        """Instance access method"""
        if PackTreeView.__instance is None:
            PackTreeView()
        return PackTreeView.__instance

    def __init__(self, parent=None):
        if PackTreeView.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super(PackTreeView, self).__init__(parent)
            PackTreeView.__instance = self
            self._upgradeMenu()

    # noinspection PyUnresolvedReferences
    def _upgradeMenu(self):
        self.openInCurrTabAct.triggered.connect(
            lambda: self.openInCurrTabClicked.emit(self.currentIndex()))
        self.openInNewTabAct.triggered.connect(
            lambda: self.openInNewTabClicked.emit(self.currentIndex()))
        self.openInBackgroundAct.triggered.connect(
            lambda: self.openInBackgroundTabClicked.emit(self.currentIndex()))

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        super(PackTreeView, self).setModel(model)
        self.selectionModel().currentChanged.connect(self._updateMenu)

    def _updateMenu(self, index: QModelIndex):
        # update add action
        obj = index.data(OBJECT_ROLE)
        if isinstance(obj, (Iterable, Submodel, Package)) or not index.isValid():
            self.addAct.setEnabled(True)
        else:
            self.addAct.setEnabled(False)

    def _addHandler(self, objVal=None):
        index = self.currentIndex()
        name = index.data(NAME_ROLE)

        if objVal:
            kwargs = {"parent": index,
                      "rmDefParams": False,
                      "objVal": objVal}
        else:
            kwargs = {"parent": index,
                      "rmDefParams": True}

        if isinstance(index.data(OBJECT_ROLE), Package) or not index.isValid():
            kwargs["parent"] = QModelIndex()
            self.addItemWithDialog(objType=Package, **kwargs)
        elif name == "shells":
            self.addItemWithDialog(objType=AssetAdministrationShell, **kwargs)
        elif name == "assets":
            self.addItemWithDialog(objType=Asset, **kwargs)
        elif name == "submodels":
            self.addItemWithDialog(objType=Submodel, **kwargs)
        elif isinstance(index.data(OBJECT_ROLE), Submodel):
            self.addItemWithDialog(objType=SubmodelElement, **kwargs)