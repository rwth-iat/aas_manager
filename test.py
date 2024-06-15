#  Copyright (C) Igor Garmaev, IAT der RWTH Aachen
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import sys
import logging
import time
import signal
from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex, QTimer, QAbstractItemModel, QPoint
from PyQt6.QtGui import QClipboard, QPalette, QColor, QMouseEvent, QKeyEvent, QAction
from PyQt6 import QtWidgets
from aas_editor import *

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w",
                    format="%(asctime)s | %(levelname)s | %(message)s")


# class TimeOutException(Exception):
#    pass
#
#
# def alarm_handler(signum, frame):
#    raise TimeOutException()


logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w",
                    format="%(asctime)s | %(levelname)s | %(message)s")


def main():
    app = QtWidgets.QApplication(sys.argv)

    from aas_editor.editorApp import EditorApp as CurrentApp
    from basyx.aas.model import Submodel

    fileToOpen = sys.argv[1] if len(sys.argv) > 1 else None
    window = CurrentApp(fileToOpen)
    window.show()

    tree = window.mainTreeView
    tree.expandAll()
    model = tree.model()
    root = model.index(0, 0)

    if root.isValid():
        root_data = model.data(root)
        print(f"Iterating Through {root_data}")
        for row in range(model.rowCount(root)):
            item_index = model.index(row, 0, root)
            item_data = model.data(item_index)
            print(f"Itering Items Under {item_data}")
            for subrow in range(model.rowCount(item_index)):
                subitem_index = model.index(subrow, 0, item_index)
                subitem_data = model.data(subitem_index)
                print(f"Item: {subitem_data}")

            # if item_data == "submodels":
            #    signal.signal(signal.SIGALRM, alarm_handler)
            #    signal.alarm(1)
            #    try:
            #        print("Add dialog for a new submodel")
            #        tree.addItemWithDialog(item_data, Submodel)
            #    except:
            #        print("Dialog timed out")
            #    signal.alarm(0)
    app.exec()


if __name__ == "__main__":

    main()
