#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from typing import Union

from aas_editor import dialogs
from aas_editor.import_feature.import_util_classes import TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES
from aas_editor.settings.app_settings import *
from aas_editor.settings import EXTENDED_COLUMNS_IN_PACK_TABLE
from aas_editor.models import StandardTable
from aas_editor.import_feature.table_import import ImportTable
from aas_editor.import_feature.treeview_import import ImportTreeView, DetailImportTreeView
from aas_editor.editorApp import EditorApp
from aas_editor.import_feature.import_file_widget import ImportManageWidget
from aas_editor.utils.util_type import issubtype, removeOptional, isUnion, getArgs
from aas_editor.widgets import TabWidget
from aas_editor.import_feature.table_import_detailed_info import DetailedInfoImportTable
from import_feature.item_import_treeview import ImportTreeViewItem


def handleTypeHint4import(objTypeHint, parent):
    def importClsInParentTypehints():
        if not hasattr(parent, "objTypes"):
            return False
        if not parent.objTypes:
            return False
        for special_import_obj_cls in TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES.values():
            if special_import_obj_cls in parent.objTypes:
                return True
        return False

    def addSpecialImportObjClsTypeHint(typehint):
        for typ in TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES:
            if issubtype(typehint, typ):
                importCls = TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES[typ]
                typehint = Union[typehint, importCls]
                return typehint
        return typehint

    objTypeHint = removeOptional(objTypeHint)

    if isUnion(objTypeHint) and not importClsInParentTypehints():
        unionTypehints = getArgs(objTypeHint)
        for typehint in unionTypehints:
            newtyp = addSpecialImportObjClsTypeHint(typehint)
            objTypeHint = Union[newtyp, objTypeHint]
    elif issubtype(objTypeHint, tuple(TYPS_TO_SPECIAL_IMPORT_OBJ_CLASSES.keys())) and not importClsInParentTypehints():
        objTypeHint = addSpecialImportObjClsTypeHint(objTypeHint)

    return objTypeHint


class ImportApp(EditorApp):

    def show(self):
        if not self.importWidget.execImportSettingsDialog():
            self.close()
            return
        setattr(dialogs.InputWidgetUtil, "handleTypeHint", handleTypeHint4import)
        super().show()

    def __del__(self):
        setattr(dialogs.InputWidgetUtil, "handleTypeHint", dialogs.InputWidgetUtil._handleTypeHint)
        del self


    def setupMainTreeView(self, parent, model: StandardTable) -> ImportTreeView:
        mainTreeView = ImportTreeView(parent, importManageWidget=self.importWidget)
        mainTreeView.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        mainTreeView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        mainTreeView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        mainTreeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        mainTreeView.setModelWithProxy(model)
        for column in range(model.columnCount(), 2, -1):
            mainTreeView.hideColumn(column)
        return mainTreeView

    def setupMainTreeModel(self) -> StandardTable:
        columns_in_packs_table = list(DEFAULT_COLUMNS_IN_PACKS_TABLE)
        columns_in_packs_table.extend(EXTENDED_COLUMNS_IN_PACK_TABLE)
        return ImportTable(columns_in_packs_table, ImportTreeViewItem(None, None))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(f"{_translate('MainWindow', WINDOW_TITLE)} Import Mode")
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

    def setupUi(self, MainWindow):
        self.importWidget = ImportManageWidget(self)
        super(ImportApp, self).setupUi(MainWindow)
        self.mainTabWidget.deleteLater()
        self.mainTabWidget = TabWidget(self.splitterTabWidgets, unclosable=True,
                                       tabClsKwargs={"treeViewCls": DetailImportTreeView,
                                                     "treeViewClsKwargs": {"treeModel": DetailedInfoImportTable}})
        self.importWidget.setTreeView(self.mainTreeView)
        self.mainVerticalLayout.insertWidget(1, self.importWidget)
