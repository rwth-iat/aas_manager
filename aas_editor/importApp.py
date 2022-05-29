#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from aas_editor.settings.app_settings import *
from aas_editor.settings import EXTENDED_COLUMNS_IN_PACK_TABLE
from aas_editor.models import StandardTable
from aas_editor.import_feature.table_import import ImportTable
from aas_editor.import_feature.treeview_import import ImportTreeView
from aas_editor import design
from aas_editor.editorApp import EditorApp
from aas_editor.import_feature.import_file_widget import ImportManageWidget


class ImportApp(EditorApp):
    def setupMainTreeView(self, parent, model: StandardTable) -> ImportTreeView:
        mainTreeView = ImportTreeView(parent, importManageWidget=self.importWidget)
        mainTreeView.setFocusPolicy(QtCore.Qt.StrongFocus)
        mainTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        mainTreeView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        mainTreeView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        mainTreeView.setModelWithProxy(model)
        for column in range(model.columnCount(), 2, -1):
            mainTreeView.hideColumn(column)
        return mainTreeView

    def setupMainTreeModel(self) -> StandardTable:
        columns_in_packs_table = list(DEFAULT_COLUMNS_IN_PACKS_TABLE)
        columns_in_packs_table.extend(EXTENDED_COLUMNS_IN_PACK_TABLE)
        return ImportTable(columns_in_packs_table)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(f"{_translate('MainWindow', APPLICATION_NAME)} Import Mode")
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

    def setupUi(self, MainWindow):
        self.importWidget = ImportManageWidget(self)
        super(ImportApp, self).setupUi(MainWindow)
        self.importWidget.setTreeView(self.mainTreeView)
        self.mainVerticalLayout.insertWidget(1, self.importWidget)

