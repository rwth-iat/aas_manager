#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

SC_COPY = QKeySequence.StandardKey.Copy
SC_CUT = QKeySequence.StandardKey.Cut
SC_PASTE = QKeySequence.StandardKey.Paste
SC_DELETE = QKeySequence.StandardKey.Delete
SC_NEW = QKeySequence.StandardKey.New
SC_REDO = QKeySequence.StandardKey.Redo
SC_UNDO = QKeySequence.StandardKey.Undo
SC_EDIT_IN_DIALOG = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_E)
SC_ZOOM_IN = QKeySequence(QKeySequence.StandardKey.ZoomIn)
SC_ZOOM_OUT = QKeySequence(QKeySequence.StandardKey.ZoomOut)
SC_BACK = QKeySequence.StandardKey.Back
SC_FORWARD = QKeySequence.StandardKey.Forward
SC_SEARCH = QKeySequence(QKeySequence.StandardKey.Find)
SC_OPEN = QKeySequence(QKeySequence.StandardKey.Open)
SC_SAVE_ALL = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_S)
SC_EXPAND_RECURS = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Plus)
SC_EXPAND = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Right)
SC_EXPAND_ALL = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_Plus)
SC_COLLAPSE = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Left)
SC_COLLAPSE_RECURS = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier | Qt.Key.Key_Minus)
SC_COLLAPSE_ALL = QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier | Qt.Key.Key_Minus)
