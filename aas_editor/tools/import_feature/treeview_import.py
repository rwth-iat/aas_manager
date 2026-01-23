#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtCore import QModelIndex

from aas_editor.tools.import_feature.import_util_classes import PreObjectImport
from aas_editor.treeviews import PackTreeView, AttrsTreeView


class ImportTreeView(PackTreeView):
    #    def updateActions(self, index: QModelIndex):
    #    def onAddAct(self, objVal=None, parent: QModelIndex = None):
    #    def onEdit

    def __init__(self, parent=None, *, importManageWidget):
        super(ImportTreeView, self).__init__(parent)
        self.importManageWidget = importManageWidget

    def _getObjFromDialog(self, dialog):
        return PreObjectImport.fromPreObject(dialog.getPreObj())

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False, **kwargs):
        kwargs["useValidators"] = False
        return super().addItemWithDialog(parent=parent, objTypeHint=objTypeHint, objVal=objVal, title=title,
                                         rmDefParams=rmDefParams, **kwargs)

    def replItemWithDialog(self, index, objTypeHint, objVal=None, title="", rmDefParams=False, **kwargs):
        kwargs["useValidators"] = False
        return super().replItemWithDialog(index=index, objTypeHint=objTypeHint, objVal=objVal,
                                          title=title, rmDefParams=rmDefParams, **kwargs)


class DetailImportTreeView(AttrsTreeView):
    def _getObjFromDialog(self, dialog):
        return PreObjectImport.fromPreObject(dialog.getPreObj())

    def addItemWithDialog(self, parent: QModelIndex, objTypeHint, objVal=None,
                          title="", rmDefParams=False, **kwargs):
        kwargs["useValidators"] = False
        return super().addItemWithDialog(parent=parent, objTypeHint=objTypeHint, objVal=objVal, title=title,
                                         rmDefParams=rmDefParams, **kwargs)

    def replItemWithDialog(self, index, objTypeHint, objVal=None, title="", rmDefParams=False, **kwargs):
        kwargs["useValidators"] = False
        return super().replItemWithDialog(index=index, objTypeHint=objTypeHint, objVal=objVal,
                                          title=title, rmDefParams=rmDefParams, **kwargs)

    def isEditableInsideCell(self, index: QModelIndex):
        return False
