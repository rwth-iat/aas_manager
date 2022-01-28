#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

SC_COPY = QKeySequence.Copy
SC_CUT = QKeySequence.Cut
SC_PASTE = QKeySequence.Paste
SC_DELETE = QKeySequence.Delete
SC_NEW = QKeySequence.New
SC_REDO = QKeySequence.Redo
SC_UNDO = QKeySequence.Undo
SC_ZOOM_IN = QKeySequence(Qt.CTRL + Qt.Key_Plus)
SC_ZOOM_OUT = QKeySequence(Qt.CTRL + Qt.Key_Minus)
SC_EXPAND_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Plus)
SC_EXPAND_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Plus)
SC_COLLAPSE_RECURS = QKeySequence(Qt.CTRL + Qt.ALT + Qt.Key_Minus)
SC_COLLAPSE_ALL = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Minus)
SC_OPEN = QKeySequence(Qt.CTRL + Qt.Key_O)
SC_SAVE_ALL = QKeySequence(Qt.CTRL + Qt.Key_S)
SC_BACK = QKeySequence.Back
SC_FORWARD = QKeySequence.Forward
SC_SEARCH = QKeySequence(Qt.CTRL + Qt.Key_F)
