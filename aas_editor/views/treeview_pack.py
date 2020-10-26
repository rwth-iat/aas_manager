from typing import Iterable

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from aas.model import Submodel, AssetAdministrationShell, Asset, SubmodelElement

from aas_editor.models import Package, ConceptDescription
from aas_editor.settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ATTRS
from aas_editor.util import isoftype
from aas_editor.views.treeview import TreeView


class PackTreeView(TreeView):
    def __init__(self, parent=None):
        super(PackTreeView, self).__init__(parent)
        PackTreeView.__instance = self
        self._upgradeMenu()

    # noinspection PyUnresolvedReferences
    def _upgradeMenu(self):
        self.openInCurrTabAct.setEnabled(True)
        self.openInNewTabAct.setEnabled(True)
        self.openInBackgroundAct.setEnabled(True)

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
        name = index.data(NAME_ROLE)

        # update paste action
        if self._isPasteOk(index):
            self.pasteAct.setEnabled(True)
        else:
            self.pasteAct.setEnabled(False)

        self.addAct.setEnabled(True)
        if isinstance(obj, Package) or not index.isValid():
            self.addAct.setText("Add package")
        elif name in PACKAGE_ATTRS:
            self.addAct.setText(f"Add {name.rstrip('s')}")
        elif isinstance(obj, Submodel):
            self.addAct.setText(f"Add submodel element")
        else:
            self.addAct.setText(f"Add")
            self.addAct.setEnabled(False)

    def _isPasteOk(self, index: QModelIndex) -> bool:
        if not self.treeObjClipboard:
            return False
        else:
            obj2paste = self.treeObjClipboard[0]

        attrName = index.data(NAME_ROLE)
        currObj = index.data(OBJECT_ROLE)

        if isinstance(obj2paste, AssetAdministrationShell):
            if isinstance(currObj, AssetAdministrationShell) or attrName == "shells":
                return True
        elif isinstance(obj2paste, Asset):
            if isinstance(currObj, Asset) or attrName == "assets":
                return True
        elif isinstance(obj2paste, Submodel):
            if isinstance(currObj, Submodel) or attrName == "submodels":
                return True
        elif isinstance(obj2paste, SubmodelElement):
            if isinstance(currObj, SubmodelElement):
                return True
        elif isinstance(obj2paste, ConceptDescription):
            if isinstance(currObj, ConceptDescription) or attrName == "concept_descriptions":
                return True
        return False

    def _addHandler(self, objVal=None, parent: QModelIndex = None):
        parent = parent if parent else self.currentIndex()
        name = parent.data(NAME_ROLE)

        if objVal:
            kwargs = {"parent": parent,
                      "rmDefParams": False,
                      "objVal": objVal}
        else:
            kwargs = {"parent": parent,
                      "rmDefParams": True}

        if isinstance(parent.data(OBJECT_ROLE), Package) or not parent.isValid():
            kwargs["parent"] = QModelIndex()
            self.addItemWithDialog(objType=Package, **kwargs)
        elif name == "shells":
            self.addItemWithDialog(objType=AssetAdministrationShell, **kwargs)
        elif name == "assets":
            self.addItemWithDialog(objType=Asset, **kwargs)
        elif name == "submodels":
            self.addItemWithDialog(objType=Submodel, **kwargs)
        elif name == "concept_descriptions":
            self.addItemWithDialog(objType=ConceptDescription, **kwargs)
        elif isinstance(parent.data(OBJECT_ROLE), Submodel):
            self.addItemWithDialog(objType=SubmodelElement, **kwargs)
        else:
            raise TypeError("Parent type is not extendable:", type(parent.data(OBJECT_ROLE)))
